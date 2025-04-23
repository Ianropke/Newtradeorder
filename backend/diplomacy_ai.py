"""
Diplomacy AI Module for Trade War Simulator

This module implements AI-driven diplomatic behavior for computer-controlled countries,
providing realistic diplomatic interactions based on economic interests, geopolitical alignment,
and historical relationships.
"""

import random
import math
import time
from typing import Dict, List, Tuple, Set, Optional, TYPE_CHECKING

# This allows forward references in type hints
if TYPE_CHECKING:
    from typing import TypeVar
    Coalition = TypeVar('Coalition')

class CountryProfile:
    """
    Comprehensive personality profile for a country, including diplomatic tendencies, 
    economic preferences, and behavioral traits.
    """
    def __init__(self,
                 # Core diplomatic traits
                 economic_focus: float = 0.5,      # 0.0-1.0: How much priority on economic interests
                 aggression: float = 0.3,          # 0.0-1.0: Tendency for aggressive actions
                 isolationism: float = 0.4,        # 0.0-1.0: Tendency to avoid international agreements
                 regional_focus: float = 0.5,      # 0.0-1.0: Focus on regional vs global diplomacy
                 ideological_rigidity: float = 0.4, # 0.0-1.0: How strictly ideology influences decisions
                 
                 # Economic preferences
                 free_market_belief: float = 0.5,   # 0.0-1.0: Preference for free market vs state control
                 protectionism: float = 0.5,        # 0.0-1.0: Tendency to protect domestic industries
                 risk_aversion: float = 0.5,        # 0.0-1.0: Conservative vs risk-taking economic policies
                 debt_tolerance: float = 0.5,       # 0.0-1.0: Willingness to accept higher debt levels
                 innovation_focus: float = 0.5,     # 0.0-1.0: Focus on innovation and R&D
                 
                 # Trade preferences
                 export_orientation: float = 0.5,   # 0.0-1.0: Focus on export-led growth
                 self_sufficiency: float = 0.5,     # 0.0-1.0: Desire for self-sufficiency in key sectors
                 sector_protection: float = 0.5,    # 0.0-1.0: Tendency to protect specific sectors
                 
                 # Diplomatic behavior
                 trust_weight: float = 0.5,         # 0.0-1.0: Weight given to trust in relationships
                 retaliation: float = 0.5,          # 0.0-1.0: Tendency to retaliate against hostile actions
                 deviousness: float = 0.3,          # 0.0-1.0: Tendency to use covert or deceptive tactics
                 diplomatic_focus: float = 0.5,     # 0.0-1.0: Priority on diplomacy vs other means
                 cooperation: float = 0.5,          # 0.0-1.0: Tendency to cooperate internationally
                 
                 # Leadership style
                 pride: float = 0.5,                # 0.0-1.0: National pride/ego in negotiations
                 accountability: float = 0.5,       # 0.0-1.0: Accountability to domestic audience
                 consistency: float = 0.5,          # 0.0-1.0: Consistency in policy over time
                 pragmatism: float = 0.5,           # 0.0-1.0: Practical vs ideological approach
                 
                 # Technology approach
                 tech_focus: float = 0.5,           # 0.0-1.0: Emphasis on technological advancement
                 tech_openness: float = 0.5,        # 0.0-1.0: Openness to share/license technology
                 tech_protectionism: float = 0.4    # 0.0-1.0: Tendency to protect technological advantages
                ):
        # Core diplomatic traits
        self.economic_focus = max(0.0, min(1.0, economic_focus))
        self.aggression = max(0.0, min(1.0, aggression))
        self.isolationism = max(0.0, min(1.0, isolationism))
        self.regional_focus = max(0.0, min(1.0, regional_focus))
        self.ideological_rigidity = max(0.0, min(1.0, ideological_rigidity))
        
        # Economic preferences
        self.free_market_belief = max(0.0, min(1.0, free_market_belief))
        self.protectionism = max(0.0, min(1.0, protectionism))
        self.risk_aversion = max(0.0, min(1.0, risk_aversion))
        self.debt_tolerance = max(0.0, min(1.0, debt_tolerance))
        self.innovation_focus = max(0.0, min(1.0, innovation_focus))
        
        # Trade preferences
        self.export_orientation = max(0.0, min(1.0, export_orientation))
        self.self_sufficiency = max(0.0, min(1.0, self_sufficiency))
        self.sector_protection = max(0.0, min(1.0, sector_protection))
        
        # Diplomatic behavior
        self.trust_weight = max(0.0, min(1.0, trust_weight))
        self.retaliation = max(0.0, min(1.0, retaliation))
        self.deviousness = max(0.0, min(1.0, deviousness))
        self.diplomatic_focus = max(0.0, min(1.0, diplomatic_focus))
        self.cooperation = max(0.0, min(1.0, cooperation))
        
        # Leadership style
        self.pride = max(0.0, min(1.0, pride))
        self.accountability = max(0.0, min(1.0, accountability))
        self.consistency = max(0.0, min(1.0, consistency))
        self.pragmatism = max(0.0, min(1.0, pragmatism))
        
        # Technology approach
        self.tech_focus = max(0.0, min(1.0, tech_focus))
        self.tech_openness = max(0.0, min(1.0, tech_openness))
        self.tech_protectionism = max(0.0, min(1.0, tech_protectionism))
    
    @classmethod
    def generate_for_country(cls, country_code: str, country_data: Dict, historical_data: Dict = None) -> 'CountryProfile':
        """
        Generate a personality profile tailored to a specific country based on its attributes and historical tendencies.
        
        Args:
            country_code: ISO code of the country
            country_data: Dictionary with country attributes (government_type, gdp, etc.)
            historical_data: Optional historical data to influence personality
            
        Returns:
            A CountryProfile instance with appropriate values
        """
        # Seed random with country code for consistency
        random.seed(hash(country_code))
        
        # Extract country attributes
        government_type = country_data.get('government_type', 'unknown').lower()
        gdp = country_data.get('gdp', 500)
        gdp_per_capita = country_data.get('gdp_per_capita', 10000)
        region = country_data.get('region', 'unknown')
        is_democracy = government_type in ['democracy', 'republic', 'parliamentary']
        is_autocracy = government_type in ['autocracy', 'dictatorship', 'authoritarian']
        is_monarchy = government_type in ['monarchy', 'constitutional_monarchy']
        
        # Start with base profiles based on government type
        if is_democracy:
            profile = democratic_profile.copy()
        elif is_autocracy:
            profile = authoritarian_profile.copy()
        elif is_monarchy:
            profile = monarchy_profile.copy()
        else:
            profile = mixed_government_profile.copy()
        
        # Regional adjustments
        if region.lower() in ['europe', 'eu', 'western_europe']:
            profile['free_market_belief'] += 0.1
            profile['cooperation'] += 0.1
            profile['isolationism'] -= 0.1
        elif region.lower() in ['asia', 'east_asia']:
            profile['export_orientation'] += 0.2
            profile['tech_focus'] += 0.1
        elif region.lower() in ['north_america']:
            profile['free_market_belief'] += 0.2
            profile['protectionism'] -= 0.1
        
        # Economic development adjustments
        if gdp_per_capita > 30000:  # Advanced economy
            profile['innovation_focus'] += 0.1
            profile['tech_openness'] += 0.1
            profile['debt_tolerance'] += 0.1
        elif gdp_per_capita < 5000:  # Developing economy
            profile['self_sufficiency'] += 0.1
            profile['risk_aversion'] += 0.1
            profile['protectionism'] += 0.1
        
        # Add randomness (±15%) to each trait for individuality
        for key in profile:
            random_adjustment = random.uniform(-0.15, 0.15)
            profile[key] = max(0.0, min(1.0, profile[key] + random_adjustment))
        
        # Apply country-specific overrides from historical data if available
        if historical_data and country_code in historical_data:
            country_history = historical_data[country_code]
            for trait, value in country_history.get('personality_traits', {}).items():
                if trait in profile:
                    profile[trait] = value
        
        # Reset random seed
        random.seed()
        
        return cls(**profile)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage/serialization"""
        return {
            # Core diplomatic traits
            'economic_focus': self.economic_focus,
            'aggression': self.aggression,
            'isolationism': self.isolationism,
            'regional_focus': self.regional_focus,
            'ideological_rigidity': self.ideological_rigidity,
            
            # Economic preferences
            'free_market_belief': self.free_market_belief,
            'protectionism': self.protectionism,
            'risk_aversion': self.risk_aversion,
            'debt_tolerance': self.debt_tolerance,
            'innovation_focus': self.innovation_focus,
            
            # Trade preferences
            'export_orientation': self.export_orientation,
            'self_sufficiency': self.self_sufficiency,
            'sector_protection': self.sector_protection,
            
            # Diplomatic behavior
            'trust_weight': self.trust_weight,
            'retaliation': self.retaliation,
            'deviousness': self.deviousness,
            'diplomatic_focus': self.diplomatic_focus,
            'cooperation': self.cooperation,
            
            # Leadership style
            'pride': self.pride,
            'accountability': self.accountability,
            'consistency': self.consistency,
            'pragmatism': self.pragmatism,
            
            # Technology approach
            'tech_focus': self.tech_focus,
            'tech_openness': self.tech_openness,
            'tech_protectionism': self.tech_protectionism
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CountryProfile':
        """Create from dictionary"""
        return cls(**data)
    
    def copy(self) -> Dict:
        """Create a copy of this profile as a dictionary"""
        return self.to_dict()
    
    def adjust_for_crisis(self, crisis_type: str, severity: float) -> None:
        """
        Adjust personality traits in response to a crisis.
        
        Args:
            crisis_type: Type of crisis ('economic', 'security', etc.)
            severity: How severe the crisis is (0.0-1.0)
        """
        adjustment = min(0.2, severity * 0.3)  # Max adjustment is 0.2 (20%)
        
        if crisis_type == 'economic':
            self.risk_aversion = min(1.0, self.risk_aversion + adjustment)
            self.protectionism = min(1.0, self.protectionism + adjustment)
            self.isolationism = min(1.0, self.isolationism + (adjustment * 0.5))
            self.free_market_belief = max(0.0, self.free_market_belief - (adjustment * 0.5))
            
        elif crisis_type == 'security':
            self.isolationism = min(1.0, self.isolationism + adjustment)
            self.self_sufficiency = min(1.0, self.self_sufficiency + adjustment)
            self.trust_weight = max(0.0, self.trust_weight - adjustment)
            self.cooperation = max(0.0, self.cooperation - (adjustment * 0.5))
            
        elif crisis_type == 'diplomatic':
            self.trust_weight = max(0.0, self.trust_weight - adjustment)
            self.retaliation = min(1.0, self.retaliation + adjustment)
            self.deviousness = min(1.0, self.deviousness + (adjustment * 0.7))
            
        elif crisis_type == 'technological':
            self.tech_protectionism = min(1.0, self.tech_protectionism + adjustment)
            self.tech_openness = max(0.0, self.tech_openness - adjustment)
            self.tech_focus = min(1.0, self.tech_focus + (adjustment * 0.5))


# Base profile templates for different government types
democratic_profile = {
    # Core diplomatic traits
    'economic_focus': 0.6,
    'aggression': 0.3,
    'isolationism': 0.3,
    'regional_focus': 0.4,
    'ideological_rigidity': 0.4,
    
    # Economic preferences
    'free_market_belief': 0.7,
    'protectionism': 0.4,
    'risk_aversion': 0.5,
    'debt_tolerance': 0.5,
    'innovation_focus': 0.6,
    
    # Trade preferences
    'export_orientation': 0.6,
    'self_sufficiency': 0.4,
    'sector_protection': 0.4,
    
    # Diplomatic behavior
    'trust_weight': 0.6,
    'retaliation': 0.4,
    'deviousness': 0.3,
    'diplomatic_focus': 0.7,
    'cooperation': 0.7,
    
    # Leadership style
    'pride': 0.5,
    'accountability': 0.8,
    'consistency': 0.5,
    'pragmatism': 0.6,
    
    # Technology approach
    'tech_focus': 0.6,
    'tech_openness': 0.7,
    'tech_protectionism': 0.4
}

authoritarian_profile = {
    # Core diplomatic traits
    'economic_focus': 0.5,
    'aggression': 0.7,
    'isolationism': 0.6,
    'regional_focus': 0.6,
    'ideological_rigidity': 0.8,
    
    # Economic preferences
    'free_market_belief': 0.3,
    'protectionism': 0.7,
    'risk_aversion': 0.4,
    'debt_tolerance': 0.4,
    'innovation_focus': 0.5,
    
    # Trade preferences
    'export_orientation': 0.5,
    'self_sufficiency': 0.7,
    'sector_protection': 0.8,
    
    # Diplomatic behavior
    'trust_weight': 0.3,
    'retaliation': 0.8,
    'deviousness': 0.7,
    'diplomatic_focus': 0.4,
    'cooperation': 0.3,
    
    # Leadership style
    'pride': 0.8,
    'accountability': 0.2,
    'consistency': 0.7,
    'pragmatism': 0.4,
    
    # Technology approach
    'tech_focus': 0.5,
    'tech_openness': 0.3,
    'tech_protectionism': 0.8
}

monarchy_profile = {
    # Core diplomatic traits
    'economic_focus': 0.5,
    'aggression': 0.4,
    'isolationism': 0.5,
    'regional_focus': 0.6,
    'ideological_rigidity': 0.6,
    
    # Economic preferences
    'free_market_belief': 0.5,
    'protectionism': 0.6,
    'risk_aversion': 0.6,
    'debt_tolerance': 0.4,
    'innovation_focus': 0.4,
    
    # Trade preferences
    'export_orientation': 0.5,
    'self_sufficiency': 0.6,
    'sector_protection': 0.6,
    
    # Diplomatic behavior
    'trust_weight': 0.5,
    'retaliation': 0.5,
    'deviousness': 0.5,
    'diplomatic_focus': 0.6,
    'cooperation': 0.5,
    
    # Leadership style
    'pride': 0.7,
    'accountability': 0.4,
    'consistency': 0.6,
    'pragmatism': 0.5,
    
    # Technology approach
    'tech_focus': 0.5,
    'tech_openness': 0.5,
    'tech_protectionism': 0.6
}

mixed_government_profile = {
    # Core diplomatic traits
    'economic_focus': 0.5,
    'aggression': 0.5,
    'isolationism': 0.5,
    'regional_focus': 0.5,
    'ideological_rigidity': 0.5,
    
    # Economic preferences
    'free_market_belief': 0.5,
    'protectionism': 0.5,
    'risk_aversion': 0.5,
    'debt_tolerance': 0.5,
    'innovation_focus': 0.5,
    
    # Trade preferences
    'export_orientation': 0.5,
    'self_sufficiency': 0.5,
    'sector_protection': 0.5,
    
    # Diplomatic behavior
    'trust_weight': 0.5,
    'retaliation': 0.5,
    'deviousness': 0.5,
    'diplomatic_focus': 0.5,
    'cooperation': 0.5,
    
    # Leadership style
    'pride': 0.5,
    'accountability': 0.5,
    'consistency': 0.5,
    'pragmatism': 0.5,
    
    # Technology approach
    'tech_focus': 0.5,
    'tech_openness': 0.5,
    'tech_protectionism': 0.5
}


# Specific country personality overrides for major powers and notable economies
country_profiles = {
    # USA-type profile
    'US': {
        'economic_focus': 0.7,
        'aggression': 0.6,
        'isolationism': 0.3,
        'regional_focus': 0.2,  # More global
        'free_market_belief': 0.8,
        'innovation_focus': 0.8,
        'diplomatic_focus': 0.7,
        'pride': 0.9,
        'tech_focus': 0.9,
        'tech_protectionism': 0.7
    },
    
    # China-type profile
    'CN': {
        'economic_focus': 0.8,
        'aggression': 0.5,
        'isolationism': 0.4,
        'free_market_belief': 0.4,
        'protectionism': 0.7,
        'export_orientation': 0.9,
        'self_sufficiency': 0.7,
        'deviousness': 0.7,
        'tech_focus': 0.8,
        'tech_protectionism': 0.9
    },
    
    # Germany/EU-type profile
    'DE': {
        'economic_focus': 0.7,
        'aggression': 0.2,
        'isolationism': 0.2,
        'free_market_belief': 0.6,
        'export_orientation': 0.8,
        'cooperation': 0.8,
        'consistency': 0.8,
        'innovation_focus': 0.7,
        'tech_openness': 0.7
    },
    
    # Russia-type profile
    'RU': {
        'economic_focus': 0.5,
        'aggression': 0.8,
        'isolationism': 0.6,
        'free_market_belief': 0.4,
        'sector_protection': 0.8,
        'trust_weight': 0.2,
        'retaliation': 0.9,
        'deviousness': 0.8,
        'pride': 0.9,
        'tech_protectionism': 0.8
    },
    
    # India-type profile
    'IN': {
        'economic_focus': 0.7,
        'isolationism': 0.5,
        'protectionism': 0.6,
        'self_sufficiency': 0.7,
        'cooperation': 0.6,
        'pragmatism': 0.7,
        'tech_focus': 0.7
    },
    
    # Japan-type profile
    'JP': {
        'economic_focus': 0.8,
        'aggression': 0.2,
        'isolationism': 0.4,
        'free_market_belief': 0.6,
        'export_orientation': 0.8,
        'tech_focus': 0.9,
        'innovation_focus': 0.8,
        'consistency': 0.8
    },
    
    # UK-type profile
    'GB': {
        'economic_focus': 0.7,
        'aggression': 0.4,
        'isolationism': 0.4,
        'free_market_belief': 0.7,
        'export_orientation': 0.6,
        'diplomatic_focus': 0.7,
        'pride': 0.7,
        'tech_focus': 0.7
    },
    
    # Middle East oil producer profile
    'oil_producer': {
        'economic_focus': 0.8,
        'sector_protection': 0.9,
        'export_orientation': 0.9,
        'self_sufficiency': 0.5,
        'tech_focus': 0.6,
        'innovation_focus': 0.5
    },
    
    # Nordic social democracy profile
    'nordic': {
        'economic_focus': 0.6,
        'aggression': 0.1,
        'isolationism': 0.3,
        'free_market_belief': 0.6,
        'cooperation': 0.9,
        'accountability': 0.9,
        'innovation_focus': 0.8,
        'tech_openness': 0.8
    },
    
    # Small developing nation profile
    'developing': {
        'economic_focus': 0.8,
        'isolationism': 0.5,
        'protectionism': 0.7,
        'risk_aversion': 0.7,
        'self_sufficiency': 0.7,
        'tech_focus': 0.4,
        'innovation_focus': 0.4
    }
}


class DiplomaticPersonality:
    """
    Represents a country's diplomatic personality and behavior tendencies.
    Legacy class maintained for backward compatibility - use CountryProfile for new code.
    """
    def __init__(self, 
                 economic_focus: float,      # 0.0-1.0: How much priority on economic interests
                 aggression: float,          # 0.0-1.0: Tendency for aggressive actions
                 isolationism: float,        # 0.0-1.0: Tendency to avoid international agreements
                 regional_focus: float,      # 0.0-1.0: Focus on regional vs global diplomacy
                 ideological_rigidity: float # 0.0-1.0: How strictly ideology influences decisions
                ):
        self.economic_focus = max(0.0, min(1.0, economic_focus))
        self.aggression = max(0.0, min(1.0, aggression))
        self.isolationism = max(0.0, min(1.0, isolationism))
        self.regional_focus = max(0.0, min(1.0, regional_focus))
        self.ideological_rigidity = max(0.0, min(1.0, ideological_rigidity))
    
    @classmethod
    def generate_for_country(cls, country_code: str, government_type: str, gdp: float) -> 'DiplomaticPersonality':
        """
        Generate a suitable diplomatic personality based on country attributes.
        
        Args:
            country_code: ISO code of the country
            government_type: Type of government (democracy, autocracy, etc.)
            gdp: Gross Domestic Product (economic size)
            
        Returns:
            A DiplomaticPersonality instance with appropriate values
        """
        # Seed the random generator with country code for consistency
        random.seed(hash(country_code))
        
        # Base values with some randomness
        base_economic_focus = 0.5 + random.uniform(-0.2, 0.2)
        base_aggression = 0.3 + random.uniform(-0.2, 0.2)
        base_isolationism = 0.4 + random.uniform(-0.2, 0.2)
        base_regional_focus = 0.5 + random.uniform(-0.2, 0.2)
        base_ideological_rigidity = 0.4 + random.uniform(-0.2, 0.2)
        
        # Adjust based on government type
        if government_type.lower() in ['democracy', 'republic', 'parliamentary']:
            base_aggression -= 0.1
            base_isolationism -= 0.1
            base_ideological_rigidity -= 0.1
        elif government_type.lower() in ['autocracy', 'dictatorship', 'authoritarian']:
            base_aggression += 0.2
            base_isolationism += 0.1
            base_ideological_rigidity += 0.2
        elif government_type.lower() in ['monarchy', 'constitutional_monarchy']:
            base_regional_focus += 0.1
        
        # Adjust based on GDP (economic size)
        # Larger economies tend to be more internationally engaged
        if gdp > 1000:  # Large economy
            base_isolationism -= 0.15
            base_regional_focus -= 0.1  # More global focus
        elif gdp < 100:  # Small economy
            base_regional_focus += 0.15  # More regional focus
            base_economic_focus += 0.1  # More economic focus

        # Reset random seed
        random.seed()
        
        return cls(
            economic_focus=base_economic_focus,
            aggression=base_aggression,
            isolationism=base_isolationism,
            regional_focus=base_regional_focus,
            ideological_rigidity=base_ideological_rigidity
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage/serialization"""
        return {
            'economic_focus': self.economic_focus,
            'aggression': self.aggression,
            'isolationism': self.isolationism,
            'regional_focus': self.regional_focus,
            'ideological_rigidity': self.ideological_rigidity
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DiplomaticPersonality':
        """Create from dictionary"""
        return cls(
            economic_focus=data.get('economic_focus', 0.5),
            aggression=data.get('aggression', 0.3),
            isolationism=data.get('isolationism', 0.4),
            regional_focus=data.get('regional_focus', 0.5),
            ideological_rigidity=data.get('ideological_rigidity', 0.4)
        )
    
    def to_country_profile(self) -> CountryProfile:
        """Convert a DiplomaticPersonality to the new CountryProfile format"""
        profile_data = {
            'economic_focus': self.economic_focus,
            'aggression': self.aggression,
            'isolationism': self.isolationism,
            'regional_focus': self.regional_focus,
            'ideological_rigidity': self.ideological_rigidity,
        }
        return CountryProfile(**profile_data)


class Coalition:
    """
    Represents a coalition of countries that work together toward common goals.
    Coalitions can form around different purposes like trade, defense, or diplomatic cooperation.
    """
    def __init__(self, 
                 name: str,
                 purpose: str,
                 founding_countries: List[str],
                 formation_turn: int,
                 leader_country: str = None,
                 cohesion_level: float = 0.5):
        self.name = name
        self.purpose = purpose  # 'trade', 'defense', 'diplomatic', etc.
        self.member_countries = set(founding_countries)
        self.formation_turn = formation_turn
        self.leader_country = leader_country or (founding_countries[0] if founding_countries else None)
        self.cohesion_level = max(0.0, min(1.0, cohesion_level))  # 0.0-1.0 how united the coalition is
        self.duration = 10  # Default coalition lasts 10 turns, can be extended
        self.membership_history = {
            country: {'joined_turn': formation_turn, 'left_turn': None}
            for country in founding_countries
        }
        self.actions_history = []  # List of actions taken by the coalition
        
    def add_country(self, country_iso: str, turn: int) -> bool:
        """Add a country to the coalition"""
        if country_iso in self.member_countries:
            return False
            
        self.member_countries.add(country_iso)
        self.membership_history[country_iso] = {
            'joined_turn': turn,
            'left_turn': None
        }
        
        # New members slightly lower cohesion
        self.update_cohesion(-0.1)
        return True
        
    def remove_country(self, country_iso: str, turn: int) -> bool:
        """Remove a country from the coalition"""
        if country_iso not in self.member_countries:
            return False
            
        self.member_countries.remove(country_iso)
        if country_iso in self.membership_history:
            self.membership_history[country_iso]['left_turn'] = turn
            
        # Country leaving lowers cohesion significantly
        self.update_cohesion(-0.2)
        
        # If leader leaves, select new leader
        if country_iso == self.leader_country and self.member_countries:
            self.leader_country = next(iter(self.member_countries))
            
        return True
    
    def update_cohesion(self, change: float) -> None:
        """Update the coalition's cohesion level"""
        # Calculate new cohesion level
        new_cohesion = self.cohesion_level + change
        # Apply min/max bounds
        bounded_cohesion = max(0.0, min(1.0, new_cohesion))
        # Force exact decimal representation to avoid floating-point errors
        self.cohesion_level = float(f"{bounded_cohesion:.1f}")
    
    def extend_duration(self, additional_turns: int) -> None:
        """Extend the coalition's duration"""
        self.duration += additional_turns
    
    def is_active(self, current_turn: int) -> bool:
        """Check if the coalition is still active"""
        return len(self.member_countries) >= 2 and current_turn < self.formation_turn + self.duration
    
    def record_action(self, action_type: str, details: Dict, turn: int) -> None:
        """Record an action taken by the coalition"""
        self.actions_history.append({
            'type': action_type,
            'details': details,
            'turn': turn
        })
        
        # Actions can affect cohesion depending on success
        if details.get('success', False):
            self.update_cohesion(0.05)  # Successful actions boost cohesion
        else:
            self.update_cohesion(-0.05)  # Failed actions reduce cohesion
    
    def get_member_influence(self, country_iso: str, game_state=None) -> float:
        """
        Calculate a member country's influence within the coalition.
        
        Returns:
            Influence score from 0.0 to 1.0
        """
        if country_iso not in self.member_countries:
            return 0.0
        
        if not game_state or country_iso not in game_state.countries:
            return 0.5  # Default influence if no game state available
        
        country = game_state.countries[country_iso]
        
        # Base influence on economic power
        gdp_influence = min(1.0, country.gdp / 5000)  # Scale to 0-1
        
        # Adjust based on time in coalition (longer = more influence)
        join_turn = self.membership_history[country_iso]['joined_turn']
        tenure = game_state.current_turn - join_turn if hasattr(game_state, 'current_turn') else 0
        tenure_factor = min(1.0, tenure / 10)  # Max benefit after 10 turns
        
        # Leader gets a bonus
        leadership_bonus = 0.2 if country_iso == self.leader_country else 0.0
        
        # Calculate final influence score
        influence = (gdp_influence * 0.6) + (tenure_factor * 0.2) + leadership_bonus
        
        return max(0.1, min(1.0, influence))  # Ensure minimum influence of 0.1
    
    def get_collective_stance(self, issue_type: str, country_stances: Dict[str, float]) -> float:
        """
        Calculate the coalition's collective stance on an issue based on member country stances.
        
        Args:
            issue_type: Type of issue ('tariff', 'sanction', etc.)
            country_stances: Dictionary mapping country ISO codes to stance values (-1.0 to 1.0)
            
        Returns:
            Coalition stance from -1.0 (oppose) to 1.0 (support)
        """
        if not self.member_countries or not country_stances:
            return 0.0
        
        # Only consider member countries
        member_stances = {
            country: stance for country, stance in country_stances.items()
            if country in self.member_countries
        }
        
        if not member_stances:
            return 0.0
        
        # Calculate weighted average of stances
        total_influence = 0.0
        weighted_stance = 0.0
        
        for country, stance in member_stances.items():
            # Leader has more influence based on cohesion
            influence = 1.0
            if country == self.leader_country:
                influence += self.cohesion_level  # Up to double influence when cohesion is high
            
            weighted_stance += stance * influence
            total_influence += influence
        
        collective_stance = weighted_stance / total_influence if total_influence > 0 else 0.0
        
        # High cohesion leads to more unified stance (closer to leader's stance)
        if self.cohesion_level > 0.7 and self.leader_country in member_stances:
            leader_stance = member_stances[self.leader_country]
            cohesion_factor = (self.cohesion_level - 0.7) / 0.3  # 0.0 to 1.0
            collective_stance = collective_stance * (1 - cohesion_factor) + leader_stance * cohesion_factor
        
        return max(-1.0, min(1.0, collective_stance))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage/serialization"""
        return {
            'name': self.name,
            'purpose': self.purpose,
            'member_countries': list(self.member_countries),
            'formation_turn': self.formation_turn,
            'leader_country': self.leader_country,
            'cohesion_level': self.cohesion_level,
            'duration': self.duration,
            'membership_history': self.membership_history,
            'actions_history': self.actions_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Coalition':
        """Create from dictionary"""
        coalition = cls(
            name=data.get('name', 'Unnamed Coalition'),
            purpose=data.get('purpose', 'general'),
            founding_countries=data.get('member_countries', []),
            formation_turn=data.get('formation_turn', 0),
            leader_country=data.get('leader_country'),
            cohesion_level=data.get('cohesion_level', 0.5)
        )
        
        coalition.duration = data.get('duration', 10)
        coalition.membership_history = data.get('membership_history', {})
        coalition.actions_history = data.get('actions_history', [])
        
        return coalition


class AIExplanationSystem:
    """
    Provides detailed explanations for AI decision-making processes to increase
    transparency for the player.
    
    This system analyzes AI decisions, factors in country profiles, and generates
    human-readable explanations that detail the reasoning behind diplomatic actions,
    economic decisions, policy choices, and more.
    """
    
    def __init__(self, explanation_detail_level: float = 0.7):
        """
        Initialize the explanation system.
        
        Args:
            explanation_detail_level: Controls how detailed explanations are (0.0-1.0)
                                      Higher values provide more detailed explanations
        """
        self.explanation_detail_level = max(0.1, min(1.0, explanation_detail_level))
        self.last_decisions = {}  # Cache of recent decisions for reference
        
    def explain_coalition_decision(self, country_iso: str, decision: Dict, country_profile: CountryProfile) -> Dict:
        """
        Generate a detailed explanation for a coalition-related decision.
        
        Args:
            country_iso: The ISO code of the country making the decision
            decision: The coalition decision dictionary 
            country_profile: The country's personality profile
            
        Returns:
            Dictionary with explanation details at multiple levels of depth
        """
        action = decision.get('action', 'unknown')
        explanation = {
            'short': '',     # One-line summary
            'medium': [],    # Bullet points
            'detailed': [],  # Paragraphs with factors and weights
            'factors': []    # Key factors that influenced the decision
        }
        
        # Short explanation (one-line summary)
        if action == 'form_coalition':
            explanation['short'] = f"Forming a {decision.get('purpose', 'unknown')} coalition to strengthen {country_iso}'s position"
        elif action == 'join_coalition':
            explanation['short'] = f"Joining coalition for strategic benefits"
        elif action == 'leave_coalition':
            explanation['short'] = f"Leaving coalition due to insufficient benefits"
        elif action == 'challenge_leadership':
            explanation['short'] = f"Challenging for leadership of coalition"
        elif action == 'recruit_member':
            explanation['short'] = f"Recruiting new member to strengthen coalition"
        elif action == 'maintain_status_quo':
            explanation['short'] = f"Maintaining current coalition arrangements"
            
        # Medium explanation (key bullet points)
        if action == 'form_coalition':
            purpose = decision.get('purpose', 'unknown')
            
            # Personality-based factors
            if purpose == 'trade' and hasattr(country_profile, 'export_orientation'):
                explanation['medium'].append(f"• High export orientation ({int(country_profile.export_orientation*100)}%) drives desire for trade partners")
            
            if purpose == 'defense' and hasattr(country_profile, 'aggression'):
                explanation['medium'].append(f"• Security concerns ({int(country_profile.aggression*100)}% aggression) motivate defensive alliance")
                
            if purpose == 'diplomatic' and hasattr(country_profile, 'diplomatic_focus'):
                explanation['medium'].append(f"• Strong diplomatic focus ({int(country_profile.diplomatic_focus*100)}%) creates opportunity for influence")
                
            if hasattr(country_profile, 'isolationism'):
                iso_factor = 100 - int(country_profile.isolationism*100)
                explanation['medium'].append(f"• {iso_factor}% international engagement tendency supports coalition-building")
                
            # Add reasoning about potential partners
            if decision.get('candidates'):
                explanation['medium'].append(f"• Selected {len(decision.get('candidates'))} partners with compatible interests")
                
            explanation['medium'].append(f"• Estimated benefit: {decision.get('reason', 'strategic advantage')}")
            
        elif action == 'leave_coalition':
            explanation['medium'].append(f"• Benefits no longer justify participation")
            
            if hasattr(country_profile, 'pragmatism'):
                explanation['medium'].append(f"• Pragmatic approach ({int(country_profile.pragmatism*100)}%) favors efficient alliances")
                
            explanation['medium'].append(f"• Reason: {decision.get('reason', 'strategic repositioning')}")
            
        elif action == 'challenge_leadership':
            if hasattr(country_profile, 'pride'):
                explanation['medium'].append(f"• National pride ({int(country_profile.pride*100)}%) drives leadership ambition")
                
            explanation['medium'].append(f"• Current country position suggests leadership potential")
            explanation['medium'].append(f"• Reason: {decision.get('reason', 'seek leadership role')}")
            
        # Detailed explanation (paragraphs with reasoning)
        if action == 'form_coalition':
            purpose = decision.get('purpose', 'unknown')
            purpose_descriptions = {
                'trade': "economic cooperation and preferential trading status",
                'defense': "mutual security guarantees and coordinated military posture",
                'diplomatic': "aligned diplomatic positions and joint negotiations",
                'regional': "regional integration and neighboring state coordination"
            }
            purpose_desc = purpose_descriptions.get(purpose, purpose)
            
            # First paragraph - Overview of strategic thinking
            strategic_para = f"{country_iso} is pursuing a coalition focused on {purpose_desc}. "
            
            if hasattr(country_profile, 'economic_focus') and hasattr(country_profile, 'diplomatic_focus'):
                if country_profile.economic_focus > country_profile.diplomatic_focus:
                    strategic_para += f"The country prioritizes economic interests ({int(country_profile.economic_focus*100)}%) over purely diplomatic goals ({int(country_profile.diplomatic_focus*100)}%). "
                else:
                    strategic_para += f"The country balances diplomatic influence ({int(country_profile.diplomatic_focus*100)}%) with economic considerations ({int(country_profile.economic_focus*100)}%). "
            
            if hasattr(country_profile, 'regional_focus'):
                if country_profile.regional_focus > 0.7:
                    strategic_para += f"There is a strong focus on regional affairs ({int(country_profile.regional_focus*100)}%). "
                elif country_profile.regional_focus < 0.3:
                    strategic_para += f"The country maintains a global rather than regional outlook ({100-int(country_profile.regional_focus*100)}% global focus). "
            
            explanation['detailed'].append(strategic_para)
            
            # Second paragraph - Specific reasoning for this coalition
            reasoning_para = f"This {purpose} coalition is being formed because "
            
            if purpose == 'trade':
                reasoning_para += f"it aligns with the country's commercial interests. "
                if hasattr(country_profile, 'protectionism') and hasattr(country_profile, 'export_orientation'):
                    if country_profile.export_orientation > country_profile.protectionism:
                        reasoning_para += f"With high export orientation ({int(country_profile.export_orientation*100)}%) and moderate protectionism ({int(country_profile.protectionism*100)}%), "
                        reasoning_para += f"the country seeks to expand markets while maintaining some domestic protection. "
                    else:
                        reasoning_para += f"Despite significant protectionist tendencies ({int(country_profile.protectionism*100)}%), "
                        reasoning_para += f"the country recognizes the value of controlled trade partnerships. "
            
            elif purpose == 'defense':
                reasoning_para += f"it addresses security concerns in an uncertain international environment. "
                if hasattr(country_profile, 'aggression') and hasattr(country_profile, 'trust_weight'):
                    if country_profile.aggression > 0.6:
                        reasoning_para += f"With high aggression ({int(country_profile.aggression*100)}%), the country takes a proactive security stance. "
                    else:
                        reasoning_para += f"The country's moderate aggression ({int(country_profile.aggression*100)}%) is balanced with "
                        reasoning_para += f"strategic trust considerations ({int(country_profile.trust_weight*100)}% trust weighting). "
            
            explanation['detailed'].append(reasoning_para)
            
            # Third paragraph - Partner selection logic
            partners_para = "Coalition partners were selected based on "
            
            if purpose == 'trade':
                partners_para += "existing trade relationships and economic compatibility. "
            elif purpose == 'defense':
                partners_para += "shared security concerns and complementary military capabilities. "
            elif purpose == 'diplomatic':
                partners_para += "aligned diplomatic positions and mutual policy interests. "
            elif purpose == 'regional':
                partners_para += "geographic proximity and regional integration potential. "
            
            if hasattr(country_profile, 'trust_weight'):
                partners_para += f"Trust considerations account for {int(country_profile.trust_weight*100)}% of the selection criteria. "
            
            explanation['detailed'].append(partners_para)
            
        elif action == 'leave_coalition':
            # First paragraph - Overview of decision
            overview_para = f"{country_iso} has determined that continued membership in this coalition no longer serves its strategic interests. "
            
            if hasattr(country_profile, 'pragmatism'):
                if country_profile.pragmatism > 0.7:
                    overview_para += f"With high pragmatism ({int(country_profile.pragmatism*100)}%), the country objectively evaluates alliance benefits. "
                else:
                    overview_para += f"Despite moderate pragmatism ({int(country_profile.pragmatism*100)}%), the costs now outweigh the benefits. "
            
            explanation['detailed'].append(overview_para)
            
            # Second paragraph - Specific reasoning
            reason = decision.get('reason', 'strategic repositioning')
            reasoning_para = f"The decision to leave is based on {reason}. "
            
            if hasattr(country_profile, 'loyalty_threshold') and hasattr(country_profile, 'ideological_rigidity'):
                reasoning_para += f"The country's loyalty threshold ({int((1-country_profile.loyalty_threshold)*100)}%) and "
                reasoning_para += f"ideological flexibility ({int((1-country_profile.ideological_rigidity)*100)}%) "
                reasoning_para += f"inform its willingness to exit underperforming alliances. "
            
            explanation['detailed'].append(reasoning_para)
        
        # Key factors (for UI highlighting)
        if action == 'form_coalition':
            if hasattr(country_profile, 'economic_focus') and country_profile.economic_focus > 0.6:
                explanation['factors'].append(('economic_focus', country_profile.economic_focus))
            
            if hasattr(country_profile, 'isolationism'):
                explanation['factors'].append(('isolationism', 1.0 - country_profile.isolationism))
                
            if hasattr(country_profile, 'regional_focus') and decision.get('purpose') == 'regional':
                explanation['factors'].append(('regional_focus', country_profile.regional_focus))
                
            if hasattr(country_profile, 'aggression') and decision.get('purpose') == 'defense':
                explanation['factors'].append(('aggression', country_profile.aggression))
                
            if hasattr(country_profile, 'export_orientation') and decision.get('purpose') == 'trade':
                explanation['factors'].append(('export_orientation', country_profile.export_orientation))
                
            if hasattr(country_profile, 'diplomatic_focus') and decision.get('purpose') == 'diplomatic':
                explanation['factors'].append(('diplomatic_focus', country_profile.diplomatic_focus))
        
        elif action == 'leave_coalition':
            if hasattr(country_profile, 'pragmatism'):
                explanation['factors'].append(('pragmatism', country_profile.pragmatism))
                
            if hasattr(country_profile, 'loyalty_threshold'):
                explanation['factors'].append(('loyalty', 1.0 - country_profile.loyalty_threshold))
        
        elif action == 'challenge_leadership':
            if hasattr(country_profile, 'pride'):
                explanation['factors'].append(('pride', country_profile.pride))
                
            if hasattr(country_profile, 'leadership_ambition'):
                explanation['factors'].append(('leadership', country_profile.leadership_ambition))
        
        # Save for reference in future explanations
        self.last_decisions[country_iso] = {
            'type': 'coalition',
            'action': action,
            'details': decision
        }
        
        return explanation
    
    def explain_trade_decision(self, country_iso: str, decision: Dict, country_profile: CountryProfile) -> Dict:
        """
        Generate a detailed explanation for a trade policy decision.
        
        Args:
            country_iso: The ISO code of the country making the decision
            decision: The trade decision dictionary
            country_profile: The country's personality profile
            
        Returns:
            Dictionary with explanation details at multiple levels of depth
        """
        action = decision.get('action', 'unknown')
        target_country = decision.get('target_country', None)
        explanation = {
            'short': '',     # One-line summary
            'medium': [],    # Bullet points
            'detailed': [],  # Paragraphs with factors and weights
            'factors': []    # Key factors that influenced the decision
        }
        
        # Short explanation
        if action == 'raise_tariffs':
            explanation['short'] = f"Raising tariffs to protect domestic industries"
        elif action == 'lower_tariffs':
            explanation['short'] = f"Lowering tariffs to boost trade"
        elif action == 'trade_agreement':
            explanation['short'] = f"Pursuing trade agreement for mutual economic benefit"
        elif action == 'trade_sanction':
            explanation['short'] = f"Imposing trade sanctions due to diplomatic tensions"
        
        # Medium explanation (bullet points)
        if action == 'raise_tariffs':
            if hasattr(country_profile, 'protectionism'):
                explanation['medium'].append(f"• Protectionist tendency ({int(country_profile.protectionism*100)}%) favors domestic industry protection")
                
            if hasattr(country_profile, 'self_sufficiency'):
                explanation['medium'].append(f"• Self-sufficiency priority ({int(country_profile.self_sufficiency*100)}%) supports reducing imports")
                
            if decision.get('sector'):
                explanation['medium'].append(f"• Targeted protection for {decision.get('sector')} sector")
                
            if target_country:
                explanation['medium'].append(f"• Applied specifically to imports from {target_country}")
                
        elif action == 'lower_tariffs':
            if hasattr(country_profile, 'free_market_belief'):
                explanation['medium'].append(f"• Free market orientation ({int(country_profile.free_market_belief*100)}%) supports open trade")
                
            if hasattr(country_profile, 'export_orientation'):
                explanation['medium'].append(f"• Export focus ({int(country_profile.export_orientation*100)}%) drives reciprocal market access")
                
            if decision.get('expected_benefit'):
                explanation['medium'].append(f"• Expected economic benefit: {decision.get('expected_benefit')}")
                
        elif action == 'trade_agreement':
            if target_country:
                explanation['medium'].append(f"• Partnership with {target_country} offers strategic advantages")
                
            if hasattr(country_profile, 'economic_focus'):
                explanation['medium'].append(f"• Economic prioritization ({int(country_profile.economic_focus*100)}%) drives cooperative arrangements")
                
            if decision.get('agreement_type'):
                explanation['medium'].append(f"• {decision.get('agreement_type')} agreement matches strategic goals")
                
        # Detailed explanations (paragraphs)
        if action == 'raise_tariffs':
            # First paragraph - Overview
            overview = f"{country_iso} is implementing higher tariffs based on its economic strategy. "
            
            if hasattr(country_profile, 'protectionism') and hasattr(country_profile, 'free_market_belief'):
                overview += f"With protectionist tendency of {int(country_profile.protectionism*100)}% and "
                overview += f"free market orientation of {int(country_profile.free_market_belief*100)}%, "
                
                if country_profile.protectionism > country_profile.free_market_belief:
                    overview += f"the country leans toward protecting domestic industries over free trade. "
                else:
                    overview += f"this represents a targeted exception to its generally market-oriented approach. "
            
            explanation['detailed'].append(overview)
            
            # Second paragraph - Specific reasoning
            reasoning = f"The decision to raise tariffs is "
            
            if decision.get('defensive') and hasattr(country_profile, 'retaliation'):
                reasoning += f"a defensive measure with retaliatory component ({int(country_profile.retaliation*100)}% tendency to retaliate). "
            else:
                reasoning += f"a proactive policy choice aligned with domestic economic priorities. "
                
            if decision.get('sector'):
                reasoning += f"By focusing on the {decision.get('sector')} sector, "
                reasoning += f"the country aims to address specific vulnerabilities or strategic industries. "
            
            explanation['detailed'].append(reasoning)
        
        # Key factors
        if action == 'raise_tariffs':
            if hasattr(country_profile, 'protectionism'):
                explanation['factors'].append(('protectionism', country_profile.protectionism))
                
            if hasattr(country_profile, 'self_sufficiency'):
                explanation['factors'].append(('self_sufficiency', country_profile.self_sufficiency))
                
            if hasattr(country_profile, 'retaliation') and decision.get('defensive'):
                explanation['factors'].append(('retaliation', country_profile.retaliation))
                
        elif action == 'lower_tariffs':
            if hasattr(country_profile, 'free_market_belief'):
                explanation['factors'].append(('free_market_belief', country_profile.free_market_belief))
                
            if hasattr(country_profile, 'export_orientation'):
                explanation['factors'].append(('export_orientation', country_profile.export_orientation))
        
        # Save for reference
        self.last_decisions[country_iso] = {
            'type': 'trade',
            'action': action,
            'details': decision
        }
        
        return explanation
    
    def explain_budget_decision(self, country_iso: str, decision: Dict, country_profile: CountryProfile, budget_policy: BudgetPolicy) -> Dict:
        """
        Generate a detailed explanation for a budget/economic policy decision.
        
        Args:
            country_iso: The ISO code of the country making the decision
            decision: The budget decision dictionary
            country_profile: The country's personality profile
            budget_policy: The country's budget policy
            
        Returns:
            Dictionary with explanation details at multiple levels of depth
        """
        action = decision.get('action', 'unknown')
        explanation = {
            'short': '',     # One-line summary
            'medium': [],    # Bullet points
            'detailed': [],  # Paragraphs with factors and weights
            'factors': []    # Key factors that influenced the decision
        }
        
        # Short explanation
        if action == 'austerity':
            explanation['short'] = f"Implementing austerity measures to reduce debt"
        elif action == 'stimulus':
            explanation['short'] = f"Deploying economic stimulus to boost growth"
        elif action == 'deficit_reduction':
            explanation['short'] = f"Reducing deficit while maintaining key services"
        elif action == 'balanced':
            explanation['short'] = f"Maintaining balanced budget approach"
        elif action == 'reallocate':
            explanation['short'] = f"Reallocating budget priorities to match economic needs"
        
        # Medium explanation (bullet points)
        if action == 'austerity':
            explanation['medium'].append(f"• Debt-to-GDP ratio exceeding target ({budget_policy.target_debt_gdp_ratio*100:.1f}%)")
            
            if decision.get('debt_gdp_ratio'):
                explanation['medium'].append(f"• Current debt level: {decision.get('debt_gdp_ratio')*100:.1f}% of GDP")
                
            if hasattr(country_profile, 'risk_aversion'):
                explanation['medium'].append(f"• Risk aversion ({int(country_profile.risk_aversion*100)}%) driving fiscal caution")
                
            if decision.get('spending_reduction'):
                explanation['medium'].append(f"• Target spending reduction: {decision.get('spending_reduction')*100:.1f}%")
                
        elif action == 'stimulus':
            if decision.get('gdp_growth'):
                explanation['medium'].append(f"• GDP growth below threshold: {decision.get('gdp_growth')*100:.1f}%")
                
            if hasattr(country_profile, 'economic_focus'):
                explanation['medium'].append(f"• Economic growth priority ({int(country_profile.economic_focus*100)}%) driving intervention")
                
            if hasattr(budget_policy, 'stimulus_threshold'):
                explanation['medium'].append(f"• Growth below stimulus threshold: {budget_policy.stimulus_threshold*100:.1f}%")
                
            if decision.get('spending_increase'):
                explanation['medium'].append(f"• Targeted stimulus size: {decision.get('spending_increase')*100:.1f}% of GDP")
        
        # Detailed explanation (paragraphs)
        if action == 'austerity':
            # First paragraph - Overview
            overview = f"{country_iso} is implementing austerity measures based on fiscal priorities. "
            
            if hasattr(country_profile, 'risk_aversion') and hasattr(country_profile, 'debt_tolerance'):
                overview += f"With risk aversion of {int(country_profile.risk_aversion*100)}% and "
                overview += f"debt tolerance of {int(country_profile.debt_tolerance*100)}%, "
                
                if country_profile.risk_aversion > country_profile.debt_tolerance:
                    overview += f"the country takes a cautious approach to fiscal management. "
                else:
                    overview += f"this represents an exception to its typically higher debt tolerance. "
            
            explanation['detailed'].append(overview)
            
            # Second paragraph - Specific reasoning
            reasoning = f"The austerity program targets "
            
            if decision.get('sectoral_cuts'):
                sectors = decision.get('sectoral_cuts', {})
                top_cuts = sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:2]
                reasoning += f"spending reductions primarily in "
                reasoning += ", ".join([f"{sector} ({cut*100:.1f}%)" for sector, cut in top_cuts])
                reasoning += ". "
            else:
                reasoning += f"balanced spending reductions across sectors. "
                
            if hasattr(budget_policy, 'fiscal_stability_weight'):
                reasoning += f"The country places {int(budget_policy.fiscal_stability_weight*100)}% weight on fiscal stability "
                reasoning += f"versus economic growth, informing its fiscal consolidation approach."
            
            explanation['detailed'].append(reasoning)
        
        # Key factors
        if action == 'austerity':
            if hasattr(country_profile, 'risk_aversion'):
                explanation['factors'].append(('risk_aversion', country_profile.risk_aversion))
                
            if hasattr(country_profile, 'debt_tolerance'):
                explanation['factors'].append(('debt_tolerance', 1.0 - country_profile.debt_tolerance))
                
        elif action == 'stimulus':
            if hasattr(country_profile, 'economic_focus'):
                explanation['factors'].append(('economic_focus', country_profile.economic_focus))
                
            if hasattr(country_profile, 'risk_aversion'):
                explanation['factors'].append(('risk_aversion', 1.0 - country_profile.risk_aversion))
        
        # Save for reference
        self.last_decisions[country_iso] = {
            'type': 'budget',
            'action': action,
            'details': decision
        }
        
        return explanation
    
    def explain_diplomatic_decision(self, country_iso: str, decision: Dict, country_profile: CountryProfile) -> Dict:
        """
        Generate a detailed explanation for a diplomatic decision.
        
        Args:
            country_iso: The ISO code of the country making the decision
            decision: The diplomatic decision dictionary
            country_profile: The country's personality profile
            
        Returns:
            Dictionary with explanation details at multiple levels of depth
        """
        action = decision.get('action', 'unknown')
        target_country = decision.get('target_country', None)
        explanation = {
            'short': '',     # One-line summary
            'medium': [],    # Bullet points
            'detailed': [],  # Paragraphs with factors and weights
            'factors': []    # Key factors that influenced the decision
        }
        
        # Short explanation
        if action == 'improve_relations':
            explanation['short'] = f"Pursuing improved diplomatic relations"
        elif action == 'downgrade_relations':
            explanation['short'] = f"Downgrading diplomatic relations due to tensions"
        elif action == 'sanction':
            explanation['short'] = f"Imposing diplomatic sanctions to pressure changes"
        elif action == 'alliance':
            explanation['short'] = f"Seeking formal alliance for strategic benefit"
        
        # Medium explanation (bullet points)
        if action == 'improve_relations':
            if hasattr(country_profile, 'diplomatic_focus'):
                explanation['medium'].append(f"• Diplomatic focus ({int(country_profile.diplomatic_focus*100)}%) values positive relations")
                
            if hasattr(country_profile, 'cooperation'):
                explanation['medium'].append(f"• Cooperation tendency ({int(country_profile.cooperation*100)}%) supports engagement")
                
            if target_country:
                explanation['medium'].append(f"• Strategic interest in improved relations with {target_country}")
                
            if decision.get('economic_benefit'):
                explanation['medium'].append(f"• Expected economic benefit from improved relations")
                
        elif action == 'downgrade_relations':
            if hasattr(country_profile, 'retaliation'):
                explanation['medium'].append(f"• Retaliation tendency ({int(country_profile.retaliation*100)}%) responds to negative actions")
                
            if hasattr(country_profile, 'pride'):
                explanation['medium'].append(f"• National pride ({int(country_profile.pride*100)}%) influences diplomatic positioning")
                
            if target_country:
                explanation['medium'].append(f"• Response to problematic behavior from {target_country}")
        
        # Detailed explanation (paragraphs)
        if action == 'improve_relations':
            # First paragraph - Overview
            overview = f"{country_iso} is pursuing improved diplomatic relations based on strategic calculations. "
            
            if hasattr(country_profile, 'diplomatic_focus') and hasattr(country_profile, 'cooperation'):
                overview += f"With diplomatic focus of {int(country_profile.diplomatic_focus*100)}% and "
                overview += f"cooperation tendency of {int(country_profile.cooperation*100)}%, "
                overview += f"the country values constructive international engagement. "
            
            explanation['detailed'].append(overview)
            
            # Second paragraph - Target-specific reasoning
            if target_country:
                reasoning = f"The decision to improve relations with {target_country} is based on "
                
                if decision.get('relation_type') == 'economic':
                    reasoning += f"economic complementarity and trade potential. "
                elif decision.get('relation_type') == 'security':
                    reasoning += f"shared security concerns and strategic alignment. "
                elif decision.get('relation_type') == 'regional':
                    reasoning += f"regional stability and neighborhood policy. "
                else:
                    reasoning += f"broader strategic calculations. "
                    
                if hasattr(country_profile, 'pragmatism'):
                    reasoning += f"The country's pragmatism level ({int(country_profile.pragmatism*100)}%) "
                    reasoning += f"guides its practical approach to relationship management."
                
                explanation['detailed'].append(reasoning)
        
        # Key factors
        if action == 'improve_relations':
            if hasattr(country_profile, 'diplomatic_focus'):
                explanation['factors'].append(('diplomatic_focus', country_profile.diplomatic_focus))
                
            if hasattr(country_profile, 'cooperation'):
                explanation['factors'].append(('cooperation', country_profile.cooperation))
                
            if hasattr(country_profile, 'pragmatism'):
                explanation['factors'].append(('pragmatism', country_profile.pragmatism))
                
        elif action == 'downgrade_relations':
            if hasattr(country_profile, 'retaliation'):
                explanation['factors'].append(('retaliation', country_profile.retaliation))
                
            if hasattr(country_profile, 'pride'):
                explanation['factors'].append(('pride', country_profile.pride))
        
        # Save for reference
        self.last_decisions[country_iso] = {
            'type': 'diplomatic',
            'action': action,
            'details': decision
        }
        
        return explanation
    
    def format_trait_for_display(self, trait_name: str) -> str:
        """Convert trait_name to a readable display format"""
        return ' '.join(word.capitalize() for word in trait_name.split('_'))
    
    def translate_factor_value(self, factor_name: str, value: float) -> str:
        """Translate a factor value to a human-readable description"""
        if value >= 0.8:
            return "Very High"
        elif value >= 0.6:
            return "High"
        elif value >= 0.4:
            return "Moderate"
        elif value >= 0.2:
            return "Low"
        else:
            return "Very Low"