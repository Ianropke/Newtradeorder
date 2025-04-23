import json
import logging
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

    def to_dict(self) -> Dict[str, float]:
        return {
            'manufacturing': self.manufacturing,
            'services': self.services,
            'agriculture': self.agriculture
        }

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

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'output': self.output,
            'employment': self.employment,
            'import_share': self.import_share,
            'price': self.price,
            'capital_stock': self.capital_stock,
            'potential_output': self.potential_output,
            'import_price': self.import_price,
            'export': self.export,
            'import_': self.import_,
            'unemployment_rate': self.unemployment_rate
        }

class Country:
    def __init__(self, name: str, iso_code: str, gdp: float, population: float,
                 industries: Industry, trade_partners: Dict, tariffs: Dict,
                 unemployment_rate: float, growth_rate: float, approval_rating: float,
                 government_type: str, is_eu_member: Optional[bool] = False,
                 sectors: Optional[List[Sector]] = None, 
                 budget: Optional[Dict] = None,
                 subsidies: Optional[Dict] = None):
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
        # Budget structure: {'revenue': {...}, 'expenses': {...}, 'balance': float}
        self.budget = budget if budget is not None else {
            'revenue': {
                'taxation': 0.0,
                'tariffs': 0.0,
                'other': 0.0
            },
            'expenses': {
                'subsidies': 0.0,
                'social_services': 0.0,
                'defense': 0.0,
                'infrastructure': 0.0,
                'education': 0.0,
                'healthcare': 0.0
            },
            'balance': 0.0,
            'debt': 0.0,
            'debt_to_gdp_ratio': 0.0
        }
        
        # Subsidies structure: {'sector_name': {'amount': float, 'percentage': float, 'effects': {...}}}
        self.subsidies = subsidies if subsidies is not None else {}

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
            sectors=sectors,
            budget=data.get('budget', None),
            subsidies=data.get('subsidies', None)
        )

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'iso_code': self.iso_code,
            'gdp': self.gdp,
            'population': self.population,
            'industries': self.industries.to_dict() if hasattr(self.industries, 'to_dict') else self.industries,
            'trade_partners': self.trade_partners,
            'tariffs': self.tariffs,
            'unemployment_rate': self.unemployment_rate,
            'growth_rate': self.growth_rate,
            'approval_rating': self.approval_rating,
            'government_type': self.government_type,
            'is_eu_member': self.is_eu_member,
            'sectors': [s.to_dict() for s in self.sectors],
            'budget': self.budget,
            'subsidies': self.subsidies
        }

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
        logging.error("Country data file not found at %s", filepath)
        return {}
    except json.JSONDecodeError:
        logging.error("Could not decode JSON from %s", filepath)
        return {}
    except KeyError as e:
        logging.error("Missing key %s in country data in %s", e, filepath)
        return {}

class GameEvent:
    """
    Represents a game event that can affect one or more countries.
    Events can be diplomatic incidents, natural disasters, technological
    breakthroughs, or other global/regional happenings.
    """
    def __init__(self, event_id, event_type, title, description, 
                 affected_countries, options=None, turn_created=1, is_resolved=False):
        self.event_id = event_id
        self.event_type = event_type  # 'diplomatic', 'economic', 'natural', 'political', etc.
        self.title = title
        self.description = description
        self.affected_countries = affected_countries  # List of country ISO codes
        self.options = options or []  # Response options for player
        self.turn_created = turn_created
        self.is_resolved = is_resolved
        self.resolution_option = None  # Which option was chosen
        self.resolution_effects = {}  # The actual effects that were applied
    
    def add_option(self, option_id, text, effects):
        """Add a response option to the event"""
        self.options.append({
            'id': option_id,
            'text': text,
            'effects': effects  # dict of effects like {'country': 'USA', 'relation_change': -10}
        })
    
    def resolve(self, option_id):
        """Mark event as resolved with the given option"""
        self.is_resolved = True
        self.resolution_option = option_id
        
        # Find the option's effects
        for option in self.options:
            if option['id'] == option_id:
                self.resolution_effects = option['effects']
                break
    
    def to_dict(self):
        """Convert event to a dictionary for JSON serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'title': self.title,
            'description': self.description,
            'affected_countries': self.affected_countries,
            'options': self.options,
            'turn_created': self.turn_created,
            'is_resolved': self.is_resolved,
            'resolution_option': self.resolution_option,
            'resolution_effects': self.resolution_effects
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an event from a dictionary"""
        event = cls(
            event_id=data['event_id'],
            event_type=data['event_type'],
            title=data['title'],
            description=data['description'],
            affected_countries=data['affected_countries'],
            options=data.get('options', []),
            turn_created=data.get('turn_created', 1),
            is_resolved=data.get('is_resolved', False)
        )
        event.resolution_option = data.get('resolution_option')
        event.resolution_effects = data.get('resolution_effects', {})
        return event


