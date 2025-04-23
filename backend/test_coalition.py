"""
Test module for Coalition functionality in diplomacy_ai.py

This script tests the Coalition class and coalition-related methods in the DiplomacyAI class.
"""

import unittest
from backend.diplomacy_ai import DiplomacyAI, Coalition, DiplomaticPersonality, CountryProfile, BudgetPolicy, CoalitionStrategy
from backend.engine import GameEngine

class MockCountry:
    """Mock country object for testing"""
    def __init__(self, iso_code, name, region, gdp=500, industry_percentage=30, 
                 agriculture_percentage=20, services_percentage=50):
        self.iso_code = iso_code
        self.name = name
        self.region = region
        self.gdp = gdp
        self.industry_percentage = industry_percentage
        self.agriculture_percentage = agriculture_percentage
        self.services_percentage = services_percentage
        self.government_type = "democracy"


class MockGameState:
    """Mock game state for testing"""
    def __init__(self):
        self.countries = {
            "DK": MockCountry("DK", "Denmark", "europe", gdp=400),
            "SE": MockCountry("SE", "Sweden", "europe", gdp=500),
            "NO": MockCountry("NO", "Norway", "europe", gdp=600),
            "DE": MockCountry("DE", "Germany", "europe", gdp=4000),
            "FR": MockCountry("FR", "France", "europe", gdp=3000),
            "US": MockCountry("US", "United States", "north_america", gdp=25000),
            "CN": MockCountry("CN", "China", "asia", gdp=15000),
        }
        self.current_turn = 5
        self.diplomacy = MockDiplomacy()


class MockDiplomacy:
    """Mock diplomacy object for testing"""
    def __init__(self):
        self.relations = []


class MockRelation:
    """Mock diplomatic relation for testing"""
    def __init__(self, country_a, country_b, relation_level):
        self.country_a = country_a
        self.country_b = country_b
        self.relation_level = relation_level


class TestCoalition(unittest.TestCase):
    """Test suite for Coalition class"""
    
    def setUp(self):
        """Set up test environment before each test method"""
        self.founding_countries = ["DK", "SE", "NO"]
        self.coalition = Coalition(
            name="Nordic Trade Alliance", 
            purpose="trade",
            founding_countries=self.founding_countries, 
            formation_turn=5,
            leader_country="DK", 
            cohesion_level=0.7
        )
        self.game_state = MockGameState()
    
    def test_init(self):
        """Test Coalition initialization"""
        self.assertEqual(self.coalition.name, "Nordic Trade Alliance")
        self.assertEqual(self.coalition.purpose, "trade")
        self.assertEqual(self.coalition.member_countries, set(self.founding_countries))
        self.assertEqual(self.coalition.formation_turn, 5)
        self.assertEqual(self.coalition.leader_country, "DK")
        self.assertEqual(self.coalition.cohesion_level, 0.7)
    
    def test_add_country(self):
        """Test adding a country to the coalition"""
        # Add Germany to the coalition
        result = self.coalition.add_country("DE", 7)
        self.assertTrue(result)
        self.assertIn("DE", self.coalition.member_countries)
        self.assertEqual(self.coalition.membership_history["DE"]["joined_turn"], 7)
        self.assertIsNone(self.coalition.membership_history["DE"]["left_turn"])
        
        # Adding same country again should return False
        result = self.coalition.add_country("DE", 8)
        self.assertFalse(result)
        
        # Verify cohesion was reduced
        self.assertLess(self.coalition.cohesion_level, 0.7)
    
    def test_remove_country(self):
        """Test removing a country from the coalition"""
        # Remove Norway from the coalition
        result = self.coalition.remove_country("NO", 8)
        self.assertTrue(result)
        self.assertNotIn("NO", self.coalition.member_countries)
        self.assertEqual(self.coalition.membership_history["NO"]["left_turn"], 8)
        
        # Removing a non-member country should return False
        result = self.coalition.remove_country("US", 8)
        self.assertFalse(result)
        
        # Verify cohesion was reduced
        self.assertLess(self.coalition.cohesion_level, 0.7)
    
    def test_remove_leader_country(self):
        """Test removing the leader country from the coalition"""
        result = self.coalition.remove_country("DK", 8)
        self.assertTrue(result)
        self.assertNotIn("DK", self.coalition.member_countries)
        
        # Verify a new leader was chosen
        self.assertIsNotNone(self.coalition.leader_country)
        self.assertIn(self.coalition.leader_country, ["SE", "NO"])
    
    def test_update_cohesion(self):
        """Test updating coalition cohesion"""
        initial_cohesion = self.coalition.cohesion_level
        
        # Increase cohesion
        self.coalition.update_cohesion(0.1)
        # Use assertAlmostEqual to handle floating-point precision issues
        self.assertAlmostEqual(self.coalition.cohesion_level, initial_cohesion + 0.1, places=10)
        
        # Decrease cohesion
        self.coalition.update_cohesion(-0.2)
        self.assertAlmostEqual(self.coalition.cohesion_level, initial_cohesion - 0.1, places=10)
        
        # Test upper bound
        self.coalition.update_cohesion(1.0)
        self.assertEqual(self.coalition.cohesion_level, 1.0)
        
        # Test lower bound
        self.coalition.update_cohesion(-2.0)
        self.assertEqual(self.coalition.cohesion_level, 0.0)
    
    def test_is_active(self):
        """Test coalition active status"""
        # Coalition should be active at formation turn + duration - 1
        self.assertTrue(self.coalition.is_active(self.coalition.formation_turn + self.coalition.duration - 1))
        
        # Coalition should be inactive after duration expires
        self.assertFalse(self.coalition.is_active(self.coalition.formation_turn + self.coalition.duration))
        
        # Test extend_duration
        original_duration = self.coalition.duration
        self.coalition.extend_duration(5)
        self.assertEqual(self.coalition.duration, original_duration + 5)
        self.assertTrue(self.coalition.is_active(self.coalition.formation_turn + original_duration + 3))
    
    def test_record_action(self):
        """Test recording coalition actions"""
        # Record a successful action
        self.coalition.record_action(
            action_type="joint_tariff",
            details={"target": "US", "rate": 10, "success": True},
            turn=6
        )
        
        # Check if action was recorded
        self.assertEqual(len(self.coalition.actions_history), 1)
        self.assertEqual(self.coalition.actions_history[0]["type"], "joint_tariff")
        self.assertEqual(self.coalition.actions_history[0]["turn"], 6)
        
        # Check if cohesion was increased (successful action)
        self.assertGreater(self.coalition.cohesion_level, 0.7)
        
        # Reset cohesion for next test
        self.coalition.cohesion_level = 0.7
        
        # Record a failed action
        self.coalition.record_action(
            action_type="joint_sanction",
            details={"target": "CN", "success": False},
            turn=7
        )
        
        # Check if cohesion was decreased (failed action)
        self.assertLess(self.coalition.cohesion_level, 0.7)
    
    def test_get_member_influence(self):
        """Test calculating member influence in coalition"""
        # Test influence of member country
        influence = self.coalition.get_member_influence("DK", self.game_state)
        self.assertGreater(influence, 0)
        
        # Test influence of non-member country
        influence = self.coalition.get_member_influence("US", self.game_state)
        self.assertEqual(influence, 0)


