"""
Diplomacy AI Module for Trade War Simulator

This module implements AI-driven diplomatic behavior for computer-controlled countries,
providing realistic diplomatic interactions based on economic interests, geopolitical alignment,
and historical relationships.
"""

import random
import math
import time
from typing import Dict, List, Tuple, Set, Optional, TYPE_CHECKING, Any

# This allows forward references in type hints
if TYPE_CHECKING:
    from typing import TypeVar
    Coalition = TypeVar('Coalition')

class CountryProfile:
    """
    Represents the personality and behavioral traits of a country in the simulation.
    These traits influence AI decision-making, diplomatic behavior, and responses to events.
    """
    
    def __init__(self, 
                 # Economic traits
                 protectionism: float = 0.5,
                 free_market_belief: float = 0.5,
                 export_orientation: float = 0.5,
                 self_sufficiency: float = 0.5,
                 sector_protection: float = 0.5,
                 innovation_focus: float = 0.5,
                 economic_focus: float = 0.5,
                 debt_tolerance: float = 0.5,
                 
                 # Diplomatic traits
                 cooperation: float = 0.5,
                 isolationism: float = 0.5,
                 retaliation: float = 0.5,
                 aggression: float = 0.5,
                 regional_focus: float = 0.5,
                 pride: float = 0.5,
                 pragmatism: float = 0.5,
                 
                 # Leadership traits
                 risk_aversion: float = 0.5,
                 accountability: float = 0.5,
                 
                 # New parameters
                 sanctions_resilience: float = 0.5,
                 technology_policy: float = 0.5,
                 environmental_policy: float = 0.5,
                 geopolitical_alignment: float = 0.5,
                 state_enterprise_dominance: float = 0.5,
                 corruption_index: float = 0.5,
                 labor_market_flexibility: float = 0.5,
                 regional_leadership_role: float = 0.5,
                 resource_nationalism: float = 0.5):
        """
        Initialize a country profile with behavioral traits.
        All traits are on a 0.0-1.0 scale where 0.5 is neutral.
        
        Args:
            protectionism: Tendency to protect domestic industries (0=open markets, 1=highly protectionist)
            free_market_belief: Commitment to free market principles (0=state control, 1=laissez-faire)
            export_orientation: Focus on exports vs. domestic consumption (0=domestic focus, 1=export focus)
            self_sufficiency: Emphasis on self-sufficiency vs. interdependence (0=interdependent, 1=autarkic)
            sector_protection: Willingness to protect vulnerable sectors (0=let markets decide, 1=protect key sectors)
            innovation_focus: Emphasis on innovation and R&D (0=traditional, 1=innovation-focused)
            economic_focus: Primacy of economic interests in foreign policy (0=non-economic priorities, 1=economy first)
            debt_tolerance: Tolerance for government debt (0=fiscally conservative, 1=comfortable with high debt)
            
            cooperation: Tendency to cooperate internationally (0=uncooperative, 1=highly cooperative)
            isolationism: Preference for isolation vs. engagement (0=internationalist, 1=isolationist)
            retaliation: Likelihood to retaliate against perceived threats (0=passive, 1=retaliatory)
            aggression: Tendency toward aggressive postures (0=peaceful, 1=aggressive)
            regional_focus: Focus on regional vs. global affairs (0=global focus, 1=regional focus)
            pride: Level of national pride and prestige-seeking (0=pragmatic, 1=prestige-focused)
            pragmatism: Flexibility in foreign policy (0=ideological, 1=pragmatic)
            
            risk_aversion: Aversion to risk in policy choices (0=risk-taking, 1=risk-averse)
            accountability: Democratic accountability vs. authoritarianism (0=authoritarian, 1=democratic)
            
            sanctions_resilience: Ability to withstand economic sanctions (0=vulnerable, 1=highly resilient)
            technology_policy: Approach to technology development (0=import-dependent, 1=tech sovereignty)
            environmental_policy: Emphasis on environmental protection (0=minimal, 1=strong climate policies)
            geopolitical_alignment: Political alignment (0=Western-aligned, 0.5=non-aligned, 1=anti-Western)
            state_enterprise_dominance: Role of state-owned enterprises (0=private sector, 1=state dominance)
            corruption_index: Level of corruption (0=low corruption, 1=high corruption)
            labor_market_flexibility: Adaptability of labor markets (0=rigid, 1=highly flexible)
            regional_leadership_role: Aspiration for regional leadership (0=minimal, 1=strong aspirations)
            resource_nationalism: Control over natural resources (0=open to foreign investment, 1=strict state control)
        """
        # Ensure all traits are in valid range
        def validate_trait(value):
            return max(0.0, min(1.0, value))
        
        # Economic traits
        self.protectionism = validate_trait(protectionism)
        self.free_market_belief = validate_trait(free_market_belief)
        self.export_orientation = validate_trait(export_orientation)
        self.self_sufficiency = validate_trait(self_sufficiency)
        self.sector_protection = validate_trait(sector_protection)
        self.innovation_focus = validate_trait(innovation_focus)
        self.economic_focus = validate_trait(economic_focus)
        self.debt_tolerance = validate_trait(debt_tolerance)
        
        # Diplomatic traits
        self.cooperation = validate_trait(cooperation)
        self.isolationism = validate_trait(isolationism)
        self.retaliation = validate_trait(retaliation)
        self.aggression = validate_trait(aggression)
        self.regional_focus = validate_trait(regional_focus)
        self.pride = validate_trait(pride)
        self.pragmatism = validate_trait(pragmatism)
        
        # Leadership traits
        self.risk_aversion = validate_trait(risk_aversion)
        self.accountability = validate_trait(accountability)
        
        # New traits
        self.sanctions_resilience = validate_trait(sanctions_resilience)
        self.technology_policy = validate_trait(technology_policy)
        self.environmental_policy = validate_trait(environmental_policy)
        self.geopolitical_alignment = validate_trait(geopolitical_alignment)
        self.state_enterprise_dominance = validate_trait(state_enterprise_dominance)
        self.corruption_index = validate_trait(corruption_index)
        self.labor_market_flexibility = validate_trait(labor_market_flexibility)
        self.regional_leadership_role = validate_trait(regional_leadership_role)
        self.resource_nationalism = validate_trait(resource_nationalism)
    
    @classmethod
    def generate_random(cls):
        """Generate a random country profile for testing."""
        return cls(**{trait: random.uniform(0.1, 0.9) for trait in [
            'protectionism', 'free_market_belief', 'export_orientation', 'self_sufficiency',
            'sector_protection', 'innovation_focus', 'economic_focus', 'debt_tolerance',
            'cooperation', 'isolationism', 'retaliation', 'aggression', 'regional_focus',
            'pride', 'pragmatism', 'risk_aversion', 'accountability',
            'sanctions_resilience', 'technology_policy', 'environmental_policy',
            'geopolitical_alignment', 'state_enterprise_dominance', 'corruption_index',
            'labor_market_flexibility', 'regional_leadership_role', 'resource_nationalism'
        ]})
    
    def get_trade_strategy(self) -> Dict[str, float]:
        """
        Get the country's overall trade strategy preferences based on its traits.
        
        Returns:
            Dictionary mapping strategy types to preference values (0.0-1.0)
        """
        strategies = {
            "protectionism": (self.protectionism * 0.5 + self.self_sufficiency * 0.3 + 
                             (1 - self.free_market_belief) * 0.2),
            
            "free_trade": (self.free_market_belief * 0.4 + (1 - self.protectionism) * 0.3 + 
                          (1 - self.isolationism) * 0.2 + self.cooperation * 0.1),
            
            "strategic_trade": (self.sector_protection * 0.3 + self.pragmatism * 0.3 + 
                               self.economic_focus * 0.2 + self.innovation_focus * 0.2),
            
            "resource_focus": (self.resource_nationalism * 0.5 + 
                              self.state_enterprise_dominance * 0.3 + 
                              self.self_sufficiency * 0.2),
            
            "technology_control": (self.technology_policy * 0.4 + 
                                  self.innovation_focus * 0.3 + 
                                  self.state_enterprise_dominance * 0.3),
            
            "regional_integration": (self.regional_focus * 0.4 + 
                                    self.regional_leadership_role * 0.3 + 
                                    self.cooperation * 0.3)
        }
        
        # Normalize to ensure all values are between 0 and 1
        for strategy in strategies:
            strategies[strategy] = max(0.0, min(1.0, strategies[strategy]))
            
        return strategies
    
    def get_sanctions_approach(self) -> Dict[str, float]:
        """
        Calculate the country's approach to imposing and responding to sanctions.
        
        Returns:
            Dictionary mapping sanction approaches to preference values (0.0-1.0)
        """
        approaches = {
            "impose_sanctions": (self.aggression * 0.3 + 
                                self.retaliation * 0.3 + 
                                self.economic_focus * 0.2 + 
                                self.pride * 0.2),
            
            "withstand_sanctions": (self.sanctions_resilience * 0.4 + 
                                   self.self_sufficiency * 0.3 + 
                                   self.pride * 0.2 + 
                                   (1 - self.cooperation) * 0.1),
            
            "diplomatic_resolution": (self.cooperation * 0.4 + 
                                     self.pragmatism * 0.3 + 
                                     (1 - self.aggression) * 0.3),
            
            "counter_sanctions": (self.retaliation * 0.5 + 
                                 self.aggression * 0.3 + 
                                 self.pride * 0.2)
        }
        
        # Normalize to ensure all values are between 0 and 1
        for approach in approaches:
            approaches[approach] = max(0.0, min(1.0, approaches[approach]))
            
        return approaches
    
    def alliance_compatibility(self, other_profile) -> float:
        """
        Calculate compatibility score with another country for potential alliance.
        
        Args:
            other_profile: CountryProfile of another country
            
        Returns:
            Compatibility score (0.0-1.0) where higher means more compatible
        """
        # Economic compatibility
        economic_compatibility = 1.0 - (
            abs(self.free_market_belief - other_profile.free_market_belief) * 0.3 +
            abs(self.protectionism - other_profile.protectionism) * 0.3 +
            abs(self.economic_focus - other_profile.economic_focus) * 0.2 +
            abs(self.innovation_focus - other_profile.innovation_focus) * 0.2
        ) / 1.0
        
        # Diplomatic compatibility
        diplomatic_compatibility = 1.0 - (
            abs(self.cooperation - other_profile.cooperation) * 0.3 +
            abs(self.isolationism - other_profile.isolationism) * 0.2 +
            abs(self.pragmatism - other_profile.pragmatism) * 0.3 +
            abs(self.regional_focus - other_profile.regional_focus) * 0.2
        ) / 1.0
        
        # Geopolitical compatibility
        geopolitical_compatibility = 1.0 - (
            abs(self.geopolitical_alignment - other_profile.geopolitical_alignment) * 0.6 +
            abs(self.regional_leadership_role - other_profile.regional_leadership_role) * 0.4
        ) / 1.0
        
        # Calculate overall compatibility with weighted components
        overall_compatibility = (
            economic_compatibility * 0.3 +
            diplomatic_compatibility * 0.4 +
            geopolitical_compatibility * 0.3
        )
        
        return max(0.0, min(1.0, overall_compatibility))
    
    def calculate_technology_stance(self, other_country):
        """
        Calculate the compatibility of technology policies between two countries.
        
        Args:
            other_country: Another CountryProfile instance to compare with
            
        Returns:
            float: Score between 0-1 indicating technology policy compatibility
        """
        # Check if both countries have numeric technology_policy values
        if (hasattr(self, 'technology_policy') and hasattr(other_country, 'technology_policy') and
            isinstance(self.technology_policy, (int, float)) and isinstance(other_country.technology_policy, (int, float))):
            # Similar technology policies increase compatibility
            compatibility = 1 - abs(self.technology_policy - other_country.technology_policy)
        else:
            # Default to moderate compatibility when values are missing
            compatibility = 0.5
            
        # Adjust based on government type - similar government types increase compatibility
        if hasattr(self, 'government_type') and hasattr(other_country, 'government_type'):
            if self.government_type == other_country.government_type:
                compatibility += 0.1
                
        # Adjust based on research investment - similar levels increase compatibility
        if hasattr(self, 'research_percent_gdp') and hasattr(other_country, 'research_percent_gdp'):
            research_diff = abs(self.research_percent_gdp - other_country.research_percent_gdp)
            if research_diff < 0.5:
                compatibility += 0.1
                
        return min(max(compatibility, 0), 1)  # Ensure result is between 0 and 1
    
    def regional_influence_factor(self):
        """
        Calculate a country's regional influence factor based on its profile attributes.
        
        Returns:
            float: Score between 0-1 indicating regional influence
        """
        influence = 0.5  # Default value
        
        # If we have specific regional leadership attribute, prioritize it
        if hasattr(self, 'regional_leadership_role') and isinstance(self.regional_leadership_role, (int, float)):
            influence = self.regional_leadership_role
        else:
            # Calculate from other factors
            if hasattr(self, 'exports_percent_gdp'):
                # Higher exports relative to GDP indicate greater economic influence
                influence += min(self.exports_percent_gdp / 100, 0.3)
                
            if hasattr(self, 'key_trade_partners') and isinstance(self.key_trade_partners, list):
                # More trade partners indicate wider influence
                influence += min(len(self.key_trade_partners) / 10, 0.2)
                
            # Government stability adds to influence
            if hasattr(self, 'leadership_traits'):
                if hasattr(self.leadership_traits, 'stability'):
                    influence += self.leadership_traits.stability * 0.2
                    
        return min(max(influence, 0), 1)  # Ensure result is between 0 and 1
    
    def resource_vulnerability_assessment(self):
        """
        Assess a country's vulnerability to resource-related trade disruptions.
        
        Returns:
            float: Score between 0-1 indicating vulnerability (higher = more vulnerable)
        """
        vulnerability = 0.5  # Default value
        
        # Resource dependency directly impacts vulnerability
        if hasattr(self, 'resource_dependency'):
            if isinstance(self.resource_dependency, (int, float)):
                vulnerability = self.resource_dependency
            elif isinstance(self.resource_dependency, str):
                # Text-based assessment - look for key terms
                dependency_text = self.resource_dependency.lower()
                if "heavily" in dependency_text or "significant" in dependency_text:
                    vulnerability += 0.2
                if "diversif" in dependency_text:  # Catches diversify, diversification
                    vulnerability -= 0.1
                    
        # Resource nationalism increases vulnerability for importers, decreases for exporters
        if hasattr(self, 'resource_nationalism') and isinstance(self.resource_nationalism, (int, float)):
            if hasattr(self, 'exports_percent_gdp') and hasattr(self, 'imports_percent_gdp'):
                if self.exports_percent_gdp > self.imports_percent_gdp:
                    # Net exporter - resource nationalism reduces vulnerability
                    vulnerability -= self.resource_nationalism * 0.2
                else:
                    # Net importer - resource nationalism increases vulnerability
                    vulnerability += self.resource_nationalism * 0.2
        
        # Sanctions resilience decreases vulnerability
        if hasattr(self, 'sanctions_resilience') and isinstance(self.sanctions_resilience, (int, float)):
            vulnerability -= self.sanctions_resilience * 0.2
            
        return min(max(vulnerability, 0), 1)  # Ensure result is between 0 and 1
    
    def environmental_policy_compatibility(self, other_country):
        """
        Calculate the compatibility of environmental policies between two countries.
        
        Args:
            other_country: Another CountryProfile instance to compare with
            
        Returns:
            float: Score between 0-1 indicating environmental policy compatibility
        """
        # Default moderate compatibility
        compatibility = 0.5
        
        # If both countries have numerical environmental policy values
        if (hasattr(self, 'environmental_policy') and hasattr(other_country, 'environmental_policy') and
            isinstance(self.environmental_policy, (int, float)) and 
            isinstance(other_country.environmental_policy, (int, float))):
            
            # Similar environmental policies increase compatibility
            compatibility = 1 - abs(self.environmental_policy - other_country.environmental_policy)
        else:
            # Text-based assessment if available
            if (hasattr(self, 'environmental_policy') and hasattr(other_country, 'environmental_policy') and
                isinstance(self.environmental_policy, str) and isinstance(other_country.environmental_policy, str)):
                
                # Look for similar terms in both descriptions
                self_env = self.environmental_policy.lower()
                other_env = other_country.environmental_policy.lower()
                
                # Check for common environmental policy terms
                common_terms = ["renewable", "sustainable", "climate", "green", "carbon"]
                matches = 0
                for term in common_terms:
                    if (term in self_env) == (term in other_env):
                        matches += 1
                
                compatibility = 0.3 + (0.7 * (matches / len(common_terms)))
        
        return min(max(compatibility, 0), 1)  # Ensure result is between 0 and 1
    
    def calculate_overall_cooperation_potential(self, other_country):
        """
        Calculate the overall potential for cooperation between two countries
        based on all available factors in their profiles.
        
        Args:
            other_country: Another CountryProfile instance to compare with
            
        Returns:
            float: Score between 0-1 indicating cooperation potential
            dict: Breakdown of factors contributing to the score
        """
        # Start with basic diplomatic compatibility
        if hasattr(self, 'calculate_alliance_compatibility'):
            diplomatic_score = self.calculate_alliance_compatibility(other_country)
        else:
            diplomatic_score = 0.5  # Default if method not available
            
        # Calculate trade compatibility
        if hasattr(self, 'calculate_trade_strategy_compatibility'):
            trade_score = self.calculate_trade_strategy_compatibility(other_country)
        else:
            trade_score = 0.5  # Default if method not available
            
        # Calculate technology stance compatibility
        tech_score = self.calculate_technology_stance(other_country)
        
        # Calculate environmental policy compatibility
        env_score = self.environmental_policy_compatibility(other_country)
        
        # Look at geopolitical alignment if available
        geo_score = 0.5  # Default
        if (hasattr(self, 'geopolitical_alignment') and hasattr(other_country, 'geopolitical_alignment') and
            isinstance(self.geopolitical_alignment, (int, float)) and 
            isinstance(other_country.geopolitical_alignment, (int, float))):
            
            geo_score = 1 - abs(self.geopolitical_alignment - other_country.geopolitical_alignment)
        
        # Check for existing diplomatic incidents
        incident_modifier = 0
        if hasattr(self, 'diplomatic_incidents') and isinstance(self.diplomatic_incidents, list):
            # Look for incidents involving the other country
            for incident in self.diplomatic_incidents:
                if isinstance(incident, dict) and 'type' in incident:
                    if incident.get('description', '').find(other_country.name) >= 0:
                        if incident['type'] == 'cooperative':
                            incident_modifier += 0.1
                        elif incident['type'] == 'aggressive':
                            incident_modifier -= 0.2
            
            # Cap the modifier
            incident_modifier = max(min(incident_modifier, 0.3), -0.3)
        
        # Calculate weighted average of all factors
        factors = {
            'diplomatic_compatibility': diplomatic_score,
            'trade_compatibility': trade_score,
            'technology_compatibility': tech_score,
            'environmental_compatibility': env_score,
            'geopolitical_alignment': geo_score
        }
        
        # Calculate overall score (weighted average)
        weights = {
            'diplomatic_compatibility': 0.3,
            'trade_compatibility': 0.3,
            'technology_compatibility': 0.15,
            'environmental_compatibility': 0.1,
            'geopolitical_alignment': 0.15
        }
        
        overall_score = sum(factors[f] * weights[f] for f in factors.keys())
        
        # Apply incident modifier
        overall_score += incident_modifier
        
        # Ensure final score is between 0 and 1
        overall_score = min(max(overall_score, 0), 1)
        
        return overall_score, factors

