import unittest
from engine import GameEngine
import os

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

if __name__ == '__main__':
    unittest.main()