class TestDiplomacyAI(unittest.TestCase):
    """Test suite for coalition-related methods in DiplomacyAI class"""
    
    def setUp(self):
        """Set up test environment before each test method"""
        self.game_state = MockGameState()
        self.diplomacy_ai = DiplomacyAI(self.game_state)
        
        # Initialize some strategic interests
        self.diplomacy_ai.strategic_interests = {
            "DK": {"SE": 0.8, "NO": 0.7, "DE": 0.5, "US": 0.3},
            "SE": {"DK": 0.8, "NO": 0.8, "DE": 0.6, "US": 0.3},
            "NO": {"DK": 0.7, "SE": 0.8, "DE": 0.5, "US": 0.4},
            "DE": {"DK": 0.5, "SE": 0.6, "NO": 0.5, "FR": 0.8, "US": 0.6},
            "FR": {"DE": 0.8, "US": 0.5},
            "US": {"DE": 0.6, "FR": 0.5, "CN": 0.2},
            "CN": {"US": 0.2}
        }
        
        # Initialize country personalities
        self.diplomacy_ai.country_personalities = {
            "DK": DiplomaticPersonality(economic_focus=0.7, aggression=0.2, isolationism=0.3, regional_focus=0.6, ideological_rigidity=0.4),
            "SE": DiplomaticPersonality(economic_focus=0.6, aggression=0.3, isolationism=0.2, regional_focus=0.5, ideological_rigidity=0.3),
            "NO": DiplomaticPersonality(economic_focus=0.8, aggression=0.2, isolationism=0.4, regional_focus=0.7, ideological_rigidity=0.3),
            "DE": DiplomaticPersonality(economic_focus=0.6, aggression=0.4, isolationism=0.2, regional_focus=0.4, ideological_rigidity=0.5),
            "FR": DiplomaticPersonality(economic_focus=0.5, aggression=0.5, isolationism=0.3, regional_focus=0.4, ideological_rigidity=0.6),
            "US": DiplomaticPersonality(economic_focus=0.6, aggression=0.6, isolationism=0.4, regional_focus=0.3, ideological_rigidity=0.5),
            "CN": DiplomaticPersonality(economic_focus=0.8, aggression=0.5, isolationism=0.6, regional_focus=0.5, ideological_rigidity=0.7)
        }
        
        # Add a mocked get_diplomatic_relation method
        self.diplomacy_ai.get_diplomatic_relation = lambda c1, c2: {"opinion": 50} if c1 in ["DK", "SE", "NO"] and c2 in ["DK", "SE", "NO"] else {"opinion": 0}
        self.diplomacy_ai.update_diplomatic_relation = lambda c1, c2, rel: None
        self.diplomacy_ai.country_relations = {
            "DK": {"SE": {"opinion": 75}, "NO": {"opinion": 70}},
            "SE": {"DK": {"opinion": 75}, "NO": {"opinion": 80}},
            "NO": {"DK": {"opinion": 70}, "SE": {"opinion": 80}}
        }
    
    def test_evaluate_coalition_candidates(self):
        """Test evaluating potential coalition candidates"""
        candidates = self.diplomacy_ai.evaluate_coalition_candidates("DK", "trade", min_compatibility=0.5)
        self.assertTrue(len(candidates) > 0)
        self.assertIn("SE", candidates)
        self.assertIn("NO", candidates)
    
    def test_propose_coalition(self):
        """Test creating a coalition proposal"""
        candidates = ["SE", "NO"]
        proposal = self.diplomacy_ai.propose_coalition("DK", "trade", candidates, 5)
        
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal["proposing_country"], "DK")
        self.assertEqual(proposal["purpose"], "trade")
        self.assertEqual(proposal["candidate_countries"], candidates)
        self.assertEqual(proposal["proposal_turn"], 5)
        self.assertIn(proposal["id"], self.diplomacy_ai.coalition_proposals)
    
    def test_respond_to_coalition_proposal(self):
        """Test responding to a coalition proposal"""
        # Create a proposal first
        candidates = ["SE", "NO"]
        proposal = self.diplomacy_ai.propose_coalition("DK", "trade", candidates, 5)
        proposal_id = proposal["id"]
        
        # Test valid response
        result = self.diplomacy_ai.respond_to_coalition_proposal("SE", proposal_id, True, 5)
        self.assertTrue(result)
        self.assertTrue(self.diplomacy_ai.coalition_proposals[proposal_id]["responses"]["SE"])
        
        # Test invalid country response
        result = self.diplomacy_ai.respond_to_coalition_proposal("CN", proposal_id, True, 5)
        self.assertFalse(result)
        
        # Complete the proposal with all responses
        self.diplomacy_ai.respond_to_coalition_proposal("NO", proposal_id, True, 5)
        
        # Check that coalition was created
        self.assertTrue(any(c.name == proposal["coalition_name"] for c in self.diplomacy_ai.coalitions))
    
    def test_get_active_coalitions(self):
        """Test retrieving active coalitions"""
        # Create a coalition first
        coalition = Coalition(
            name="Nordic Trade Alliance", 
            purpose="trade",
            founding_countries=["DK", "SE", "NO"], 
            formation_turn=5,
            leader_country="DK", 
            cohesion_level=0.7
        )
        self.diplomacy_ai.coalitions.append(coalition)
        
        # Test get all coalitions
        all_coalitions = self.diplomacy_ai.get_active_coalitions()
        self.assertEqual(len(all_coalitions), 1)
        
        # Test get coalitions for a country
        dk_coalitions = self.diplomacy_ai.get_active_coalitions("DK")
        self.assertEqual(len(dk_coalitions), 1)
        
        us_coalitions = self.diplomacy_ai.get_active_coalitions("US")
        self.assertEqual(len(us_coalitions), 0)
    
    def test_update_coalitions(self):
        """Test coalition updates over time"""
        # Create a coalition with low cohesion
        low_cohesion_coalition = Coalition(
            name="Fragile Alliance", 
            purpose="defense",
            founding_countries=["FR", "DE"], 
            formation_turn=5,
            leader_country="FR", 
            cohesion_level=0.25
        )
        self.diplomacy_ai.coalitions.append(low_cohesion_coalition)
        
        # Create an expired coalition
        expired_coalition = Coalition(
            name="Old Pact", 
            purpose="diplomatic",
            founding_countries=["US", "CN"], 
            formation_turn=1,
            leader_country="US", 
            cohesion_level=0.5
        )
        expired_coalition.duration = 3  # Will expire at turn 4
        self.diplomacy_ai.coalitions.append(expired_coalition)
        
        # Create a stable coalition
        stable_coalition = Coalition(
            name="Nordic Trade Alliance", 
            purpose="trade",
            founding_countries=["DK", "SE", "NO"], 
            formation_turn=5,
            leader_country="DK", 
            cohesion_level=0.7
        )
        self.diplomacy_ai.coalitions.append(stable_coalition)
        
        # Update coalitions at turn 10
        events = self.diplomacy_ai.update_coalitions(10)
        
        # Check for expected events
        self.assertEqual(len(events), 2)  # Should have 2 dissolution events
        
        dissolution_events = [e for e in events if e["type"] == "coalition_dissolved"]
        self.assertEqual(len(dissolution_events), 2)
        
        # Verify only stable coalition remains
        self.assertEqual(len(self.diplomacy_ai.coalitions), 1)
        self.assertEqual(self.diplomacy_ai.coalitions[0].name, "Nordic Trade Alliance")


