"""
Event Types Module for Trade War Simulator

This module defines all event types available in the game with their triggers, effects, and probability.
"""

import random
import uuid
from typing import Dict, List, Any, Callable

# Event type categories
EVENT_CATEGORIES = {
    'economic': {
        'name': 'Økonomisk',
        'description': 'Begivenheder relateret til økonomi, handel og finansielle markeder'
    },
    'political': {
        'name': 'Politisk',
        'description': 'Begivenheder relateret til politik, valg og regeringsskift'
    },
    'environmental': {
        'name': 'Miljø',
        'description': 'Begivenheder relateret til klima, naturkatastrofer og miljømæssige faktorer'
    },
    'technological': {
        'name': 'Teknologisk', 
        'description': 'Begivenheder relateret til teknologiske gennembrud og innovation'
    },
    'diplomatic': {
        'name': 'Diplomatisk',
        'description': 'Begivenheder relateret til internationale relationer og alliancer'
    },
    'social': {
        'name': 'Social',
        'description': 'Begivenheder relateret til sociale bevægelser og folkelig opinion'
    },
    'security': {
        'name': 'Sikkerhed',
        'description': 'Begivenheder relateret til national sikkerhed, militær og konflikter'
    },
    'trade': {
        'name': 'Handel',
        'description': 'Begivenheder specifikt relateret til handelskonflikter og -aftaler'
    }
}

# Effect types and how they should be processed
EFFECT_PROCESSORS = {
    'gdp_change': lambda country, value: setattr(country, 'gdp', country.gdp * (1 + value)),
    'approval_change': lambda country, value: setattr(country, 'approval_rating', min(1.0, max(0.0, country.approval_rating + value))),
    'relation_change': lambda game_state, country_a, country_b, value: game_state.adjust_relation(country_a, country_b, value),
    'trade_volume_change': lambda relation, value: setattr(relation, 'trade_volume', relation.trade_volume * (1 + value)),
    'industry_efficiency': lambda country, industry, value: setattr(country.industries[industry], 'efficiency', country.industries[industry].efficiency * (1 + value)),
    'productivity': lambda country, value: setattr(country, 'productivity', country.productivity * (1 + value)),
    'coalition_cohesion': lambda coalition, value: setattr(coalition, 'cohesion_level', min(1.0, max(0.0, coalition.cohesion_level + value))),
    'strategic_resource_gain': lambda country, resource, amount: country.add_resource(resource, amount)
}

class EventOption:
    """Class representing a response option for an event"""
    
    def __init__(self, 
                id: str,
                text: str,
                effects: List[Dict[str, Any]],
                ai_preference_factors: Dict[str, float] = None,
                requires_attribute: Dict[str, Any] = None,
                tooltip: str = None
               ):
        self.id = id
        self.text = text
        self.effects = effects
        self.ai_preference_factors = ai_preference_factors or {}
        self.requires_attribute = requires_attribute
        self.tooltip = tooltip
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'text': self.text,
            'effects': self.effects,
            'tooltip': self.tooltip
        }
    
    def is_available(self, country):
        """Check if this option is available based on country attributes"""
        if not self.requires_attribute:
            return True
            
        for attr_name, required_value in self.requires_attribute.items():
            # Handle nested attributes with dot notation
            if '.' in attr_name:
                parts = attr_name.split('.')
                obj = country
                for part in parts[:-1]:
                    if not hasattr(obj, part):
                        return False
                    obj = getattr(obj, part)
                
                if not hasattr(obj, parts[-1]):
                    return False
                    
                value = getattr(obj, parts[-1])
            else:
                if not hasattr(country, attr_name):
                    return False
                value = getattr(country, attr_name)
                
            # Check if the value meets the requirement
            if isinstance(required_value, dict):
                # Support for operators like 'min', 'max', 'equals'
                if 'min' in required_value and value < required_value['min']:
                    return False
                if 'max' in required_value and value > required_value['max']:
                    return False
                if 'equals' in required_value and value != required_value['equals']:
                    return False
            else:
                # Simple equality check
                if value != required_value:
                    return False
        
        return True
    
    def get_ai_preference(self, country_ai_profile):
        """Calculate how much an AI with a given profile would prefer this option"""
        preference_score = 0.5  # Base neutral score
        
        for factor, weight in self.ai_preference_factors.items():
            if hasattr(country_ai_profile, factor):
                factor_value = getattr(country_ai_profile, factor)
                preference_score += factor_value * weight
        
        # Normalize to 0-1 range
        return max(0.0, min(1.0, preference_score))

