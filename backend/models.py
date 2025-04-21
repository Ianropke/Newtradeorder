import json
from typing import Dict, Optional, List

class Industry:
    def __init__(self, manufacturing: float, services: float, agriculture: float):
        self.manufacturing = manufacturing
        self.services = services
        self.agriculture = agriculture

    @classmethod
    def from_dict(cls, data: Dict[str, float]):
        return cls(
            manufacturing=data.get('manufacturing', 0.0),
            services=data.get('services', 0.0),
            agriculture=data.get('agriculture', 0.0)
        )

class Sector:
    """
    Repræsenterer en økonomisk sektor i et land.
    Attributes:
        name: Navn på sektoren (fx 'manufacturing', 'services', 'agriculture')
        output: Aktuelt output/værditilvækst (fx i mio. USD)
        employment: Antal beskæftigede i sektoren
        import_share: Andel af sektorens forbrug der importeres (μ_s)
        price: Aktuel pris på sektorens varer
        capital_stock: Kapitalbeholdning (til investering/kapacitet)
        potential_output: Potentielt output (kapacitetsgrænse)
        import_price: Pris på importerede varer i sektoren
        export: Eksportvolumen
        import_: Importvolumen
        unemployment_rate: Ledighed i sektoren
    """
    def __init__(self, name: str, output: float, employment: float, import_share: float,
                 price: float = 1.0, capital_stock: float = 0.0, potential_output: float = 0.0,
                 import_price: float = 1.0, export: float = 0.0, import_: float = 0.0,
                 unemployment_rate: float = 0.0):
        self.name = name
        self.output = output
        self.employment = employment
        self.import_share = import_share
        self.price = price
        self.capital_stock = capital_stock
        self.potential_output = potential_output
        self.import_price = import_price
        self.export = export
        self.import_ = import_
        self.unemployment_rate = unemployment_rate

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            name=data.get('name', ''),
            output=data.get('output', 0.0),
            employment=data.get('employment', 0.0),
            import_share=data.get('import_share', 0.0),
            price=data.get('price', 1.0),
            capital_stock=data.get('capital_stock', 0.0),
            potential_output=data.get('potential_output', 0.0),
            import_price=data.get('import_price', 1.0),
            export=data.get('export', 0.0),
            import_=data.get('import_', 0.0),
            unemployment_rate=data.get('unemployment_rate', 0.0)
        )

class Country:
    def __init__(self, name: str, iso_code: str, gdp: float, population: float,
                 industries: Industry, trade_partners: Dict, tariffs: Dict,
                 unemployment_rate: float, growth_rate: float, approval_rating: float,
                 government_type: str, is_eu_member: Optional[bool] = False,
                 sectors: Optional[List[Sector]] = None):
        self.name = name
        self.iso_code = iso_code
        self.gdp = gdp
        self.population = population
        self.industries = industries
        self.trade_partners = trade_partners # { "iso_code": { "exports": value, "imports": value } }
        self.tariffs = tariffs # { "iso_code": { "goods_category": rate } }
        self.unemployment_rate = unemployment_rate
        self.growth_rate = growth_rate
        self.approval_rating = approval_rating
        self.government_type = government_type
        self.is_eu_member = is_eu_member
        self.sectors = sectors if sectors is not None else []

    @classmethod
    def from_dict(cls, data: Dict):
        industries_data = data.get('industries', {})
        sectors_data = data.get('sectors', [])
        sectors = [Sector.from_dict(s) for s in sectors_data]
        return cls(
            name=data['name'],
            iso_code=data['iso_code'],
            gdp=data['gdp'],
            population=data['population'],
            industries=Industry.from_dict(industries_data),
            trade_partners=data.get('trade_partners', {}),
            tariffs=data.get('tariffs', {}),
            unemployment_rate=data['unemployment_rate'],
            growth_rate=data['growth_rate'],
            approval_rating=data['approval_rating'],
            government_type=data['government_type'],
            is_eu_member=data.get('is_eu_member', False),
            sectors=sectors
        )

class TradeBloc:
    """
    Repræsenterer en handelsblok (fx EU, NAFTA) med fælles politikker og medlemslande.
    """
    def __init__(self, name: str, members: list, common_tariffs: dict = None):
        self.name = name
        self.members = members  # Liste af ISO-koder
        self.common_tariffs = common_tariffs or {}  # { sektor: sats }

# Eksempel på handelsblokke (kan udvides og evt. lægges i datafil)
TRADE_BLOCS = [
    TradeBloc(
        name="EU",
        members=["DNK", "DEU", "FRA", "ITA", "ESP", "NLD", "BEL", "SWE", "FIN", "POL", "AUT", "CZE", "HUN", "SVK", "SVN", "EST", "LVA", "LTU", "HRV", "IRL", "PRT", "GRC", "ROU", "BGR", "LUX", "MLT", "CYP"],
        common_tariffs={"manufacturing": 0.03, "services": 0.01, "agriculture": 0.08}
    ),
    TradeBloc(
        name="NAFTA",
        members=["USA", "CAN", "MEX"],
        common_tariffs={"manufacturing": 0.01, "services": 0.0, "agriculture": 0.05}
    ),
    # Flere blokke kan tilføjes her
]

# Hjælpefunktion til at finde et lands handelsblok
def get_trade_bloc_for_country(iso_code):
    for bloc in TRADE_BLOCS:
        if iso_code in bloc.members:
            return bloc
    return None

class EconomicModel:
    """
    Overordnet økonomisk model, der holder styr på lande, sektorer og aggregering.
    """
    def __init__(self, countries: Dict[str, 'Country']):
        self.countries = countries  # Dict[iso_code, Country]
        # Sektorer kan evt. ligge i Country, men kan også samles her hvis global analyse ønskes

    def aggregate_gdp(self, country: 'Country') -> float:
        """Summerer output på tværs af sektorer for at beregne BNP."""
        if hasattr(country, 'sectors'):
            return sum(sector.output for sector in country.sectors)
        return country.gdp

    def aggregate_unemployment(self, country: 'Country') -> float:
        """Vægtet gennemsnit af sektorers ledighed."""
        if hasattr(country, 'sectors'):
            total_labor = sum(sector.employment for sector in country.sectors)
            if total_labor == 0:
                return 0.0
            return sum(sector.unemployment_rate * sector.employment for sector in country.sectors) / total_labor
        return country.unemployment_rate

def load_countries_from_file(filepath: str) -> Dict[str, Country]:
    """Loads country data from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            countries_data = json.load(f)
        
        countries = {}
        for country_data in countries_data:
            country = Country.from_dict(country_data)
            countries[country.iso_code] = country
        return countries
    except FileNotFoundError:
        print(f"Error: Country data file not found at {filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return {}
    except KeyError as e:
        print(f"Error: Missing key {e} in country data in {filepath}")
        return {}

# Example usage (can be removed later):
# if __name__ == '__main__':
#     # Assuming countries.json is in ../data/ relative to this file
#     import os
#     script_dir = os.path.dirname(__file__) 
#     data_path = os.path.join(script_dir, '../data/countries.json')
#     loaded_countries = load_countries_from_file(data_path)
#     if loaded_countries:
#         print(f"Loaded {len(loaded_countries)} countries.")
#         print(f"Example - USA GDP: {loaded_countries['USA'].gdp}")
#         print(f"Example - Denmark Industries: {loaded_countries['DNK'].industries.__dict__}")

