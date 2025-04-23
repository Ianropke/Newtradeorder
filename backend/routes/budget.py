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

@budget_blueprint.route('/api/budget/<country_id>/subsidies/preview', methods=['POST'])
def preview_subsidy_effects(country_id):
    """
    Preview the economic effects of a subsidy without actually applying it.
    """
    # Get request data
    data = request.json
    if not data or 'sector' not in data or 'percentage' not in data:
        return jsonify({"error": "Missing required parameters: sector and percentage"}), 400
    
    sector_name = data['sector']
    subsidy_percentage = data['percentage']
    
    # Validate percentage
    try:
        subsidy_percentage = float(subsidy_percentage)
        if subsidy_percentage < 0 or subsidy_percentage > 100:
            return jsonify({"error": "Percentage must be between 0 and 100"}), 400
    except ValueError:
        return jsonify({"error": "Percentage must be a number"}), 400
    
    # Get country 
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    # Find the sector
    target_sector = None
    for sector in country.sectors:
        if sector.name.lower() == sector_name.lower():
            target_sector = sector
            break
    
    if not target_sector:
        return jsonify({"error": f"Sector '{sector_name}' not found"}), 404
    
    # Create budget manager and calculate effects without applying
    budget_manager = BudgetManager(game_engine.economic_model)
    
    # Convert percentage to fraction
    subsidy_fraction = subsidy_percentage / 100.0
    
    # Calculate projected effects (similar to manage_subsidies but without actually applying)
    output_boost_efficiency = 0.7  # 70% efficiency in converting subsidies to output
    subsidy_amount = target_sector.output * subsidy_fraction
    output_boost = subsidy_amount * output_boost_efficiency
    
    # Calculate unemployment effect
    employment_boost_percentage = subsidy_fraction * 0.5
    unemployment_reduction = target_sector.unemployment_rate * employment_boost_percentage
    
    # Calculate price effect
    price_reduction_percentage = subsidy_fraction * 0.3 * 100  # Convert to percentage
    
    # Calculate export boost
    export_increase_percentage = 0
    if subsidy_percentage > 5:  # Only significant subsidies affect exports
        export_increase_percentage = price_reduction_percentage * 1.5  # Price reduction has leveraged effect on exports
    
    # Return preview data
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
    """
    Get historical budget data for a country across multiple years.
    """
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    # Check if historical budget data exists
    if not hasattr(country, 'budget_history') or not country.budget_history:
        # Generate some mock historical data if real data doesn't exist
        current_year = game_engine.current_year
        history = []
        
        # Use current budget as template and create historical variations
        current_budget = country.budget
        gdp_baseline = country.gdp
        
        for year in range(current_year - 10, current_year):
            # Create GDP variation - assuming 1-3% growth on average
            year_factor = (year - (current_year - 10)) / 10  # 0 to 1 factor based on proximity to current year
            gdp_variation = gdp_baseline * (0.85 + year_factor * 0.25)  # 85% to 110% of current GDP
            
            # Create budget variations based on GDP
            gdp_ratio = gdp_variation / gdp_baseline
            
            # Create year entry
            year_budget = {
                "year": year,
                "gdp": gdp_variation,
                "totalRevenue": current_budget["totalRevenue"] * gdp_ratio * (0.9 + (year_factor * 0.2)),
                "totalExpenditure": current_budget["totalExpenditure"] * gdp_ratio * (0.85 + (year_factor * 0.3)),
                "balance": 0,  # Will be calculated below
                "debt": current_budget["debt"] * (0.7 + year_factor * 0.4)  # Debt grows over time
            }
            
            # Calculate balance
            year_budget["balance"] = year_budget["totalRevenue"] - year_budget["totalExpenditure"]
            
            history.append(year_budget)
        
        return jsonify({"history": history})
    
    # Return real historical data if it exists
    return jsonify({"history": country.budget_history})

@budget_blueprint.route('/api/budget/<country_id>/simulate', methods=['POST'])
def simulate_budget_effects(country_id):
    """
    Simulate the effects of a budget change without actually applying it.
    """
    # Get request data
    data = request.json
    if not data or 'category' not in data or 'value' not in data:
        return jsonify({"error": "Missing required parameters: category and value"}), 400
    
    category = data['category']
    new_value = float(data['value'])
    
    # Get country
    from main import game_engine
    
    country = game_engine.countries.get(country_id.upper())
    if not country:
        return jsonify({"error": f"Country with ID {country_id} not found"}), 404
    
    if category not in country.budget['expenses']:
        return jsonify({"error": f"Budget category '{category}' not found"}), 400
    
    # Get current value
    current_value = country.budget['expenses'][category]
    
    # Create budget manager
    budget_manager = BudgetManager(game_engine.economic_model)
    
    # Calculate effects (similar to adjust_budget_allocation but without actually applying)
    effects = budget_manager._calculate_budget_allocation_effects(country, category, current_value, new_value)
    
    # Calculate new balance
    total_revenue = country.budget['totalRevenue']
    total_expenses = sum([
        value if expense != category else new_value 
        for expense, value in country.budget['expenses'].items()
    ])
    new_balance = total_revenue - total_expenses
    
    # Generate economic impact estimates
    change = new_value - current_value
    change_ratio = change / country.gdp if country.gdp > 0 else 0
    
    # Simplified effects based on category
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
    
    # Generate description based on changes
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
    
    # Return simulated effects
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