class EventType:
    """Class representing a specific type of event that can occur in the game"""
    
    def __init__(self, 
                id: str,
                category: str, 
                title_template: str,
                description_template: str,
                base_probability: float, # 0.0-1.0 per turn
                min_turn: int, # Minimum turn this can occur
                effects: List[Dict[str, Any]],
                options: List[EventOption],
                country_triggers: Dict[str, float] = None, # Country attributes that affect occurrence
                global_triggers: Dict[str, float] = None, # Global conditions that affect occurrence
                relation_triggers: Dict[str, float] = None, # Relation conditions that affect occurrence
                coalition_triggers: Dict[str, float] = None, # Coalition-related triggers
                max_occurrences: int = None, # Max times this can occur per game
                cooldown_turns: int = None, # Minimum turns between occurrences
                narrative_follow_ups: Dict[str, str] = None, # Narrative follow-up text keyed by option_id
                special_triggers: Dict[str, Callable] = None, # Special trigger functions for complex conditions
                exclusive_with: List[str] = None # Event IDs that can't trigger if this event has occurred
               ):
        self.id = id
        self.category = category
        self.title_template = title_template
        self.description_template = description_template
        self.base_probability = max(0.0, min(1.0, base_probability))
        self.min_turn = min_turn
        self.effects = effects
        self.options = options
        self.country_triggers = country_triggers or {}
        self.global_triggers = global_triggers or {}
        self.relation_triggers = relation_triggers or {}
        self.coalition_triggers = coalition_triggers or {}
        self.max_occurrences = max_occurrences
        self.cooldown_turns = cooldown_turns
        self.narrative_follow_ups = narrative_follow_ups or {}
        self.special_triggers = special_triggers or {}
        self.exclusive_with = exclusive_with or []
        
    def calculate_probability(self, game_state, country_code=None):
        """Calculate the actual probability of this event occurring based on game state"""
        if game_state.current_turn < self.min_turn:
            return 0.0
        
        # Check cooldown
        if hasattr(game_state, 'event_history'):
            last_occurrence = None
            for event in reversed(game_state.event_history):
                if event.get('type_id', '') == self.id and (not country_code or country_code in event.get('affected_countries', [])):
                    last_occurrence = event.get('turn')
                    break
                    
            if last_occurrence and self.cooldown_turns and game_state.current_turn - last_occurrence < self.cooldown_turns:
                return 0.0
        
        # Check max occurrences
        if self.max_occurrences:
            occurrences = 0
            for event in game_state.event_history:
                if event.get('type_id', '') == self.id and (not country_code or country_code in event.get('affected_countries', [])):
                    occurrences += 1
            
            if occurrences >= self.max_occurrences:
                return 0.0
        
        # Check exclusivity
        if hasattr(game_state, 'event_history'):
            for exclusive_event_id in self.exclusive_with:
                for event in game_state.event_history:
                    if event.get('type_id', '') == exclusive_event_id and (not country_code or country_code in event.get('affected_countries', [])):
                        return 0.0
            
        # Start with base probability
        probability = self.base_probability
        
        # Apply country-specific triggers if country is provided
        if country_code and country_code in game_state.countries:
            country = game_state.countries[country_code]
            for attribute, modifier in self.country_triggers.items():
                # Handle nested attributes with dot notation
                if '.' in attribute:
                    parts = attribute.split('.')
                    obj = country
                    for part in parts[:-1]:
                        if not hasattr(obj, part):
                            continue
                        obj = getattr(obj, part)
                    
                    if hasattr(obj, parts[-1]):
                        value = getattr(obj, parts[-1])
                        probability += value * modifier
                else:
                    if hasattr(country, attribute):
                        value = getattr(country, attribute)
                        probability += value * modifier
        
        # Apply global triggers
        for condition, modifier in self.global_triggers.items():
            # Global conditions could be things like "global_recession" or "climate_crisis"
            if hasattr(game_state, condition):
                value = getattr(game_state, condition)
                probability += value * modifier
        
        # Apply relation triggers
        if country_code and hasattr(game_state, 'diplomacy'):
            for other_country, modifier in self.relation_triggers.items():
                relation = game_state.diplomacy.get_relation(country_code, other_country)
                if relation:
                    relation_value = relation.relation_level
                    probability += relation_value * modifier
        
        # Apply coalition triggers
        if country_code and hasattr(game_state, 'diplomacy') and hasattr(game_state.diplomacy, 'coalitions'):
            for trigger, modifier in self.coalition_triggers.items():
                if trigger == 'is_in_coalition':
                    # Check if country is in any coalition
                    in_coalition = False
                    for coalition in game_state.diplomacy.coalitions:
                        if country_code in coalition.member_countries:
                            in_coalition = True
                            break
                    
                    if in_coalition:
                        probability += modifier
                elif trigger == 'is_coalition_leader':
                    # Check if country leads any coalition
                    is_leader = False
                    for coalition in game_state.diplomacy.coalitions:
                        if coalition.leader_country == country_code:
                            is_leader = True
                            break
                    
                    if is_leader:
                        probability += modifier
        
        # Apply special trigger functions
        for trigger_name, trigger_func in self.special_triggers.items():
            if trigger_func(game_state, country_code):
                # This is a boolean trigger that adds a specific value to probability
                probability += 0.1  # Could be parametrized per trigger
        
        return max(0.0, min(1.0, probability))
    
    def generate_event(self, game_state, country_code=None, turn=1):
        """Generate a concrete event from this template"""
        # For now, we'll just use a simple placeholder implementation
        affected_countries = [country_code] if country_code else []
        
        # Prepare templating variables
        template_vars = {
            'country': country_code if not country_code else game_state.countries[country_code].name
        }
        
        # Add other countries in random relations as template vars
        other_countries = list(game_state.countries.keys())
        if country_code and country_code in other_countries:
            other_countries.remove(country_code)
            
        if other_countries:
            template_vars['other_country'] = game_state.countries[random.choice(other_countries)].name
        
        # Industry sectors available
        sectors = ["Technology", "Manufacturing", "Agriculture", "Energy", "Services", "Finance"]
        template_vars['sector'] = random.choice(sectors)
        
        # Create options based on templates
        options = []
        for option in self.options:
            # Check if option is available based on country attributes
            if country_code and not option.is_available(game_state.countries[country_code]):
                continue
                
            options.append(option.to_dict())
        
        # If the event somehow ended up with no options, add a generic one
        if not options:
            options.append({
                'id': 'default_option',
                'text': 'Acceptér situationen',
                'effects': []
            })
        
        # Create event as a dictionary for flexibility
        event = {
            'event_id': f"{self.id}_{country_code if country_code else 'global'}_{turn}_{str(uuid.uuid4())[:8]}",
            'type_id': self.id,
            'category': self.category,
            'title': self.title_template.format(**template_vars),
            'description': self.description_template.format(**template_vars),
            'affected_countries': affected_countries,
            'turn_created': turn,
            'is_resolved': False,
            'options': options,
            'base_effects': self.effects
        }
        
        return event
    
    def apply_option_effects(self, game_state, event, option_id):
        """Apply the effects of a chosen option"""
        country_code = event['affected_countries'][0] if event['affected_countries'] else None
        
        # Find the selected option
        selected_option = None
        for option in event['options']:
            if option['id'] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return False
        
        # Apply option effects
        self._apply_effects(game_state, country_code, selected_option['effects'])
        
        # Also apply base event effects
        self._apply_effects(game_state, country_code, event.get('base_effects', []))
        
        # Mark event as resolved
        event['is_resolved'] = True
        event['resolution_option'] = option_id
        
        # Add narrative follow-up if available
        if option_id in self.narrative_follow_ups:
            event['narrative_follow_up'] = self.narrative_follow_ups[option_id].format(
                country=game_state.countries[country_code].name if country_code else 'The country'
            )
        
        return True
    
    def _apply_effects(self, game_state, country_code, effects):
        """Helper method to apply a list of effects"""
        if not country_code:
            return
            
        country = game_state.countries.get(country_code)
        if not country:
            return
            
        for effect in effects:
            effect_type = effect.get('type')
            value = effect.get('value', 0)
            
            # Handle different effect types
            if effect_type == 'gdp_change':
                if hasattr(country, 'gdp'):
                    country.gdp *= (1 + value)
                    
            elif effect_type == 'approval_change':
                if hasattr(country, 'approval_rating'):
                    country.approval_rating = min(1.0, max(0.0, country.approval_rating + value))
                    
            elif effect_type == 'relation_change':
                target_country = effect.get('target_country')
                if target_country and hasattr(game_state, 'diplomacy'):
                    game_state.diplomacy.adjust_relation(country_code, target_country, value)
                    
            elif effect_type == 'productivity':
                if hasattr(country, 'productivity'):
                    country.productivity *= (1 + value)
                    
            elif effect_type == 'industry_efficiency':
                industry = effect.get('industry')
                if industry and hasattr(country, 'industries') and industry in country.industries:
                    country.industries[industry].efficiency *= (1 + value)
                    
            # Handle other effect types as needed...