class TestBudgetPolicy(unittest.TestCase):
    """Test suite for BudgetPolicy class"""
    
    def setUp(self):
        """Set up test environment before each test method"""
        # Create a country profile with economic traits
        self.profile = CountryProfile(
            economic_focus=0.7,
            risk_aversion=0.4,
            debt_tolerance=0.6,
            free_market_belief=0.6
        )
        
        # Create a budget policy
        self.budget_policy = BudgetPolicy()
        
        # Create a mock country for fiscal evaluation
        self.mock_country = MockCountry("DK", "Denmark", "europe", gdp=1000)
        self.mock_country.national_debt = 600  # 60% debt-to-GDP
        self.mock_country.budget_deficit = 30  # 3% deficit-to-GDP
        
        # Add industry data
        self.mock_country.industries = {
            "manufacturing": type('obj', (object,), {
                'efficiency': 0.8,
                'employment_share': 0.3
            }),
            "technology": type('obj', (object,), {
                'efficiency': 0.9,
                'employment_share': 0.2
            }),
            "agriculture": type('obj', (object,), {
                'efficiency': 0.7,
                'employment_share': 0.1
            })
        }
        
        # Add profile to country
        self.mock_country.profile = self.profile
    
    def test_generate_for_country(self):
        """Test generating a budget policy from country profile"""
        economic_data = {
            "gdp": 1000,
            "debt": 600,
            "deficit": 30
        }
        
        policy = BudgetPolicy.generate_for_country(self.profile, economic_data)
        
        # Verify policy was created with appropriate values
        self.assertIsNotNone(policy)
        self.assertTrue(0.01 <= policy.target_deficit_gdp_ratio <= 0.05)
        self.assertTrue(0.05 <= policy.max_deficit_gdp_ratio <= 0.15)
        self.assertTrue(0.3 <= policy.target_debt_gdp_ratio <= 1.0)
        
        # Test that sectoral priorities are normalized and sum to approximately 1.0
        total_priorities = sum(policy.sectoral_priorities.values())
        self.assertAlmostEqual(total_priorities, 1.0, places=5)
    
    def test_update_economic_history(self):
        """Test updating economic history data"""
        initial_length = len(self.budget_policy.gdp_history)
        
        # Add data points
        self.budget_policy.update_economic_history(1000, 30, 600)
        self.budget_policy.update_economic_history(1050, 35, 650)
        
        # Verify data was added
        self.assertEqual(len(self.budget_policy.gdp_history), initial_length + 2)
        self.assertEqual(len(self.budget_policy.deficit_history), initial_length + 2)
        self.assertEqual(len(self.budget_policy.debt_history), initial_length + 2)
        
        # Test limiting to 10 data points
        for i in range(12):
            self.budget_policy.update_economic_history(1000 + i*50, 30 + i, 600 + i*25)
        
        # Should still have only 10 data points
        self.assertEqual(len(self.budget_policy.gdp_history), 10)
        self.assertEqual(len(self.budget_policy.deficit_history), 10)
        self.assertEqual(len(self.budget_policy.debt_history), 10)
    
    def test_calculate_gdp_growth(self):
        """Test calculating GDP growth rate"""
        # Add data points
        self.budget_policy.gdp_history = [1000, 1050]
        growth = self.budget_policy.calculate_gdp_growth()
        
        # Expected growth: (1050-1000)/1000 = 0.05 = 5%
        self.assertAlmostEqual(growth, 0.05)
        
        # Test with insufficient data
        self.budget_policy.gdp_history = [1000]
        growth = self.budget_policy.calculate_gdp_growth()
        self.assertEqual(growth, 0.0)  # Default return value
    
    def test_evaluate_fiscal_situation(self):
        """Test evaluating fiscal situation"""
        # Update economic history first
        self.budget_policy.update_economic_history(950, 28, 550)
        self.budget_policy.update_economic_history(1000, 30, 600)
        
        # Evaluate fiscal situation
        eval_result = self.budget_policy.evaluate_fiscal_situation(self.mock_country)
        
        # Verify result structure
        self.assertIn('fiscal_status', eval_result)
        self.assertIn('policy', eval_result)
        self.assertIn('debt_gdp_ratio', eval_result)
        self.assertIn('deficit_gdp_ratio', eval_result)
        self.assertIn('sectoral_priorities', eval_result)
        
        # Test with critical debt
        self.mock_country.national_debt = 1100  # 110% debt-to-GDP
        eval_critical = self.budget_policy.evaluate_fiscal_situation(self.mock_country)
        self.assertEqual(eval_critical['fiscal_status'], 'critical')
        self.assertEqual(eval_critical['policy'], 'austerity')
    
    def test_calculate_subsidy_allocations(self):
        """Test calculating subsidy allocations"""
        # Calculate subsidy allocations
        available_budget = 100
        allocations = self.budget_policy.calculate_subsidy_allocations(self.mock_country, available_budget)
        
        # Verify result
        self.assertTrue(len(allocations) > 0)
        self.assertEqual(sum(allocations.values()), available_budget)
        
        # Test with country without industries
        country_no_industries = MockCountry("SE", "Sweden", "europe", gdp=1000)
        allocations_generic = self.budget_policy.calculate_subsidy_allocations(country_no_industries, available_budget)
        
        # Should default to generic allocations
        self.assertTrue(len(allocations_generic) > 0)
        self.assertEqual(sum(allocations_generic.values()), available_budget)


