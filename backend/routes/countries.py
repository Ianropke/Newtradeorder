from flask import Blueprint, jsonify, request
from models import GameState
from engine import HistoricalDataset
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
countries_bp = Blueprint('countries', __name__)

# Initialize historical dataset
historical_data = HistoricalDataset(os.path.join('data', 'historical_data.json'))

# Get game state reference (it will be properly initialized in main.py)
game_state = GameState()

@countries_bp.route('/countries', methods=['GET'])
def get_countries():
    """Get all countries"""
    if not game_state.countries:
        return jsonify({'error': 'No countries loaded'}), 404
    
    return jsonify({'countries': game_state.countries})

@countries_bp.route('/countries/<iso_code>', methods=['GET'])
def get_country(iso_code):
    """Get a specific country by ISO code"""
    if not game_state.countries or iso_code not in game_state.countries:
        return jsonify({'error': f'Country not found: {iso_code}'}), 404
    
    return jsonify(game_state.countries[iso_code])

@countries_bp.route('/countries/<iso_code>/historical-benchmarks', methods=['GET'])
def get_historical_benchmarks(iso_code):
    """Get historical benchmark data for a country"""
    logger.info(f"Fetching historical benchmarks for {iso_code}")
    try:
        # Get parameters
        start_year = request.args.get('start_year', type=int)
        end_year = request.args.get('end_year', type=int)
        
        # Handle case if historical data isn't loaded or available
        if not historical_data.loaded:
            logger.warning("Historical data not loaded, generating mock data")
            # Return basic structure that frontend can understand
            return jsonify({
                'status': 'mock',
                'message': 'Using generated mock data as historical data is not available',
                'years': list(range(2010, 2025)),
                'metrics': {
                    'gdp_growth': {
                        'country_values': [random_value(2, 3) for _ in range(15)],
                        'regional_values': [random_value(1.5, 2.5) for _ in range(15)],
                        'global_values': [random_value(1, 2) for _ in range(15)]
                    },
                    'inflation': {
                        'country_values': [random_value(1, 4) for _ in range(15)],
                        'regional_values': [random_value(1.5, 3) for _ in range(15)],
                        'global_values': [random_value(2, 2.5) for _ in range(15)]
                    },
                    'unemployment': {
                        'country_values': [random_value(3, 8) for _ in range(15)],
                        'regional_values': [random_value(4, 7) for _ in range(15)],
                        'global_values': [random_value(5, 6) for _ in range(15)]
                    },
                    'trade_balance': {
                        'country_values': [random_value(-3, 3) for _ in range(15)],
                        'regional_values': [random_value(-2, 2) for _ in range(15)],
                        'global_values': [random_value(-1, 1) for _ in range(15)]
                    }
                }
            })
        
        # If country doesn't exist in historical data, provide informative response
        country_data = historical_data.get_historical_data(iso_code, start_year, end_year)
        if not country_data:
            logger.warning(f"No historical data for {iso_code}, returning mock data")
            return jsonify({
                'status': 'mock',
                'message': f'No historical data available for {iso_code}',
                'years': list(range(2010, 2025)),
                'metrics': {
                    'gdp_growth': {'country_values': [], 'regional_values': [], 'global_values': []},
                    'inflation': {'country_values': [], 'regional_values': [], 'global_values': []},
                    'unemployment': {'country_values': [], 'regional_values': [], 'global_values': []},
                    'trade_balance': {'country_values': [], 'regional_values': [], 'global_values': []}
                }
            })
        
        # Convert yearly data to time series format for chart display
        years = sorted([int(year) for year in country_data.keys()])
        metrics = ['gdp_growth', 'inflation', 'unemployment', 'trade_balance']
        
        result = {
            'status': 'success',
            'years': years,
            'metrics': {}
        }
        
        # Process each metric
        for metric in metrics:
            # Get benchmark data including country, regional and global values
            benchmark_data = historical_data.get_benchmark_data(iso_code, metric, years)
            result['metrics'][metric] = benchmark_data
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error retrieving historical data: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Helper function for mock data generation
def random_value(min_val, max_val):
    import random
    return round(random.uniform(min_val, max_val), 2)