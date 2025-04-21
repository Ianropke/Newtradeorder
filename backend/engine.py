from typing import Dict, Optional
from .models import Country, load_countries_from_file, EconomicModel
import random  # For simple simulation

class AIProfile:
    """
    AI-profil/personlighed for et land: styrer vægtning af mål og adfærd.
    """
    def __init__(self, regime_type, risk_aversion, retaliation, trust_weight, growth_weight, sector_protection):
        self.regime_type = regime_type  # 'democracy', 'autocracy', 'hybrid'
        self.risk_aversion = risk_aversion  # 0-1
        self.retaliation = retaliation  # 0-1
        self.trust_weight = trust_weight  # 0-1
        self.growth_weight = growth_weight  # 0-1
        self.sector_protection = sector_protection  # 0-1

# Eksempel-profiler (kan gøres mere avanceret og lægges i data)
AI_PROFILES = {
    'democracy': AIProfile('democracy', risk_aversion=0.7, retaliation=0.4, trust_weight=0.7, growth_weight=0.8, sector_protection=0.5),
    'autocracy': AIProfile('autocracy', risk_aversion=0.3, retaliation=0.8, trust_weight=0.3, growth_weight=0.6, sector_protection=0.8),
    'hybrid': AIProfile('hybrid', risk_aversion=0.5, retaliation=0.6, trust_weight=0.5, growth_weight=0.7, sector_protection=0.6)
}

class AIStrategyState:
    """
    Simpel FSM/BT-tilstand for AI-land (kan udvides).
    """
    def __init__(self, state):
        self.state = state  # fx 'neutral', 'aggressive', 'cooperative'

