from flask import Flask, jsonify
from flask_cors import CORS
from models import GameState, EventSystem
from routes.countries import countries_bp
from routes.policy import policy_bp
from routes.diplomacy import diplomacy_bp
from routes.events import events_bp, event_system
from diplomacy_ai import DiplomacyAI
from engine import GameEngine

app = Flask(__name__)
CORS(app)

# Initialize game engine
game_engine = GameEngine('data/countries.json')
game_state = GameState()
game_state.load_countries()
game_state.current_turn = 0

# Initialize diplomacy AI system
diplomacy_ai = DiplomacyAI(game_state)
diplomacy_ai.initialize_personalities(game_state.countries)
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
app.register_blueprint(countries_bp, url_prefix='/api')
app.register_blueprint(policy_bp, url_prefix='/api')
app.register_blueprint(diplomacy_bp, url_prefix='/api')
app.register_blueprint(events_bp, url_prefix='/api')

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'running',
        'version': '0.2.0',
        'countries_loaded': len(game_state.countries),
        'active_events': len(routes.events.event_system.events),
        'current_turn': game_state.current_turn,
        'diplomacy_ai_initialized': hasattr(game_state, 'diplomacy') and hasattr(game_state.diplomacy, 'ai')
    })

@app.route('/api/turn', methods=['POST'])
def advance_turn():
    """Advance the game by one turn"""
    # Process turn logic using game engine
    game_state.current_turn += 1
    
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
                        'decisions': decisions
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
    
    return jsonify({
        'message': f'Advanced to turn {game_state.current_turn}',
        'new_events': new_events,
        'ai_decisions': ai_decisions
    })

if __name__ == '__main__':
    # Initialize strategic interests for AI
    if hasattr(game_state, 'diplomacy') and hasattr(game_state.diplomacy, 'ai'):
        # Initialize with empty relations for now
        game_state.diplomacy.ai.calculate_strategic_interests(game_state.countries, [])
    
    app.run(debug=True)