# Define a set of common economic event options
COMMON_ECONOMIC_OPTIONS = [
    EventOption(
        id="invest_stimulus",
        text="Investér i økonomiske stimuli",
        effects=[
            {"type": "gdp_change", "value": 0.03},
            {"type": "budget_impact", "value": -0.05},
            {"type": "approval_change", "value": 0.02}
        ],
        ai_preference_factors={
            "growth_weight": 0.6,
            "risk_aversion": -0.3
        },
        tooltip="Kortsigtet vækst på bekostning af budgetunderskud"
    ),
    EventOption(
        id="austerity_measures",
        text="Implementér besparelser",
        effects=[
            {"type": "gdp_change", "value": -0.02},
            {"type": "budget_impact", "value": 0.04},
            {"type": "approval_change", "value": -0.04}
        ],
        ai_preference_factors={
            "growth_weight": -0.5,
            "risk_aversion": 0.6
        },
        tooltip="Styrker budgettet, men bremser væksten og er upopulært"
    ),
    EventOption(
        id="balanced_approach",
        text="Balanceret tilgang",
        effects=[
            {"type": "gdp_change", "value": 0.01},
            {"type": "budget_impact", "value": -0.01},
            {"type": "approval_change", "value": 0.01}
        ],
        ai_preference_factors={
            "risk_aversion": 0.3
        },
        tooltip="Moderat effekt på alle områder"
    )
]

# Define a set of common diplomatic event options
COMMON_DIPLOMATIC_OPTIONS = [
    EventOption(
        id="aggressive_stance",
        text="Indtag en bestemt og hård position",
        effects=[
            {"type": "relation_change", "value": -0.1},
            {"type": "approval_change", "value": 0.05}
        ],
        ai_preference_factors={
            "retaliation": 0.7,
            "trust_weight": -0.5
        },
        tooltip="Populært hjemme, men forværrer internationale relationer"
    ),
    EventOption(
        id="diplomatic_solution",
        text="Søg diplomatisk løsning",
        effects=[
            {"type": "relation_change", "value": 0.08},
            {"type": "approval_change", "value": -0.02}
        ],
        ai_preference_factors={
            "trust_weight": 0.6,
            "retaliation": -0.4
        },
        tooltip="Forbedrer internationale relationer, men kan ses som svagt hjemme"
    ),
    EventOption(
        id="call_allies",
        text="Søg støtte fra allierede",
        effects=[
            {"type": "relation_change", "value": 0.03},
            {"type": "coalition_cohesion", "value": 0.05}
        ],
        ai_preference_factors={
            "trust_weight": 0.3
        },
        requires_attribute={"is_in_coalition": True},
        tooltip="Styrker relationer med allierede, men har begrænset direkte effekt"
    )
]

