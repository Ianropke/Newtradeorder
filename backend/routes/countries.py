from flask import Blueprint, request, jsonify
import json
import os
import numpy as np
from datetime import datetime
from models import GameState
from engine import HistoricalDataset
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
countries_blueprint = Blueprint('countries', __name__)

# Initialize historical dataset
historical_data = HistoricalDataset(os.path.join('data', 'historical_data.json'))

# Get game state reference (it will be properly initialized in main.py)
game_state = GameState()

@countries_blueprint.route('/countries', methods=['GET'])
def get_countries():
    """Get all countries"""
    from main import game_engine
    
    country_data = {}
    for iso, country in game_engine.countries.items():
        country_dict = country_to_dict(country)
        country_data[iso] = country_dict
    
    # Return as array for frontend compatibility
    return jsonify(list(country_data.values()))

@countries_blueprint.route('/countries/<country_id>', methods=['GET'])
def get_country(country_id):
    """Get a specific country by ISO code"""
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    return jsonify(country_to_dict(country))

@countries_blueprint.route('/countries/<country_id>/historical-benchmarks', methods=['GET'])
def get_historical_benchmarks(country_id):
    """
    Get historical benchmark data for a specific country.
    Includes economic metrics compared to regional and global averages.
    """
    from main import game_engine
    
    try:
        country = game_engine.countries.get(country_id.upper())
        if not country:
            return jsonify({"error": f"Country with ID {country_id} not found"}), 404
        
        historical_dataset = getattr(game_engine, 'historical_dataset', None)
        
        if not historical_dataset:
            return generate_mock_historical_data(country)
        
        benchmarks = historical_dataset.get_country_benchmarks(country_id.upper())
        
        if not benchmarks or not benchmarks.get('metrics'):
            return generate_mock_historical_data(country)
            
        benchmarks['status'] = 'real'
        benchmarks['country_name'] = country.name
        benchmarks['region'] = country.region
        benchmarks['key_events'] = get_key_historical_events(country_id.upper(), historical_dataset)
        benchmarks['performance'] = calculate_performance_metrics(benchmarks)
        
        return jsonify(benchmarks)
        
    except Exception as e:
        logger.error(f"Error fetching historical benchmarks: {e}")
        if 'country' in locals() and country:
            return generate_mock_historical_data(country)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def generate_mock_historical_data(country):
    """Generate mock historical data when actual data is unavailable"""
    logger.info(f"Generating mock historical data for {country.name}")
    
    years = []
    current_year = datetime.now().year
    
    # Generate last 10 years
    for i in range(10):
        years.append(current_year - 9 + i)
    
    # Generate metrics with country, regional and global values
    metrics = {
        'gdp_growth': {
            'country_values': [round((np.random.random() * 6) - 0.5, 2) for _ in range(10)],
            'regional_values': [round((np.random.random() * 4) + 0.5, 2) for _ in range(10)],
            'global_values': [round((np.random.random() * 3) + 1, 2) for _ in range(10)]
        },
        'inflation': {
            'country_values': [round((np.random.random() * 5) + 0.5, 2) for _ in range(10)],
            'regional_values': [round((np.random.random() * 3) + 1, 2) for _ in range(10)],
            'global_values': [round((np.random.random() * 2) + 1.5, 2) for _ in range(10)]
        },
        'unemployment': {
            'country_values': [round((np.random.random() * 8) + 2, 2) for _ in range(10)],
            'regional_values': [round((np.random.random() * 5) + 3, 2) for _ in range(10)],
            'global_values': [round((np.random.random() * 3) + 4, 2) for _ in range(10)]
        },
        'trade_balance': {
            'country_values': [round((np.random.random() * 14) - 7, 2) for _ in range(10)],
            'regional_values': [round((np.random.random() * 10) - 5, 2) for _ in range(10)],
            'global_values': [round((np.random.random() * 6) - 3, 2) for _ in range(10)]
        }
    }
    
    # Generate key historical events
    key_events = [
        {
            'year': years[2],
            'event': 'Handelspolitisk reform',
            'impact': 'Positive',
            'magnitude': 'Medium'
        },
        {
            'year': years[5],
            'event': 'Global økonomisk krise',
            'impact': 'Negative',
            'magnitude': 'High'
        },
        {
            'year': years[8],
            'event': 'Teknologisk gennembrud',
            'impact': 'Positive',
            'magnitude': 'Medium'
        }
    ]
    
    # Calculate performance metrics
    latestYearIndex = 9  # Last index
    performance = {
        'gdp_growth': metrics['gdp_growth']['country_values'][latestYearIndex],
        'region_gdp_growth': metrics['gdp_growth']['regional_values'][latestYearIndex],
        'relative_performance': metrics['gdp_growth']['country_values'][latestYearIndex] - 
                             metrics['gdp_growth']['regional_values'][latestYearIndex],
        'unemployment': metrics['unemployment']['country_values'][latestYearIndex],
        'region_unemployment': metrics['unemployment']['regional_values'][latestYearIndex],
        'unemployment_performance': metrics['unemployment']['regional_values'][latestYearIndex] - 
                                metrics['unemployment']['country_values'][latestYearIndex]
    }
    
    # Return complete mock data in the expected format
    return jsonify({
        'status': 'mock',
        'message': 'Using simulated historical data',
        'country_name': country.name,
        'region': country.region,
        'years': years,
        'metrics': metrics,
        'performance': performance,
        'key_events': key_events
    })