class AIExplanationSystem:
    """
    Provides detailed explanations of AI decision processes to increase transparency for players.
    Generates human-readable explanations based on countries' profiles, economic situations,
    diplomatic relations, and other contextual factors.
    """
    
    def __init__(self, game_state=None):
        """Initialize the explanation system."""
        self.game_state = game_state
        self.explanation_templates = self._load_explanation_templates()
        self.explanation_history = {}  # Track explanations by country and turn
        
    def _load_explanation_templates(self):
        """Load templates for various types of explanations."""
        return {
            "trade": {
                "tariff_increase": [
                    "{country} raised tariffs on {target_country} because: \n"
                    "• {primary_reason}\n"
                    "• {secondary_reason}\n"
                    "• {tertiary_reason}"
                ],
                "tariff_decrease": [
                    "{country} lowered tariffs on {target_country} because: \n"
                    "• {primary_reason}\n"
                    "• {secondary_reason}\n"
                    "• {tertiary_reason}"
                ],
                "subsidy": [
                    "{country} subsidized its {sector} sector because: \n"
                    "• {primary_reason}\n"
                    "• {secondary_reason}\n"
                    "• {tertiary_reason}"
                ]
            },
            "coalition": {
                "form": [
                    "{country} formed a {purpose} coalition because: \n"
                    "• {primary_reason}\n"
                    "• {secondary_reason}\n"
                    "• Historical context: {historical_context}"
                ],
                "join": [
                    "{country} joined the {coalition_name} because: \n"
                    "• {primary_reason}\n"
                    "• {secondary_reason}\n"
                    "• Strategic alignment: {strategic_reason}"
                ],
                "leave": [
                    "{country} left the {coalition_name} because: \n"
                    "• {primary_reason}\n"
                    "• {secondary_reason}\n"
                    "• Changed circumstances: {changed_circumstance}"
                ],
                "challenge_leadership": [
                    "{country} challenged {target_country}'s leadership of the {coalition_name} because: \n"
                    "• {primary_reason}\n"
                    "• {secondary_reason}\n"
                    "• Power dynamics: {power_dynamics}"
                ]
            },
            "diplomatic": {
                "improve_relations": [
                    "{country} is improving relations with {target_country} because: \n"
                    "• {primary_reason}\n"
                    "• {secondary_reason}\n"
                    "• Diplomatic strategy: {strategy_reason}"
                ],
                "deteriorate_relations": [
                    "{country} is worsening relations with {target_country} because: \n"
                    "• {primary_reason}\n"
                    "• {secondary_reason}\n"
                    "• Conflict of interest: {conflict_reason}"
                ]
            },
            "budget": {
                "increase_spending": [
                    "{country} increased spending on {category} because: \n"
                    "• {primary_reason}\n"
                    "• {secondary_reason}\n"
                    "• Economic context: {economic_context}"
                ],
                "decrease_spending": [
                    "{country} decreased spending on {category} because: \n"
                    "• {primary_reason}\n"
                    "• {secondary_reason}\n"
                    "• Fiscal reality: {fiscal_reality}"
                ]
            }
        }
    
    def explain_decision(self, country_iso, decision_type, decision_details, game_state=None):
        """
        Generate a detailed explanation for an AI country's decision.
        
        Args:
            country_iso: ISO code of the country
            decision_type: Type of decision (trade, coalition, diplomatic, budget)
            decision_details: Dictionary with decision details
            game_state: Current game state (optional - will use stored state if not provided)
            
        Returns:
            A human-readable explanation of the decision with context
        """
        if game_state:
            self.game_state = game_state
            
        # If game state is still None, we can't generate context-aware explanations
        if not self.game_state:
            return self._generate_simple_explanation(country_iso, decision_type, decision_details)
        
        # Get country profile and current situation
        country_profile = self._get_country_profile(country_iso)
        country_context = self._analyze_country_context(country_iso)
        
        # Generate specific explanation based on decision type
        if decision_type == "trade":
            explanation = self._explain_trade_decision(country_iso, country_profile, country_context, decision_details)
        elif decision_type == "coalition":
            explanation = self._explain_coalition_decision(country_iso, country_profile, country_context, decision_details)
        elif decision_type == "diplomatic":
            explanation = self._explain_diplomatic_decision(country_iso, country_profile, country_context, decision_details)
        elif decision_type == "budget":
            explanation = self._explain_budget_decision(country_iso, country_profile, country_context, decision_details)
        else:
            explanation = self._generate_simple_explanation(country_iso, decision_type, decision_details)
        
        # Store in history
        current_turn = getattr(self.game_state, 'current_turn', 0)
        if country_iso not in self.explanation_history:
            self.explanation_history[country_iso] = []
            
        self.explanation_history[country_iso].append({
            'turn': current_turn,
            'type': decision_type,
            'details': decision_details,
            'explanation': explanation
        })
        
        return explanation
    
    def _generate_simple_explanation(self, country_iso, decision_type, decision_details):
        """Generate a simple explanation when context is limited."""
        action = decision_details.get('action', 'unknown action')
        target = decision_details.get('target_country', '')
        explanation = decision_details.get('explanation', '')
        
        return f"{country_iso} took {action} {('toward ' + target) if target else ''}: {explanation}"
    
    def _get_country_profile(self, country_iso):
        """Get the country profile for generating explanations."""
        # Try to get from game state
        if hasattr(self.game_state, 'countries') and country_iso in self.game_state.countries:
            country = self.game_state.countries[country_iso]
            if hasattr(country, 'profile'):
                return country.profile
                
        # Try to get from diplomacy system
        if hasattr(self.game_state, 'diplomacy'):
            diplomacy = self.game_state.diplomacy
            if hasattr(diplomacy, 'country_personalities') and country_iso in diplomacy.country_personalities:
                return diplomacy.country_personalities[country_iso]
        
        # Default to a neutral profile if nothing found
        return CountryProfile()
    
    def _analyze_country_context(self, country_iso):
        """Analyze the current economic and diplomatic context of a country."""
        context = {
            'economic': {},
            'diplomatic': {},
            'domestic': {}
        }
        
        # Get economic data
        if hasattr(self.game_state, 'countries') and country_iso in self.game_state.countries:
            country = self.game_state.countries[country_iso]
            
            # Economic indicators
            if hasattr(country, 'gdp'):
                context['economic']['gdp'] = country.gdp
            if hasattr(country, 'gdp_growth'):
                context['economic']['gdp_growth'] = country.gdp_growth
            if hasattr(country, 'unemployment_rate'):
                context['economic']['unemployment'] = country.unemployment_rate
            if hasattr(country, 'inflation'):
                context['economic']['inflation'] = country.inflation
                
            # Domestic situation
            if hasattr(country, 'approval_rating'):
                context['domestic']['approval'] = country.approval_rating
            if hasattr(country, 'stability'):
                context['domestic']['stability'] = country.stability
        
        # Get diplomatic context
        if hasattr(self.game_state, 'diplomacy'):
            diplomacy = self.game_state.diplomacy
            
            # Relations with other countries
            if hasattr(diplomacy, 'country_relations') and country_iso in diplomacy.country_relations:
                context['diplomatic']['relations'] = diplomacy.country_relations[country_iso]
            
            # Coalition memberships
            if hasattr(diplomacy, 'get_active_coalitions'):
                coalitions = diplomacy.get_active_coalitions(country_iso)
                context['diplomatic']['coalitions'] = coalitions
        
        return context
    
    def _explain_trade_decision(self, country_iso, profile, context, decision_details):
        """Generate explanations for trade-related decisions."""
        action = decision_details.get('action', '')
        
        if 'tariff' in action:
            return self._explain_tariff_decision(country_iso, profile, context, decision_details)
        elif 'subsidy' in action:
            return self._explain_subsidy_decision(country_iso, profile, context, decision_details)
        else:
            return self._generate_simple_explanation(country_iso, 'trade', decision_details)
    
    def _explain_tariff_decision(self, country_iso, profile, context, decision_details):
        """Explain a tariff-related decision."""
        target_country = decision_details.get('target_country', 'trading partners')
        tariff_rate = decision_details.get('rate', 0)
        sector = decision_details.get('sector', 'all sectors')
        increase = decision_details.get('increase', False)
        
        # Determine countries' name
        country_name = self._get_country_name(country_iso)
        target_name = self._get_country_name(target_country)
        
        # Select template
        template_key = "tariff_increase" if increase else "tariff_decrease"
        templates = self.explanation_templates["trade"][template_key]
        template = random.choice(templates)
        
        # Generate reasons based on country profile and context
        reasons = []
        
        # Economic reasons
        economic_context = context.get('economic', {})
        if increase:
            # Reasons for increasing tariffs
            if profile.protectionism > 0.6:
                reasons.append(f"Strong protectionist tendencies (Protectionism: {profile.protectionism:.1f})")
            
            if profile.sector_protection > 0.7:
                reasons.append(f"Policy of protecting domestic {sector} sector from foreign competition")
            
            if economic_context.get('unemployment', 0) > 7:
                reasons.append(f"High unemployment rate of {economic_context.get('unemployment')}% creates pressure to protect domestic jobs")
                
            if profile.retaliation > 0.7:
                reasons.append(f"Retaliation against {target_name}'s trade policies (Retaliation tendency: {profile.retaliation:.1f})")
                
            if profile.economic_focus > 0.7:
                reasons.append(f"Prioritizing economic sovereignty over international cooperation")
        else:
            # Reasons for decreasing tariffs
            if profile.free_market_belief > 0.7:
                reasons.append(f"Strong free market ideology (Free market belief: {profile.free_market_belief:.1f})")
                
            if profile.export_orientation > 0.7:
                reasons.append(f"Export-oriented economic strategy that benefits from open markets")
                
            if profile.cooperation > 0.7:
                reasons.append(f"Commitment to international cooperation (Cooperation: {profile.cooperation:.1f})")
                
            relations = context.get('diplomatic', {}).get('relations', {}).get(target_country, {}).get('opinion', 50)
            if relations > 70:
                reasons.append(f"Excellent diplomatic relations with {target_name} (Relations: {relations}/100)")
        
        # Fill in the template
        while len(reasons) < 3:
            reasons.append("General alignment with national economic strategy")
            
        explanation = template.format(
            country=country_name,
            target_country=target_name,
            primary_reason=reasons[0],
            secondary_reason=reasons[1] if len(reasons) > 1 else "Internal policy considerations",
            tertiary_reason=reasons[2] if len(reasons) > 2 else "Domestic political factors"
        )
        
        return explanation
    
    def _explain_subsidy_decision(self, country_iso, profile, context, decision_details):
        """Explain a subsidy-related decision."""
        sector = decision_details.get('sector', 'unspecified')
        amount = decision_details.get('amount', 0)
        
        # Get country name
        country_name = self._get_country_name(country_iso)
        
        # Select template
        template = random.choice(self.explanation_templates["trade"]["subsidy"])
        
        # Generate reasons based on profile and context
        reasons = []
        
        if profile.sector_protection > 0.6:
            reasons.append(f"Strong belief in protecting key industries (Sector protection: {profile.sector_protection:.1f})")
            
        if profile.self_sufficiency > 0.7:
            reasons.append(f"Strategic goal of self-sufficiency in {sector}")
            
        economic_context = context.get('economic', {})
        if economic_context.get('unemployment', 0) > 6:
            reasons.append(f"Need to preserve jobs in the {sector} sector amid {economic_context.get('unemployment')}% unemployment")
            
        if profile.innovation_focus > 0.7 and sector in ['technology', 'research', 'advanced_manufacturing']:
            reasons.append(f"Strategic focus on technological innovation and advancement")
            
        # Fill in the template
        while len(reasons) < 3:
            reasons.append("Alignment with national economic priorities")
            
        explanation = template.format(
            country=country_name,
            sector=sector,
            primary_reason=reasons[0],
            secondary_reason=reasons[1] if len(reasons) > 1 else "Domestic economic considerations",
            tertiary_reason=reasons[2] if len(reasons) > 2 else "Industry lobbying and political influence"
        )
        
        return explanation
    
    def _explain_coalition_decision(self, country_iso, profile, context, decision_details):
        """Generate explanations for coalition-related decisions."""
        action = decision_details.get('action', '')
        
        if action == 'form_coalition':
            return self._explain_coalition_formation(country_iso, profile, context, decision_details)
        elif action == 'join_coalition':
            return self._explain_coalition_join(country_iso, profile, context, decision_details)
        elif action == 'leave_coalition':
            return self._explain_coalition_leave(country_iso, profile, context, decision_details)
        elif action == 'challenge_leadership':
            return self._explain_leadership_challenge(country_iso, profile, context, decision_details)
        else:
            return self._generate_simple_explanation(country_iso, 'coalition', decision_details)
    
    def _explain_coalition_formation(self, country_iso, profile, context, decision_details):
        """Explain a coalition formation decision."""
        coalition_data = decision_details.get('coalition_data', {})
        purpose = coalition_data.get('purpose', 'unspecified')
        candidates = coalition_data.get('candidates', [])
        name = coalition_data.get('name', 'New Coalition')
        
        # Get country name
        country_name = self._get_country_name(country_iso)
        
        # Select template
        template = random.choice(self.explanation_templates["coalition"]["form"])
        
        # Generate reasons based on profile and context
        reasons = []
        
        # Purpose-specific reasons
        if purpose == 'trade':
            if profile.economic_focus > 0.6:
                reasons.append(f"Strong focus on economic interests (Economic focus: {profile.economic_focus:.1f})")
            if profile.free_market_belief > 0.6:
                reasons.append(f"Belief in economic integration and free trade")
                
        elif purpose == 'defense':
            if profile.aggression < 0.4:
                reasons.append(f"Defensive posture requires allies for security (Aggression: {profile.aggression:.1f})")
            if profile.isolationism < 0.4:
                reasons.append(f"Recognition that security requires international partnerships")
                
        elif purpose == 'regional':
            if profile.regional_focus > 0.7:
                reasons.append(f"Strong focus on regional affairs (Regional focus: {profile.regional_focus:.1f})")
                
        elif purpose == 'counter':
            if profile.retaliation > 0.6:
                reasons.append(f"Tendency to counter perceived threats with alliances (Retaliation: {profile.retaliation:.1f})")
        
        # General coalition-forming reasons
        if profile.cooperation > 0.6:
            reasons.append(f"Strong cooperative approach to international relations")
        
        if profile.isolationism < 0.3:
            reasons.append(f"Internationalist outlook favors coalition-building")
        
        # Strategic context
        if len(candidates) > 2:
            reasons.append(f"Opportunity to form a powerful bloc with {len(candidates)} like-minded countries")
        
        # Historical context possibilities
        historical_contexts = [
            f"Continuing a pattern of {purpose}-focused alliance-building",
            f"Response to changing global dynamics requiring new partnerships",
            f"Building on existing bilateral relationships to create a stronger multilateral framework",
            f"Evolution of informal cooperation into a formal structure"
        ]
        
        # Fill in the template
        while len(reasons) < 2:
            reasons.append("Strategic alignment with national priorities")
            
        explanation = template.format(
            country=country_name,
            purpose=purpose,
            primary_reason=reasons[0],
            secondary_reason=reasons[1] if len(reasons) > 1 else "Alignment with strategic objectives",
            historical_context=random.choice(historical_contexts)
        )
        
        return explanation
    
    def _explain_coalition_join(self, country_iso, profile, context, decision_details):
        """Explain a decision to join a coalition."""
        coalition_id = decision_details.get('coalition_id', '')
        coalition_name = decision_details.get('coalition_name', 'the coalition')
        
        # Try to get more coalition details if possible
        coalition_details = self._get_coalition_details(coalition_id)
        
        # Get country name
        country_name = self._get_country_name(country_iso)
        
        # Select template
        template = random.choice(self.explanation_templates["coalition"]["join"])
        
        # Generate reasons based on profile and context
        reasons = []
        
        # Purpose-specific reasons based on coalition type
        purpose = coalition_details.get('purpose', '')
        if purpose == 'trade':
            if profile.economic_focus > 0.6:
                reasons.append(f"Economic benefits of joining a trade-focused coalition")
            if profile.free_market_belief > 0.6:
                reasons.append(f"Alignment with free market principles of the coalition")
                
        elif purpose == 'defense':
            if profile.aggression < 0.4:
                reasons.append(f"Security benefits of collective defense")
                
        elif purpose == 'regional':
            if profile.regional_focus > 0.6:
                reasons.append(f"Priority placed on regional integration and cooperation")
                
        # Leader-based reasons
        leader_country = coalition_details.get('leader_country', '')
        if leader_country:
            leader_name = self._get_country_name(leader_country)
            diplomatic_context = context.get('diplomatic', {})
            relations = diplomatic_context.get('relations', {}).get(leader_country, {}).get('opinion', 50)
            
            if relations > 70:
                reasons.append(f"Strong relations with coalition leader {leader_name} (Relations: {relations}/100)")
        
        # General coalition-joining reasons
        if profile.isolationism < 0.4:
            reasons.append(f"Internationalist approach to foreign policy (Low isolationism: {profile.isolationism:.1f})")
            
        if profile.cooperation > 0.6:
            reasons.append(f"Strong cooperative tendencies in international affairs")
        
        # Strategic alignment possibilities
        strategic_reasons = [
            f"Coalition membership strengthens {country_name}'s international position",
            f"Joining provides access to new markets and resources",
            f"Membership offers protection against common rivals",
            f"Alignment with the coalition's goals serves national interests"
        ]
        
        # Fill in the template
        while len(reasons) < 2:
            reasons.append("Alignment with national strategic interests")
            
        explanation = template.format(
            country=country_name,
            coalition_name=coalition_name,
            primary_reason=reasons[0],
            secondary_reason=reasons[1] if len(reasons) > 1 else "Diplomatic calculus favors membership",
            strategic_reason=random.choice(strategic_reasons)
        )
        
        return explanation
    
    def _explain_coalition_leave(self, country_iso, profile, context, decision_details):
        """Explain a decision to leave a coalition."""
        coalition_id = decision_details.get('coalition_id', '')
        reason = decision_details.get('reason', 'strategic_decision')
        
        # Try to get more coalition details
        coalition_details = self._get_coalition_details(coalition_id)
        coalition_name = coalition_details.get('name', 'the coalition')
        
        # Get country name
        country_name = self._get_country_name(country_iso)
        
        # Select template
        template = random.choice(self.explanation_templates["coalition"]["leave"])
        
        # Generate reasons based on profile, context, and stated reason
        reasons = []
        
        if reason == 'low_effectiveness':
            reasons.append(f"The coalition has not been effective in achieving its stated goals")
            
        elif reason == 'leadership_dispute':
            leader = coalition_details.get('leader_country', '')
            if leader:
                leader_name = self._get_country_name(leader)
                reasons.append(f"Disagreement with {leader_name}'s leadership direction")
            else:
                reasons.append(f"Disagreement with the coalition's leadership")
                
        elif reason == 'policy_misalignment':
            reasons.append(f"The coalition's policies no longer align with {country_name}'s interests")
            
        elif reason == 'member_conflict':
            reasons.append(f"Conflicts with other member countries have become untenable")
            
        # Profile-based reasons
        if profile.isolationism > 0.7:
            reasons.append(f"Shift toward more independent foreign policy (High isolationism: {profile.isolationism:.1f})")
            
        if profile.pragmatism > 0.7:
            reasons.append(f"Pragmatic reassessment of the benefits of membership")
            
        # Changed circumstances possibilities
        changed_circumstances = [
            f"Domestic political pressures now favor withdrawal",
            f"The coalition's purpose has evolved away from {country_name}'s priorities",
            f"New bilateral relationships have diminished the value of multilateral cooperation",
            f"The international situation has changed, making membership less advantageous"
        ]
        
        # Fill in the template
        while len(reasons) < 2:
            reasons.append("Strategic realignment of foreign policy priorities")
            
        explanation = template.format(
            country=country_name,
            coalition_name=coalition_name,
            primary_reason=reasons[0],
            secondary_reason=reasons[1] if len(reasons) > 1 else "Shifting national priorities",
            changed_circumstance=random.choice(changed_circumstances)
        )
        
        return explanation
    
    def _explain_leadership_challenge(self, country_iso, profile, context, decision_details):
        """Explain a decision to challenge coalition leadership."""
        coalition_id = decision_details.get('coalition_id', '')
        
        # Try to get more coalition details
        coalition_details = self._get_coalition_details(coalition_id)
        coalition_name = coalition_details.get('name', 'the coalition')
        
        # Get target country (current leader)
        leader_country = coalition_details.get('leader_country', '')
        
        # Get country names
        country_name = self._get_country_name(country_iso)
        target_name = self._get_country_name(leader_country) if leader_country else "the current leader"
        
        # Select template
        template = random.choice(self.explanation_templates["coalition"]["challenge_leadership"])
        
        # Generate reasons based on profile and context
        reasons = []
        
        if profile.pride > 0.7:
            reasons.append(f"National pride and ambition to lead (Pride: {profile.pride:.1f})")
            
        if profile.economic_focus > 0.7 and coalition_details.get('purpose') == 'trade':
            reasons.append(f"Belief that {country_name} can better lead a trade-focused coalition")
            
        if profile.aggression > 0.6:
            reasons.append(f"Assertive foreign policy approach (Aggression: {profile.aggression:.1f})")
            
        # Leader-specific reasons
        if leader_country:
            diplomatic_context = context.get('diplomatic', {})
            relations = diplomatic_context.get('relations', {}).get(leader_country, {}).get('opinion', 50)
            
            if relations < 40:
                reasons.append(f"Poor relations with current leader {target_name} (Relations: {relations}/100)")
        
        # Power dynamics possibilities
        power_dynamics = [
            f"{country_name} has grown in influence while {target_name}'s has diminished",
            f"The coalition needs fresh leadership to address new challenges",
            f"Other member countries have encouraged {country_name} to step forward",
            f"Internal coalition dynamics have shifted in {country_name}'s favor"
        ]
        
        # Fill in the template
        while len(reasons) < 2:
            reasons.append("Strategic reassessment of coalition leadership needs")
            
        explanation = template.format(
            country=country_name,
            target_country=target_name,
            coalition_name=coalition_name,
            primary_reason=reasons[0],
            secondary_reason=reasons[1] if len(reasons) > 1 else "Desire for greater influence",
            power_dynamics=random.choice(power_dynamics)
        )
        
        return explanation
    
    def _explain_diplomatic_decision(self, country_iso, profile, context, decision_details):
        """Generate explanations for diplomatic decisions."""
        action = decision_details.get('action', '')
        target_country = decision_details.get('target_country', '')
        
        if not target_country:
            return self._generate_simple_explanation(country_iso, 'diplomatic', decision_details)
        
        # Determine if this is about improving or deteriorating relations
        is_improving = action in ['improve_relations', 'diplomatic_mission', 'propose_treaty', 'send_aid']
        template_key = "improve_relations" if is_improving else "deteriorate_relations"
        
        # Get country names
        country_name = self._get_country_name(country_iso)
        target_name = self._get_country_name(target_country)
        
        # Select template
        template = random.choice(self.explanation_templates["diplomatic"][template_key])
        
        # Generate reasons based on profile and context
        reasons = []
        
        # Get current relations if available
        diplomatic_context = context.get('diplomatic', {})
        current_relations = diplomatic_context.get('relations', {}).get(target_country, {}).get('opinion', 50)
        
        if is_improving:
            # Reasons for improving relations
            if profile.cooperation > 0.6:
                reasons.append(f"General cooperative approach to diplomacy (Cooperation: {profile.cooperation:.1f})")
                
            if profile.economic_focus > 0.6:
                reasons.append(f"Economic benefits of stronger ties with {target_name}")
                
            if current_relations < 40:
                reasons.append(f"Need to repair previously strained relations (Current relations: {current_relations}/100)")
                
            if profile.pragmatism > 0.7:
                reasons.append(f"Pragmatic assessment that cooperation is beneficial")
                
            # Strategy reasons
            strategy_reasons = [
                f"Part of a broader diplomatic outreach strategy",
                f"Building alliances to counter regional rivals",
                f"Diversifying international partnerships",
                f"Preparing ground for future economic or security cooperation"
            ]
        else:
            # Reasons for deteriorating relations
            if profile.aggression > 0.6:
                reasons.append(f"Assertive approach to international relations (Aggression: {profile.aggression:.1f})")
                
            if profile.retaliation > 0.7:
                reasons.append(f"Response to perceived hostile actions by {target_name}")
                
            if profile.pride > 0.7 and current_relations < 50:
                reasons.append(f"Pride and unwillingness to overlook past slights (Pride: {profile.pride:.1f})")
                
            # Conflict reasons
            conflict_reasons = [
                f"Fundamental conflict of interests in {random.choice(['trade', 'security', 'regional influence'])}",
                f"Ideological differences that have become increasingly prominent",
                f"Competition over resources or markets",
                f"Alignment with rival powers against {target_name}"
            ]
        
        # Fill in the template
        while len(reasons) < 2:
            reasons.append("Alignment with strategic national interests")
            
        explanation = template.format(
            country=country_name,
            target_country=target_name,
            primary_reason=reasons[0],
            secondary_reason=reasons[1] if len(reasons) > 1 else "Changing geopolitical calculations",
            strategy_reason=random.choice(strategy_reasons) if is_improving else "N/A",
            conflict_reason=random.choice(conflict_reasons) if not is_improving else "N/A"
        )
        
        return explanation
    
    def _explain_budget_decision(self, country_iso, profile, context, decision_details):
        """Generate explanations for budget-related decisions."""
        category = decision_details.get('category', '')
        amount = decision_details.get('amount', 0)
        original_amount = decision_details.get('prior_amount', 0)
        
        is_increase = amount > original_amount if original_amount else True
        template_key = "increase_spending" if is_increase else "decrease_spending"
        
        # Get country name
        country_name = self._get_country_name(country_iso)
        
        # Select template
        template = random.choice(self.explanation_templates["budget"][template_key])
        
        # Generate reasons based on profile and context
        reasons = []
        economic_context = context.get('economic', {})
        
        if is_increase:
            # Reasons for increasing spending
            if category == 'education' and profile.innovation_focus > 0.6:
                reasons.append(f"Strong focus on innovation and human capital development")
                
            elif category == 'defense' and profile.aggression > 0.6:
                reasons.append(f"Assertive security posture requires increased military capabilities")
                
            elif category == 'infrastructure' and profile.economic_focus > 0.7:
                reasons.append(f"Priority on economic development through infrastructure investment")
                
            elif category == 'healthcare' and profile.accountability > 0.7:
                reasons.append(f"Strong commitment to public welfare and healthcare access")
                
            # General economic context
            if economic_context.get('gdp_growth', 0) > 2:
                reasons.append(f"Strong economic growth of {economic_context.get('gdp_growth')}% enables increased spending")
                
            if category == 'subsidies' and profile.sector_protection > 0.7:
                reasons.append(f"Policy of protecting and supporting key economic sectors")
                
            economic_contexts = [
                f"Taking advantage of a strong fiscal position to invest in {category}",
                f"Responding to public demand for improved {category} services",
                f"Strategic long-term investment in national capabilities",
                f"Part of a stimulus package to boost economic growth"
            ]
        else:
            # Reasons for decreasing spending
            if profile.risk_aversion > 0.7:
                reasons.append(f"Conservative fiscal approach prioritizes deficit reduction")
                
            if profile.debt_tolerance < 0.3:
                reasons.append(f"Low tolerance for government debt (Debt tolerance: {profile.debt_tolerance:.1f})")
                
            if economic_context.get('gdp_growth', 0) < 0:
                reasons.append(f"Economic contraction of {abs(economic_context.get('gdp_growth', 0))}% requires fiscal restraint")
                
            if category == 'defense' and profile.aggression < 0.3:
                reasons.append(f"Peaceful foreign policy reduces need for military spending")
                
            fiscal_realities = [
                f"Budget constraints require reallocation of resources away from {category}",
                f"Fiscal consolidation necessary to maintain economic stability",
                f"Shift in priorities toward more pressing national needs",
                f"Efficiency measures aimed at reducing waste while maintaining services"
            ]
        
        # Fill in the template
        while len(reasons) < 2:
            reasons.append("Alignment with government fiscal priorities")
            
        explanation = template.format(
            country=country_name,
            category=category,
            primary_reason=reasons[0],
            secondary_reason=reasons[1] if len(reasons) > 1 else "Changing budget priorities",
            economic_context=random.choice(economic_contexts) if is_increase else "N/A",
            fiscal_reality=random.choice(fiscal_realities) if not is_increase else "N/A"
        )
        
        return explanation
    
    def _get_country_name(self, country_iso):
        """Get the full name of a country from its ISO code."""
        if not country_iso:
            return "Unknown country"
            
        if hasattr(self.game_state, 'countries') and country_iso in self.game_state.countries:
            country = self.game_state.countries[country_iso]
            if hasattr(country, 'name'):
                return country.name
                
        # Common countries fallback
        country_names = {
            'US': 'United States',
            'CN': 'China',
            'RU': 'Russia',
            'DE': 'Germany',
            'FR': 'France',
            'GB': 'United Kingdom',
            'JP': 'Japan',
            'IN': 'India',
            'BR': 'Brazil',
            'IT': 'Italy',
            'CA': 'Canada',
            'KR': 'South Korea',
            'AU': 'Australia',
            'ES': 'Spain',
            'MX': 'Mexico',
            'ID': 'Indonesia',
            'TR': 'Turkey',
            'SA': 'Saudi Arabia',
            'CH': 'Switzerland',
            'NL': 'Netherlands',
            'SE': 'Sweden',
            'NO': 'Norway',
            'DK': 'Denmark',
            'FI': 'Finland'
        }
        
        return country_names.get(country_iso, country_iso)
    
    def _get_coalition_details(self, coalition_id):
        """Get details about a specific coalition."""
        if not hasattr(self.game_state, 'diplomacy') or not hasattr(self.game_state.diplomacy, 'coalitions'):
            return {'name': 'the coalition'}
            
        for coalition in self.game_state.diplomacy.coalitions:
            if hasattr(coalition, 'id') and coalition.id == coalition_id:
                return {
                    'id': coalition.id,
                    'name': coalition.name,
                    'purpose': coalition.purpose,
                    'leader_country': coalition.leader_country,
                    'members': list(coalition.member_countries),
                    'cohesion': coalition.cohesion_level
                }
                
        return {'name': 'the coalition'}
    
    def get_recent_explanations(self, country_iso=None, limit=5):
        """Get recent decision explanations, optionally filtered by country."""
        if country_iso:
            if country_iso not in self.explanation_history:
                return []
                
            explanations = self.explanation_history[country_iso]
        else:
            # Flatten all country explanations
            explanations = []
            for country, history in self.explanation_history.items():
                explanations.extend([dict(item, country=country) for item in history])
                
        # Sort by turn (most recent first)
        explanations.sort(key=lambda x: x.get('turn', 0), reverse=True)
        
        # Return the most recent ones
        return explanations[:limit]
    
    def generate_explanation_report(self, country_iso):
        """Generate a comprehensive report of a country's decision patterns."""
        if country_iso not in self.explanation_history or not self.explanation_history[country_iso]:
            return f"No decision history available for {self._get_country_name(country_iso)}"
            
        history = self.explanation_history[country_iso]
        
        # Count decision types
        decision_counts = {}
        for item in history:
            decision_type = item.get('type', 'unknown')
            decision_counts[decision_type] = decision_counts.get(decision_type, 0) + 1
            
        # Identify common patterns
        patterns = []
        
        # Most common decision type
        most_common_type = max(decision_counts.items(), key=lambda x: x[1])
        if most_common_type[1] > 1:
            patterns.append(f"Frequently makes {most_common_type[0]} decisions ({most_common_type[1]} times)")
            
        # Check for common targets in diplomatic decisions
        diplomatic_targets = {}
        for item in history:
            if item.get('type') == 'diplomatic':
                target = item.get('details', {}).get('target_country')
                if target:
                    diplomatic_targets[target] = diplomatic_targets.get(target, 0) + 1
                    
        if diplomatic_targets:
            most_common_target = max(diplomatic_targets.items(), key=lambda x: x[1])
            if most_common_target[1] > 1:
                patterns.append(f"Frequently engages diplomatically with {self._get_country_name(most_common_target[0])} ({most_common_target[1]} times)")
        
        # Generate the report
        country_name = self._get_country_name(country_iso)
        report = f"Decision Pattern Analysis for {country_name}\n\n"
        
        report += "Decision Type Summary:\n"
        for decision_type, count in decision_counts.items():
            report += f"- {decision_type.capitalize()}: {count} decisions\n"
            
        if patterns:
            report += "\nIdentified Patterns:\n"
            for pattern in patterns:
                report += f"- {pattern}\n"
                
        report += f"\nTotal decisions analyzed: {len(history)}"
        
        return report