class GameEngine:
    def __init__(self, countries_data_path: str):
        self.countries: Dict[str, Country] = load_countries_from_file(countries_data_path)
        self.current_turn: int = 0
        self.player_country_iso: str = ""  # Will be set when player chooses

        if not self.countries:
            raise ValueError("Failed to load country data. Cannot initialize engine.")

    def set_player_country(self, iso_code: str):
        if iso_code in self.countries:
            self.player_country_iso = iso_code
            print(f"Player country set to: {self.countries[iso_code].name}")
        else:
            print(f"Error: Country with ISO code {iso_code} not found.")

    def next_turn(self):
        """Advances the game by one turn."""
        self.current_turn += 1
        print(f"\n--- Advancing to Turn {self.current_turn} ---")

        # 1. AI Decisions (Placeholder)
        self._run_ai_turns()

        # 2. Apply Policies / Actions (Placeholder)
        # This is where tariff effects, etc., would be calculated

        # 3. Economic Update (Placeholder)
        self._update_economies()

        # 4. Check Game End Conditions (Placeholder)

        print(f"--- Turn {self.current_turn} End ---")

    def apply_policy(self, iso_code: str, policy: dict):
        """Modtager og anvender politikvalg fra UI (skat, G, subsidier, rente)."""
        country = self.countries.get(iso_code)
        if not country:
            return {"status": "error", "message": "Country not found"}
        # Fiskalpolitik
        if 'tax' in policy:
            country.tax_rate = float(policy['tax'])
        if 'gov' in policy:
            country.government_spending = float(policy['gov']) * country.gdp  # G i % af BNP
        # Subsidier
        if 'subsidySector' in policy and 'subsidyAmount' in policy:
            for sector in getattr(country, 'sectors', []):
                if sector.name == policy['subsidySector'] and policy['subsidySector'] != 'none':
                    sector.output += float(policy['subsidyAmount']) * 0.00001  # Effektfaktor kan kalibreres
                    country.government_spending = getattr(country, 'government_spending', 0.18 * country.gdp) + float(policy['subsidyAmount'])
        # Rente
        if 'interest' in policy:
            country.policy_rate = float(policy['interest'])
        # Told
        if 'sector' in policy and 'rate' in policy:
            if 'WORLD' not in country.tariffs:
                country.tariffs['WORLD'] = {}
            country.tariffs['WORLD'][policy['sector']] = float(policy['rate'])
        return {"status": "success", "message": "Policy applied"}

    def _run_ai_turns(self):
        """AI-logik for ikke-spillerlande: utility-baseret beslutning + FSM-tilstand."""
        print("AI countries are thinking...")
        for iso_code, country in self.countries.items():
            if iso_code == self.player_country_iso:
                continue
            # --- AI-profil/personlighed ---
            regime = getattr(country, 'government_type', 'democracy')
            ai_profile = AI_PROFILES.get(regime, AI_PROFILES['democracy'])
            # --- FSM/BT-tilstand (placeholder: kun 'neutral' nu) ---
            if not hasattr(country, 'ai_state'):
                country.ai_state = AIStrategyState('neutral')
            # --- Utility-baseret beslutning om told og sektorbeskyttelse ---
            # Eksempel: vægtet sum af mål (kan udvides)
            utility = 0
            # Vægt på vækst
            utility += ai_profile.growth_weight * getattr(country, 'growth_rate', 1.0)
            # Vægt på trust/approval
            utility += ai_profile.trust_weight * getattr(country, 'approval_rating', 50) / 100
            # Vægt på sektorbeskyttelse (fx hvis nøglesektor falder)
            if getattr(country, 'sectors', []):
                key_sector = max(country.sectors, key=lambda s: s.output)
                if key_sector.output < 0.9 * key_sector.potential_output:
                    utility += ai_profile.sector_protection * (1 - key_sector.output / key_sector.potential_output)
                    # Beskyt sektor med told hvis utility lav
                    if utility < 1.5:
                        if 'WORLD' not in country.tariffs:
                            country.tariffs['WORLD'] = {}
                        country.tariffs['WORLD'][key_sector.name] = min(0.3, country.tariffs['WORLD'].get(key_sector.name, 0.0) + 0.05)
            # Retaliation: gengæld hvis spiller har hævet told
            player = self.countries.get(self.player_country_iso)
            if player and player.tariffs and iso_code in player.tariffs:
                if ai_profile.retaliation > 0.5:
                    for sector_name, rate in player.tariffs[iso_code].items():
                        if iso_code not in country.tariffs:
                            country.tariffs[iso_code] = {}
                        country.tariffs[iso_code][sector_name] = rate
            # Placeholder: juster skat/rente hvis gæld er høj
            if getattr(country, 'debt', 0.0) > 1.0 * getattr(country, 'gdp', 1.0):
                country.tax_rate = min(0.5, getattr(country, 'tax_rate', 0.2) + 0.01)
                country.policy_rate = min(5.0, getattr(country, 'policy_rate', 2.0) + 0.1)
            # Forklarende feedback (kan sendes til UI)
            country.last_ai_explanation = f"AI ({regime}) utility: {utility:.2f}, state: {country.ai_state.state}, key sector: {key_sector.name if getattr(country, 'sectors', []) else 'N/A'}"

    def _update_economies(self):
        """Opdaterer økonomiske indikatorer for alle lande og deres sektorer."""
        print("Updating economic indicators...")
        for country in self.countries.values():
            # --- Handelsblokke: brug fælles tariffer hvis landet er medlem ---
            from .models import get_trade_bloc_for_country
            bloc = get_trade_bloc_for_country(country.iso_code)
            if bloc:
                for sector in getattr(country, 'sectors', []):
                    # Overskriv evt. nationale tariffer med blok-tariffer
                    if not country.tariffs.get('WORLD'):
                        country.tariffs['WORLD'] = {}
                    country.tariffs['WORLD'][sector.name] = bloc.common_tariffs.get(sector.name, 0.0)
            # Opdater sektorer først
            for sector in getattr(country, 'sectors', []):
                # --- Handels- og prisdynamik pr. sektor ---
                # Eksempel: toldsats og importpris (kan udvides med flere lande og sektorer)
                tariff = 0.0
                if country.tariffs and sector.name in country.tariffs.get('WORLD', {}):
                    tariff = country.tariffs['WORLD'][sector.name]
                # Importpris: P_import = P_f * valutakurs * (1 + t_s)
                # For nu antages P_f = 1, valutakurs = 1 (kan udvides)
                sector.import_price = 1.0 * 1.0 * (1 + tariff)
                # Sektorens pris: P_d = (1 - μ_s) * P_hjem + μ_s * P_import
                sector.price = (1 - sector.import_share) * sector.price + sector.import_share * sector.import_price
                # --- Import/eksport elasticitet (forenklet placeholder) ---
                price_elasticity = -1.2  # Kan gøres sektorspecifik
                # Importvolumen reagerer på prisændring
                if hasattr(sector, 'import_'):
                    sector.import_ *= (sector.import_price / 1.0) ** price_elasticity
                # Eksportvolumen kan også afhænge af pris (placeholder)
                if hasattr(sector, 'export'):
                    sector.export *= (1.0 / sector.price) ** price_elasticity
                # Nettoeksport: NX_s = Export_s - Import_s
                sector.net_exports = sector.export - sector.import_
                # Output kan påvirkes af nettoeksport (forenklet)
                sector.output *= (1 + 0.01 * sector.net_exports / max(1, sector.output))
                # Opdater ledighed via Okuns lov (sektorspecifikt, placeholder)
                sector.unemployment_rate = max(0.5, sector.unemployment_rate - 0.05 * country.growth_rate)
            # Aggreger BNP og arbejdsløshed fra sektorer
            if getattr(country, 'sectors', []):
                country.gdp = sum(s.output for s in country.sectors)
                total_labor = sum(s.employment for s in country.sectors)
                if total_labor > 0:
                    country.unemployment_rate = sum(s.unemployment_rate * s.employment for s in country.sectors) / total_labor
            # --- Konsumfunktion (forbrug) ---
            mpc = 0.65
            c0 = 0.0
            tax_rate = getattr(country, 'tax_rate', 0.2)
            y_disposable = (1 - tax_rate) * country.gdp
            country.consumption = c0 + mpc * y_disposable
            # --- Opdater statsbudget og gæld inkl. subsidier ---
            g = getattr(country, 'government_spending', 0.18 * country.gdp)
            if hasattr(country, 'subsidy_total'):
                g += country.subsidy_total
            country.tax_revenue = tax_rate * country.gdp
            country.debt = getattr(country, 'debt', 0.0) + (g - country.tax_revenue)
            # --- Politisk tillid/approval (forenklet) ---
            growth = getattr(country, 'growth_rate', 1.0)
            inflation = getattr(country, 'inflation', 2.0)
            unemployment = getattr(country, 'unemployment_rate', 5.0)
            approval = getattr(country, 'approval_rating', 50)
            approval += 10 * (growth - 1) - 5 * (unemployment - 5) - 2 * max(0, inflation - 2)
            country.approval_rating = max(0, min(100, approval))
            # --- Makroøkonomisk feedback: valutakurs (placeholder) ---
            # Eksempel: delta_fx = k1 * (policyRate - policyRate_foreign) - k2 * (NX_current - NX_last)
            # For nu antages policyRate = 2.0, policyRate_foreign = 1.5, k1=0.5, k2=0.1
            k1 = 0.5
            k2 = 0.1
            policy_rate = getattr(country, 'policy_rate', 2.0)
            policy_rate_foreign = 1.5  # Kan gøres dynamisk
            nx_current = sum(getattr(s, 'net_exports', 0.0) for s in getattr(country, 'sectors', []))
            nx_last = getattr(country, 'nx_last', nx_current)
            delta_fx = k1 * (policy_rate - policy_rate_foreign) - k2 * (nx_current - nx_last)
            country.exchange_rate = getattr(country, 'exchange_rate', 1.0) + delta_fx
            country.nx_last = nx_current
            # --- Investering og kapacitetsudbygning (placeholder) ---
            # I = max(0, i0 + i1 * ΔGDP - i2 * r)
            i0, i1, i2 = 100, 1.0, 2.0
            gdp_last = getattr(country, 'gdp_last', country.gdp)
            delta_gdp = country.gdp - gdp_last
            investment = max(0, i0 + i1 * delta_gdp - i2 * policy_rate)
            # Fordel investering proportionalt med output
            total_output = sum(s.output for s in getattr(country, 'sectors', []))
            for sector in getattr(country, 'sectors', []):
                share = sector.output / total_output if total_output > 0 else 0
                sector.capital_stock += investment * share
                sector.potential_output += investment * share  # Forenklet
            country.gdp_last = country.gdp
            # --- Finanspolitik (placeholder) ---
            # Skatteprovenu og gæld
            tax_rate = getattr(country, 'tax_rate', 0.2)
            country.tax_revenue = tax_rate * country.gdp
            g = getattr(country, 'government_spending', 0.18 * country.gdp)
            country.debt = getattr(country, 'debt', 0.0) + (g - country.tax_revenue)

    def get_country_data(self, iso_code: str) -> Optional[Country]:
        """Returns the data for a specific country."""
        return self.countries.get(iso_code)

    def get_all_countries_data(self) -> Dict[str, Country]:
        """Returns the data for all countries."""
        return self.countries

    def get_country_list(self):
        """Returns a list of basic country info (name, iso_code)."""
        return [{'name': c.name, 'iso_code': c.iso_code} for c in self.countries.values()]

    def get_country_details(self, iso_code: str):
        """Returns detailed info for a specific country."""
        country = self.countries.get(iso_code)
        if country:
            # Convert Industry object to dict for JSON serialization
            industries_dict = country.industries.__dict__ if country.industries else {}
            # Return a dictionary representation of the country
            return {
                'name': country.name,
                'iso_code': country.iso_code,
                'gdp': country.gdp,
                'population': country.population,
                'industries': industries_dict,
                'trade_partners': country.trade_partners,
                'tariffs': country.tariffs,
                'unemployment_rate': country.unemployment_rate,
                'growth_rate': country.growth_rate,
                'approval_rating': country.approval_rating,
                'government_type': country.government_type,
                'is_eu_member': country.is_eu_member
            }
        return None

    def advance_turn(self):
        """Advances the game simulation by one turn."""
        self.current_turn += 1
        print(f"Advancing to turn {self.current_turn}")

        # --- Simple Economic Simulation Step ---
        for country in self.countries.values():
            # Basic GDP growth simulation (random fluctuation around growth rate)
            growth_factor = 1 + (country.growth_rate / 100) + (random.uniform(-0.5, 0.5) / 100)
            country.gdp *= growth_factor

            # Basic unemployment change (inversely related to growth, with randomness)
            unemployment_change = -0.1 * (growth_factor - 1) * 100 + random.uniform(-0.1, 0.1)
            country.unemployment_rate = max(0.5, country.unemployment_rate + unemployment_change)  # Ensure unemployment doesn't go below 0.5

            # Basic approval rating change (related to growth and unemployment)
            approval_change = (growth_factor - 1) * 50 - unemployment_change * 10 + random.uniform(-1, 1)
            country.approval_rating = max(0, min(100, country.approval_rating + approval_change))

            # TODO: Implement more sophisticated economic model based on Neoklassisk_Model_Simulationsspil.pdf
            # TODO: Simulate trade interactions, tariff effects, policy impacts, etc.

        print("Turn simulation complete.")
        # In a real application, you'd return the updated state or specific changes
        return {"message": f"Advanced to turn {self.current_turn}", "status": "success"}

# Example usage (can be removed later):
# if __name__ == '__main__':
#     import os
#     script_dir = os.path.dirname(__file__)
#     data_path = os.path.join(script_dir, '../data/countries.json')
#     engine = GameEngine(data_path)
#     print("Initial USA GDP:", engine.countries['USA'].gdp)
#     engine.advance_turn()
#     print("USA GDP after turn 1:", engine.countries['USA'].gdp)
#     print("USA Unemployment after turn 1:", engine.countries['USA'].unemployment_rate)
#     print("USA Approval after turn 1:", engine.countries['USA'].approval_rating)