def get_key_historical_events(country_iso, historical_dataset):
    """Get key historical economic events for a specific country"""
    return [
        {"year": 2008, "event": "Global Financial Crisis", "impact": "Negative", "magnitude": "High", 
         "description": "Severe global economic downturn triggered by a financial crisis originating in the US housing market."},
        {"year": 2020, "event": "COVID-19 Pandemic", "impact": "Negative", "magnitude": "Very High", 
         "description": "Worldwide economic shutdown due to the coronavirus pandemic, causing significant disruption to global trade and economic activity."}
    ]

def calculate_performance_metrics(benchmark_data):
    """Calculate economic performance metrics based on historical data"""
    if not benchmark_data or 'metrics' not in benchmark_data or 'years' not in benchmark_data:
        return {}
    
    years = benchmark_data['years']
    if not years:
        return {}
    
    latest_year_idx = len(years) - 1
    
    metrics = benchmark_data['metrics']
    performance = {}
    
    if 'gdp_growth' in metrics:
        gdp_data = metrics['gdp_growth']
        if 'country_values' in gdp_data and 'regional_values' in gdp_data and len(gdp_data['country_values']) > latest_year_idx:
            performance['gdp_growth'] = gdp_data['country_values'][latest_year_idx]
            performance['region_gdp_growth'] = gdp_data['regional_values'][latest_year_idx]
            performance['relative_performance'] = performance['gdp_growth'] - performance['region_gdp_growth']
    
    if 'unemployment' in metrics:
        unemp_data = metrics['unemployment']
        if 'country_values' in unemp_data and 'regional_values' in unemp_data and len(unemp_data['country_values']) > latest_year_idx:
            performance['unemployment'] = unemp_data['country_values'][latest_year_idx]
            performance['region_unemployment'] = unemp_data['regional_values'][latest_year_idx]
            performance['unemployment_performance'] = performance['region_unemployment'] - performance['unemployment']
    
    if 'trade_balance' in metrics:
        trade_data = metrics['trade_balance']
        if 'country_values' in trade_data and len(trade_data['country_values']) > latest_year_idx:
            performance['trade_balance'] = trade_data['country_values'][latest_year_idx]
    
    return performance

def country_to_dict(country):
    """Convert country object to dictionary representation"""
    return {
        "name": country.name,
        "iso_code": country.iso_code,
        "region": getattr(country, 'region', None),
        "gdp": getattr(country, 'gdp', None),
        "growth_rate": getattr(country, 'growth_rate', None),
        "unemployment_rate": getattr(country, 'unemployment_rate', None),
        "inflation_rate": getattr(country, 'inflation_rate', None),
        "exports": getattr(country, 'exports', None),
        "imports": getattr(country, 'imports', None)
    }