class Coalition:
    """
    Represents a coalition of countries working together toward a common goal.
    Coalitions can form for trade, defense, regional cooperation, or countering other coalitions.
    """
    
    def __init__(self, name: str, purpose: str, founding_countries: List[str], 
                 formation_turn: int, leader_country: str = None, cohesion_level: float = 0.5):
        """
        Initialize a new coalition.
        
        Args:
            name: Name of the coalition
            purpose: Primary purpose ('trade', 'defense', 'regional', 'counter')
            founding_countries: List of country ISO codes of founding members
            formation_turn: Game turn when the coalition was formed
            leader_country: ISO code of the country leading the coalition
            cohesion_level: Initial cohesion level (0.0-1.0)
        """
        self.id = f"c_{int(time.time())}_{random.randint(1000, 9999)}"
        self.name = name
        self.purpose = purpose
        self.member_countries = set(founding_countries)
        self.formation_turn = formation_turn
        self.end_turn = None
        self.leader_country = leader_country if leader_country else founding_countries[0]
        self.cohesion_level = max(0.0, min(1.0, cohesion_level))
        self.target_coalition = None  # For counter-coalitions
        self.history = []
        self.record_event("formation", {
            "founding_members": founding_countries,
            "leader": self.leader_country,
            "turn": formation_turn
        })
        
    def add_country(self, country_iso: str, turn: int) -> bool:
        """
        Add a country to the coalition.
        
        Args:
            country_iso: ISO code of the country to add
            turn: Current game turn
            
        Returns:
            True if successfully added, False if already a member
        """
        if country_iso in self.member_countries:
            return False
            
        self.member_countries.add(country_iso)
        self.record_event("join", {
            "country": country_iso,
            "turn": turn
        })
        return True
        
    def remove_country(self, country_iso: str, turn: int) -> bool:
        """
        Remove a country from the coalition.
        
        Args:
            country_iso: ISO code of the country to remove
            turn: Current game turn
            
        Returns:
            True if successfully removed, False if wasn't a member
        """
        if country_iso not in self.member_countries:
            return False
            
        # If the leader leaves, select a new leader
        if country_iso == self.leader_country and len(self.member_countries) > 1:
            self.member_countries.remove(country_iso)
            self.leader_country = next(iter(self.member_countries))
        else:
            self.member_countries.remove(country_iso)
            
        self.record_event("leave", {
            "country": country_iso,
            "turn": turn
        })
        
        # Update cohesion - member leaving decreases cohesion
        self.update_cohesion(-0.1)
        
        return True
        
    def dissolve(self, turn: int, reason: str) -> None:
        """
        Dissolve the coalition.
        
        Args:
            turn: Current game turn
            reason: Reason for dissolution
        """
        self.end_turn = turn
        self.record_event("dissolution", {
            "turn": turn,
            "reason": reason,
            "final_members": list(self.member_countries)
        })
        
    def update_cohesion(self, change: float) -> float:
        """
        Update the coalition's cohesion level.
        
        Args:
            change: Amount to change cohesion by (-1.0 to 1.0)
            
        Returns:
            New cohesion level
        """
        self.cohesion_level = max(0.0, min(1.0, self.cohesion_level + change))
        return self.cohesion_level
        
    def is_active(self, current_turn: int = None) -> bool:
        """
        Check if the coalition is still active.
        
        Args:
            current_turn: Current game turn (optional)
            
        Returns:
            True if active, False if dissolved
        """
        if self.end_turn is None:
            return True
        if current_turn is not None:
            return current_turn <= self.end_turn
        return False
        
    def get_strength(self, game_state: Any) -> float:
        """
        Calculate the overall strength of the coalition based on member countries.
        
        Args:
            game_state: Current game state for accessing country data
            
        Returns:
            Strength score
        """
        strength = 0.0
        
        # Sum member country strengths
        for country_iso in self.member_countries:
            if hasattr(game_state, 'countries') and country_iso in game_state.countries:
                country = game_state.countries[country_iso]
                
                # Base on GDP
                if hasattr(country, 'gdp'):
                    strength += country.gdp / 1000  # Scale down
                else:
                    strength += 1.0  # Default value
                    
                # Adjust for cohesion
                strength *= (0.5 + (self.cohesion_level * 0.5))  # 50-100% effectiveness based on cohesion
        
        return strength
        
    def get_purpose_effectiveness(self, game_state: Any) -> float:
        """
        Evaluate how effectively the coalition is fulfilling its purpose.
        
        Args:
            game_state: Current game state
            
        Returns:
            Effectiveness score (0.0-1.0)
        """
        if self.purpose == 'trade':
            # For trade coalitions, measure trade growth between members
            return self._evaluate_trade_effectiveness(game_state)
            
        elif self.purpose == 'defense':
            # For defense coalitions, evaluate security improvements
            return self._evaluate_defense_effectiveness(game_state)
            
        elif self.purpose == 'counter' and self.target_coalition:
            # For counter-coalitions, measure relative strength vs target
            own_strength = self.get_strength(game_state)
            target_strength = self.target_coalition.get_strength(game_state)
            if target_strength > 0:
                return min(1.0, own_strength / target_strength)
        
        # Default effectiveness
        return 0.5
        
    def _evaluate_trade_effectiveness(self, game_state: Any) -> float:
        """Evaluate trade improvement between coalition members"""
        # Implementation depends on trade model in the game
        # Simple placeholder
        return 0.6 + (random.random() * 0.2)
        
    def _evaluate_defense_effectiveness(self, game_state: Any) -> float:
        """Evaluate defense improvement from coalition"""
        # Implementation depends on security model in the game
        # Simple placeholder
        return 0.5 + (random.random() * 0.3)
        
    def record_event(self, event_type: str, details: Dict) -> None:
        """Record an event in the coalition's history"""
        self.history.append({
            "type": event_type,
            "details": details,
            "timestamp": details.get("turn", 0)
        })
        
    def __repr__(self) -> str:
        status = "Active" if self.is_active() else "Dissolved"
        return f"{self.name} ({status}, {len(self.member_countries)} members, Leader: {self.leader_country})"