# Event types specific to trade conflicts
TRADE_EVENT_TYPES = [
    EventType(
        id="trade_tariff_threat",
        category="trade",
        title_template="Trusler om Toldsatser fra {other_country}",
        description_template="{other_country} truer med at indføre nye toldsatser på eksport fra {country}, hvilket kan ramme økonomien betydeligt.",
        base_probability=0.04,
        min_turn=3,
        effects=[{"type": "export_competitiveness", "value": -0.03}],
        options=[
            EventOption(
                id="reciprocal_tariffs",
                text="Indfør gengældelsestoldsatser",
                effects=[
                    {"type": "relation_change", "target_country": "{other_country}", "value": -0.15},
                    {"type": "trade_volume_change", "target_country": "{other_country}", "value": -0.1},
                    {"type": "gdp_change", "value": -0.01},
                    {"type": "approval_change", "value": 0.04}
                ],
                ai_preference_factors={"retaliation": 0.8, "growth_weight": -0.3},
                tooltip="Eskalerer konflikten og skader handel, men viser styrke"
            ),
            EventOption(
                id="negotiate",
                text="Foreslå handelsforhandlinger",
                effects=[
                    {"type": "relation_change", "target_country": "{other_country}", "value": 0.05},
                    {"type": "trade_volume_change", "target_country": "{other_country}", "value": -0.02},
                    {"type": "approval_change", "value": -0.01}
                ],
                ai_preference_factors={"trust_weight": 0.7, "retaliation": -0.5},
                tooltip="Minimerer skaden og åbner for dialog, men kan ses som svagt"
            ),
            EventOption(
                id="wto_complaint",
                text="Indbring sagen for WTO",
                effects=[
                    {"type": "trade_volume_change", "target_country": "{other_country}", "value": -0.05},
                    {"type": "global_reputation", "value": 0.03}
                ],
                ai_preference_factors={"trust_weight": 0.3, "retaliation": 0.3},
                tooltip="En mellemvej der bruger internationale institutioner"
            )
        ],
        country_triggers={"export_dependency": 0.2},
        relation_triggers={"{other_country}": -0.2},
        narrative_follow_ups={
            "reciprocal_tariffs": "Handelsministeren i {country} annoncerede i dag en pakke af gengældelsestoldsatser rettet mod import fra {other_country}. Analytikere frygter en eskalerende handelskrig.",
            "negotiate": "Diplomatiske kanaler er blevet åbnet mellem {country} og {other_country} for at løse handelsspændingerne gennem forhandling.",
            "wto_complaint": "{country} har formelt indbragt en klage til WTO over {other_country}s truende toldsatser, hvilket starter en længere juridisk proces."
        }
    ),
    EventType(
        id="supply_chain_disruption",
        category="trade",
        title_template="Forsyningskædeforstyrrelse i {sector} Sektoren",
        description_template="Globale forsyningskæder for {sector} er blevet afbrudt, hvilket påvirker produktionen og priserne i {country}.",
        base_probability=0.05,
        min_turn=2,
        effects=[{"type": "industry_efficiency", "industry": "{sector}", "value": -0.05}],
        options=[
            EventOption(
                id="domestic_investment",
                text="Investér i indenlandsk produktion",
                effects=[
                    {"type": "industry_efficiency", "industry": "{sector}", "value": 0.03},
                    {"type": "budget_impact", "value": -0.04},
                    {"type": "self_sufficiency", "industry": "{sector}", "value": 0.1}
                ],
                ai_preference_factors={"self_reliance": 0.6, "risk_aversion": -0.2},
                tooltip="Reducerer fremtidig sårbarhed, men er dyrt"
            ),
            EventOption(
                id="diversify_suppliers",
                text="Diversificér internationale leverandører",
                effects=[
                    {"type": "industry_efficiency", "industry": "{sector}", "value": 0.02},
                    {"type": "trade_dependency_diversification", "value": 0.05}
                ],
                ai_preference_factors={"trust_weight": 0.3, "risk_aversion": 0.3},
                tooltip="Balanceret tilgang der spreder risiko"
            ),
            EventOption(
                id="strategic_reserves",
                text="Opbyg strategiske reserver",
                effects=[
                    {"type": "strategic_resource_gain", "resource": "{sector}_materials", "amount": 100},
                    {"type": "budget_impact", "value": -0.02}
                ],
                ai_preference_factors={"risk_aversion": 0.6},
                tooltip="Kortsigtet buffer mod fremtidige forstyrrelser"
            )
        ],
        cooldown_turns=5,
        narrative_follow_ups={
            "domestic_investment": "{country} lancerer et ambitiøst program for at styrke den indenlandske {sector} produktion og reducere afhængighed af usikre globale forsyningskæder.",
            "diversify_suppliers": "Handelsministeren i {country} har mødt potentielle nye internationale leverandører for at diversificere landets {sector} forsyningskæder.",
            "strategic_reserves": "{country} begynder at opbygge strategiske reserver af kritiske {sector} materialer for at beskytte mod fremtidige forsyningsafbrydelser."
        }
    ),
    EventType(
        id="commodity_price_shock",
        category="economic",
        title_template="Global Prisstigning på Råvarer",
        description_template="Internationale priser på nøgleråvarer er steget kraftigt, hvilket presser industriens omkostninger i {country}.",
        base_probability=0.06,
        min_turn=2,
        effects=[
            {"type": "inflation", "value": 0.01},
            {"type": "production_costs", "value": 0.05}
        ],
        options=[
            EventOption(
                id="price_controls",
                text="Indfør midlertidige priskontroller",
                effects=[
                    {"type": "inflation", "value": -0.008},
                    {"type": "market_distortion", "value": 0.04},
                    {"type": "approval_change", "value": 0.03}
                ],
                ai_preference_factors={"market_intervention": 0.7, "growth_weight": -0.2},
                tooltip="Reducerer inflationen, men skaber markedsforvridninger"
            ),
            EventOption(
                id="stockpile_release",
                text="Frigiv strategiske reserver",
                effects=[
                    {"type": "production_costs", "value": -0.03},
                    {"type": "strategic_resource_loss", "resource": "commodity", "amount": 50}
                ],
                ai_preference_factors={"risk_aversion": -0.4},
                requires_attribute={"strategic_reserves.commodity": {"min": 50}},
                tooltip="Effektiv kortsigtet løsning hvis du har tilstrækkelige reserver"
            ),
            EventOption(
                id="market_adjustment",
                text="Lad markedet tilpasse sig",
                effects=[
                    {"type": "production_costs", "value": 0.02},
                    {"type": "inflation", "value": 0.005},
                    {"type": "economic_resilience", "value": 0.03}
                ],
                ai_preference_factors={"market_intervention": -0.6, "risk_aversion": 0.3},
                tooltip="Kortsigtet smerte, men styrker langsigtet markedseffektivitet"
            )
        ],
        max_occurrences=3,
        cooldown_turns=8
    ),
    EventType(
        id="export_breakthrough",
        category="trade",
        title_template="Eksportgennembrud i {sector} Industrien",
        description_template="{country}s {sector} industri har opnået et betydeligt gennembrud på eksportmarkederne.",
        base_probability=0.03,
        min_turn=5,
        effects=[
            {"type": "export_competitiveness", "industry": "{sector}", "value": 0.08},
            {"type": "gdp_change", "value": 0.01}
        ],
        options=[
            EventOption(
                id="trade_mission",
                text="Lancér handelsmissioner for at kapitalisere",
                effects=[
                    {"type": "export_competitiveness", "industry": "{sector}", "value": 0.05},
                    {"type": "new_market_access", "value": 0.07},
                    {"type": "budget_impact", "value": -0.01}
                ],
                ai_preference_factors={"growth_weight": 0.6, "risk_aversion": -0.2},
                tooltip="Investér for at maksimere effekten og åbne nye markeder"
            ),
            EventOption(
                id="export_incentives",
                text="Tilbyd eksportincitamenter",
                effects=[
                    {"type": "export_competitiveness", "industry": "{sector}", "value": 0.03},
                    {"type": "budget_impact", "value": -0.02},
                    {"type": "industry_growth", "industry": "{sector}", "value": 0.04}
                ],
                ai_preference_factors={"sector_protection": 0.4, "growth_weight": 0.4},
                tooltip="Styrker industrien og eksporten med skattefordele"
            ),
            EventOption(
                id="technology_protection",
                text="Implementér teknologibeskyttelse",
                effects=[
                    {"type": "technology_leadership", "industry": "{sector}", "value": 0.05},
                    {"type": "export_competitiveness", "industry": "{sector}", "value": -0.01}
                ],
                ai_preference_factors={"technology_protectionism": 0.7, "trust_weight": -0.3},
                tooltip="Beskytter forspring på længere sigt, begrænser eksport nu"
            )
        ],
        country_triggers={"industries.{sector}.efficiency": 0.3},
        narrative_follow_ups={
            "trade_mission": "{country}s handelsminister leder en delegation af {sector} virksomheder på en global turné for at promovere eksport efter det nylige gennembrud.",
            "export_incentives": "Regeringen i {country} annoncerer en pakke af skattefordele og incitamenter for at øge {sector} eksporten og kapitalisere på det nylige gennembrud.",
            "technology_protection": "{country} indfører strenge patentbeskyttelser og eksportkontroller for at beskytte det teknologiske forspring i {sector} industrien."
        }
    ),
    EventType(
        id="trade_bloc_formation",
        category="diplomatic",
        title_template="Dannelse af Ny Handelsblok",
        description_template="En gruppe af lande forbereder dannelsen af en ny handelsblok, hvilket kan have stor indflydelse på {country}s eksportmarkeder.",
        base_probability=0.02,
        min_turn=10,
        effects=[{"type": "market_access_risk", "value": 0.05}],
        options=[
            EventOption(
                id="join_bloc",
                text="Ansøg om medlemskab",
                effects=[
                    {"type": "trade_bloc_participation", "value": 1},
                    {"type": "trade_dependency", "value": 0.05},
                    {"type": "market_access", "value": 0.08},
                    {"type": "economic_sovereignty", "value": -0.04}
                ],
                ai_preference_factors={"trust_weight": 0.5, "self_reliance": -0.6},
                tooltip="Giver markedsadgang men øger afhængighed og reducerer suverænitet"
            ),
            EventOption(
                id="negotiate_external_deal",
                text="Forhandl særaftale som ikke-medlem",
                effects=[
                    {"type": "market_access", "value": 0.04},
                    {"type": "diplomatic_focus", "value": 0.05}
                ],
                ai_preference_factors={"trust_weight": 0.2, "self_reliance": 0.2},
                tooltip="Balanceret tilgang der giver delvis adgang uden fuld integration"
            ),
            EventOption(
                id="form_counter_bloc",
                text="Initiativer til modvægt-alliance",
                effects=[
                    {"type": "diplomatic_focus", "value": 0.1},
                    {"type": "coalition_formation", "value": 0.5},
                    {"type": "international_tension", "value": 0.05}
                ],
                ai_preference_factors={"retaliation": 0.3, "self_reliance": 0.7},
                tooltip="Ambitiøs strategi for at danne din egen handelsblok"
            )
        ],
        global_triggers={"international_tension": 0.2},
        narrative_follow_ups={
            "join_bloc": "{country} har officielt indgivet ansøgning om medlemskab i den nyoprettede handelsblok, hvilket signalerer et skift i landets handelsstrategi.",
            "negotiate_external_deal": "Forhandlere fra {country} har indledt samtaler om en særlig handelsaftale med den nye handelsblok, samtidig med at landet bevarer sin uafhængighed.",
            "form_counter_bloc": "I et dristigt modtræk har {country} indkaldt til forhandlinger med ligesindede nationer om at danne en konkurrerende handelsalliance."
        }
    )
]

