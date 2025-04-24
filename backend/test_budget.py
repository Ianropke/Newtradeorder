import unittest
import os
import json
from unittest.mock import MagicMock, patch
from backend.models import Country, GameState
from backend.engine import GameEngine
from backend.routes.budget import budget_blueprint

class TestBudgetSystem(unittest.TestCase):
    """Test suite for the budget and fiscal management system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        data_path = os.path.join(os.path.dirname(__file__), '../data/countries.json')
        cls.engine = GameEngine(data_path)
        cls.game_state = cls.engine.game_state
        
        # Ensure the budget system is initialized
        if not hasattr(cls.engine, 'budget_system'):
            cls.engine.budget_system = cls.engine.get_system('budget')
    
    def setUp(self):
        """Set up before each test"""
        # Reset country data for testing
        self.usa = self.engine.countries['USA']
        self.usa.gdp = 25000000
        self.usa.population = 330000000
        self.usa.tax_rate = 0.3
        self.usa.gdp_growth = 0.02
        self.usa.inflation_rate = 0.02
        self.usa.stability = 0.8
        
        # Set up budget components if not present
        if not hasattr(self.usa, 'budget'):
            self.usa.budget = {
                'revenue': {
                    'tax': 0.0,
                    'tariffs': 0.0,
                    'other': 0.0
                },
                'spending': {
                    'military': 0.0,
                    'healthcare': 0.0,
                    'education': 0.0,
                    'infrastructure': 0.0,
                    'research': 0.0,
                    'subsidies': 0.0,
                    'interest': 0.0,
                    'other': 0.0
                },
                'balance': 0.0,
                'debt': 0.0,
                'deficit_ratio': 0.0,
                'debt_ratio': 0.0
            }
        
        # Set up initial spending allocation
        self.usa.spending_allocation = {
            'military': 0.2,
            'healthcare': 0.25,
            'education': 0.15,
            'infrastructure': 0.1,
            'research': 0.05,
            'subsidies': 0.1,
            'other': 0.15
        }
        
        self.usa.debt = 20000000  # National debt
        self.usa.interest_rate = 0.03  # Interest rate on debt
    
    def test_budget_calculation(self):
        """Test budget revenue and spending calculation"""
        # Calculate budget
        self.engine.budget_system.calculate_country_budget(self.usa.id)
        
        # Check tax revenue calculation
        expected_tax_revenue = self.usa.gdp * self.usa.tax_rate
        self.assertAlmostEqual(self.usa.budget['revenue']['tax'], expected_tax_revenue)
        
        # Check spending calculations
        total_revenue = sum(self.usa.budget['revenue'].values())
        for category, allocation in self.usa.spending_allocation.items():
            expected_spending = total_revenue * allocation
            self.assertAlmostEqual(self.usa.budget['spending'][category], expected_spending)
        
        # Check budget balance
        total_spending = sum(self.usa.budget['spending'].values())
        expected_balance = total_revenue - total_spending
        self.assertAlmostEqual(self.usa.budget['balance'], expected_balance)
        
        # Check deficit and debt ratios
        if expected_balance < 0:
            expected_deficit_ratio = abs(expected_balance) / self.usa.gdp
            self.assertAlmostEqual(self.usa.budget['deficit_ratio'], expected_deficit_ratio)
        
        expected_debt_ratio = self.usa.debt / self.usa.gdp
        self.assertAlmostEqual(self.usa.budget['debt_ratio'], expected_debt_ratio)
    
    def test_tariff_revenue(self):
        """Test tariff revenue calculation"""
        # Set up initial tariffs and trade data
        self.usa.tariffs = {
            'global': 0.05,  # 5% default tariff
            'specific': {
                'CHN': 0.25,  # 25% tariff on Chinese goods
                'MEX': 0.1    # 10% tariff on Mexican goods
            }
        }
        
        # Mock trade data
        self.usa.trade = {
            'imports': {
                'CHN': 500000,  # $500B imports from China
                'MEX': 300000,  # $300B imports from Mexico
                'DEU': 150000,  # $150B imports from Germany
                'JPN': 130000   # $130B imports from Japan
            }
        }
        
        # Calculate tariff revenue
        tariff_revenue = self.engine.budget_system.calculate_tariff_revenue(self.usa.id)
        
        # Expected tariff revenue calculation
        expected_china_tariff = 500000 * 0.25
        expected_mexico_tariff = 300000 * 0.1
        expected_other_tariff = (150000 + 130000) * 0.05
        expected_total = expected_china_tariff + expected_mexico_tariff + expected_other_tariff
        
        self.assertAlmostEqual(tariff_revenue, expected_total)
        
        # Update budget and check tariff revenue was included
        self.engine.budget_system.calculate_country_budget(self.usa.id)
        self.assertAlmostEqual(self.usa.budget['revenue']['tariffs'], tariff_revenue)
    
    def test_budget_effects(self):
        """Test budget allocation effects on country metrics"""
        # Original country metrics
        original_military = getattr(self.usa, 'military_strength', 1.0)
        original_research = getattr(self.usa, 'research_level', 1.0)
        original_education = getattr(self.usa, 'education_level', 1.0)
        original_healthcare = getattr(self.usa, 'healthcare_level', 1.0)
        
        # Change budget allocation to prioritize military and research
        self.usa.spending_allocation = {
            'military': 0.3,      # Increase from 0.2
            'healthcare': 0.15,   # Decrease from 0.25
            'education': 0.1,     # Decrease from 0.15
            'infrastructure': 0.1,
            'research': 0.2,      # Increase from 0.05
            'subsidies': 0.05,    # Decrease from 0.1
            'other': 0.1
        }
        
        # Calculate budget with new allocation
        self.engine.budget_system.calculate_country_budget(self.usa.id)
        
        # Apply budget effects
        self.engine.budget_system.apply_budget_effects(self.usa.id)
        
        # Check that military and research metrics increased
        if hasattr(self.usa, 'military_strength'):
            self.assertGreater(self.usa.military_strength, original_military)
        
        if hasattr(self.usa, 'research_level'):
            self.assertGreater(self.usa.research_level, original_research)
        
        # Check that healthcare and education metrics decreased
        if hasattr(self.usa, 'education_level'):
            self.assertLess(self.usa.education_level, original_education)
        
        if hasattr(self.usa, 'healthcare_level'):
            self.assertLess(self.usa.healthcare_level, original_healthcare)
    
    def test_deficit_and_debt(self):
        """Test deficit handling and debt accumulation"""
        # Create a deficit scenario
        self.usa.tax_rate = 0.2  # Lower tax rate to create deficit
        
        # Calculate initial budget
        self.engine.budget_system.calculate_country_budget(self.usa.id)
        initial_debt = self.usa.debt
        
        # Force deficit by setting high spending
        total_revenue = sum(self.usa.budget['revenue'].values())
        # Set spending higher than revenue
        for category in self.usa.budget['spending']:
            self.usa.budget['spending'][category] = total_revenue * 0.2  # Overspend in each category
        
        # Update balance after overspending
        total_spending = sum(self.usa.budget['spending'].values())
        self.usa.budget['balance'] = total_revenue - total_spending
        
        # Convert deficit to debt
        self.engine.budget_system.process_deficit(self.usa.id)
        
        # Debt should increase by the deficit amount
        expected_debt = initial_debt - self.usa.budget['balance']  # Negative balance adds to debt
        self.assertAlmostEqual(self.usa.debt, expected_debt)
        
        # Interest payments should increase in next budget
        original_interest = self.usa.budget['spending']['interest']
        self.engine.budget_system.calculate_country_budget(self.usa.id)
        new_interest = self.usa.budget['spending']['interest']
        self.assertGreater(new_interest, original_interest)
    
    def test_debt_crisis(self):
        """Test handling of debt crisis events"""
        # Create a high debt scenario
        self.usa.debt = 30000000  # Unrealistically high debt
        self.usa.gdp = 20000000   # Lower GDP to make debt ratio worse
        
        # Calculate debt ratio
        debt_ratio = self.usa.debt / self.usa.gdp
        self.assertGreater(debt_ratio, 1.0)  # Debt exceeds GDP
        
        # Check debt crisis risk
        crisis_risk = self.engine.budget_system.calculate_debt_crisis_risk(self.usa.id)
        self.assertGreater(crisis_risk, 0.5)  # High risk
        
        # Simulate debt crisis effects
        if crisis_risk > 0.5:
            original_interest_rate = self.usa.interest_rate
            original_stability = self.usa.stability
            
            self.engine.budget_system.trigger_debt_crisis(self.usa.id)
            
            # Interest rates should increase
            self.assertGreater(self.usa.interest_rate, original_interest_rate)
            
            # Stability should decrease
            self.assertLess(self.usa.stability, original_stability)
            
            # GDP growth should be affected
            self.assertLess(self.usa.gdp_growth, 0.02)
    
    def test_austerity_measures(self):
        """Test implementation of austerity measures"""
        # Create a deficit scenario requiring austerity
        self.usa.debt = 25000000
        self.usa.budget['balance'] = -1000000  # Large deficit
        
        # Record initial spending
        initial_spending = {}
        for category, amount in self.usa.budget['spending'].items():
            initial_spending[category] = amount
        
        # Implement austerity
        austerity_cut_percentage = 0.1  # 10% spending cut
        austerity_result = self.engine.budget_system.implement_austerity(
            self.usa.id, austerity_cut_percentage)
        
        # Verify spending cuts
        for category in initial_spending:
            if category != 'interest':  # Interest payments can't be cut
                self.assertLess(
                    self.usa.budget['spending'][category],
                    initial_spending[category]
                )
        
        # Check for side effects
        if hasattr(self.usa, 'stability'):
            self.assertLess(self.usa.stability, 0.8)  # Stability should decrease
    
    def test_stimulus_package(self):
        """Test implementation of stimulus spending"""
        # Record initial values
        initial_gdp_growth = self.usa.gdp_growth
        initial_stability = self.usa.stability
        initial_debt = self.usa.debt
        
        # Implement stimulus
        stimulus_amount = 500000  # $500B stimulus
        stimulus_allocation = {
            'infrastructure': 0.4,
            'subsidies': 0.3,
            'healthcare': 0.2,
            'education': 0.1
        }
        
        stimulus_result = self.engine.budget_system.implement_stimulus(
            self.usa.id, 
            stimulus_amount, 
            stimulus_allocation
        )
        
        # Debt should increase
        self.assertEqual(self.usa.debt, initial_debt + stimulus_amount)
        
        # GDP growth should increase
        self.assertGreater(self.usa.gdp_growth, initial_gdp_growth)
        
        # Check that stimulus spending was added to budget
        for category, percentage in stimulus_allocation.items():
            expected_increase = stimulus_amount * percentage
            self.assertGreaterEqual(self.usa.budget['spending'][category], expected_increase)
    
    def test_tax_policy_changes(self):
        """Test effects of changing tax policies"""
        # Initial values
        initial_tax_rate = self.usa.tax_rate
        initial_stability = self.usa.stability
        
        # Test tax increase
        new_tax_rate = initial_tax_rate + 0.05  # 5% tax increase
        
        tax_change_result = self.engine.budget_system.change_tax_rate(
            self.usa.id, new_tax_rate)
        
        # Calculate new budget with higher taxes
        self.engine.budget_system.calculate_country_budget(self.usa.id)
        
        # Tax revenue should increase
        self.assertGreater(
            self.usa.budget['revenue']['tax'],
            self.usa.gdp * initial_tax_rate
        )
        
        # Stability should decrease
        self.assertLess(self.usa.stability, initial_stability)
        
        # Test tax decrease
        self.usa.stability = initial_stability  # Reset stability
        new_tax_rate = initial_tax_rate - 0.05  # 5% tax decrease
        
        tax_change_result = self.engine.budget_system.change_tax_rate(
            self.usa.id, new_tax_rate)
        
        # Calculate new budget with lower taxes
        self.engine.budget_system.calculate_country_budget(self.usa.id)
        
        # Tax revenue should decrease
        self.assertLess(
            self.usa.budget['revenue']['tax'],
            self.usa.gdp * initial_tax_rate
        )
        
        # Stability might increase (if taxes were high)
        if initial_tax_rate > 0.3:
            self.assertGreater(self.usa.stability, initial_stability)
    
    def test_budget_history_tracking(self):
        """Test tracking budget history over multiple turns"""
        # Clear budget history
        if hasattr(self.usa, 'budget_history'):
            self.usa.budget_history = []
        
        # Calculate budget for multiple turns
        for turn in range(1, 6):
            # Update game state turn
            self.game_state.current_turn = turn
            self.game_state.current_year = 2025 + turn
            
            # Calculate budget
            self.engine.budget_system.calculate_country_budget(self.usa.id)
            
            # Save budget history
            self.engine.budget_system.save_budget_history(self.usa.id)
            
            # GDP grows each turn
            self.usa.gdp *= (1 + self.usa.gdp_growth)
        
        # Check that budget history was saved
        self.assertTrue(hasattr(self.usa, 'budget_history'))
        self.assertEqual(len(self.usa.budget_history), 5)
        
        # Check history structure
        for entry in self.usa.budget_history:
            self.assertIn('year', entry)
            self.assertIn('revenue', entry)
            self.assertIn('spending', entry)
            self.assertIn('balance', entry)
            self.assertIn('debt', entry)
        
        # Verify that debt accumulates correctly
        if self.usa.budget_history[0]['balance'] < 0:
            # Deficit in first year should increase debt in second year
            self.assertGreater(
                self.usa.budget_history[1]['debt'],
                self.usa.budget_history[0]['debt']
            )
    
    def test_subsidy_effects(self):
        """Test effects of industry subsidies on economic metrics"""
        # Set up industry data if not present
        if not hasattr(self.usa, 'industries'):
            self.usa.industries = {
                'agriculture': {'output': 100000, 'growth': 0.01},
                'manufacturing': {'output': 300000, 'growth': 0.015},
                'technology': {'output': 500000, 'growth': 0.03},
                'services': {'output': 800000, 'growth': 0.02}
            }
        
        # Record initial growth rates
        initial_growth_rates = {}
        for industry, data in self.usa.industries.items():
            initial_growth_rates[industry] = data['growth']
        
        # Implement industry subsidies
        subsidy_amount = 200000  # $200B in subsidies
        subsidy_allocation = {
            'agriculture': 0.2,
            'manufacturing': 0.5,
            'technology': 0.3,
            'services': 0.0
        }
        
        subsidy_result = self.engine.budget_system.allocate_industry_subsidies(
            self.usa.id, subsidy_amount, subsidy_allocation)
        
        # Check for growth effects in subsidized industries
        for industry, allocation in subsidy_allocation.items():
            if allocation > 0:
                self.assertGreater(
                    self.usa.industries[industry]['growth'],
                    initial_growth_rates[industry]
                )
        
        # Non-subsidized industries shouldn't change
        for industry, allocation in subsidy_allocation.items():
            if allocation == 0:
                self.assertEqual(
                    self.usa.industries[industry]['growth'],
                    initial_growth_rates[industry]
                )
    
    def test_foreign_aid(self):
        """Test allocation and effects of foreign aid"""
        # Set up a recipient country
        if 'ETH' not in self.engine.countries:
            self.engine.countries['ETH'] = Country('ETH', 'Ethiopia')
            self.engine.countries['ETH'].gdp = 100000
            self.engine.countries['ETH'].gdp_growth = 0.04
            self.engine.countries['ETH'].stability = 0.5
            self.engine.countries['ETH'].relations = {'USA': {'opinion': 60}}
        
        recipient = self.engine.countries['ETH']
        
        # Initial values
        initial_usa_balance = self.usa.budget['balance']
        initial_eth_gdp_growth = recipient.gdp_growth
        initial_eth_opinion = recipient.relations['USA']['opinion']
        
        # Allocate foreign aid
        aid_amount = 20000  # $20B in aid
        foreign_aid_result = self.engine.budget_system.allocate_foreign_aid(
            self.usa.id, 'ETH', aid_amount)
        
        # USA budget balance should decrease
        self.assertLess(self.usa.budget['balance'], initial_usa_balance)
        
        # Recipient growth should increase
        self.assertGreater(recipient.gdp_growth, initial_eth_gdp_growth)
        
        # Recipient opinion should improve
        self.assertGreater(
            recipient.relations['USA']['opinion'],
            initial_eth_opinion
        )
    
    def test_inflation_impact(self):
        """Test impact of inflation on budget calculations"""
        # Initial values
        original_inflation = self.usa.inflation_rate
        
        # Calculate budget with normal inflation
        self.engine.budget_system.calculate_country_budget(self.usa.id)
        normal_tax_revenue = self.usa.budget['revenue']['tax']
        
        # Increase inflation
        self.usa.inflation_rate = 0.1  # 10% inflation
        
        # Recalculate budget
        self.engine.budget_system.calculate_country_budget(self.usa.id)
        high_inflation_tax_revenue = self.usa.budget['revenue']['tax']
        
        # Nominal tax revenue should be higher due to inflation
        self.assertGreater(high_inflation_tax_revenue, normal_tax_revenue)
        
        # But inflation should also increase costs
        # Check government spending increases
        for category in self.usa.budget['spending']:
            if category in ['military', 'healthcare', 'education']:
                # These categories should see spending increases due to inflation
                self.assertGreater(
                    self.usa.budget['spending'][category] / self.usa.gdp,
                    normal_tax_revenue / (self.usa.gdp / (1 + self.usa.inflation_rate - original_inflation))
                )

class TestBudgetAPI(unittest.TestCase):
    """Test suite for budget API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        from flask import Flask
        from unittest.mock import MagicMock
        
        # Create Flask app
        cls.app = Flask(__name__)
        cls.app.register_blueprint(budget_blueprint)
        cls.client = cls.app.test_client()
        
        # Mock budget system for API tests
        cls.mock_budget_system = MagicMock()
        
        # Setup mock country budget
        cls.mock_budget_system.get_country_budget.return_value = {
            'revenue': {
                'tax': 7500000,
                'tariffs': 500000,
                'other': 200000
            },
            'spending': {
                'military': 1600000,
                'healthcare': 2000000,
                'education': 1200000,
                'infrastructure': 800000,
                'research': 400000,
                'subsidies': 800000,
                'interest': 600000,
                'other': 1200000
            },
            'balance': -400000,
            'debt': 20000000,
            'deficit_ratio': 0.016,
            'debt_ratio': 0.8
        }
        
        # Setup mock budget history
        cls.mock_budget_system.get_budget_history.return_value = [
            {
                'year': 2025,
                'revenue': 7800000,
                'spending': 8000000,
                'balance': -200000,
                'debt': 19600000
            },
            {
                'year': 2026,
                'revenue': 8200000,
                'spending': 8600000,
                'balance': -400000,
                'debt': 20000000
            }
        ]
        
        # Patch main module to use mock budget system
        patcher = patch('backend.routes.budget.budget_system', cls.mock_budget_system)
        cls.mock_module_budget_system = patcher.start()
        cls.addClassCleanup(patcher.stop)
    
    def test_get_country_budget(self):
        """Test GET endpoint for country budget"""
        # Make request
        response = self.client.get('/api/budget/country/USA')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('revenue', data)
        self.assertIn('spending', data)
        self.assertIn('balance', data)
        self.assertIn('debt', data)
        
        # Check revenue components
        self.assertEqual(data['revenue']['tax'], 7500000)
        self.assertEqual(data['revenue']['tariffs'], 500000)
        
        # Check spending components
        self.assertEqual(data['spending']['military'], 1600000)
        self.assertEqual(data['spending']['healthcare'], 2000000)
    
    def test_get_budget_history(self):
        """Test GET endpoint for budget history"""
        # Make request
        response = self.client.get('/api/budget/history/USA')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['year'], 2025)
        self.assertEqual(data[1]['year'], 2026)
    
    def test_update_spending_allocation(self):
        """Test PUT endpoint for updating spending allocation"""
        # Mock update response
        self.mock_budget_system.update_spending_allocation.return_value = {
            'success': True,
            'message': 'Spending allocation updated successfully'
        }
        
        # Make request
        new_allocation = {
            'military': 0.25,
            'healthcare': 0.2,
            'education': 0.15,
            'infrastructure': 0.15,
            'research': 0.1,
            'subsidies': 0.05,
            'other': 0.1
        }
        
        response = self.client.put(
            '/api/budget/allocation/USA',
            json=new_allocation,
            content_type='application/json'
        )
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify budget system was called
        self.mock_budget_system.update_spending_allocation.assert_called_with(
            'USA', new_allocation)
    
    def test_implement_budget_policy(self):
        """Test POST endpoint for implementing budget policies"""
        # Mock policy implementation response
        self.mock_budget_system.implement_policy.return_value = {
            'success': True,
            'message': 'Austerity measures implemented',
            'effects': {
                'stability': -0.05,
                'gdp_growth': -0.01,
                'deficit_reduction': 300000
            }
        }
        
        # Make request for austerity policy
        policy_data = {
            'type': 'austerity',
            'parameters': {
                'cut_percentage': 0.1
            }
        }
        
        response = self.client.post(
            '/api/budget/policy/USA',
            json=policy_data,
            content_type='application/json'
        )
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('effects', data)
        
        # Make request for stimulus policy
        policy_data = {
            'type': 'stimulus',
            'parameters': {
                'amount': 500000,
                'allocation': {
                    'infrastructure': 0.5,
                    'subsidies': 0.3,
                    'healthcare': 0.2
                }
            }
        }
        
        # Mock different response for stimulus
        self.mock_budget_system.implement_policy.return_value = {
            'success': True,
            'message': 'Stimulus package implemented',
            'effects': {
                'gdp_growth': 0.02,
                'debt_increase': 500000
            }
        }
        
        response = self.client.post(
            '/api/budget/policy/USA',
            json=policy_data,
            content_type='application/json'
        )
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('effects', data)
        self.assertEqual(data['effects']['debt_increase'], 500000)

if __name__ == "__main__":
    unittest.main()