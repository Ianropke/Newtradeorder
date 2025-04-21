import os
from flask import Flask, jsonify, send_from_directory, request
from engine import GameEngine

# --- Configuration ---
# Determine the absolute path to the project root directory
# This assumes main.py is in the 'backend' folder
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'countries.json')
FRONTEND_FOLDER = os.path.join(PROJECT_ROOT, 'frontend')

# --- Initialization ---
app = Flask(__name__, static_folder=FRONTEND_FOLDER)
try:
    game_engine = GameEngine(DATA_PATH)
except ValueError as e:
    print(f"Error initializing game engine: {e}")
    # Handle error appropriately - maybe exit or provide a default state
    game_engine = None  # Or some fallback

# --- API Endpoints ---
@app.route('/api/countries', methods=['GET'])
def get_countries():
    """API endpoint to get data for all countries."""
    if not game_engine:
        return jsonify({"error": "Game engine not initialized"}), 500
    countries_data = game_engine.get_all_countries_data()
    # Convert Country objects to dictionaries for JSON serialization
    countries_dict = {iso: country.__dict__ for iso, country in countries_data.items()}
    # Convert Industry objects within country dicts
    for iso in countries_dict:
        if hasattr(countries_dict[iso]['industries'], '__dict__'):
            countries_dict[iso]['industries'] = countries_dict[iso]['industries'].__dict__
    return jsonify(countries_dict)

@app.route('/api/countries/<string:iso_code>', methods=['GET'])
def get_country(iso_code):
    """Returns details for a specific country."""
    if not game_engine:
        return jsonify({"error": "Game engine not initialized"}), 500
    details = game_engine.get_country_details(iso_code.upper())
    if details:
        return jsonify(details)
    else:
        return jsonify({"error": "Country not found"}), 404

@app.route('/api/next_turn', methods=['POST'])
def next_turn():
    """Advances the simulation to the next turn."""
    if not game_engine:
        return jsonify({"error": "Game engine not initialized"}), 500
    result = game_engine.advance_turn()
    return jsonify(result)

@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    """API endpoint to get the current game state (e.g., turn number)."""
    if not game_engine:
        return jsonify({"error": "Game engine not initialized"}), 500
    state = {
        'current_turn': game_engine.current_turn,
        'player_country_iso': game_engine.player_country_iso
    }
    return jsonify(state)

@app.route('/api/policy', methods=['POST'])
def apply_policy():
    """API endpoint to apply a policy to a country (tax, gov spending, subsidy, interest, tariff)."""
    if not game_engine:
        return jsonify({"error": "Game engine not initialized"}), 500
    data = request.get_json()
    iso_code = data.get('iso_code', '').upper()
    policy = data.get('policy', {})
    if not iso_code or not policy:
        return jsonify({"error": "iso_code and policy required"}), 400
    result = game_engine.apply_policy(iso_code, policy)
    # Return updated country details
    details = game_engine.get_country_details(iso_code)
    return jsonify({"result": result, "country": details})

# --- Serve Frontend --- 
# Route for serving index.html
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

# Route for serving other static files (CSS, JS, images, etc.)
@app.route('/<path:path>')
def serve_static_files(path):
    # Basic security check: prevent accessing files outside frontend folder
    if '..' in path or path.startswith('/'):
        return "Not Found", 404
    if os.path.exists(os.path.join(FRONTEND_FOLDER, path)):
        return send_from_directory(FRONTEND_FOLDER, path)
    else:
        return send_from_directory(FRONTEND_FOLDER, 'index.html')

# --- Run Application ---
if __name__ == '__main__':
    # Note: debug=True is helpful for development but should be False in production
    app.run(debug=True, port=5001)  # Use a different port like 5001
