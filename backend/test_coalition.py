"""
Test module for Coalition functionality in diplomacy_ai.py

This script tests the Coalition class and coalition-related methods in the DiplomacyAI class.
"""

import unittest
import os
import json
from unittest.mock import MagicMock, patch
from backend.diplomacy_ai import DiplomacyAI, Coalition, DiplomaticPersonality, CountryProfile, BudgetPolicy, CoalitionStrategy
from backend.engine import GameEngine
from backend.models import Country, GameState

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


class TestCoalitionSystem(unittest.TestCase):
    """Test suite for the coalition and alliance system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        data_path = os.path.join(os.path.dirname(__file__), '../data/countries.json')
        cls.engine = GameEngine(data_path)
        cls.game_state = cls.engine.game_state
        # Ensure the coalition system is initialized
        if not hasattr(cls.engine, 'coalition_system'):
            cls.engine.coalition_system = cls.engine.get_system('coalition')
    
    def setUp(self):
        """Set up before each test"""
        # Reset coalitions for testing
        self.game_state.coalitions = []
        
        # Set up some test countries with relations
        self.usa = self.engine.countries['USA']
        self.deu = self.engine.countries['DEU']
        self.fra = self.engine.countries['FRA']
        self.gbr = self.engine.countries['GBR']
        self.chn = self.engine.countries['CHN']
        self.rus = self.engine.countries['RUS']
        
        # Setup friendly relations within Western countries
        for c1, c2 in [('USA', 'DEU'), ('USA', 'FRA'), ('USA', 'GBR'), 
                       ('DEU', 'FRA'), ('DEU', 'GBR'), ('FRA', 'GBR')]:
            if c2 not in self.engine.countries[c1].relations:
                self.engine.countries[c1].relations[c2] = {}
            if c1 not in self.engine.countries[c2].relations:
                self.engine.countries[c2].relations[c1] = {}
                
            self.engine.countries[c1].relations[c2]['opinion'] = 75
            self.engine.countries[c2].relations[c1]['opinion'] = 75
            self.engine.countries[c1].relations[c2]['trade_agreement'] = True
            self.engine.countries[c2].relations[c1]['trade_agreement'] = True
        
        # Setup tense relations between major powers
        for c1, c2 in [('USA', 'CHN'), ('USA', 'RUS'), ('CHN', 'RUS')]:
            if c2 not in self.engine.countries[c1].relations:
                self.engine.countries[c1].relations[c2] = {}
            if c1 not in self.engine.countries[c2].relations:
                self.engine.countries[c2].relations[c1] = {}
                
            self.engine.countries[c1].relations[c2]['opinion'] = 30
            self.engine.countries[c2].relations[c1]['opinion'] = 30
            self.engine.countries[c1].relations[c2]['trade_tension'] = 0.4
            self.engine.countries[c2].relations[c1]['trade_tension'] = 0.4
    
    def test_coalition_formation(self):
        """Test coalition formation based on common interests"""
        # Test creating a coalition
        coalition_data = {
            'name': 'Western Alliance',
            'leader': 'USA',
            'members': ['USA', 'DEU', 'FRA', 'GBR'],
            'focus': 'TRADE',  # Could be TRADE, MILITARY, TECHNOLOGY, etc.
            'formation_date': self.game_state.current_date,
            'status': 'active'
        }
        
        coalition_id = self.engine.coalition_system.create_coalition(coalition_data)
        
        # Verify coalition was created
        self.assertIsNotNone(coalition_id)
        self.assertEqual(len(self.game_state.coalitions), 1)
        
        # Check coalition properties
        coalition = self.game_state.coalitions[0]
        self.assertEqual(coalition['name'], 'Western Alliance')
        self.assertEqual(coalition['leader'], 'USA')
        self.assertEqual(len(coalition['members']), 4)
        self.assertEqual(coalition['focus'], 'TRADE')
        
        # Check automatic fields
        self.assertIn('id', coalition)
        self.assertIn('formation_date', coalition)
        self.assertIn('status', coalition)
        
        # Verify that coalition formation affected country relations
        for member1 in coalition['members']:
            for member2 in coalition['members']:
                if member1 != member2:
                    # Coalition members should have improved relations
                    relation = self.engine.countries[member1].relations[member2]
                    self.assertGreaterEqual(relation['opinion'], 75)  # Should be at least the original value
    
    def test_coalition_membership(self):
        """Test adding and removing members from coalitions"""
        # Create a coalition
        coalition_id = self.engine.coalition_system.create_coalition({
            'name': 'Western Alliance',
            'leader': 'USA',
            'members': ['USA', 'DEU', 'FRA'],
            'focus': 'TRADE'
        })
        
        # Add a new member
        new_member = 'GBR'
        self.engine.coalition_system.add_member_to_coalition(coalition_id, new_member)
        
        # Verify member was added
        coalition = next(c for c in self.game_state.coalitions if c['id'] == coalition_id)
        self.assertIn(new_member, coalition['members'])
        
        # Adding the same member twice should not duplicate
        self.engine.coalition_system.add_member_to_coalition(coalition_id, new_member)
        self.assertEqual(coalition['members'].count(new_member), 1)
        
        # Remove a member
        member_to_remove = 'FRA'
        self.engine.coalition_system.remove_member_from_coalition(coalition_id, member_to_remove)
        
        # Verify member was removed
        self.assertNotIn(member_to_remove, coalition['members'])
        
        # Leader cannot be removed
        with self.assertRaises(Exception):
            self.engine.coalition_system.remove_member_from_coalition(coalition_id, 'USA')
    
    def test_coalition_benefits(self):
        """Test benefits that coalitions provide to members"""
        # Create a trade coalition
        trade_coalition_id = self.engine.coalition_system.create_coalition({
            'name': 'Free Trade Association',
            'leader': 'USA',
            'members': ['USA', 'DEU', 'FRA', 'GBR'],
            'focus': 'TRADE',
            'benefits': {
                'tariff_reduction': 0.5,  # 50% reduction in tariffs
                'market_access_bonus': 0.2,  # 20% bonus to market access
                'trade_growth_multiplier': 1.2  # 20% bonus to trade growth
            }
        })
        
        # Apply coalition benefits
        self.engine.coalition_system.apply_coalition_benefits(self.game_state)
        
        # Check trade benefits between members
        for member1 in ['USA', 'DEU', 'FRA', 'GBR']:
            for member2 in ['USA', 'DEU', 'FRA', 'GBR']:
                if member1 != member2:
                    # Tariffs between members should be reduced
                    country1 = self.engine.countries[member1]
                    if hasattr(country1, 'tariffs') and 'specific' in country1.tariffs:
                        if member2 in country1.tariffs['specific']:
                            self.assertLess(
                                country1.tariffs['specific'][member2],
                                country1.tariffs.get('global', 0.05)  # Compare to global tariff
                            )
        
        # Create a military coalition
        military_coalition_id = self.engine.coalition_system.create_coalition({
            'name': 'Defense Pact',
            'leader': 'RUS',
            'members': ['RUS', 'CHN'],
            'focus': 'MILITARY',
            'benefits': {
                'defense_bonus': 0.15,  # 15% boost to defense
                'military_technology_sharing': True
            }
        })
        
        # Apply coalition benefits
        self.engine.coalition_system.apply_coalition_benefits(self.game_state)
        
        # Check for military benefits
        for member in ['RUS', 'CHN']:
            country = self.engine.countries[member]
            if hasattr(country, 'defense_bonus'):
                self.assertGreater(country.defense_bonus, 0)
    
    def test_coalition_conflicts(self):
        """Test conflict resolution between coalitions"""
        # Create two opposing coalitions
        western_coalition_id = self.engine.coalition_system.create_coalition({
            'name': 'Western Alliance',
            'leader': 'USA',
            'members': ['USA', 'DEU', 'FRA', 'GBR'],
            'focus': 'TRADE',
            'relations': {}  # Will be filled with relations to other coalitions
        })
        
        eastern_coalition_id = self.engine.coalition_system.create_coalition({
            'name': 'Eastern Partnership',
            'leader': 'CHN',
            'members': ['CHN', 'RUS'],
            'focus': 'TRADE',
            'relations': {}
        })
        
        # Set up tension between coalitions
        western_coalition = next(c for c in self.game_state.coalitions if c['id'] == western_coalition_id)
        eastern_coalition = next(c for c in self.game_state.coalitions if c['id'] == eastern_coalition_id)
        
        western_coalition['relations'][eastern_coalition_id] = {
            'opinion': 20,
            'trade_tension': 0.7,
            'status': 'hostile'
        }
        
        eastern_coalition['relations'][western_coalition_id] = {
            'opinion': 20,
            'trade_tension': 0.7,
            'status': 'hostile'
        }
        
        # Simulate a trade conflict
        conflict_data = {
            'type': 'TRADE_WAR',
            'initiator_coalition': western_coalition_id,
            'target_coalition': eastern_coalition_id,
            'intensity': 0.8,
            'duration': 5,  # turns
            'start_turn': self.game_state.current_turn
        }
        
        conflict_id = self.engine.coalition_system.start_coalition_conflict(conflict_data)
        
        # Check that conflict was created
        self.assertIsNotNone(conflict_id)
        self.assertIn('conflicts', self.game_state.__dict__)
        self.assertGreaterEqual(len(self.game_state.conflicts), 1)
        
        # Check that conflict affects country relations
        for west_member in ['USA', 'DEU', 'FRA', 'GBR']:
            for east_member in ['CHN', 'RUS']:
                west_country = self.engine.countries[west_member]
                
                # Trade tension should increase
                self.assertGreater(
                    west_country.relations[east_member]['trade_tension'],
                    0.4  # Original value
                )
    
    def test_coalition_leader_change(self):
        """Test changing coalition leadership"""
        # Create a coalition
        coalition_id = self.engine.coalition_system.create_coalition({
            'name': 'European Union',
            'leader': 'DEU',
            'members': ['DEU', 'FRA', 'GBR'],
            'focus': 'ECONOMIC'
        })
        
        coalition = next(c for c in self.game_state.coalitions if c['id'] == coalition_id)
        
        # Change leadership
        new_leader = 'FRA'
        self.engine.coalition_system.change_coalition_leader(coalition_id, new_leader)
        
        # Verify leader was changed
        self.assertEqual(coalition['leader'], new_leader)
        
        # Attempting to set a non-member as leader should fail
        with self.assertRaises(Exception):
            self.engine.coalition_system.change_coalition_leader(coalition_id, 'USA')
    
    def test_coalition_dissolution(self):
        """Test coalition dissolution conditions"""
        # Create a coalition with tension between members
        coalition_id = self.engine.coalition_system.create_coalition({
            'name': 'Fragile Alliance',
            'leader': 'DEU',
            'members': ['DEU', 'FRA', 'GBR'],
            'focus': 'ECONOMIC',
            'cohesion': 0.5  # Starting cohesion (out of 1.0)
        })
        
        coalition = next(c for c in self.game_state.coalitions if c['id'] == coalition_id)
        
        # Introduce internal tensions
        self.engine.countries['DEU'].relations['FRA']['opinion'] = 30  # Reduced from 75
        self.engine.countries['FRA'].relations['DEU']['opinion'] = 30
        
        # Check stability
        stability = self.engine.coalition_system.calculate_coalition_stability(coalition_id)
        self.assertLess(stability, 0.7)  # Should be unstable
        
        # Decrease cohesion over multiple turns
        for _ in range(3):
            self.engine.coalition_system.update_coalition_cohesion(coalition_id)
        
        # Recalculate stability
        stability = self.engine.coalition_system.calculate_coalition_stability(coalition_id)
        self.assertLess(stability, 0.5)  # Should be even more unstable
        
        # Check if coalition is at risk of dissolution
        at_risk = self.engine.coalition_system.check_dissolution_risk(coalition_id)
        self.assertTrue(at_risk)
        
        # Force dissolution
        self.engine.coalition_system.dissolve_coalition(coalition_id)
        
        # Verify coalition was dissolved
        self.assertEqual(len([c for c in self.game_state.coalitions if c['id'] == coalition_id and c['status'] == 'active']), 0)
    
    def test_coalition_merging(self):
        """Test merging two coalitions"""
        # Create two compatible coalitions
        coalition1_id = self.engine.coalition_system.create_coalition({
            'name': 'Franco-German Alliance',
            'leader': 'DEU',
            'members': ['DEU', 'FRA'],
            'focus': 'ECONOMIC'
        })
        
        coalition2_id = self.engine.coalition_system.create_coalition({
            'name': 'Anglo-American Partnership',
            'leader': 'USA',
            'members': ['USA', 'GBR'],
            'focus': 'ECONOMIC'
        })
        
        # Check compatibility for merger
        compatibility = self.engine.coalition_system.check_merger_compatibility(coalition1_id, coalition2_id)
        self.assertTrue(compatibility > 0.5)  # Should be compatible
        
        # Merge coalitions
        new_coalition_data = {
            'name': 'North Atlantic Alliance',
            'leader': 'USA',  # New leader
            'focus': 'ECONOMIC',
            'benefits': {
                'tariff_reduction': 0.6,
                'market_access_bonus': 0.25
            }
        }
        
        new_coalition_id = self.engine.coalition_system.merge_coalitions(
            coalition1_id, 
            coalition2_id, 
            new_coalition_data
        )
        
        # Verify new coalition was created
        new_coalition = next(c for c in self.game_state.coalitions if c['id'] == new_coalition_id)
        self.assertEqual(new_coalition['name'], 'North Atlantic Alliance')
        self.assertEqual(len(new_coalition['members']), 4)  # All members from both coalitions
        
        # Old coalitions should be inactive
        self.assertEqual(
            len([c for c in self.game_state.coalitions if c['id'] in [coalition1_id, coalition2_id] and c['status'] == 'active']), 
            0
        )
    
    def test_coalition_voting(self):
        """Test coalition voting and decision making"""
        # Create a coalition with voting rules
        coalition_id = self.engine.coalition_system.create_coalition({
            'name': 'Democratic Alliance',
            'leader': 'USA',
            'members': ['USA', 'DEU', 'FRA', 'GBR'],
            'focus': 'POLITICAL',
            'voting_system': {
                'type': 'majority',  # Options: consensus, majority, weighted
                'leader_veto': True,
                'weights': {  # Only used for weighted voting
                    'USA': 5,
                    'DEU': 3,
                    'FRA': 3,
                    'GBR': 2
                }
            }
        })
        
        # Test majority voting
        proposal = {
            'type': 'new_member',
            'content': 'ITA',
            'proposed_by': 'FRA'
        }
        
        # Simulate votes
        votes = {
            'USA': 'yes',
            'DEU': 'yes',
            'FRA': 'yes',
            'GBR': 'no'
        }
        
        result = self.engine.coalition_system.process_coalition_vote(coalition_id, proposal, votes)
        self.assertTrue(result['passed'])
        self.assertEqual(result['yes_votes'], 3)
        self.assertEqual(result['no_votes'], 1)
        
        # Test with leader veto
        votes['USA'] = 'no'  # Leader votes no
        result = self.engine.coalition_system.process_coalition_vote(coalition_id, proposal, votes)
        self.assertFalse(result['passed'])  # Should fail due to leader veto
        
        # Change voting system to weighted
        coalition = next(c for c in self.game_state.coalitions if c['id'] == coalition_id)
        coalition['voting_system']['type'] = 'weighted'
        
        # Test weighted voting
        votes = {
            'USA': 'no',    # 5 votes
            'DEU': 'yes',   # 3 votes
            'FRA': 'yes',   # 3 votes
            'GBR': 'yes'    # 2 votes
        }
        
        result = self.engine.coalition_system.process_coalition_vote(coalition_id, proposal, votes)
        # 8 yes votes vs 5 no votes, but leader (USA) has veto
        self.assertFalse(result['passed'])
        
        # Disable leader veto
        coalition['voting_system']['leader_veto'] = False
        result = self.engine.coalition_system.process_coalition_vote(coalition_id, proposal, votes)
        # Now should pass with 8 yes votes vs 5 no votes
        self.assertTrue(result['passed'])
    
    def test_competing_coalitions(self):
        """Test competition between coalitions for member countries"""
        # Create two competing coalitions
        western_id = self.engine.coalition_system.create_coalition({
            'name': 'Western Alliance',
            'leader': 'USA',
            'members': ['USA', 'GBR'],
            'focus': 'TRADE',
            'benefits': {
                'tariff_reduction': 0.5,
                'market_access_bonus': 0.2
            }
        })
        
        european_id = self.engine.coalition_system.create_coalition({
            'name': 'European Union',
            'leader': 'DEU',
            'members': ['DEU', 'FRA'],
            'focus': 'TRADE',
            'benefits': {
                'tariff_reduction': 0.6,
                'market_access_bonus': 0.3
            }
        })
        
        # Target country to recruit
        target = 'ESP'
        if target not in self.engine.countries:
            # Add Spain if it doesn't exist
            self.engine.countries[target] = Country(target, 'Spain')
            self.engine.countries[target].gdp = 1500000
            self.engine.countries[target].relations = {
                'USA': {'opinion': 65},
                'GBR': {'opinion': 60},
                'DEU': {'opinion': 70},
                'FRA': {'opinion': 75}
            }
        
        # Calculate attraction scores
        western_score = self.engine.coalition_system.calculate_recruitment_score(western_id, target)
        european_score = self.engine.coalition_system.calculate_recruitment_score(european_id, target)
        
        # European Union should be more attractive to Spain
        self.assertGreater(european_score, western_score)
        
        # Attempt recruitment
        recruitment_result = self.engine.coalition_system.recruit_country(european_id, target)
        self.assertTrue(recruitment_result['success'])
        
        # Verify Spain joined the European Union
        european = next(c for c in self.game_state.coalitions if c['id'] == european_id)
        self.assertIn(target, european['members'])
        
        # Attempt to poach from other coalition
        poaching_target = 'GBR'
        poaching_result = self.engine.coalition_system.recruit_country(european_id, poaching_target)
        
        # Success depends on relative coalition strengths and country opinions
        if poaching_result['success']:
            # If successful, GBR should leave Western Alliance and join European Union
            western = next(c for c in self.game_state.coalitions if c['id'] == western_id)
            self.assertNotIn(poaching_target, western['members'])
            self.assertIn(poaching_target, european['members'])

if __name__ == "__main__":
    unittest.main()