class TestCoalitionStrategy(unittest.TestCase):
    """Test suite for CoalitionStrategy class"""
    
    def setUp(self):
        """Set up test environment before each test method"""
        # Create country profile for strategy tests
        self.profile = CountryProfile(
            economic_focus=0.6,
            regional_focus=0.7,
            isolationism=0.3,
            pride=0.6,
            trust_weight=0.4,
            risk_aversion=0.5,
            consistency=0.6,
            aggression=0.4
        )
        
        # Create strategy
        self.strategy = CoalitionStrategy("DK", self.profile)
        
        # Create mock game state with relations
        self.game_state = MockGameState()
        
        # Add mock relations to the game state
        self.set_mock_relations()
    
    def set_mock_relations(self):
        """Set up mock diplomatic relations for testing"""
        # Create a get_relation method for the mock diplomacy
        def get_relation(country_a, country_b):
            # Define Nordic countries relations (positive)
            if country_a in ["DK", "SE", "NO"] and country_b in ["DK", "SE", "NO"]:
                return type('obj', (object,), {
                    'relation_level': 0.7,
                    'trade_volume': 100
                })
            
            # Define relations with Germany (positive)
            elif (country_a in ["DK", "SE", "NO"] and country_b == "DE") or \
                 (country_b in ["DK", "SE", "NO"] and country_a == "DE"):
                return type('obj', (object,), {
                    'relation_level': 0.5,
                    'trade_volume': 150
                })
            
            # Define relations with China (negative for Denmark)
            elif (country_a == "DK" and country_b == "CN") or (country_b == "DK" and country_a == "CN"):
                return type('obj', (object,), {
                    'relation_level': -0.4,
                    'trade_volume': 50
                })
            
            # Define China's relations with others
            elif (country_a == "CN" or country_b == "CN") and \
                 (country_a in ["US", "FR"] or country_b in ["US", "FR"]):
                return type('obj', (object,), {
                    'relation_level': -0.3,
                    'trade_volume': 500
                })
            
            # Default neutral relation
            else:
                return type('obj', (object,), {
                    'relation_level': 0.0,
                    'trade_volume': 10
                })
        
        self.game_state.diplomacy.get_relation = get_relation
    
    def test_initialize_from_profile(self):
        """Test strategy initialization from country profile"""
        # Verify strategy parameters were set based on profile
        self.assertGreater(self.strategy.coalition_preference, 0.5)  # High due to low isolationism
        self.assertEqual(self.strategy.leadership_ambition, self.profile.pride)
        self.assertGreater(self.strategy.strategic_patience, 0.5)  # Based on risk_aversion and consistency
        self.assertLess(self.strategy.loyalty_threshold, 0.5)  # Based on trust_weight
    
    def test_evaluate_potential_coalitions(self):
        """Test evaluating potential coalitions"""
        # Set up existing coalitions to avoid duplicates
        self.game_state.diplomacy.coalitions = []
        
        # Test coalition evaluation
        potential_coalitions = self.strategy.evaluate_potential_coalitions(self.game_state)
        
        # Verify results
        self.assertTrue(len(potential_coalitions) > 0)
        
        # Check that results contain expected fields
        for coalition in potential_coalitions:
            self.assertIn('purpose', coalition)
            self.assertIn('name', coalition)
            self.assertIn('candidates', coalition)
            self.assertIn('evaluation_score', coalition)
    
    def test_trade_partners_identification(self):
        """Test identification of trade partners for coalition"""
        trade_partners = self.strategy._identify_trade_partners(self.game_state)
        
        # Should include countries with positive relations and significant trade
        self.assertIn("SE", trade_partners)
        self.assertIn("NO", trade_partners)
        self.assertIn("DE", trade_partners)
        
        # Should not include countries with negative relations
        self.assertNotIn("CN", trade_partners)
    
    def test_defensive_partners_identification(self):
        """Test identification of defensive partners"""
        defensive_partners = self.strategy._identify_defensive_partners(self.game_state)
        
        # Should include countries that share our rivals (China)
        self.assertTrue(len(defensive_partners) > 0)
        
        # Countries with negative relations with China should be included
        for partner in defensive_partners:
            relation_with_cn = self.game_state.diplomacy.get_relation(partner, "CN")
            if hasattr(relation_with_cn, 'relation_level'):
                self.assertLess(relation_with_cn.relation_level, 0)
    
    def test_regional_partners_identification(self):
        """Test identification of regional partners"""
        regional_partners = self.strategy._identify_regional_partners(self.game_state)
        
        # Should include Nordic countries in same region
        self.assertIn("SE", regional_partners)
        self.assertIn("NO", regional_partners)
        
        # Should not include countries from other regions
        self.assertNotIn("US", regional_partners)
        self.assertNotIn("CN", regional_partners)
    
    def test_calculate_coalition_benefits(self):
        """Test calculation of coalition benefits"""
        members = ["SE", "NO"]
        
        # Test trade coalition benefit
        trade_benefit = self.strategy._calculate_trade_coalition_benefit(members, self.game_state)
        self.assertGreater(trade_benefit, 0.0)
        self.assertLessEqual(trade_benefit, 1.0)
        
        # Test defense coalition benefit
        defense_benefit = self.strategy._calculate_defense_coalition_benefit(members, self.game_state)
        self.assertGreater(defense_benefit, 0.0)
        self.assertLessEqual(defense_benefit, 1.0)
        
        # Test regional coalition benefit
        regional_benefit = self.strategy._calculate_regional_coalition_benefit(members, self.game_state)
        self.assertGreater(regional_benefit, 0.0)
        self.assertLessEqual(regional_benefit, 1.0)
    
    def test_evaluate_existing_coalition(self):
        """Test evaluation of an existing coalition"""
        # Create a test coalition
        coalition = Coalition(
            name="Nordic Alliance",
            purpose="trade",
            founding_countries=["DK", "SE", "NO"],
            formation_turn=5,
            leader_country="SE",
            cohesion_level=0.7
        )
        
        # Test evaluation when we're a member
        evaluation = self.strategy.evaluate_existing_coalition(coalition, self.game_state)
        
        # Verify evaluation structure
        self.assertIn('value', evaluation)
        self.assertIn('action', evaluation)
        self.assertIn('leadership_desire', evaluation)
        
        # Test leadership desire (should want to challenge SE for leadership)
        self.assertGreater(evaluation['leadership_desire'], 0.5)
        
        # Test evaluation when not a member
        strategy_fr = CoalitionStrategy("FR", self.profile)
        eval_nonmember = strategy_fr.evaluate_existing_coalition(coalition, self.game_state)
        self.assertEqual(eval_nonmember['action'], 'not_member')
    
    def test_decide_coalition_action(self):
        """Test deciding on coalition action"""
        # Add existing coalitions to game state
        nordic_coalition = Coalition(
            name="Nordic Alliance",
            purpose="trade",
            founding_countries=["DK", "SE", "NO"],
            formation_turn=5,
            leader_country="SE", 
            cohesion_level=0.7
        )
        
        eu_coalition = Coalition(
            name="EU Cooperation",
            purpose="diplomatic",
            founding_countries=["DE", "FR", "DK"],
            formation_turn=4,
            leader_country="DE",
            cohesion_level=0.6
        )
        
        self.game_state.diplomacy.coalitions = [nordic_coalition, eu_coalition]
        
        # Test decision making
        decision = self.strategy.decide_coalition_action(self.game_state)
        
        # Verify decision structure
        self.assertIn('action', decision)
        self.assertIn('reason', decision)
        
        # Should recommend either challenging leadership or maintaining status quo
        self.assertIn(decision['action'], 
                      ['challenge_leadership', 'recruit_member', 'maintain_status_quo'])
    
    def test_counter_coalition_opportunity(self):
        """Test identifying counter-coalition opportunities"""
        # Create a threatening coalition
        rival_coalition = Coalition(
            name="Pacific Partnership",
            purpose="trade",
            founding_countries=["CN", "JP", "KR"],
            formation_turn=5,
            leader_country="CN",
            cohesion_level=0.8
        )
        
        self.game_state.diplomacy.coalitions = [rival_coalition]
        
        # Test counter opportunity identification
        counter_op = self.strategy._identify_counter_coalition_opportunity(
            self.game_state, self.game_state.diplomacy.coalitions)
        
        # Verify result
        self.assertIsNotNone(counter_op)
        self.assertEqual(counter_op['purpose'], 'counter')
        self.assertIn('candidates', counter_op)
        self.assertIn('target_coalition', counter_op)
        self.assertEqual(counter_op['target_coalition'], rival_coalition)
    
    def test_assess_coalition_members(self):
        """Test assessing coalition members for relationships"""
        # Create a coalition with mixed relationships
        coalition = Coalition(
            name="Mixed Alliance",
            purpose="diplomatic",
            founding_countries=["DK", "SE", "DE", "CN"],
            formation_turn=5,
            leader_country="DK",
            cohesion_level=0.5
        )
        
        # Test member assessment
        assessment = self.strategy._assess_coalition_members(coalition, self.game_state)
        
        # Verify structure
        self.assertIn('problematic', assessment)
        self.assertIn('strong_supporters', assessment)
        
        # CN should be problematic (negative relation with DK)
        self.assertIn("CN", assessment['problematic'])
        
        # SE should be a strong supporter (positive relation with DK)
        self.assertIn("SE", assessment['strong_supporters'])


