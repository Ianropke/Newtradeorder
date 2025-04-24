from flask import Blueprint, request, jsonify
from ..engine import BudgetManager
from ..models import Country
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

budget_blueprint = Blueprint('budget', __name__)

@budget_blueprint.route('/api/countries/<country_id>/budget', methods=['GET'])
def get_country_budget(country_id):
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    return jsonify(country.budget)

@budget_blueprint.route('/api/countries/<country_id>/budget', methods=['POST'])
def update_budget_allocation(country_id):
    data = request.json
    if not data or 'category' not in data or 'amount' not in data:
        return jsonify({"error": "Missing required parameters: category and amount"}), 400
    
    category = data['category']
    amount = data['amount']
    
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({"error": "Amount must be a number"}), 400
    
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    budget_manager = BudgetManager(game_engine.economic_model)
    result = budget_manager.adjust_budget_allocation(country, category, amount)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@budget_blueprint.route('/api/countries/<country_id>/subsidies', methods=['GET'])
def get_country_subsidies(country_id):
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    return jsonify(country.subsidies)

@budget_blueprint.route('/api/countries/<country_id>/subsidies/<sector_name>', methods=['POST'])
def add_subsidy(country_id, sector_name):
    data = request.json
    if not data or 'percentage' not in data:
        return jsonify({"error": "Missing required parameter: percentage"}), 400
    
    subsidy_percentage = data['percentage']
    
    try:
        subsidy_percentage = float(subsidy_percentage)
        if subsidy_percentage < 0 or subsidy_percentage > 100:
            return jsonify({"error": "Percentage must be between 0 and 100"}), 400
    except ValueError:
        return jsonify({"error": "Percentage must be a number"}), 400
    
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    budget_manager = BudgetManager(game_engine.economic_model)
    effects = budget_manager.manage_subsidies(country, sector_name, subsidy_percentage)
    
    if "error" in effects:
        return jsonify(effects), 400
    
    return jsonify({
        "message": f"Subsidy of {subsidy_percentage}% applied to {sector_name}",
        "effects": effects,
        "budget": country.budget
    })

@budget_blueprint.route('/api/countries/<country_id>/subsidies/<sector_name>', methods=['DELETE'])
def remove_subsidy(country_id, sector_name):
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    if sector_name not in country.subsidies:
        return jsonify({"error": f"No subsidy found for sector {sector_name}"}), 404
    
    budget_manager = BudgetManager(game_engine.economic_model)
    result = budget_manager.remove_subsidy(country, sector_name)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@budget_blueprint.route('/api/budget/categories', methods=['GET'])
def get_budget_categories():
    categories = {
        "revenue": ["taxation", "tariffs", "other"],
        "expenses": ["subsidies", "social_services", "defense", "infrastructure", "education", "healthcare"]
    }
    
    return jsonify(categories)

@budget_blueprint.route('/api/countries/<country_id>/calibrate', methods=['POST'])
def calibrate_economic_parameters(country_id):
    data = request.json
    target_metrics = data.get('target_metrics', ['gdp_growth', 'inflation', 'unemployment'])
    
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    if not hasattr(game_engine, 'historical_data') or not game_engine.historical_data.loaded:
        return jsonify({"error": "Historical data not available for calibration"}), 400
    
    calibrator = game_engine.economic_calibrator
    if not calibrator:
        from ..engine import EconomicCalibrator
        calibrator = EconomicCalibrator(game_engine.historical_data)
        game_engine.economic_calibrator = calibrator
    
    original_params = country.economic_model.copy() if hasattr(country, 'economic_model') else {}
    
    try:
        calibrated_params = calibrator.calibrate_parameters(country_id, 
                                                          country.economic_model, 
                                                          target_metrics)
        
        country.economic_model = calibrated_params
        
        report = calibrator.get_calibration_report(country_id)
        
        return jsonify({
            "message": f"Economic parameters for {country_id} have been calibrated",
            "original_params": original_params,
            "calibrated_params": calibrated_params,
            "report": report
        })
    except Exception as e:
        return jsonify({"error": f"Calibration failed: {str(e)}"}), 500