ALL_EVENT_TYPES = TRADE_EVENT_TYPES

def check_and_trigger_events(game_engine):
    """
    Checks event conditions and triggers appropriate events.
    Returns a list of new events to be added to the game state.
    """
    new_events = []
    current_turn = game_engine.current_turn
    
    # Get all countries data
    countries = game_engine.get_all_countries_data()
    
    # Check each event type for trigger conditions
    for event_type in ALL_EVENT_TYPES:
        # Skip if minimum turn requirement not met
        if event_type.min_turn > current_turn:
            continue
            
        # Check max occurrences if implemented
        if hasattr(event_type, 'max_occurrences') and hasattr(game_engine, 'event_history'):
            past_occurrences = sum(1 for e in game_engine.event_history 
                                 if e.get('event_type_id') == event_type.id)
            if past_occurrences >= event_type.max_occurrences:
                continue
        
        # Check cooldown if implemented
        if hasattr(event_type, 'cooldown_turns') and hasattr(game_engine, 'event_history'):
            last_occurrence = next((e for e in reversed(game_engine.event_history) 
                                 if e.get('event_type_id') == event_type.id), None)
            if last_occurrence and (current_turn - last_occurrence.get('turn_created', 0)) < event_type.cooldown_turns:
                continue
        
        # Check global triggers
        global_triggers_active = True
        if hasattr(event_type, 'global_triggers') and event_type.global_triggers:
            for trigger_name, probability in event_type.global_triggers.items():
                # For now, simply use the probability as a check
                # Later, implement more complex trigger conditions
                if random.random() > probability:
                    global_triggers_active = False
                    break
        
        if not global_triggers_active:
            continue
            
        # For each country, check if this event could affect it
        for country_iso, country_data in countries.items():
            # Skip processing if probability test fails
            if random.random() > event_type.base_probability:
                continue
                
            # Check country-specific triggers
            country_triggers_active = True
            if hasattr(event_type, 'country_triggers') and event_type.country_triggers:
                for trigger_name, probability in event_type.country_triggers.items():
                    # If the country has a relevant attribute, use it to modify probability
                    # Otherwise just use the base probability
                    country_value = country_data.get(trigger_name, 0)
                    trigger_probability = probability * (1 + country_value)
                    
                    if random.random() > trigger_probability:
                        country_triggers_active = False
                        break
            
            if not country_triggers_active:
                continue
                
            # Event triggered for this country
            country_name = country_data.get('name', country_iso)
            
            # Format the title and description
            title = event_type.title_template.format(country=country_name)
            description = event_type.description_template.format(country=country_name)
            
            # Convert event options to expected format
            formatted_options = []
            for option in event_type.options:
                # Convert effect formats from type-value to target-attribute-change
                formatted_effects = []
                for effect in option.effects:
                    formatted_effect = _convert_effect_format(effect, country_iso)
                    formatted_effects.append(formatted_effect)
                
                formatted_options.append({
                    'id': option.id,
                    'text': option.text,
                    'effects': formatted_effects,
                    'ai_preference_factors': option.ai_preference_factors if hasattr(option, 'ai_preference_factors') else {},
                    'tooltip': option.tooltip if hasattr(option, 'tooltip') else None
                })
            
            # Create the new event
            new_event = {
                'event_id': f"{event_type.id}_{current_turn}_{country_iso}",
                'event_type_id': event_type.id,
                'event_type': event_type.category,
                'title': title,
                'description': description,
                'affected_countries': [country_iso],
                'options': formatted_options,
                'turn_created': current_turn,
                'is_resolved': False,
                'narrative_follow_ups': event_type.narrative_follow_ups if hasattr(event_type, 'narrative_follow_ups') else {}
            }
            
            # Convert main event effects
            formatted_effects = []
            for effect in event_type.effects:
                formatted_effect = _convert_effect_format(effect, country_iso)
                formatted_effects.append(formatted_effect)
            
            new_event['effects'] = formatted_effects
            
            # Add to the new events list
            new_events.append(new_event)
    
    # Add an event history property if not present
    if not hasattr(game_engine, 'event_history'):
        game_engine.event_history = []
    
    # Add the new events to history
    game_engine.event_history.extend(new_events)
    
    return new_events