class TestGameEngineCoalitionIntegration(unittest.TestCase):
    """
    Test integration af koalitionsstrategier med GameEngine
    """
    
    def setUp(self):
        """Set up test environment before each test method"""
        # Opret en GameEngine instans
        self.engine = GameEngine()
        self.engine.current_turn = 1
        
        # Tilføj testlande
        from models import Country
        
        dk = Country(iso_code="DK", name="Danmark", region="northern_europe")
        dk.gdp = 400
        dk.budget_surplus_deficit = -5
        dk.national_debt = 160
        dk.industry_percentage = 25
        dk.agriculture_percentage = 5
        dk.services_percentage = 70
        dk.profile = CountryProfile(
            economic_focus=0.7,
            isolationism=0.3,
            aggression=0.2,
            regional_focus=0.8,
            pride=0.5
        )
        
        se = Country(iso_code="SE", name="Sverige", region="northern_europe")
        se.gdp = 500
        se.budget_surplus_deficit = -3
        se.national_debt = 200
        se.industry_percentage = 30
        se.agriculture_percentage = 3
        se.services_percentage = 67
        se.profile = CountryProfile(
            economic_focus=0.8,
            isolationism=0.2,
            aggression=0.3,
            regional_focus=0.7,
            pride=0.6
        )
        
        no = Country(iso_code="NO", name="Norge", region="northern_europe")
        no.gdp = 600
        no.budget_surplus_deficit = 10  # Olieoverskud
        no.national_debt = 120
        no.industry_percentage = 35
        no.agriculture_percentage = 2
        no.services_percentage = 63
        no.profile = CountryProfile(
            economic_focus=0.9,
            isolationism=0.4,
            aggression=0.1,
            regional_focus=0.7,
            pride=0.5
        )
        
        fi = Country(iso_code="FI", name="Finland", region="northern_europe")
        fi.gdp = 350
        fi.budget_surplus_deficit = -4
        fi.national_debt = 140
        fi.industry_percentage = 28
        fi.agriculture_percentage = 4
        fi.services_percentage = 68
        fi.profile = CountryProfile(
            economic_focus=0.7,
            isolationism=0.3,
            aggression=0.2,
            regional_focus=0.7,
            pride=0.4
        )
        
        de = Country(iso_code="DE", name="Tyskland", region="western_europe")
        de.gdp = 4000
        de.budget_surplus_deficit = 0
        de.national_debt = 2400
        de.industry_percentage = 40
        de.agriculture_percentage = 1
        de.services_percentage = 59
        de.profile = CountryProfile(
            economic_focus=0.6,
            isolationism=0.2,
            aggression=0.4,
            regional_focus=0.5,
            pride=0.7
        )
        
        # Gem lande i GameEngine
        self.engine.countries = {
            "DK": dk,
            "SE": se,
            "NO": no,
            "FI": fi,
            "DE": de
        }
        
        # Initialiser diplomati
        self.engine.initialize_diplomacy()
        
        # Opsæt landerelationer
        self.engine.diplomacy.country_relations = {
            "DK": {
                "SE": {"opinion": 85, "trade_treaty": True},
                "NO": {"opinion": 80, "trade_treaty": True},
                "FI": {"opinion": 75, "trade_treaty": True},
                "DE": {"opinion": 70, "trade_treaty": True}
            },
            "SE": {
                "DK": {"opinion": 85, "trade_treaty": True},
                "NO": {"opinion": 90, "trade_treaty": True},
                "FI": {"opinion": 85, "trade_treaty": True},
                "DE": {"opinion": 65, "trade_treaty": True}
            },
            "NO": {
                "DK": {"opinion": 80, "trade_treaty": True},
                "SE": {"opinion": 90, "trade_treaty": True},
                "FI": {"opinion": 75, "trade_treaty": True},
                "DE": {"opinion": 60, "trade_treaty": True}
            },
            "FI": {
                "DK": {"opinion": 75, "trade_treaty": True},
                "SE": {"opinion": 85, "trade_treaty": True},
                "NO": {"opinion": 75, "trade_treaty": True},
                "DE": {"opinion": 65, "trade_treaty": True}
            },
            "DE": {
                "DK": {"opinion": 70, "trade_treaty": True},
                "SE": {"opinion": 65, "trade_treaty": True},
                "NO": {"opinion": 60, "trade_treaty": True},
                "FI": {"opinion": 65, "trade_treaty": True}
            }
        }
    
    def test_initialize_coalition_strategies(self):
        """Test at koalitionsstrategier initialiseres korrekt for alle lande"""
        # Kontroller at der er strategier for alle lande
        self.assertEqual(len(self.engine.country_strategies), len(self.engine.countries))
        
        # Kontroller at strategierne har de korrekte landekoder
        for country_iso in self.engine.countries:
            self.assertIn(country_iso, self.engine.country_strategies)
            self.assertEqual(self.engine.country_strategies[country_iso].country_iso, country_iso)
            
            # Kontroller at strategiparametrene afspejler landets profil
            profile = self.engine.countries[country_iso].profile
            strategy = self.engine.country_strategies[country_iso]
            
            # Isolationisme har omvendt forhold til koalitionspræference
            if profile.isolationism < 0.5:
                self.assertGreater(strategy.coalition_preference, 0.5)
            else:
                self.assertLessEqual(strategy.coalition_preference, 0.5)
    
    def test_evaluate_coalition_opportunities(self):
        """Test evaluering af koalitionsmuligheder"""
        # Evaluer muligheder for Danmark
        opportunities = self.engine.evaluate_coalition_opportunities("DK")
        
        # Kontroller resultatet
        self.assertIn("DK", opportunities)
        self.assertTrue(len(opportunities["DK"]) > 0)
        
        # Kontroller at mulighederne indeholder de forventede felter
        for opportunity in opportunities["DK"]:
            self.assertIn("purpose", opportunity)
            self.assertIn("name", opportunity)
            self.assertIn("candidates", opportunity)
            self.assertIn("evaluation_score", opportunity)
            
            # Nordiske lande bør være inkluderet i de fleste koalitioner
            candidates = opportunity["candidates"]
            nordic_count = sum(1 for c in ["SE", "NO", "FI"] if c in candidates)
            self.assertGreater(nordic_count, 0, "Koalitionsmuligheder bør inkludere nordiske lande")
    
    def test_coalition_formation_and_dynamics(self):
        """Test dannelse af koalition og dynamik over tid"""
        # 1. Simuler dannelse af nordisk koalition
        result = self.engine.simulate_coalition_negotiations(
            "DK", "trade", ["SE", "NO", "FI"]
        )
        
        # Kontroller at forhandlingen lykkedes
        self.assertTrue(result.get("successful", False), "Nordisk koalition bør dannes succesfuldt")
        
        # 2. Hent koalitionsrapport
        report = self.engine.get_coalition_report("DK")
        
        # Kontroller at koalitionen er aktiv
        self.assertGreater(len(report["active_coalitions"]), 0, "Koalitionen bør være aktiv")
        coalition = report["active_coalitions"][0]
        self.assertEqual(coalition["leader"], "DK", "Danmark bør være leder af koalitionen")
        
        # Gem koalitions-ID til senere
        coalition_id = coalition["id"]
        
        # 3. Simuler koalitionshandling (fælles handelspolitik)
        action_result = self.engine.simulate_coalition_action(
            coalition_id, 
            "joint_trade", 
            target_country="DE",
            details={"trade_boost": 0.1, "tariff_reduction": 0.05}
        )
        
        # Kontroller resultat af handlingen
        self.assertTrue(action_result.get("success", False), "Koalitionshandlingen bør være succesfuld")
        
        # 4. Øg spilrunder og opdater koalitionsdynamik
        self.engine.current_turn = 5
        events = self.engine.update_coalition_dynamics()
        
        # Hent opdateret rapport
        report = self.engine.get_coalition_report("DK")
        
        # Kontroller at koalitionen stadig eksisterer med opdateret samhørighed
        self.assertGreater(len(report["active_coalitions"]), 0, "Koalitionen bør stadig eksistere")
        coalition = report["active_coalitions"][0]
        self.assertGreater(coalition["cohesion"], 0.5, "Koalitionens samhørighed bør være over 0.5")
        
        # 5. Simuler Sverige, der forlader koalitionen
        leave_action = self.engine.simulate_coalition_action(
            coalition_id,
            "member_action",
            target_country="SE",
            details={"action": "leave", "reason": "economic_interests"}
        )
        
        # 6. Kontroller diplomatiske konsekvenser for Sverige
        sweden_report = self.engine.get_coalition_report("SE")
        self.assertGreater(len(sweden_report.get("diplomatic_effects", [])), 0, 
                        "Sverige bør opleve diplomatiske konsekvenser")
    
    def test_diplomatic_consequences(self):
        """Test beregning og anvendelse af diplomatiske konsekvenser"""
        # 1. Opret en koalition
        result = self.engine.simulate_coalition_negotiations(
            "DK", "defense", ["SE", "NO"]
        )
        coalition_id = None
        for c in self.engine.diplomacy.coalitions:
            if c.leader_country == "DK":
                coalition_id = c.id
                break
        
        self.assertIsNotNone(coalition_id, "Koalitionen bør være oprettet")
        
        # 2. Beregn konsekvenser af Tyskland der afviser at tilslutte sig
        # Først tilføj Tyskland som kandidat
        for c in self.engine.diplomacy.coalitions:
            if c.id == coalition_id:
                c.invited_countries = ["DE"]
                break
        
        # Simuler afvisning
        effects = self.engine.diplomatic_consequence.calculate_rejection_consequences(
            "DK", "DE", "defense", self.engine.current_turn
        )
        
        # Kontroller at der er konsekvenser
        self.assertGreater(len(effects), 0, "Der bør være konsekvenser af afvisning")
        
        # 3. Anvend konsekvenserne
        self.engine.diplomatic_consequence.apply_effects(effects, self.engine)
        
        # 4. Kontroller at relationerne er påvirket
        relation = self.engine.diplomacy.country_relations["DK"]["DE"]["opinion"]
        self.assertLess(relation, 70, "Danmarks mening om Tyskland bør være reduceret")
        
        # 5. Simuler koalitionshandling og beregn konsekvenser
        action_result = self.engine.simulate_coalition_action(
            coalition_id,
            "joint_declaration",
            target_country="DE",
            details={"topic": "security", "stance": "critical"}
        )
        
        # Kontroller at handlingen påvirker relationerne yderligere
        relation_after = self.engine.diplomacy.country_relations["DK"]["DE"]["opinion"]
        self.assertLessEqual(relation_after, relation, "Relationerne bør forværres efter kritisk erklæring")

if __name__ == "__main__":
    unittest.main()