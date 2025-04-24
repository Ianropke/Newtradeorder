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

@countries_blueprint.route('/api/countries', methods=['GET'])
def get_countries():
    """Get all countries"""
    from main import game_engine
    
    country_data = {}
    for iso, country in game_engine.countries.items():
        country_dict = country_to_dict(country)
        country_data[iso] = country_dict
    
    return jsonify(country_data)

@countries_blueprint.route('/api/countries/<country_id>', methods=['GET'])
def get_country(country_id):
    """Get a specific country by ISO code"""
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    return jsonify(country_to_dict(country))

@countries_blueprint.route('/api/countries/<country_id>/historical-benchmarks', methods=['GET'])
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
    """
    Generate realistic mock historical data when real data is not available.
    This ensures the frontend can still function and display visualizations.
    """
    current_year = datetime.now().year
    years = list(range(current_year - 10, current_year + 1))
    
    gdp_growth_current = getattr(country, 'growth_rate', 2.0)
    unemployment_current = getattr(country, 'unemployment_rate', 5.0)
    inflation_current = getattr(country, 'inflation_rate', 2.0)
    
    np.random.seed(int(country.iso_code.encode().hex(), 16) % 10000)
    
    base_growth = 2.5
    cycle_amplitude = 1.5
    gdp_values = [
        base_growth + cycle_amplitude * np.sin(i/3) + np.random.normal(0, 0.8) 
        for i in range(len(years))
    ]
    
    base_unemployment = 5.0
    unemployment_values = [
        base_unemployment - 0.7 * gdp_values[max(0, i-1)] + np.random.normal(0, 0.5) 
        for i in range(len(years))
    ]
    unemployment_values = [max(2.0, min(15.0, u)) for u in unemployment_values]
    
    base_inflation = 2.0
    inflation_values = [
        base_inflation + 0.3 * gdp_values[i] + cycle_amplitude * 0.5 * np.sin(i/2 + 1) + np.random.normal(0, 0.7) 
        for i in range(len(years))
    ]
    inflation_values = [max(0.0, min(12.0, inf)) for inf in inflation_values]
    
    trade_balance_values = [
        (getattr(country, 'exports', 0) - getattr(country, 'imports', 0)) / max(1, getattr(country, 'gdp', 100)) * 100 +
        2.0 * np.sin(i/2.5) + np.random.normal(0, 1.5)
        for i in range(len(years))
    ]
    
    crisis_years = {2008: 'financial_crisis', 2020: 'covid_pandemic'}
    for year_idx, year in enumerate(years):
        if year in crisis_years:
            if crisis_years[year] == 'financial_crisis':
                gdp_values[year_idx] = -3.0 + np.random.normal(0, 1.0)
                unemployment_values[year_idx] += 2.0 + np.random.normal(0, 0.5)
                inflation_values[year_idx] = 1.0 + np.random.normal(0, 0.5)
            elif crisis_years[year] == 'covid_pandemic':
                gdp_values[year_idx] = -5.0 + np.random.normal(0, 1.5)
                unemployment_values[year_idx] += 3.0 + np.random.normal(0, 0.8)
                inflation_values[year_idx] = 0.5 + np.random.normal(0, 0.3)
    
    regional_gdp = [v * (0.9 + np.random.normal(0, 0.15)) for v in gdp_values]
    global_gdp = [v * (0.8 + np.random.normal(0, 0.2)) for v in gdp_values]
    
    regional_unemployment = [v * (0.95 + np.random.normal(0, 0.1)) for v in unemployment_values]
    global_unemployment = [v * (0.9 + np.random.normal(0, 0.15)) for v in unemployment_values]
    
    regional_inflation = [v * (0.9 + np.random.normal(0, 0.1)) for v in inflation_values]
    global_inflation = [v * (0.85 + np.random.normal(0, 0.15)) for v in inflation_values]
    
    regional_trade = [v * (0.7 + np.random.normal(0, 0.2)) for v in trade_balance_values]
    global_trade = [v * (0.4 + np.random.normal(0, 0.3)) for v in trade_balance_values]
    
    benchmark_data = {
        "status": "mock",
        "message": "Using generated mock data as real historical data is not available",
        "country_name": country.name,
        "region": getattr(country, 'region', 'Unknown Region'),
        "years": years,
        "metrics": {
            "gdp_growth": {
                "country_values": gdp_values,
                "regional_values": regional_gdp,
                "global_values": global_gdp
            },
            "unemployment": {
                "country_values": unemployment_values,
                "regional_values": regional_unemployment,
                "global_values": global_unemployment
            },
            "inflation": {
                "country_values": inflation_values,
                "regional_values": regional_inflation,
                "global_values": global_inflation
            },
            "trade_balance": {
                "country_values": trade_balance_values,
                "regional_values": regional_trade,
                "global_values": global_trade
            }
        },
        "key_events": [
            {"year": 2008, "event": "Global Financial Crisis", "impact": "Negative", "magnitude": "High", 
             "description": "Severe global economic downturn triggered by a financial crisis originating in the US housing market."},
            {"year": 2020, "event": "COVID-19 Pandemic", "impact": "Negative", "magnitude": "Very High", 
             "description": "Worldwide economic shutdown due to the coronavirus pandemic, causing significant disruption to global trade and economic activity."}
        ]
    }
    
    benchmark_data['performance'] = calculate_performance_metrics(benchmark_data)
    
    return jsonify(benchmark_data)

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

@countries_blueprint.route('/api/trade_partners/<country_id>', methods=['GET'])
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
                
                dependency_score = trade_volume / max(1, country.gdp)
                
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
            
        return jsonify({
            "partners": partners
        })
        
    except Exception as e:
        logger.error(f"Error fetching trade partners: {e}")
        return jsonify({
            "error": str(e)
        }), 500

@countries_blueprint.route('/api/competitors/<country_id>', methods=['GET'])
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