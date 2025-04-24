import unittest
from backend.engine import GameEngine, HistoricalDataset, EconomicCalibrator
import os
import random

class TestEconomicModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_path = os.path.join(os.path.dirname(__file__), '../data/countries.json')
        cls.engine = GameEngine(data_path)
        cls.iso = 'USA'
        cls.engine.set_player_country(cls.iso)
        country = cls.engine.countries[cls.iso]
        if not hasattr(country, 'debt'):
            country.debt = 0.0

    def test_gdp_aggregation(self):
        country = self.engine.countries[self.iso]
        gdp_calc = sum(s.output for s in country.sectors)
        self.assertAlmostEqual(country.gdp, gdp_calc, places=2)

    def test_budget_balance(self):
        country = self.engine.countries[self.iso]
        if not hasattr(country, 'debt'):
            country.debt = 0.0
        debt_before = country.debt
        self.engine.apply_policy(self.iso, {'tax': 0.25, 'gov': 0.20})
        self.engine._update_economies()
        debt_after = country.debt
        g_after = getattr(country, 'government_spending', 0.18 * country.gdp)
        tax_revenue_after = getattr(country, 'tax_rate', 0.2) * country.gdp
        # Nu sammenlignes med de faktiske værdier efter update
        self.assertAlmostEqual(debt_after, debt_before + (g_after - tax_revenue_after), places=2)

    def test_sector_output_nonnegative(self):
        self.engine.apply_policy(self.iso, {'sector': 'manufacturing', 'rate': 1.0})
        self.engine._update_economies()
        country = self.engine.countries[self.iso]
        for s in country.sectors:
            self.assertGreaterEqual(s.output, 0.0)

    def test_zero_population(self):
        country = self.engine.countries[self.iso]
        country.population = 0
        try:
            self.engine._update_economies()
        except Exception as e:
            self.fail(f"_update_economies() fejlede ved nul befolkning: {e}")
            
    def test_tariff_effects(self):
        """Test that tariffs reduce trade volumes and increase prices."""
        country = self.engine.countries[self.iso]
        partner_iso = random.choice([iso for iso in self.engine.countries.keys() if iso != self.iso])
        
        # Save original values
        original_trade_volume = sum(country.trade_partners.get(partner_iso, {}).get('imports', 0) 
                                   for country in self.engine.countries.values())
        original_price_level = getattr(country, 'price_level', 1.0)
        
        # Apply tariff policy
        self.engine.apply_policy(self.iso, {
            'type': 'tariff', 
            'target': partner_iso, 
            'rate': 0.25
        })
        
        # Update economy
        self.engine._update_economies()
        
        # Get new values
        new_trade_volume = sum(country.trade_partners.get(partner_iso, {}).get('imports', 0) 
                              for country in self.engine.countries.values())
        new_price_level = getattr(country, 'price_level', 1.0)
        
        # Trade volume should decrease and prices should increase
        self.assertLessEqual(new_trade_volume, original_trade_volume, 
                           "Tariffs should reduce trade volume")
        self.assertGreaterEqual(new_price_level, original_price_level, 
                              "Tariffs should increase domestic prices")
    
    def test_subsidy_effects(self):
        """Test that subsidies increase sector output and reduce unemployment."""
        country = self.engine.countries[self.iso]
        
        # Choose a sector to subsidize
        sector = country.sectors[0]
        original_output = sector.output
        original_unemployment = getattr(sector, 'unemployment_rate', 0.05)
        
        # Apply subsidy policy
        self.engine.apply_policy(self.iso, {
            'type': 'subsidy', 
            'sector': sector.name, 
            'rate': 0.15
        })
        
        # Update economy
        self.engine._update_economies()
        
        # Get new values
        new_output = sector.output
        new_unemployment = getattr(sector, 'unemployment_rate', 0.05)
        
        # Output should increase and unemployment should decrease
        self.assertGreaterEqual(new_output, original_output, 
                              "Subsidies should increase sector output")
        self.assertLessEqual(new_unemployment, original_unemployment, 
                           "Subsidies should decrease sector unemployment")
    
    def test_multiple_turns(self):
        """Test economic model over multiple turns."""
        # Save initial GDP
        initial_gdp = self.engine.countries[self.iso].gdp
        
        # Run multiple turns and ensure the economy changes in some way
        for _ in range(5):
            self.engine._update_economies()
        
        # GDP should change over time
        current_gdp = self.engine.countries[self.iso].gdp
        self.assertNotEqual(initial_gdp, current_gdp, 
                          "GDP should change over multiple turns")
    
    def test_historical_dataset_loading(self):
        """Test loading and using historical economic data."""
        # Create a test historical dataset
        dataset = HistoricalDataset()
        self.assertFalse(dataset.loaded, "New dataset should not be loaded")
        
        # Test calculating averages with sample data
        dataset.data = {
            'USA': {
                'region': 'North America',
                'yearly_data': {
                    '2020': {'gdp_growth': 2.5, 'inflation': 1.8},
                    '2021': {'gdp_growth': 3.0, 'inflation': 2.1}
                }
            },
            'CAN': {
                'region': 'North America',
                'yearly_data': {
                    '2020': {'gdp_growth': 2.2, 'inflation': 1.6},
                    '2021': {'gdp_growth': 2.8, 'inflation': 1.9}
                }
            }
        }
        
        dataset._calculate_averages()
        
        # Check global averages
        self.assertAlmostEqual(dataset.global_averages['gdp_growth']['2020'], 2.35, places=2)
        self.assertAlmostEqual(dataset.global_averages['inflation']['2021'], 2.0, places=2)
        
        # Check regional averages
        na_avg = dataset.regional_averages['North America']['2020']['gdp_growth']
        self.assertAlmostEqual(na_avg, 2.35, places=2)
    
    def test_economic_calibration(self):
        """Test calibrating economic parameters."""
        # Setup historical data
        dataset = HistoricalDataset()
        dataset.data = {
            'USA': {
                'region': 'North America',
                'yearly_data': {
                    '2018': {'gdp_growth': 2.1, 'inflation': 1.5, 'unemployment': 4.0},
                    '2019': {'gdp_growth': 2.3, 'inflation': 1.6, 'unemployment': 3.8},
                    '2020': {'gdp_growth': 2.5, 'inflation': 1.8, 'unemployment': 3.6},
                    '2021': {'gdp_growth': 3.0, 'inflation': 2.1, 'unemployment': 3.5},
                    '2022': {'gdp_growth': 2.8, 'inflation': 2.0, 'unemployment': 3.7}
                }
            }
        }
        
        calibrator = EconomicCalibrator(dataset)
        
        # Create sample model parameters
        params = {
            'productivity_factor': 1.0,
            'capital_elasticity': 0.5,
            'labor_elasticity': 0.5,
            'natural_rate': 4.0,
            'monetary_policy_effect': 0.5,
            'phillips_curve_slope': 0.3,
            'okun_coefficient': 2.0
        }
        
        # Calibrate parameters
        calibrated = calibrator.calibrate_parameters('USA', params)
        
        # Check that calibration returns a valid result
        self.assertIsNotNone(calibrated)
        self.assertTrue(isinstance(calibrated, dict))
        self.assertEqual(set(params.keys()), set(calibrated.keys()))

if __name__ == '__main__':
    unittest.main()