def _convert_effect_format(effect, country_iso):
    """
    Converts the effect format from {type: value} to the format expected by the engine:
    {target: string, attribute: string, change: number}
    """
    formatted_effect = {}
    
    # Extract the effect type and value
    effect_type = effect.get('type')
    effect_value = effect.get('value', 0)
    
    # Map effect types to target attributes
    effect_mapping = {
        # Economy effects
        'gdp_change': {'target': 'country', 'attribute': 'gdp_growth'},
        'trade_volume_change': {'target': 'country', 'attribute': 'trade_volume'},
        'production_costs': {'target': 'country', 'attribute': 'production_cost_multiplier'},
        'budget_impact': {'target': 'country', 'attribute': 'budget'},
        'strategic_independence': {'target': 'country', 'attribute': 'economic_independence'},
        'trade_route_resilience': {'target': 'country', 'attribute': 'trade_resilience'},
        'trade_efficiency': {'target': 'country', 'attribute': 'trade_efficiency'},
        'trade_vulnerability': {'target': 'country', 'attribute': 'trade_vulnerability'},
        'economic_resilience': {'target': 'country', 'attribute': 'economic_resilience'},
        'capital_efficiency': {'target': 'country', 'attribute': 'capital_efficiency'},
        'strategic_resource_stockpile': {'target': 'country', 'attribute': 'resource_stockpile'},
        
        # Security and infrastructure effects
        'critical_infrastructure_damage': {'target': 'country', 'attribute': 'infrastructure_integrity'},
        'critical_infrastructure_protection': {'target': 'country', 'attribute': 'infrastructure_integrity'},
        'digital_vulnerability': {'target': 'country', 'attribute': 'cyber_vulnerability'},
        'digital_deterrence': {'target': 'country', 'attribute': 'cyber_deterrence'},
        'infrastructure_damage': {'target': 'country', 'attribute': 'infrastructure_integrity'},
        'infrastructure_modernization': {'target': 'country', 'attribute': 'infrastructure_quality'},
        'infrastructure_quality': {'target': 'country', 'attribute': 'infrastructure_quality'},
        'future_disaster_vulnerability': {'target': 'country', 'attribute': 'disaster_vulnerability'},
        
        # Diplomatic and social effects
        'relation_change': {'target': 'relation', 'attribute': 'relation_level'},
        'international_tension': {'target': 'country', 'attribute': 'international_tension'},
        'global_reputation': {'target': 'country', 'attribute': 'global_reputation'},
        'diplomatic_focus': {'target': 'country', 'attribute': 'diplomatic_focus'},
        'intelligence_sharing': {'target': 'country', 'attribute': 'intel_sharing_level'},
        'digital_connectivity': {'target': 'country', 'attribute': 'digital_connectivity'},
        'public_confidence': {'target': 'country', 'attribute': 'public_approval'},
        'social_stability': {'target': 'country', 'attribute': 'social_stability'},
        'approval_change': {'target': 'country', 'attribute': 'public_approval'},
        
        # Technology effects
        'technological_leadership': {'target': 'country', 'attribute': 'tech_leadership'},
        'cryptographic_security': {'target': 'country', 'attribute': 'crypto_security'},
        'academic_prestige': {'target': 'country', 'attribute': 'academic_reputation'},
        'computing_power': {'target': 'country', 'attribute': 'computing_capability'},
        'talent_attraction': {'target': 'country', 'attribute': 'talent_attraction'},
        'tech_independence': {'target': 'country', 'attribute': 'tech_independence'},
        'technology_development': {'target': 'country', 'attribute': 'tech_development_rate'},
        'scientific_collaboration': {'target': 'country', 'attribute': 'scientific_collaboration'},
        'technological_diffusion': {'target': 'country', 'attribute': 'tech_diffusion_rate'},
        
        # Political effects
        'political_stability': {'target': 'country', 'attribute': 'political_stability'},
        'decision_making_effectiveness': {'target': 'country', 'attribute': 'decision_effectiveness'},
        'democratic_institutions': {'target': 'country', 'attribute': 'democratic_strength'},
        'decision_making_speed': {'target': 'country', 'attribute': 'decision_speed'},
        'diplomatic_reputation': {'target': 'country', 'attribute': 'diplomatic_reputation'},
        'civil_liberties': {'target': 'country', 'attribute': 'civil_liberties'},
        'domestic_opposition': {'target': 'country', 'attribute': 'opposition_strength'},
        'income_inequality': {'target': 'country', 'attribute': 'income_inequality'},
        'fiscal_sustainability': {'target': 'country', 'attribute': 'fiscal_sustainability'},
        'democratic_responsiveness': {'target': 'country', 'attribute': 'democratic_responsiveness'},
        'public_participation': {'target': 'country', 'attribute': 'public_participation'},
        
        # Resource and industry effects
        'agricultural_output': {'target': 'country', 'attribute': 'agricultural_output'},
        'climate_resilience': {'target': 'country', 'attribute': 'climate_resilience'},
        'private_sector_confidence': {'target': 'country', 'attribute': 'business_confidence'},
        'economic_recovery_speed': {'target': 'country', 'attribute': 'economic_recovery_rate'},
        'climate_leadership': {'target': 'country', 'attribute': 'climate_leadership'},
        'strategic_resource_access': {'target': 'country', 'attribute': 'strategic_resources'},
        'foreign_investor_interest': {'target': 'country', 'attribute': 'foreign_investment_attractiveness'},
        'regional_influence': {'target': 'country', 'attribute': 'regional_influence'},
        'economic_potential': {'target': 'country', 'attribute': 'economic_potential'},
        'resource_development_speed': {'target': 'country', 'attribute': 'resource_development_rate'},
        'environmental_reputation': {'target': 'country', 'attribute': 'environmental_reputation'},
        'resource_longevity': {'target': 'country', 'attribute': 'resource_sustainability'},
        'green_technology_development': {'target': 'country', 'attribute': 'green_tech_development'},
        'resource_market_power': {'target': 'country', 'attribute': 'resource_market_power'}
    }
    
    # Handle sector-specific effects
    if 'industry' in effect:
        formatted_effect['target'] = 'sector'
        formatted_effect['sector_name'] = effect['industry']
        formatted_effect['attribute'] = 'efficiency'
        formatted_effect['change'] = effect_value
        return formatted_effect
    
    # Handle relation effects with target country
    if 'target_country' in effect:
        formatted_effect['target'] = 'relation'
        formatted_effect['country_a'] = country_iso
        formatted_effect['country_b'] = effect['target_country']
        formatted_effect['attribute'] = 'relation_level'
        formatted_effect['change'] = effect_value
        return formatted_effect
    
    # Handle general effects
    if effect_type in effect_mapping:
        mapping = effect_mapping[effect_type]
        formatted_effect['target'] = mapping['target']
        formatted_effect['attribute'] = mapping['attribute']
        formatted_effect['change'] = effect_value
        
        # Add country code for country targets
        if mapping['target'] == 'country':
            formatted_effect['country_code'] = country_iso
    else:
        # Default fallback for unknown effect types
        formatted_effect['target'] = 'country'
        formatted_effect['attribute'] = effect_type
        formatted_effect['change'] = effect_value
        formatted_effect['country_code'] = country_iso
    
    # Set a default duration of 3 turns if not specified
    formatted_effect['duration'] = effect.get('duration', 3)
    
    return formatted_effect

