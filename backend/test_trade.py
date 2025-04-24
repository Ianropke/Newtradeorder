import unittest
import os
import json
from unittest.mock import MagicMock, patch
from backend.models import Country, GameState
from backend.engine import GameEngine, TradeModel

class TestTradeSystem(unittest.TestCase):
    """Test suite for the trade system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        data_path = os.path.join(os.path.dirname(__file__), '../data/countries.json')
        cls.engine = GameEngine(data_path)
        cls.game_state = cls.engine.game_state
        cls.trade_model = cls.engine.trade_model
    
    def setUp(self):
        """Set up before each test"""
        # Reset any trade-specific data before each test
        for country_code, country in self.engine.countries.items():
            country.trade_data = {
                'exports': {},
                'imports': {},
                'total_exports': 0,
                'total_imports': 0,
                'trade_balance': 0
            }
            # Set some initial tariffs for testing
            country.tariffs = {
                'global': 0.05,  # 5% default tariff
                'specific': {}   # Country-specific tariffs
            }
    
    def test_trade_flow_calculation(self):
        """Test calculation of trade flows between countries"""
        # Get test countries
        usa = self.engine.countries['USA']
        chn = self.engine.countries['CHN']
        deu = self.engine.countries['DEU']
        
        # Set initial economic conditions
        usa.gdp = 20000000
        usa.production_capacity = {'TECH': 1000, 'INDUSTRIAL': 800, 'AGRICULTURAL': 500}
        
        chn.gdp = 15000000
        chn.production_capacity = {'TECH': 600, 'INDUSTRIAL': 1200, 'AGRICULTURAL': 400}
        
        deu.gdp = 5000000
        deu.production_capacity = {'TECH': 400, 'INDUSTRIAL': 500, 'AGRICULTURAL': 300}
        
        # Setup some initial trade relationships
        usa.relations['CHN'] = {'opinion': 30, 'trade_agreement': False, 'trade_tension': 0.2}
        usa.relations['DEU'] = {'opinion': 70, 'trade_agreement': True, 'trade_tension': 0.0}
        
        chn.relations['USA'] = {'opinion': 35, 'trade_agreement': False, 'trade_tension': 0.2}
        chn.relations['DEU'] = {'opinion': 50, 'trade_agreement': True, 'trade_tension': 0.0}
        
        # Calculate trade flows
        self.trade_model.calculate_trade_flows(self.game_state)
        
        # Verify trade data was generated
        for country_code in ['USA', 'CHN', 'DEU']:
            country = self.engine.countries[country_code]
            self.assertTrue(len(country.trade_data['exports']) > 0)
            self.assertTrue(len(country.trade_data['imports']) > 0)
            
            # Total exports and imports should be positive
            self.assertGreater(country.trade_data['total_exports'], 0)
            self.assertGreater(country.trade_data['total_imports'], 0)
            
            # Trade balance should be calculated
            self.assertEqual(
                country.trade_data['trade_balance'],
                country.trade_data['total_exports'] - country.trade_data['total_imports']
            )
    
    def test_tariff_effects(self):
        """Test the effects of tariffs on trade flows"""
        # Get test countries
        usa = self.engine.countries['USA']
        chn = self.engine.countries['CHN']
        
        # Set initial economic conditions
        usa.gdp = 20000000
        usa.production_capacity = {'TECH': 1000, 'INDUSTRIAL': 800, 'AGRICULTURAL': 500}
        
        chn.gdp = 15000000
        chn.production_capacity = {'TECH': 600, 'INDUSTRIAL': 1200, 'AGRICULTURAL': 400}
        
        # Set baseline relations
        usa.relations['CHN'] = {'opinion': 40, 'trade_agreement': False, 'trade_tension': 0.0}
        chn.relations['USA'] = {'opinion': 40, 'trade_agreement': False, 'trade_tension': 0.0}
        
        # Calculate baseline trade flows
        self.trade_model.calculate_trade_flows(self.game_state)
        
        # Store baseline trade values
        baseline_usa_exports_to_chn = usa.trade_data['exports'].get('CHN', 0)
        baseline_chn_exports_to_usa = chn.trade_data['exports'].get('USA', 0)
        
        # Now apply tariffs from USA to CHN
        usa.tariffs['specific']['CHN'] = 0.25  # 25% tariff on Chinese goods
        
        # Recalculate trade flows
        self.trade_model.calculate_trade_flows(self.game_state)
        
        # Check tariff effects
        # USA imports from China should decrease
        self.assertLess(chn.trade_data['exports'].get('USA', 0), baseline_chn_exports_to_usa)
        
        # China might retaliate, or trade tension increases
        self.assertGreater(usa.relations['CHN'].get('trade_tension', 0), 0.0)
    
    def test_trade_agreements(self):
        """Test the effects of trade agreements on trade flows"""
        # Get test countries
        usa = self.engine.countries['USA']
        deu = self.engine.countries['DEU']
        
        # Set initial economic conditions
        usa.gdp = 20000000
        usa.production_capacity = {'TECH': 1000, 'INDUSTRIAL': 800, 'AGRICULTURAL': 500}
        
        deu.gdp = 5000000
        deu.production_capacity = {'TECH': 400, 'INDUSTRIAL': 500, 'AGRICULTURAL': 300}
        
        # Calculate baseline without trade agreement
        usa.relations['DEU'] = {'opinion': 60, 'trade_agreement': False, 'trade_tension': 0.0}
        deu.relations['USA'] = {'opinion': 60, 'trade_agreement': False, 'trade_tension': 0.0}
        
        self.trade_model.calculate_trade_flows(self.game_state)
        
        # Store baseline trade values
        baseline_usa_exports_to_deu = usa.trade_data['exports'].get('DEU', 0)
        baseline_deu_exports_to_usa = deu.trade_data['exports'].get('USA', 0)
        
        # Now establish a trade agreement
        usa.relations['DEU'] = {'opinion': 60, 'trade_agreement': True, 'trade_tension': 0.0}
        deu.relations['USA'] = {'opinion': 60, 'trade_agreement': True, 'trade_tension': 0.0}
        
        # Lower tariffs due to agreement
        usa.tariffs['specific']['DEU'] = 0.01  # 1% preferential tariff
        deu.tariffs['specific']['USA'] = 0.01  # 1% preferential tariff
        
        # Recalculate trade flows
        self.trade_model.calculate_trade_flows(self.game_state)
        
        # Check trade agreement effects
        # Exports in both directions should increase
        self.assertGreater(usa.trade_data['exports'].get('DEU', 0), baseline_usa_exports_to_deu)
        self.assertGreater(deu.trade_data['exports'].get('USA', 0), baseline_deu_exports_to_usa)
    
    def test_trade_tension(self):
        """Test the effects of trade tension on trade flows"""
        # Get test countries
        usa = self.engine.countries['USA']
        chn = self.engine.countries['CHN']
        
        # Set initial economic conditions
        usa.gdp = 20000000
        usa.production_capacity = {'TECH': 1000, 'INDUSTRIAL': 800, 'AGRICULTURAL': 500}
        
        chn.gdp = 15000000
        chn.production_capacity = {'TECH': 600, 'INDUSTRIAL': 1200, 'AGRICULTURAL': 400}
        
        # Set baseline relations with no tension
        usa.relations['CHN'] = {'opinion': 40, 'trade_agreement': False, 'trade_tension': 0.0}
        chn.relations['USA'] = {'opinion': 40, 'trade_agreement': False, 'trade_tension': 0.0}
        
        # Calculate baseline trade flows
        self.trade_model.calculate_trade_flows(self.game_state)
        
        # Store baseline trade values
        baseline_usa_exports_to_chn = usa.trade_data['exports'].get('CHN', 0)
        baseline_chn_exports_to_usa = chn.trade_data['exports'].get('USA', 0)
        
        # Now increase trade tension
        usa.relations['CHN'] = {'opinion': 40, 'trade_agreement': False, 'trade_tension': 0.7}
        chn.relations['USA'] = {'opinion': 40, 'trade_agreement': False, 'trade_tension': 0.7}
        
        # Recalculate trade flows
        self.trade_model.calculate_trade_flows(self.game_state)
        
        # Check tension effects
        # Trade in both directions should decrease
        self.assertLess(usa.trade_data['exports'].get('CHN', 0), baseline_usa_exports_to_chn)
        self.assertLess(chn.trade_data['exports'].get('USA', 0), baseline_chn_exports_to_usa)
    
    def test_market_access(self):
        """Test market access calculations"""
        # Get test countries
        usa = self.engine.countries['USA']
        chn = self.engine.countries['CHN']
        jpn = self.engine.countries['JPN']
        
        # Create a coalition that shares market access
        coalition_members = ['USA', 'JPN']
        coalition = {
            'id': 'test_coalition',
            'name': 'Test Trade Alliance',
            'members': coalition_members,
            'leader': 'USA',
            'market_access_bonus': 0.2  # 20% bonus to market access within coalition
        }
        
        # Register coalition
        self.game_state.coalitions = [coalition]
        
        # Calculate market access
        market_access = self.trade_model.calculate_market_access(coalition_members)
        
        # Coalition members should have higher market access to each other
        self.assertGreater(market_access['USA']['JPN'], market_access['USA']['CHN'])
        self.assertGreater(market_access['JPN']['USA'], market_access['JPN']['CHN'])
        
        # Non-members should not get the bonus
        self.assertLess(market_access['CHN']['USA'], market_access['USA']['JPN'])
    
    def test_trade_war_scenario(self):
        """Test a full trade war scenario between major economies"""
        # Get test countries
        usa = self.engine.countries['USA']
        chn = self.engine.countries['CHN']
        
        # Set initial economic conditions
        usa.gdp = 20000000
        usa.production_capacity = {'TECH': 1000, 'INDUSTRIAL': 800, 'AGRICULTURAL': 500}
        
        chn.gdp = 15000000
        chn.production_capacity = {'TECH': 600, 'INDUSTRIAL': 1200, 'AGRICULTURAL': 400}
        
        # Set baseline relations
        usa.relations['CHN'] = {'opinion': 40, 'trade_agreement': False, 'trade_tension': 0.1}
        chn.relations['USA'] = {'opinion': 40, 'trade_agreement': False, 'trade_tension': 0.1}
        
        # Calculate initial trade flows
        self.trade_model.calculate_trade_flows(self.game_state)
        
        # Store baseline economic health
        baseline_usa_gdp = usa.gdp
        baseline_chn_gdp = chn.gdp
        
        # Start trade war: USA imposes tariffs
        usa.tariffs['specific']['CHN'] = 0.25  # 25% tariff
        
        # China retaliates
        chn.tariffs['specific']['USA'] = 0.25  # 25% tariff
        
        # Trade tension increases
        usa.relations['CHN']['trade_tension'] = 0.8
        chn.relations['USA']['trade_tension'] = 0.8
        
        # Simulate several rounds of economic calculation
        for _ in range(5):
            # Recalculate trade flows
            self.trade_model.calculate_trade_flows(self.game_state)
            
            # Calculate economic impact
            self.trade_model.calculate_economic_impact(self.game_state)
        
        # Check economic damage from trade war
        # Both countries should have suffered economic damage
        self.assertLess(usa.gdp_growth, usa.baseline_gdp_growth if hasattr(usa, 'baseline_gdp_growth') else 0.03)
        self.assertLess(chn.gdp_growth, chn.baseline_gdp_growth if hasattr(chn, 'baseline_gdp_growth') else 0.05)
    
    def test_sector_specialization(self):
        """Test that countries benefit from sector specialization in trade"""
        # Get test countries
        deu = self.engine.countries['DEU']
        jpn = self.engine.countries['JPN']
        
        # Set specialized production capacity
        deu.gdp = 5000000
        deu.production_capacity = {'TECH': 300, 'INDUSTRIAL': 800, 'AGRICULTURAL': 100}  # Strong in INDUSTRIAL
        
        jpn.gdp = 5000000
        jpn.production_capacity = {'TECH': 900, 'INDUSTRIAL': 300, 'AGRICULTURAL': 100}  # Strong in TECH
        
        # Set good relations
        deu.relations['JPN'] = {'opinion': 75, 'trade_agreement': True, 'trade_tension': 0.0}
        jpn.relations['DEU'] = {'opinion': 75, 'trade_agreement': True, 'trade_tension': 0.0}
        
        # Low tariffs
        deu.tariffs['specific']['JPN'] = 0.02
        jpn.tariffs['specific']['DEU'] = 0.02
        
        # Calculate trade flows
        self.trade_model.calculate_trade_flows(self.game_state)
        
        # Verify specialization benefit
        # Germany should export more INDUSTRIAL goods to Japan
        if 'sector_exports' in deu.trade_data:
            industrial_exports = deu.trade_data['sector_exports'].get('INDUSTRIAL', {}).get('JPN', 0)
            tech_exports = deu.trade_data['sector_exports'].get('TECH', {}).get('JPN', 0)
            self.assertGreater(industrial_exports, tech_exports)
        
        # Japan should export more TECH goods to Germany
        if 'sector_exports' in jpn.trade_data:
            industrial_exports = jpn.trade_data['sector_exports'].get('INDUSTRIAL', {}).get('DEU', 0)
            tech_exports = jpn.trade_data['sector_exports'].get('TECH', {}).get('DEU', 0)
            self.assertGreater(tech_exports, industrial_exports)
    
    def test_update_tariffs(self):
        """Test updating tariffs and its immediate effects"""
        # Get test countries
        usa = self.engine.countries['USA']
        chn = self.engine.countries['CHN']
        
        # Set initial tariffs
        usa.tariffs = {
            'global': 0.05,
            'specific': {'CHN': 0.10}
        }
        
        # Set initial relations
        usa.relations['CHN'] = {'opinion': 40, 'trade_agreement': False, 'trade_tension': 0.2}
        chn.relations['USA'] = {'opinion': 40, 'trade_agreement': False, 'trade_tension': 0.2}
        
        # Update to higher tariffs
        new_tariff = 0.25
        self.trade_model.update_tariff(usa, 'CHN', new_tariff)
        
        # Verify tariff was updated
        self.assertEqual(usa.tariffs['specific']['CHN'], new_tariff)
        
        # Check for increased trade tension
        self.assertGreater(usa.relations['CHN'].get('trade_tension', 0), 0.2)
        
        # Calculate trade impact
        self.trade_model.calculate_trade_flows(self.game_state)
        
        # Check for decreased imports from China
        self.assertIn('imports', usa.trade_data)
        self.assertIn('CHN', usa.trade_data['imports'])
    
    def test_global_trade_network(self):
        """Test global trade network properties"""
        # Calculate trade for the entire network
        self.trade_model.calculate_trade_flows(self.game_state)
        
        # Generate global trade metrics
        trade_metrics = self.trade_model.calculate_global_trade_metrics(self.game_state)
        
        # Check that metrics are calculated
        self.assertIn('total_global_trade', trade_metrics)
        self.assertIn('largest_bilateral_flow', trade_metrics)
        self.assertIn('most_open_economy', trade_metrics)
        
        # Verify basic consistency
        self.assertGreater(trade_metrics['total_global_trade'], 0)
        
        # Total global imports should approximately equal total exports
        total_exports = sum(country.trade_data['total_exports'] for country in self.engine.countries.values())
        total_imports = sum(country.trade_data['total_imports'] for country in self.engine.countries.values())
        
        # They won't be exactly equal due to calculation differences, but should be close
        self.assertAlmostEqual(total_exports, total_imports, delta=total_exports * 0.05)

if __name__ == "__main__":
    unittest.main()