@budget_blueprint.route('/api/budget/<country_id>/subsidies/preview', methods=['POST'])
def preview_subsidy_effects(country_id):
    data = request.json
    if not data or 'sector' not in data or 'percentage' not in data:
        return jsonify({"error": "Missing required parameters: sector and percentage"}), 400
    
    sector_name = data['sector']
    subsidy_percentage = data['percentage']
    
    try:
        subsidy_percentage = float(subsidy_percentage)
        if subsidy_percentage < 0 or subsidy_percentage > 100:
            return jsonify({"error": "Percentage must be between 0 and 100"}), 400
    except ValueError:
        return jsonify({"error": "Percentage must be a number"}), 400
    
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    target_sector = None
    for sector in country.sectors:
        if sector.name.lower() == sector_name.lower():
            target_sector = sector
            break
    
    if not target_sector:
        return jsonify({"error": f"Sector '{sector_name}' not found"}), 404
    
    budget_manager = BudgetManager(game_engine.economic_model)
    
    subsidy_fraction = subsidy_percentage / 100.0
    
    output_boost_efficiency = 0.7
    subsidy_amount = target_sector.output * subsidy_fraction
    output_boost = subsidy_amount * output_boost_efficiency
    
    employment_boost_percentage = subsidy_fraction * 0.5
    unemployment_reduction = target_sector.unemployment_rate * employment_boost_percentage
    
    price_reduction_percentage = subsidy_fraction * 0.3 * 100
    
    export_increase_percentage = 0
    if subsidy_percentage > 5:
        export_increase_percentage = price_reduction_percentage * 1.5
    
    preview_data = {
        "annual_cost": subsidy_amount,
        "output_increase": output_boost,
        "output_increase_percentage": (output_boost / target_sector.output) * 100 if target_sector.output > 0 else 0,
        "unemployment_reduction": unemployment_reduction,
        "price_reduction_percentage": price_reduction_percentage,
        "export_increase_percentage": export_increase_percentage
    }
    
    return jsonify(preview_data)

@budget_blueprint.route('/api/budget/<country_id>/historical', methods=['GET'])
def get_historical_budgets(country_id):
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    if not hasattr(country, 'budget_history') or not country.budget_history:
        current_year = game_engine.current_year
        history = []
        
        current_budget = country.budget
        gdp_baseline = country.gdp
        
        for year in range(current_year - 10, current_year):
            year_factor = (year - (current_year - 10)) / 10
            gdp_variation = gdp_baseline * (0.85 + year_factor * 0.25)
            
            gdp_ratio = gdp_variation / gdp_baseline
            
            year_budget = {
                "year": year,
                "gdp": gdp_variation,
                "totalRevenue": current_budget["totalRevenue"] * gdp_ratio * (0.9 + (year_factor * 0.2)),
                "totalExpenditure": current_budget["totalExpenditure"] * gdp_ratio * (0.85 + (year_factor * 0.3)),
                "balance": 0,
                "debt": current_budget["debt"] * (0.7 + year_factor * 0.4)
            }
            
            year_budget["balance"] = year_budget["totalRevenue"] - year_budget["totalExpenditure"]
            
            history.append(year_budget)
        
        return jsonify({"history": history})
    
    return jsonify({"history": country.budget_history})