class EventSystem:
    """
    System for managing game events including creation, resolution, and history tracking.
    """
    
    def __init__(self):
        self.events = []  # Active events
        self.event_history = []  # Resolved events
        
    def add_event(self, event):
        """Add a new event to the system"""
        self.events.append(event)
        
    def get_events_for_country(self, country_iso, include_resolved=False):
        """Get events that affect a specific country"""
        country_events = []
        
        # Check active events
        for event in self.events:
            affected_countries = event.get('affected_countries', []) if isinstance(event, dict) else getattr(event, 'affected_countries', [])
            if country_iso in affected_countries:
                country_events.append(event)
        
        # Include resolved events if requested
        if include_resolved:
            for event in self.event_history:
                affected_countries = event.get('affected_countries', []) if isinstance(event, dict) else getattr(event, 'affected_countries', [])
                if country_iso in affected_countries:
                    country_events.append(event)
        
        return country_events
    
    def resolve_event(self, event_id, option_id, game_state):
        """
        Resolve an event with the selected option and apply its effects.
        Returns the resolved event and applied effects.
        """
        # Find the event
        event = None
        for e in self.events:
            event_id_value = e.get('event_id') if isinstance(e, dict) else getattr(e, 'event_id', None)
            if event_id_value == event_id:
                event = e
                break
        
        if not event:
            return None, []
        
        # Process the event resolution
        effects_applied = []
        
        if isinstance(event, dict):
            # Find the selected option
            selected_option = None
            for option in event.get('options', []):
                if option.get('id') == option_id:
                    selected_option = option
                    break
            
            if selected_option:
                # Apply the effects
                effects = selected_option.get('effects', [])
                event['is_resolved'] = True
                event['resolution_option'] = option_id
                event['resolution_effects'] = effects
                event['resolution_turn'] = game_state.current_turn
                
                # Apply effects through game engine
                game_state._apply_event_effects([event])
                effects_applied = effects
                
                # Move from active to history
                self.events.remove(event)
                self.event_history.append(event)
        else:
            # Handle class-based events
            effects_applied = self.apply_event_effects(event, game_state, option_id)
            
        return event, effects_applied
        
    def apply_event_effects(self, event, game_state, option_id):
        """Apply the effects of an event option to the game state"""
        # This method handles class-based events
        # For dict-based events, effects are applied directly in resolve_event
        
        # Implementation depends on your event class structure
        return []
        
    def process_turn_events(self, game_state):
        """
        Process events for the current turn.
        This should be called at the beginning of each turn.
        """
        # Generate new events
        new_events = check_and_trigger_events(game_state)
        
        # Add them to the active events
        for event in new_events:
            self.add_event(event)
            
        # Process any ongoing event effects
        # (e.g., events with duration > 1 turn)
        
        return new_events
        
    def cleanup_expired_events(self, game_state):
        """Remove events that have expired (e.g., time-limited events)"""
        current_turn = game_state.current_turn
        
        # Check for expired events
        expired = []
        for event in self.events:
            # Get expiration turn if available
            expiration = event.get('expires_on_turn') if isinstance(event, dict) else getattr(event, 'expires_on_turn', None)
            
            # Add to expired list if past expiration
            if expiration and current_turn > expiration:
                expired.append(event)
        
        # Remove expired events
        for event in expired:
            self.events.remove(event)
            
            # Add to history if not already there
            if event not in self.event_history:
                event['expired'] = True
                self.event_history.append(event)
                
        return expired