@countries_blueprint.route('/trade_partners/<country_id>', methods=['GET'])
def get_trade_partners(country_id):
    """
    Get the trade partners for a specific country.
    Returns detailed information about imports, exports, and trade balances.
    """
    from main import game_engine
    
    try:
        country = game_engine.countries.get(country_id.upper())
        if not country:
            return jsonify({"error": f"Country with ID {country_id} not found"}), 404
        
        partners = []
        
        if hasattr(country, 'trade_partners') and country.trade_partners:
            for partner_iso, trade_data in country.trade_partners.items():
                partner_country = game_engine.countries.get(partner_iso)
                
                if not partner_country:
                    continue
                
                import_volume = trade_data.get('imports', 0)
                export_volume = trade_data.get('exports', 0)
                trade_volume = import_volume + export_volume
                trade_balance = export_volume - import_volume
                
                dependency_score = trade_volume / max(1, getattr(country, 'gdp', 10000))
                
                partners.append({
                    'country': {
                        'name': partner_country.name,
                        'iso_code': partner_country.iso_code,
                        'region': getattr(partner_country, 'region', None)
                    },
                    'iso_code': partner_country.iso_code,
                    'importVolume': import_volume,
                    'exportVolume': export_volume,
                    'tradeVolume': trade_volume,
                    'tradeBalance': trade_balance,
                    'dependencyScore': dependency_score,
                    'isCritical': dependency_score > 0.05
                })
            
            partners.sort(key=lambda x: x['tradeVolume'], reverse=True)
        
        # If no trade partners are found, generate some mock data
        if not partners:
            partners = generate_mock_trade_partners(country, game_engine.countries)
            
        return jsonify({
            "partners": partners
        })
        
    except Exception as e:
        logger.error(f"Error fetching trade partners: {e}")
        # Generate mock data in case of error
        try:
            partners = generate_mock_trade_partners(game_engine.countries.get(country_id.upper()), 
                                                   game_engine.countries)
            return jsonify({"partners": partners, "status": "mock"})
        except:
            # Return minimal response that frontend can handle
            return jsonify({"partners": [], "error": str(e)})

def generate_mock_trade_partners(country, all_countries):
    """Generate mock trade partner data when actual data is unavailable"""
    logger.info(f"Generating mock trade partners for {country.name}")
    partners = []
    
    # Get a list of countries excluding the current one
    potential_partners = [c for c in all_countries.values() if c.iso_code != country.iso_code]
    
    # If we don't have enough countries, just return empty
    if not potential_partners:
        return []
    
    # Select up to 5 partners
    partner_count = min(5, len(potential_partners))
    for i in range(partner_count):
        partner = potential_partners[i]
        
        # Generate reasonable mock trade values
        country_gdp = getattr(country, 'gdp', 100000)
        import_volume = round(np.random.random() * country_gdp * 0.05, 2)
        export_volume = round(np.random.random() * country_gdp * 0.05, 2)
        trade_volume = import_volume + export_volume
        trade_balance = export_volume - import_volume
        
        dependency_score = trade_volume / max(1, country_gdp)
        
        partners.append({
            'country': {
                'name': partner.name,
                'iso_code': partner.iso_code, 
                'region': getattr(partner, 'region', None)
            },
            'iso_code': partner.iso_code,
            'importVolume': import_volume,
            'exportVolume': export_volume,
            'tradeVolume': trade_volume,
            'tradeBalance': trade_balance,
            'dependencyScore': dependency_score,
            'isCritical': dependency_score > 0.05
        })
    
    # Sort by trade volume
    partners.sort(key=lambda x: x['tradeVolume'], reverse=True)
    return partners

@countries_blueprint.route('/competitors/<country_id>', methods=['GET'])
def get_competitors(country_id):
    """
    Get the main economic competitors for a specific country.
    Identifies countries with similar economic profiles and export sectors.
    """
    from main import game_engine
    
    try:
        country = game_engine.countries.get(country_id.upper())
        if not country:
            return jsonify({"error": f"Country with ID {country_id} not found"}), 404
        
        competitors = []
        
        for iso, competitor in game_engine.countries.items():
            if iso == country_id.upper():
                continue
            
            overlap_score = 0
            if hasattr(country, 'industries') and hasattr(competitor, 'industries'):
                for industry, percentage in country.industries.items():
                    if industry in competitor.industries:
                        overlap_score += min(percentage, competitor.industries[industry])
            
            gdp_factor = min(competitor.gdp, country.gdp) / max(competitor.gdp, country.gdp)
            competition_intensity = overlap_score * gdp_factor
            
            if competition_intensity > 0.05:
                competitors.append({
                    'country': {
                        'name': competitor.name,
                        'iso_code': competitor.iso_code,
                        'region': getattr(competitor, 'region', None)
                    },
                    'overlapScore': overlap_score,
                    'competitionIntensity': competition_intensity,
                    'mainIndustries': competitor.industries if hasattr(competitor, 'industries') else {}
                })
        
        competitors.sort(key=lambda x: x['competitionIntensity'], reverse=True)
        competitors = competitors[:8]
        
        return jsonify({
            "competitors": competitors
        })
        
    except Exception as e:
        logger.error(f"Error fetching competitors: {e}")
        return jsonify({
            "error": str(e)
        }), 500