@budget_blueprint.route('/api/budget/<country_id>/simulate', methods=['POST'])
def simulate_budget_effects(country_id):
    data = request.json
    if not data or 'category' not in data or 'value' not in data:
        return jsonify({"error": "Missing required parameters: category and value"}), 400
    
    category = data['category']
    new_value = float(data['value'])
    
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    if category not in country.budget['expenses']:
        return jsonify({"error": f"Budget category '{category}' not found"}), 400
    
    current_value = country.budget['expenses'][category]
    
    budget_manager = BudgetManager(game_engine.economic_model)
    
    effects = budget_manager._calculate_budget_allocation_effects(country, category, current_value, new_value)
    
    total_revenue = country.budget['totalRevenue']
    total_expenses = sum([
        value if expense != category else new_value 
        for expense, value in country.budget['expenses'].items()
    ])
    new_balance = total_revenue - total_expenses
    
    change = new_value - current_value
    change_ratio = change / country.gdp if country.gdp > 0 else 0
    
    gdp_growth_change = 0
    unemployment_change = 0
    inflation_change = 0
    approval_change = 0
    
    if category == 'education':
        gdp_growth_change = change_ratio * 0.5
        unemployment_change = -change_ratio * 0.2
        approval_change = change_ratio * 0.7
    elif category == 'healthcare':
        gdp_growth_change = change_ratio * 0.3
        approval_change = change_ratio * 0.8
    elif category == 'infrastructure':
        gdp_growth_change = change_ratio * 0.7
        unemployment_change = -change_ratio * 0.4
        inflation_change = change_ratio * 0.1
        approval_change = change_ratio * 0.5
    elif category == 'defense':
        inflation_change = change_ratio * 0.3
        approval_change = change_ratio * 0.4
    elif category == 'social_services':
        unemployment_change = -change_ratio * 0.3
        inflation_change = change_ratio * 0.2
        approval_change = change_ratio * 1.0
    elif category == 'subsidies':
        gdp_growth_change = change_ratio * 0.4
        unemployment_change = -change_ratio * 0.5
        inflation_change = change_ratio * 0.4
        approval_change = change_ratio * 0.6
    
    descriptions = {
        'education': [
            "Increasing education budget will improve long-term economic growth and workforce quality.",
            "Decreasing education spending may limit future economic potential and innovation."
        ],
        'healthcare': [
            "Higher healthcare spending improves workforce productivity and public wellbeing.",
            "Reducing healthcare budget may impact workforce availability and productivity."
        ],
        'infrastructure': [
            "Infrastructure investments boost economic capacity and create jobs.",
            "Cutting infrastructure spending can limit economic growth potential."
        ],
        'defense': [
            "Increased defense spending strengthens security but diverts resources from productive sectors.",
            "Defense budget reduction may free up resources for other areas but could impact security."
        ],
        'social_services': [
            "Expanding social services improves social stability and supports vulnerable populations.",
            "Reducing social spending may increase inequality and social tensions."
        ],
        'subsidies': [
            "Increased subsidies can support specific sectors but may distort markets.",
            "Reducing subsidies promotes market efficiency but may cause short-term economic pain."
        ]
    }
    
    description = descriptions.get(category, ["Budget changes will impact economic performance."])[0 if change > 0 else 1]
    
    simulation_results = {
        "gdpGrowthChange": gdp_growth_change,
        "unemploymentChange": unemployment_change,
        "inflationChange": inflation_change,
        "approvalChange": approval_change,
        "newBalance": new_balance,
        "description": description,
        "effects": effects
    }
    
    return jsonify(simulation_results)

@budget_blueprint.route('/api/budget/<country_id>', methods=['GET'])
def get_budget(country_id):
    from main import game_engine
    
    try:
        country = game_engine.countries.get(country_id.upper())
        if not country:
            return jsonify({"error": f"Country with ID {country_id} not found"}), 404
        
        budget_data = {
            "gdp": country.gdp,
            "balance": country.budget.get('balance', 0),
            "debt": country.budget.get('debt', 0),
            "debt_to_gdp_ratio": country.budget.get('debt_to_gdp_ratio', 0),
            "totalRevenue": sum(country.budget.get('revenue', {}).values()),
            "totalExpenditure": sum(country.budget.get('expenses', {}).values()),
            "revenue": country.budget.get('revenue', {}),
            "expenses": country.budget.get('expenses', {}),
            "editableCategories": [
                "education", "healthcare", "infrastructure", 
                "military", "social_services", "research_development"
            ],
            "economicImpact": {
                "growthEffect": country.budget.get('growth_effect', 0),
                "employmentEffect": country.budget.get('employment_effect', 0),
                "investmentEffect": country.budget.get('investment_effect', 0),
                "publicApproval": country.budget.get('approval_effect', 0)
            }
        }
        
        return jsonify(budget_data)
        
    except Exception as e:
        logger.error(f"Error fetching budget: {e}")
        return jsonify({"error": str(e)}), 500

