from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime

from models import GameState, EventSystem
from routes.countries import countries_blueprint
from routes.policy import policy_blueprint
from routes.diplomacy import diplomacy_blueprint
from routes.events import events_blueprint
from routes.budget import budget_blueprint
from diplomacy_ai import DiplomacyAI, AIExplanationSystem
from engine import GameEngine, HistoricalDataset, EconomicCalibrator, BudgetManager, EnhancedFeedbackSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize game engine and components
game_engine = GameEngine('data/countries.json')

# Create data directories if they don't exist
for dir_path in ['data/budget_impacts', 'data/historical_data']:
    os.makedirs(dir_path, exist_ok=True)

# Initialize historical dataset
try:
    historical_data_path = os.path.join('data', 'historical_data', 'economic_data.json')
    if os.path.exists(historical_data_path):
        game_engine.historical_dataset = HistoricalDataset(historical_data_path)
        logger.info(f"Loaded historical dataset from {historical_data_path}")
    else:
        logger.warning(f"No historical data file found at {historical_data_path}. Will generate mock data.")
        # Create a default historical dataset with mock data
        game_engine.historical_dataset = HistoricalDataset()
except Exception as e:
    logger.error(f"Error loading historical dataset: {e}")
    game_engine.historical_dataset = None

# Initialize state manager for persistent data
game_engine.state_manager = type('StateManager', (), {
    'budget_impact_history': {},
    'decision_history': {},
    'player_preferences': {}
})()

# Initialize other advanced components
game_engine.budget_manager = BudgetManager(game_engine)
game_engine.economic_calibrator = EconomicCalibrator(game_engine.historical_dataset) if game_engine.historical_dataset else None
game_engine.feedback_system = EnhancedFeedbackSystem(game_engine)

# Initialize game state
game_state = GameState()
game_state.load_countries()
game_state.current_turn = 0
game_state.current_year = datetime.now().year  # Start in current year
game_engine.current_year = game_state.current_year

# Initialize diplomacy AI system with explanation capabilities
diplomacy_ai = DiplomacyAI(game_state)
diplomacy_ai.initialize_personalities(game_state.countries)
diplomacy_ai.explanation_system = AIExplanationSystem()
if not hasattr(game_state, 'diplomacy'):
    game_state.diplomacy = type('obj', (), {})()
game_state.diplomacy.ai = diplomacy_ai

# Initialize event system
events_module_event_system = EventSystem()
# Make the event_system variable in events.py point to our instance
import routes.events
routes.events.event_system = events_module_event_system
game_state.events = events_module_event_system

# Register blueprints
app.register_blueprint(countries_blueprint, url_prefix='/api')
app.register_blueprint(policy_blueprint, url_prefix='/api')
app.register_blueprint(diplomacy_blueprint, url_prefix='/api')
app.register_blueprint(events_blueprint, url_prefix='/api')
app.register_blueprint(budget_blueprint, url_prefix='/api')

@app.route('/api/status', methods=['GET'])
def status():
    """Get the current status of the game system"""
    return jsonify({
        'status': 'running',
        'version': '0.3.0',
        'countries_loaded': len(game_state.countries),
        'active_events': len(routes.events.event_system.events),
        'current_turn': game_state.current_turn,
        'current_year': game_state.current_year,
        'diplomacy_ai_initialized': hasattr(game_state, 'diplomacy') and hasattr(game_state.diplomacy, 'ai'),
        'historical_data_available': game_engine.historical_dataset is not None,
        'budget_manager_initialized': hasattr(game_engine, 'budget_manager'),
        'economic_calibrator_available': game_engine.economic_calibrator is not None,
        'feedback_system_initialized': hasattr(game_engine, 'feedback_system')
    })

@app.route('/api/turn', methods=['POST'])
def advance_turn():
    """Advance the game by one turn"""
    # Process turn logic using game engine
    game_state.current_turn += 1
    game_state.current_year += 1  # Advance one year per turn
    game_engine.current_year = game_state.current_year
    
    # Set player country if not already set (temporary - should be set through proper route)
    if not hasattr(game_state, 'player_country_iso') or not game_state.player_country_iso:
        if game_state.countries:
            game_state.player_country_iso = list(game_state.countries.keys())[0]  # First country as player by default
    
    # Pass required attributes to game engine
    game_engine.current_turn = game_state.current_turn
    game_engine.player_country_iso = getattr(game_state, 'player_country_iso', None)
    if hasattr(game_state, 'diplomacy'):
        game_engine.diplomacy = game_state.diplomacy
    
    # AI decisions for each country
    ai_decisions = []
    for country_iso, country in game_state.countries.items():
        if country_iso != game_state.player_country_iso:  # Skip player country
            if hasattr(game_state, 'diplomacy') and hasattr(game_state.diplomacy, 'ai'):
                # Run AI decision logic
                decisions = game_state.diplomacy.ai.ai_turn_logic(country_iso, game_state.current_turn)
                if decisions:
                    ai_decisions.append({
                        'country': country_iso,
                        'decisions': decisions,
                        'explanation': game_state.diplomacy.ai.explanation_system.generate_explanation(
                            country_iso, decisions, game_state
                        ) if hasattr(game_state.diplomacy.ai, 'explanation_system') else None
                    })
    
    # Update economy for all countries
    for country in game_state.countries.values():
        game_state.update_economy(country.iso_code)
    
    # Generate events using our new system
    import event_types
    new_events = event_types.check_and_trigger_events(game_state)
    
    # Add new events to the event system
    for event in new_events:
        routes.events.event_system.add_event(event)
    
    # Apply immediate event effects
    game_engine._apply_event_effects(new_events)
    
    # Update active events and remove expired ones
    game_engine._update_active_events()
    
    # Generate enhanced feedback using the feedback system
    feedback = None
    player_country = game_state.countries.get(game_state.player_country_iso)
    if player_country and hasattr(game_engine, 'feedback_system'):
        feedback = game_engine.feedback_system.generate_turn_feedback(
            player_country, 
            game_state.current_turn, 
            new_events
        )
    
    # Generate turn summary
    turn_summary = game_engine._generate_turn_summary(game_state) if hasattr(game_engine, '_generate_turn_summary') else None
    
    return jsonify({
        'message': f'Advanced to turn {game_state.current_turn} (Year {game_state.current_year})',
        'new_events': new_events,
        'ai_decisions': ai_decisions,
        'turn_summary': turn_summary,
        'feedback': feedback
    })

if __name__ == '__main__':
    # Initialize strategic interests for AI
    if hasattr(game_state, 'diplomacy') and hasattr(game_state.diplomacy, 'ai'):
        # Initialize with empty relations for now
        game_state.diplomacy.ai.calculate_strategic_interests(game_state.countries, [])
    
    app.run(debug=True, port=5000)
