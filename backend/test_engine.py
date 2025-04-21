import unittest
from .engine import GameEngine
import os

class TestEconomicModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Brug testdata eller den rigtige countries.json
        data_path = os.path.join(os.path.dirname(__file__), '../data/countries.json')
        cls.engine = GameEngine(data_path)
        # Vælg et land til test (fx USA)
        cls.iso = 'USA'
        cls.engine.set_player_country(cls.iso)

    def test_gdp_aggregation(self):
        """BNP skal svare til summen af sektoroutput."""
        country = self.engine.countries[self.iso]
        gdp_calc = sum(s.output for s in country.sectors)
        self.assertAlmostEqual(country.gdp, gdp_calc, places=2)

    def test_budget_balance(self):
        """Statsgæld skal opdateres korrekt efter finanspolitik."""
        country = self.engine.countries[self.iso]
        debt_before = country.debt
        # Simuler en finanspolitisk ændring
        self.engine.apply_policy(self.iso, {'tax': 0.25, 'gov': 0.20})
        self.engine._update_economies()
        debt_after = country.debt
        # Gælden bør ændre sig med forskellen mellem G og T
        tax_revenue = country.tax_rate * country.gdp
        g = getattr(country, 'government_spending', 0.18 * country.gdp)
        self.assertAlmostEqual(debt_after, debt_before + (g - tax_revenue), places=2)

    def test_sector_output_nonnegative(self):
        """Sektoroutput må ikke blive negativt selv ved ekstreme tariffer."""
        self.engine.apply_policy(self.iso, {'sector': 'manufacturing', 'rate': 1.0})  # 100% told
        self.engine._update_economies()
        country = self.engine.countries[self.iso]
        for s in country.sectors:
            self.assertGreaterEqual(s.output, 0.0)

    def test_zero_population(self):
        """Edge case: Land med nul befolkning bør ikke give crash."""
        country = self.engine.countries[self.iso]
        country.population = 0
        try:
            self.engine._update_economies()
        except Exception as e:
            self.fail(f"_update_economies() fejlede ved nul befolkning: {e}")

if __name__ == '__main__':
    unittest.main()