def check_and_trigger_events(game_state):
    """
    Check conditions and trigger appropriate events based on game state.
    Returns a list of new event instances that were triggered.
    """
    new_events = []
    
    # Get all registered event types
    event_types_to_check = [et for et in globals().values() 
                          if isinstance(et, type) and issubclass(et, EventType) and et != EventType]
    
    # If no custom event types are defined, use predefined events
    if not event_types_to_check:
        # Fall back to basic events dictionary (if defined elsewhere in this module)
        event_types_to_check = globals().get('BASIC_EVENTS', {}).values()
    
    # Check each event type to see if it should trigger
    for event_type in event_types_to_check:
        if isinstance(event_type, type):
            # It's a class, instantiate it
            event_instance = event_type()
            prob = event_instance.calculate_probability(game_state)
        else:
            # It's already an instance
            prob = event_type.calculate_probability(game_state)
            event_instance = event_type
            
        # Roll the dice to see if this event occurs
        if random.random() < prob:
            # Event is triggered!
            event_data = {
                'event_id': str(uuid.uuid4()),
                'type_id': event_instance.id,
                'category': event_instance.category,
                'title': event_instance.title_template,
                'description': event_instance.description_template,
                'turn': game_state.current_turn,
                'effects': event_instance.effects,
                'options': [option.to_dict() for option in event_instance.options],
                'is_resolved': False,
                'affected_countries': _determine_affected_countries(game_state, event_instance),
            }
            
            # Format title and description with country names
            if '{country}' in event_data['title'] and event_data['affected_countries']:
                primary_country = event_data['affected_countries'][0]
                country_name = game_state.countries[primary_country].name if primary_country in game_state.countries else primary_country
                event_data['title'] = event_data['title'].replace('{country}', country_name)
                
            if '{country}' in event_data['description'] and event_data['affected_countries']:
                primary_country = event_data['affected_countries'][0]
                country_name = game_state.countries[primary_country].name if primary_country in game_state.countries else primary_country
                event_data['description'] = event_data['description'].replace('{country}', country_name)
            
            new_events.append(event_data)
    
    return new_events

def _determine_affected_countries(game_state, event_type):
    """
    Determine which countries are affected by an event based on event type and game state.
    """
    affected = []
    
    # If the event specifies countries directly, use those
    if hasattr(event_type, 'affected_countries') and event_type.affected_countries:
        return event_type.affected_countries
    
    # Otherwise use country triggers to determine affected nations
    for country_code, country in game_state.countries.items():
        # Skip if country doesn't match any triggers
        matches_all_triggers = True
        
        for attr, value in event_type.country_triggers.items():
            if not hasattr(country, attr):
                matches_all_triggers = False
                break
                
            country_value = getattr(country, attr)
            
            # Handle different types of trigger values
            if isinstance(value, dict):
                # Complex trigger with min/max/equals
                if 'min' in value and country_value < value['min']:
                    matches_all_triggers = False
                    break
                if 'max' in value and country_value > value['max']:
                    matches_all_triggers = False
                    break
                if 'equals' in value and country_value != value['equals']:
                    matches_all_triggers = False
                    break
            elif isinstance(value, (list, tuple)):
                # Value must be in the list
                if country_value not in value:
                    matches_all_triggers = False
                    break
            else:
                # Simple equality
                if country_value != value:
                    matches_all_triggers = False
                    break
        
        # Check special triggers if defined
        if matches_all_triggers and event_type.special_triggers:
            for trigger_name, trigger_func in event_type.special_triggers.items():
                if not trigger_func(country, game_state):
                    matches_all_triggers = False
                    break
        
        if matches_all_triggers:
            affected.append(country_code)
    
    # If no countries match but the event needs countries, pick random ones
    if not affected and event_type.effects:
        needs_countries = False
        for effect in event_type.effects:
            if effect.get('target', '') in ['country', 'relation']:
                needs_countries = True
                break
                
        if needs_countries:
            # Pick a random country or countries for the event
            country_codes = list(game_state.countries.keys())
            if country_codes:
                affected.append(random.choice(country_codes))
                
                # For relation events, we need at least two countries
                if any(effect.get('target', '') == 'relation' for effect in event_type.effects) and len(country_codes) > 1:
                    second_country = random.choice([c for c in country_codes if c != affected[0]])
                    affected.append(second_country)
    
    return affected