@budget_blueprint.route('/api/budget/<country_id>/allocate', methods=['POST'])
def allocate_budget(country_id):
    from main import game_engine
    
    try:
        data = request.get_json()
        if not data or 'category' not in data or 'value' not in data:
            return jsonify({"error": "Missing required data (category, value)"}), 400
        
        country = game_engine.countries.get(country_id.upper())
        if not country:
            return jsonify({"error": f"Country with ID {country_id} not found"}), 404
        
        category = data['category']
        value = float(data['value'])
        
        editable_categories = [
            "education", "healthcare", "infrastructure", 
            "military", "social_services", "research_development"
        ]
        
        if category not in editable_categories:
            return jsonify({"error": f"Category {category} is not editable"}), 400
        
        previous_value = country.budget.get('expenses', {}).get(category, 0)
        
        effects = game_engine.budget_manager.adjust_budget_allocation(country, category, value)
        
        store_budget_impact(country_id, category, previous_value, value, effects)
        
        return jsonify({
            "success": True,
            "message": f"Budget for {category} has been adjusted to {value}",
            "effects": effects
        })
        
    except Exception as e:
        logger.error(f"Error allocating budget: {e}")
        return jsonify({"error": str(e)}), 500

@budget_blueprint.route('/api/budget/<country_id>/impact-history', methods=['GET'])
def get_impact_history(country_id):
    from main import game_engine
    
    try:
        country = game_engine.countries.get(country_id.upper())
        if not country:
            return jsonify({"error": f"Country with ID {country_id} not found"}), 404
        
        impact_history = get_budget_impact_history(country_id)
        
        return jsonify({
            "history": impact_history
        })
        
    except Exception as e:
        logger.error(f"Error getting impact history: {e}")
        return jsonify({"error": str(e)}), 500

def get_budget_impact_history(country_id):
    from main import game_engine
    
    if hasattr(game_engine, 'state_manager') and hasattr(game_engine.state_manager, 'budget_impact_history'):
        return game_engine.state_manager.budget_impact_history.get(country_id, {})
    
    try:
        import os
        history_file = os.path.join('data', 'budget_impacts', f'{country_id}.json')
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load budget impact history from file: {e}")
    
    return {}

def store_budget_impact(country_id, category, previous_value, new_value, effects):
    from main import game_engine
    
    impact_data = {
        "gdpGrowthChange": effects.get('gdp_effect', 0),
        "unemploymentChange": effects.get('unemployment_effect', 0),
        "inflationChange": effects.get('inflation_effect', 0),
        "approvalChange": effects.get('approval_effect', 0),
        "timestamp": effects.get('timestamp', ''),
        "prior_amount": previous_value,
        "new_amount": new_value,
        "description": effects.get('description', '')
    }
    
    if hasattr(game_engine, 'state_manager'):
        if not hasattr(game_engine.state_manager, 'budget_impact_history'):
            game_engine.state_manager.budget_impact_history = {}
        
        if country_id not in game_engine.state_manager.budget_impact_history:
            game_engine.state_manager.budget_impact_history[country_id] = {}
        
        if category not in game_engine.state_manager.budget_impact_history[country_id]:
            game_engine.state_manager.budget_impact_history[country_id][category] = []
        
        history = game_engine.state_manager.budget_impact_history[country_id][category]
        history.append(impact_data)
        game_engine.state_manager.budget_impact_history[country_id][category] = history[-10:]
    
    try:
        import os
        
        os.makedirs(os.path.join('data', 'budget_impacts'), exist_ok=True)
        
        history_file = os.path.join('data', 'budget_impacts', f'{country_id}.json')
        history = {}
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        
        if category not in history:
            history[category] = []
        
        history[category].append(impact_data)
        history[category] = history[category][-10:]
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        logger.warning(f"Could not save budget impact to file: {e}")