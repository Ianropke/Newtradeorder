from flask import Blueprint, request, jsonify
from ..engine import BudgetManager
from ..models import Country

budget_blueprint = Blueprint('budget', __name__)

@budget_blueprint.route('/api/countries/<country_id>/budget', methods=['GET'])
def get_country_budget(country_id):
    # Assuming we have a function to get country from the engine
    # This would normally be pulled from a database or from the engine's state
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    return jsonify(country.budget)

@budget_blueprint.route('/api/countries/<country_id>/budget', methods=['POST'])
def update_budget_allocation(country_id):
    # Get request data
    data = request.json
    if not data or 'category' not in data or 'amount' not in data:
        return jsonify({"error": "Missing required parameters: category and amount"}), 400
    
    category = data['category']
    amount = data['amount']
    
    # Validate amount
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({"error": "Amount must be a number"}), 400
    
    # Get country and update budget
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    # Create budget manager and adjust allocation
    budget_manager = BudgetManager(game_engine.economic_model)
    result = budget_manager.adjust_budget_allocation(country, category, amount)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@budget_blueprint.route('/api/countries/<country_id>/subsidies', methods=['GET'])
def get_country_subsidies(country_id):
    # Get country data
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    return jsonify(country.subsidies)

@budget_blueprint.route('/api/countries/<country_id>/subsidies/<sector_name>', methods=['POST'])
def add_subsidy(country_id, sector_name):
    # Get request data
    data = request.json
    if not data or 'percentage' not in data:
        return jsonify({"error": "Missing required parameter: percentage"}), 400
    
    subsidy_percentage = data['percentage']
    
    # Validate percentage
    try:
        subsidy_percentage = float(subsidy_percentage)
        if subsidy_percentage < 0 or subsidy_percentage > 100:
            return jsonify({"error": "Percentage must be between 0 and 100"}), 400
    except ValueError:
        return jsonify({"error": "Percentage must be a number"}), 400
    
    # Get country and apply subsidy
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    # Create budget manager and apply subsidy
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
    # Get country
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    # Check if subsidy exists
    if sector_name not in country.subsidies:
        return jsonify({"error": f"No subsidy found for sector {sector_name}"}), 404
    
    # Create budget manager and remove subsidy
    budget_manager = BudgetManager(game_engine.economic_model)
    result = budget_manager.remove_subsidy(country, sector_name)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

# Get possible budget categories
@budget_blueprint.route('/api/budget/categories', methods=['GET'])
def get_budget_categories():
    # Return the standard budget categories that can be used
    categories = {
        "revenue": ["taxation", "tariffs", "other"],
        "expenses": ["subsidies", "social_services", "defense", "infrastructure", "education", "healthcare"]
    }
    
    return jsonify(categories)

@budget_blueprint.route('/api/countries/<country_id>/calibrate', methods=['POST'])
def calibrate_economic_parameters(country_id):
    """
    Calibrate economic parameters for a country based on historical data.
    """
    data = request.json
    target_metrics = data.get('target_metrics', ['gdp_growth', 'inflation', 'unemployment'])
    
    # Get country
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    # Check if historical data is available
    if not hasattr(game_engine, 'historical_data') or not game_engine.historical_data.loaded:
        return jsonify({"error": "Historical data not available for calibration"}), 400
    
    # Create calibrator and calibrate parameters
    calibrator = game_engine.economic_calibrator
    if not calibrator:
        from ..engine import EconomicCalibrator
        calibrator = EconomicCalibrator(game_engine.historical_data)
        game_engine.economic_calibrator = calibrator
    
    # Store original parameters for comparison
    original_params = country.economic_model.copy() if hasattr(country, 'economic_model') else {}
    
    # Perform calibration
    try:
        calibrated_params = calibrator.calibrate_parameters(country_id, 
                                                          country.economic_model, 
                                                          target_metrics)
        
        # Update country's economic model with calibrated parameters
        country.economic_model = calibrated_params
        
        # Get calibration report
        report = calibrator.get_calibration_report(country_id)
        
        return jsonify({
            "message": f"Economic parameters for {country_id} have been calibrated",
            "original_params": original_params,
            "calibrated_params": calibrated_params,
            "report": report
        })
    except Exception as e:
        return jsonify({"error": f"Calibration failed: {str(e)}"}), 500