class DiplomaticMission:
    """
    Represents a diplomatic mission between countries, such as trade delegations,
    cultural exchanges, state visits, or other diplomatic activities.
    """
    def __init__(self, mission_id: str, mission_type: str, 
                 origin_country: str, target_country: str,
                 title: str, description: str, 
                 turn_started: int, duration: int,
                 status: str = "ongoing", 
                 benefits: Dict = None,
                 cost: float = 0.0):
        """
        Initialize a diplomatic mission.
        
        Args:
            mission_id: Unique identifier for the mission
            mission_type: Type of mission (trade_delegation, cultural_exchange, state_visit, etc.)
            origin_country: ISO code of the country initiating the mission
            target_country: ISO code of the country receiving the mission
            title: Short title describing the mission
            description: Full description of the mission
            turn_started: Game turn when the mission began
            duration: Expected duration in turns
            status: Current status (proposed, ongoing, completed, failed)
            benefits: Dictionary of expected or actual benefits
            cost: Economic cost of the mission to the initiating country
        """
        self.mission_id = mission_id
        self.mission_type = mission_type
        self.origin_country = origin_country
        self.target_country = target_country
        self.title = title
        self.description = description
        self.turn_started = turn_started
        self.duration = duration
        self.status = status
        self.benefits = benefits or {}
        self.cost = cost
        self.events = []  # Special events that occurred during the mission
        self.outcomes = {}  # Actual outcomes after completion
        
    def add_event(self, event_title: str, event_description: str, turn: int, impact: Dict = None):
        """Add a special event that occurred during the mission"""
        self.events.append({
            'title': event_title,
            'description': event_description,
            'turn': turn,
            'impact': impact or {}
        })
        
    def complete(self, outcomes: Dict, success_level: float = 1.0):
        """Mark the mission as completed with specific outcomes"""
        self.status = "completed"
        self.outcomes = outcomes
        
        # Apply outcome multiplier based on success level (0.0 to 1.0)
        for key, value in self.outcomes.items():
            if isinstance(value, (int, float)):
                self.outcomes[key] = value * success_level
                
    def abort(self, reason: str):
        """Abort the mission before completion"""
        self.status = "failed"
        self.outcomes = {"reason_for_failure": reason}
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'mission_id': self.mission_id,
            'mission_type': self.mission_type,
            'origin_country': self.origin_country,
            'target_country': self.target_country,
            'title': self.title,
            'description': self.description,
            'turn_started': self.turn_started,
            'duration': self.duration,
            'status': self.status,
            'benefits': self.benefits,
            'cost': self.cost,
            'events': self.events,
            'outcomes': self.outcomes
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        mission = cls(
            mission_id=data['mission_id'],
            mission_type=data['mission_type'],
            origin_country=data['origin_country'],
            target_country=data['target_country'],
            title=data['title'],
            description=data['description'],
            turn_started=data['turn_started'],
            duration=data['duration'],
            status=data.get('status', 'ongoing'),
            benefits=data.get('benefits', {}),
            cost=data.get('cost', 0.0)
        )
        mission.events = data.get('events', [])
        mission.outcomes = data.get('outcomes', {})
        return mission

