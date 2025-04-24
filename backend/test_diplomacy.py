import unittest
import os
import json
from unittest.mock import MagicMock, patch
from backend.diplomacy_ai import DiplomacyAI, DiplomaticRelation, DiplomaticPersonality
from backend.models import GameState, Country
from backend.engine import GameEngine

class TestDiplomacySystem(unittest.TestCase):
    """Test suite for the diplomacy system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        data_path = os.path.join(os.path.dirname(__file__), '../data/countries.json')
        cls.engine = GameEngine(data_path)
        cls.game_state = cls.engine.game_state
        
        # Create diplomacy AI for testing
        cls.diplomacy_ai = DiplomacyAI(cls.game_state)
        
        # Initialize personalities for major countries
        cls.personalities = {
            'USA': DiplomaticPersonality(
                economic_focus=0.7,
                aggression=0.6,
                isolationism=0.3,
                regional_focus=0.5,
                ideological_rigidity=0.6
            ),
            'CHN': DiplomaticPersonality(
                economic_focus=0.8,
                aggression=0.7,
                isolationism=0.4,
                regional_focus=0.6,
                ideological_rigidity=0.8
            ),
            'DEU': DiplomaticPersonality(
                economic_focus=0.8,
                aggression=0.3,
                isolationism=0.2,
                regional_focus=0.7,
                ideological_rigidity=0.5
            ),
            'JPN': DiplomaticPersonality(
                economic_focus=0.7,
                aggression=0.4,
                isolationism=0.5,
                regional_focus=0.6,
                ideological_rigidity=0.5
            )
        }
    
    def setUp(self):
        """Set up before each test"""
        # Ensure country relations are initialized
        if not hasattr(self.diplomacy_ai, 'country_relations'):
            self.diplomacy_ai.country_relations = {}
        
        # Initialize relations between major countries
        countries = ['USA', 'CHN', 'DEU', 'JPN', 'GBR', 'FRA']
        
        # Create initial relations
        for i, country1 in enumerate(countries):
            if country1 not in self.diplomacy_ai.country_relations:
                self.diplomacy_ai.country_relations[country1] = {}
                
            for country2 in countries[i+1:]:
                if country2 not in self.diplomacy_ai.country_relations:
                    self.diplomacy_ai.country_relations[country2] = {}
                
                # Set initial relation level based on predefined geopolitical alignments
                relation_level = self._get_initial_relation(country1, country2)
                
                # Set bilateral relations
                self.diplomacy_ai.country_relations[country1][country2] = {
                    'opinion': relation_level,
                    'trade_deals': [],
                    'trade_volume': self._get_trade_volume(country1, country2),
                    'agreements': []
                }
                
                self.diplomacy_ai.country_relations[country2][country1] = {
                    'opinion': relation_level,
                    'trade_deals': [],
                    'trade_volume': self._get_trade_volume(country2, country1),
                    'agreements': []
                }
    
    def _get_initial_relation(self, country1, country2):
        """Helper to get initial relation level between countries"""
        # Western allies have good relations
        western_allies = ['USA', 'GBR', 'DEU', 'FRA']
        if country1 in western_allies and country2 in western_allies:
            return 75
        
        # USA and China have tense relations
        if (country1 == 'USA' and country2 == 'CHN') or (country1 == 'CHN' and country2 == 'USA'):
            return 30
        
        # China and Japan have tense relations
        if (country1 == 'CHN' and country2 == 'JPN') or (country1 == 'JPN' and country2 == 'CHN'):
            return 25
        
        # Default neutral relations
        return 50
    
    def _get_trade_volume(self, country1, country2):
        """Helper to get initial trade volume between countries"""
        if country1 in self.engine.countries and country2 in self.engine.countries:
            country1_gdp = self.engine.countries[country1].gdp
            country2_gdp = self.engine.countries[country2].gdp
            
            # Simple model: trade volume is proportional to GDP product, scaled by a factor
            trade_scale = 0.0000001
            
            # Adjust for geopolitical factors
            relation_level = self._get_initial_relation(country1, country2)
            relation_boost = relation_level / 50.0  # 1.0 for neutral, higher for friends
            
            return int(country1_gdp * country2_gdp * trade_scale * relation_boost)
        return 1000  # Default value
        
    def test_diplomatic_personality(self):
        """Test diplomatic personality initialization and influence"""
        # Test personality creation
        personality = DiplomaticPersonality(
            economic_focus=0.7,
            aggression=0.5,
            isolationism=0.3,
            regional_focus=0.6,
            ideological_rigidity=0.4
        )
        
        # Test values are set correctly
        self.assertEqual(personality.economic_focus, 0.7)
        self.assertEqual(personality.aggression, 0.5)
        self.assertEqual(personality.isolationism, 0.3)
        
        # Test personality influence on decision making
        proposal = {
            'type': 'trade_deal',
            'benefit': 100,
            'risk': 0.2
        }
        
        # Economic focused personality should prioritize trade deals
        economic_personality = DiplomaticPersonality(economic_focus=0.9, aggression=0.2)
        econ_score = economic_personality.evaluate_proposal(proposal)
        
        # Aggressive personality should be less interested in trade
        aggressive_personality = DiplomaticPersonality(economic_focus=0.3, aggression=0.8)
        aggr_score = aggressive_personality.evaluate_proposal(proposal)
        
        # Economic personality should rate trade deals higher
        self.assertGreater(econ_score, aggr_score)
        
        # Test personality compatibility
        usa_personality = self.personalities['USA']
        deu_personality = self.personalities['DEU']
        chn_personality = self.personalities['CHN']
        
        # Germany and USA should have higher compatibility than China and USA
        usa_deu_compat = usa_personality.get_compatibility(deu_personality)
        usa_chn_compat = usa_personality.get_compatibility(chn_personality)
        
        self.assertGreater(usa_deu_compat, usa_chn_compat)
        
        # Test different proposal types evaluation
        security_proposal = {
            'type': 'defense_pact',
            'benefit': 80,
            'risk': 0.5
        }
        
        # Aggressive personality should prefer security deals over economic ones
        aggr_econ_score = aggressive_personality.evaluate_proposal(proposal)
        aggr_security_score = aggressive_personality.evaluate_proposal(security_proposal)
        self.assertGreater(aggr_security_score, aggr_econ_score)
        
        # Economic personality should prefer economic deals over security ones
        econ_econ_score = economic_personality.evaluate_proposal(proposal)
        econ_security_score = economic_personality.evaluate_proposal(security_proposal)
        self.assertGreater(econ_econ_score, econ_security_score)
        
        # Test high-risk proposal evaluation
        high_risk_proposal = {
            'type': 'joint_military_operation',
            'benefit': 200,
            'risk': 0.8
        }
        
        # Create personalities with different risk tolerances
        risk_averse = DiplomaticPersonality(
            economic_focus=0.5,
            aggression=0.5,
            isolationism=0.5,
            regional_focus=0.5,
            ideological_rigidity=0.5,
            risk_tolerance=0.2  # Very risk-averse
        )
        
        risk_seeking = DiplomaticPersonality(
            economic_focus=0.5,
            aggression=0.5,
            isolationism=0.5,
            regional_focus=0.5,
            ideological_rigidity=0.5,
            risk_tolerance=0.9  # Very risk-seeking
        )
        
        # Risk-seeking personality should value high-risk proposal more
        averse_score = risk_averse.evaluate_proposal(high_risk_proposal)
        seeking_score = risk_seeking.evaluate_proposal(high_risk_proposal)
        self.assertGreater(seeking_score, averse_score)
        
        # Test personality influence on different proposal types
        isolationist = DiplomaticPersonality(isolationism=0.9, regional_focus=0.8)
        globalist = DiplomaticPersonality(isolationism=0.1, regional_focus=0.2)
        
        regional_proposal = {
            'type': 'regional_pact',
            'benefit': 100,
            'risk': 0.3,
            'scope': 'regional'
        }
        
        global_proposal = {
            'type': 'global_pact',
            'benefit': 100,
            'risk': 0.3,
            'scope': 'global'
        }
        
        # Isolationist should prefer regional deals
        iso_regional_score = isolationist.evaluate_proposal(regional_proposal)
        iso_global_score = isolationist.evaluate_proposal(global_proposal)
        self.assertGreater(iso_regional_score, iso_global_score)
        
        # Globalist should prefer global deals
        glob_regional_score = globalist.evaluate_proposal(regional_proposal)
        glob_global_score = globalist.evaluate_proposal(global_proposal)
        self.assertGreater(glob_global_score, glob_regional_score)
        
    def test_diplomatic_personality_edge_cases(self):
        """Test edge cases for diplomatic personality"""
        # Test extreme values
        extreme_personality = DiplomaticPersonality(
            economic_focus=1.0,
            aggression=1.0,
            isolationism=1.0,
            regional_focus=1.0,
            ideological_rigidity=1.0
        )
        
        # Values should be capped at 1.0
        self.assertEqual(extreme_personality.economic_focus, 1.0)
        self.assertEqual(extreme_personality.aggression, 1.0)
        
        # Test minimum values
        min_personality = DiplomaticPersonality(
            economic_focus=0.0,
            aggression=0.0,
            isolationism=0.0,
            regional_focus=0.0,
            ideological_rigidity=0.0
        )
        
        # Values should be floored at 0.0
        self.assertEqual(min_personality.economic_focus, 0.0)
        self.assertEqual(min_personality.aggression, 0.0)
        
        # Test personality creation with invalid values (negative)
        invalid_personality = DiplomaticPersonality(
            economic_focus=-0.5,
            aggression=-0.2
        )
        
        # Values should be clamped to valid range
        self.assertGreaterEqual(invalid_personality.economic_focus, 0.0)
        self.assertGreaterEqual(invalid_personality.aggression, 0.0)
        
        # Test personality creation with invalid values (greater than 1)
        invalid_personality2 = DiplomaticPersonality(
            economic_focus=1.5,
            aggression=1.2
        )
        
        # Values should be clamped to valid range
        self.assertLessEqual(invalid_personality2.economic_focus, 1.0)
        self.assertLessEqual(invalid_personality2.aggression, 1.0)
        
        # Test compatibility with identical personalities
        personality1 = DiplomaticPersonality(
            economic_focus=0.6,
            aggression=0.4,
            isolationism=0.3,
            regional_focus=0.5,
            ideological_rigidity=0.7
        )
        
        personality2 = DiplomaticPersonality(
            economic_focus=0.6,
            aggression=0.4,
            isolationism=0.3,
            regional_focus=0.5,
            ideological_rigidity=0.7
        )
        
        # Identical personalities should have high compatibility
        compat = personality1.get_compatibility(personality2)
        self.assertGreaterEqual(compat, 0.9)
        
        # Test compatibility with opposite personalities
        opposite_personality = DiplomaticPersonality(
            economic_focus=0.4,
            aggression=0.6,
            isolationism=0.7,
            regional_focus=0.5,
            ideological_rigidity=0.3
        )
        
        # Opposite personalities should have low compatibility
        opposite_compat = personality1.get_compatibility(opposite_personality)
        self.assertLessEqual(opposite_compat, 0.5)
        
    def test_diplomatic_personality_proposal_evaluation_edge_cases(self):
        """Test edge cases for diplomatic personality proposal evaluation"""
        # Create a test personality
        personality = DiplomaticPersonality(
            economic_focus=0.6,
            aggression=0.4,
            isolationism=0.3,
            regional_focus=0.5,
            ideological_rigidity=0.6
        )
        
        # Test evaluation of proposal with extremely high benefit
        high_benefit_proposal = {
            'type': 'trade_deal',
            'benefit': 10000,
            'risk': 0.2
        }
        
        high_score = personality.evaluate_proposal(high_benefit_proposal)
        
        # Test evaluation of proposal with extremely low benefit
        low_benefit_proposal = {
            'type': 'trade_deal',
            'benefit': 1,
            'risk': 0.2
        }
        
        low_score = personality.evaluate_proposal(low_benefit_proposal)
        
        # High benefit should get higher score
        self.assertGreater(high_score, low_score)
        
        # Test evaluation of proposal with extremely high risk
        high_risk_proposal = {
            'type': 'trade_deal',
            'benefit': 100,
            'risk': 0.99
        }
        
        # Test evaluation of proposal with extremely low risk
        low_risk_proposal = {
            'type': 'trade_deal',
            'benefit': 100,
            'risk': 0.01
        }
        
        # Low risk should get higher score
        high_risk_score = personality.evaluate_proposal(high_risk_proposal)
        low_risk_score = personality.evaluate_proposal(low_risk_proposal)
        self.assertGreater(low_risk_score, high_risk_score)
        
        # Test proposal with missing fields
        incomplete_proposal = {
            'type': 'trade_deal'
            # Missing benefit and risk
        }
        
        # Should handle gracefully and return a default score
        incomplete_score = personality.evaluate_proposal(incomplete_proposal)
        self.assertIsInstance(incomplete_score, (int, float))
        
        # Test proposal with unknown type
        unknown_proposal = {
            'type': 'unknown_action',
            'benefit': 100,
            'risk': 0.2
        }
        
        # Should handle gracefully and return a reasonable score
        unknown_score = personality.evaluate_proposal(unknown_proposal)
        self.assertIsInstance(unknown_score, (int, float))

    def test_diplomatic_relations(self):
        """Test diplomatic relations between countries"""
        # Test getting relation
        usa_deu_relation = self.diplomacy_ai.get_diplomatic_relation('USA', 'DEU')
        self.assertIsNotNone(usa_deu_relation)
        self.assertIn('opinion', usa_deu_relation)
        
        # Test updating relation
        original_opinion = usa_deu_relation['opinion']
        self.diplomacy_ai.update_diplomatic_relation('USA', 'DEU', {'opinion': original_opinion + 10})
        
        # Check relation was updated
        updated_relation = self.diplomacy_ai.get_diplomatic_relation('USA', 'DEU')
        self.assertEqual(updated_relation['opinion'], original_opinion + 10)
        
        # Test relation bonuses calculation
        usa = self.engine.countries['USA']
        deu = self.engine.countries['DEU']
        
        # Add some trade data for testing
        usa_deu_relation = self.diplomacy_ai.get_diplomatic_relation('USA', 'DEU')
        usa_deu_relation['trade_volume'] = 5000
        
        # Calculate relation bonuses
        bonuses = self.diplomacy_ai.calculate_relation_bonuses('USA', 'DEU')
        
        # Check bonuses structure
        self.assertIn('trade_bonus', bonuses)
        self.assertIn('alliance_bonus', bonuses)
        self.assertIn('ideology_bonus', bonuses)
        
        # Trade bonus should be positive with high trade volume
        self.assertGreater(bonuses['trade_bonus'], 0)
    
    def test_diplomatic_actions(self):
        """Test diplomatic actions between countries"""
        # Test create trade deal
        trade_deal = self.diplomacy_ai.create_trade_deal('USA', 'DEU', {
            'tariff_reduction': 5,
            'duration': 10,
            'sectors': ['technology', 'automotive']
        })
        
        self.assertIsNotNone(trade_deal)
        self.assertEqual(trade_deal['proposing_country'], 'USA')
        self.assertEqual(trade_deal['target_country'], 'DEU')
        self.assertEqual(trade_deal['status'], 'proposed')
        
        # Test accepting a deal
        deal_id = trade_deal['id']
        self.diplomacy_ai.respond_to_deal(deal_id, 'accept')
        
        # Check deal status was updated
        updated_deal = self.diplomacy_ai.get_deal(deal_id)
        self.assertEqual(updated_deal['status'], 'active')
        
        # Check relation was improved
        relation = self.diplomacy_ai.get_diplomatic_relation('USA', 'DEU')
        self.assertGreater(relation['opinion'], 75)  # Starting value was 75
        
        # Test creating a different type of action: sanction
        sanction = self.diplomacy_ai.create_sanction('USA', 'CHN', {
            'intensity': 0.3,
            'sectors': ['electronics'],
            'duration': 5
        })
        
        self.assertIsNotNone(sanction)
        self.assertEqual(sanction['type'], 'sanction')
        self.assertEqual(sanction['proposing_country'], 'USA')
        self.assertEqual(sanction['target_country'], 'CHN')
        
        # Check relation was deteriorated
        relation = self.diplomacy_ai.get_diplomatic_relation('USA', 'CHN')
        self.assertLess(relation['opinion'], 30)  # Starting value was 30
    
    def test_diplomatic_stance(self):
        """Test setting and getting diplomatic stance"""
        # Set a stance
        self.diplomacy_ai.set_diplomatic_stance('USA', 'CHN', 'rivalry')
        
        # Check stance was set
        stance = self.diplomacy_ai.get_diplomatic_stance('USA', 'CHN')
        self.assertEqual(stance, 'rivalry')
        
        # Test that stance affects relation changes
        original_relation = self.diplomacy_ai.get_diplomatic_relation('USA', 'CHN')
        original_opinion = original_relation['opinion']
        
        # With rivalry stance, positive events should have less impact
        self.diplomacy_ai.process_diplomatic_event({
            'type': 'positive',
            'country_a': 'USA',
            'country_b': 'CHN',
            'base_opinion_change': 10
        })
        
        # Check that opinion improved by less than base amount
        new_relation = self.diplomacy_ai.get_diplomatic_relation('USA', 'CHN')
        opinion_change = new_relation['opinion'] - original_opinion
        self.assertLess(opinion_change, 10)
        
        # Set a friendly stance
        self.diplomacy_ai.set_diplomatic_stance('USA', 'DEU', 'friendly')
        
        # With friendly stance, positive events should have more impact
        original_relation = self.diplomacy_ai.get_diplomatic_relation('USA', 'DEU')
        original_opinion = original_relation['opinion']
        
        self.diplomacy_ai.process_diplomatic_event({
            'type': 'positive',
            'country_a': 'USA',
            'country_b': 'DEU',
            'base_opinion_change': 10
        })
        
        # Check that opinion improved by more than base amount
        new_relation = self.diplomacy_ai.get_diplomatic_relation('USA', 'DEU')
        opinion_change = new_relation['opinion'] - original_opinion
        self.assertGreater(opinion_change, 10)
    
    def test_ai_decision_making(self):
        """Test AI diplomatic decision making"""
        # Test proposal evaluation
        proposal = {
            'type': 'trade_deal',
            'proposing_country': 'DEU',
            'target_country': 'USA',
            'details': {
                'tariff_reduction': 5,
                'sectors': ['automotive', 'technology'],
                'duration': 10
            },
            'economic_benefit': 100,
            'relations_benefit': 5
        }
        
        # Test with friendly country (DEU->USA)
        decision = self.diplomacy_ai.evaluate_proposal_ai('USA', proposal)
        
        # Should be likely to accept
        self.assertIn('accept_probability', decision)
        self.assertGreater(decision['accept_probability'], 0.6)
        
        # Test with rival country (CHN->USA)
        proposal['proposing_country'] = 'CHN'
        decision = self.diplomacy_ai.evaluate_proposal_ai('USA', proposal)
        
        # Should be less likely to accept
        self.assertLess(decision['accept_probability'], 0.6)
        
        # Test risk assessment
        risky_proposal = {
            'type': 'defense_pact',
            'proposing_country': 'USA',
            'target_country': 'DEU',
            'details': {
                'mutual_defense': True,
                'duration': 20
            },
            'risk_level': 0.7,
            'economic_benefit': 50,
            'relations_benefit': 15
        }
        
        # Germany (low aggression) should be cautious about defense pacts
        decision = self.diplomacy_ai.evaluate_proposal_ai('DEU', risky_proposal)
        self.assertLess(decision['accept_probability'], 0.5)
        
        # If proposing country is a rival, should be very unlikely to accept
        risky_proposal['proposing_country'] = 'CHN'
        decision = self.diplomacy_ai.evaluate_proposal_ai('DEU', risky_proposal)
        self.assertLess(decision['accept_probability'], 0.2)
    
    def test_diplomatic_events(self):
        """Test diplomatic events generation and processing"""
        # Test generating events based on world state
        events = self.diplomacy_ai.generate_diplomatic_events(self.game_state)
        
        # Should generate at least some events
        self.assertGreater(len(events), 0)
        
        # Process an event
        test_event = {
            'type': 'diplomatic_incident',
            'country_a': 'USA',
            'country_b': 'CHN',
            'severity': 0.5,
            'description': 'Diplomatic tensions over trade policies.',
            'base_opinion_change': -15
        }
        
        original_relation = self.diplomacy_ai.get_diplomatic_relation('USA', 'CHN')
        original_opinion = original_relation['opinion']
        
        # Process the event
        results = self.diplomacy_ai.process_diplomatic_event(test_event)
        
        # Check that event was processed
        self.assertIn('opinion_change', results)
        self.assertIn('prior_opinion', results)
        self.assertIn('new_opinion', results)
        
        # Check that opinion decreased
        new_relation = self.diplomacy_ai.get_diplomatic_relation('USA', 'CHN')
        self.assertLess(new_relation['opinion'], original_opinion)
        
        # Test event that affects multiple countries
        global_event = {
            'type': 'global_summit',
            'host_country': 'DEU',
            'participating_countries': ['USA', 'CHN', 'JPN', 'FRA'],
            'outcome': 'successful',
            'base_opinion_change': 5
        }
        
        # Store original opinions
        original_opinions = {}
        for country1 in global_event['participating_countries']:
            original_opinions[country1] = {}
            for country2 in global_event['participating_countries']:
                if country1 != country2:
                    original_opinions[country1][country2] = self.diplomacy_ai.get_diplomatic_relation(
                        country1, country2)['opinion']
        
        # Process the global event
        self.diplomacy_ai.process_global_diplomatic_event(global_event)
        
        # Check that opinions improved between participating countries
        for country1 in global_event['participating_countries']:
            for country2 in global_event['participating_countries']:
                if country1 != country2:
                    new_opinion = self.diplomacy_ai.get_diplomatic_relation(country1, country2)['opinion']
                    self.assertGreater(new_opinion, original_opinions[country1][country2])
    
    def test_trade_agreement_effects(self):
        """Test the effects of trade agreements on economic metrics"""
        # Create a trade agreement
        agreement = self.diplomacy_ai.create_trade_deal('USA', 'DEU', {
            'tariff_reduction': 8,
            'duration': 10,
            'sectors': ['technology', 'automotive', 'pharmaceuticals']
        })
        
        # Accept the agreement
        deal_id = agreement['id']
        self.diplomacy_ai.respond_to_deal(deal_id, 'accept')
        
        # Get countries and store original values
        usa = self.engine.countries['USA']
        deu = self.engine.countries['DEU']
        
        original_usa_gdp_growth = usa.gdp_growth if hasattr(usa, 'gdp_growth') else 0.02
        original_deu_gdp_growth = deu.gdp_growth if hasattr(deu, 'gdp_growth') else 0.02
        
        # Apply the economic effects
        effects = self.diplomacy_ai.apply_trade_agreement_effects(agreement)
        
        # Check effects structure
        self.assertIn('usa_effects', effects)
        self.assertIn('deu_effects', effects)
        
        # Check that effects are positive
        self.assertGreater(effects['usa_effects']['gdp_growth_impact'], 0)
        self.assertGreater(effects['deu_effects']['gdp_growth_impact'], 0)
        
        # Applied effects should be reflected in country metrics
        self.assertGreater(usa.gdp_growth, original_usa_gdp_growth)
        self.assertGreater(deu.gdp_growth, original_deu_gdp_growth)
        
        # Test canceling agreement
        self.diplomacy_ai.cancel_agreement(deal_id)
        
        # Agreement should be marked as canceled
        updated_deal = self.diplomacy_ai.get_deal(deal_id)
        self.assertEqual(updated_deal['status'], 'canceled')
        
        # Economic effects should be reversed
        self.assertAlmostEqual(usa.gdp_growth, original_usa_gdp_growth, places=6)
        self.assertAlmostEqual(deu.gdp_growth, original_deu_gdp_growth, places=6)
    
    def test_sanctions(self):
        """Test the impact of sanctions on countries"""
        # Create a sanction
        sanction = self.diplomacy_ai.create_sanction('USA', 'CHN', {
            'intensity': 0.5,
            'sectors': ['electronics', 'automotive'],
            'duration': 5
        })
        
        # Get countries and store original values
        chn = self.engine.countries['CHN']
        usa = self.engine.countries['USA']
        
        original_chn_gdp_growth = chn.gdp_growth if hasattr(chn, 'gdp_growth') else 0.06
        original_usa_gdp_growth = usa.gdp_growth if hasattr(usa, 'gdp_growth') else 0.02
        
        # Apply sanction effects
        effects = self.diplomacy_ai.apply_sanction_effects(sanction)
        
        # Check effects structure
        self.assertIn('target_effects', effects)
        self.assertIn('sender_effects', effects)
        
        # Sanctions should harm both countries, but target more
        self.assertLess(effects['target_effects']['gdp_growth_impact'], 0)
        self.assertLess(effects['sender_effects']['gdp_growth_impact'], 0)
        self.assertLess(effects['target_effects']['gdp_growth_impact'], 
                      effects['sender_effects']['gdp_growth_impact'])
        
        # Applied effects should be reflected in country metrics
        self.assertLess(chn.gdp_growth, original_chn_gdp_growth)
        self.assertLess(usa.gdp_growth, original_usa_gdp_growth)
        
        # Test lifting sanctions
        self.diplomacy_ai.lift_sanction(sanction['id'])
        
        # Sanction should be marked as lifted
        updated_sanction = self.diplomacy_ai.get_sanction(sanction['id'])
        self.assertEqual(updated_sanction['status'], 'lifted')
        
        # Economic effects should be reversed
        self.assertAlmostEqual(chn.gdp_growth, original_chn_gdp_growth, places=6)
        self.assertAlmostEqual(usa.gdp_growth, original_usa_gdp_growth, places=6)
    
    def test_alliance_formation(self):
        """Test forming and managing alliances"""
        # Create an alliance
        alliance = self.diplomacy_ai.form_alliance({
            'name': 'Western Defense Alliance',
            'founding_countries': ['USA', 'DEU', 'FRA', 'GBR'],
            'purpose': 'defense',
            'leader': 'USA'
        })
        
        # Check alliance creation
        self.assertIsNotNone(alliance)
        self.assertEqual(alliance['name'], 'Western Defense Alliance')
        self.assertEqual(len(alliance['members']), 4)
        self.assertEqual(alliance['leader'], 'USA')
        
        # Test adding a member
        result = self.diplomacy_ai.add_alliance_member(alliance['id'], 'JPN')
        self.assertTrue(result['success'])
        
        # Check that member was added
        updated_alliance = self.diplomacy_ai.get_alliance(alliance['id'])
        self.assertIn('JPN', updated_alliance['members'])
        
        # Check that relations improved between all members
        for country1 in updated_alliance['members']:
            for country2 in updated_alliance['members']:
                if country1 != country2:
                    relation = self.diplomacy_ai.get_diplomatic_relation(country1, country2)
                    self.assertGreaterEqual(relation['opinion'], 75)  # Should be at least friendly
        
        # Test alliance voting on proposal
        proposal = {
            'type': 'trade_sanction',
            'target_country': 'CHN',
            'proposed_by': 'USA',
            'intensity': 0.4
        }
        
        vote_result = self.diplomacy_ai.alliance_vote(alliance['id'], proposal)
        
        # Check vote result
        self.assertIn('approved', vote_result)
        self.assertIn('votes_for', vote_result)
        self.assertIn('votes_against', vote_result)
        self.assertIn('abstentions', vote_result)
    
    def test_alliance_cohesion(self):
        """Test alliance cohesion over time"""
        # Create an alliance
        alliance = self.diplomacy_ai.form_alliance({
            'name': 'Global Partnership',
            'founding_countries': ['USA', 'JPN', 'DEU'],
            'purpose': 'economic',
            'leader': 'USA',
            'initial_cohesion': 0.8
        })
        
        # Store original cohesion
        original_cohesion = alliance['cohesion']
        
        # Simulate an event that reduces cohesion
        self.diplomacy_ai.update_alliance_cohesion(
            alliance['id'], -0.2, 'Disagreement on trade policy')
        
        # Check cohesion was reduced
        updated_alliance = self.diplomacy_ai.get_alliance(alliance['id'])
        self.assertLess(updated_alliance['cohesion'], original_cohesion)
        
        # Add entries to the alliance history
        self.diplomacy_ai.add_alliance_history_entry(
            alliance['id'], 
            'leadership_conflict', 
            {'challenger': 'DEU', 'outcome': 'failed'}
        )
        
        # Check that history entry was added
        updated_alliance = self.diplomacy_ai.get_alliance(alliance['id'])
        self.assertEqual(len(updated_alliance['history']), 1)
        
        # Test alliance dissolution
        self.diplomacy_ai.dissolve_alliance(alliance['id'], 'Irreconcilable differences')
        
        # Check alliance is marked as dissolved
        updated_alliance = self.diplomacy_ai.get_alliance(alliance['id'])
        self.assertFalse(updated_alliance['active'])
        self.assertEqual(updated_alliance['dissolution_reason'], 'Irreconcilable differences')
    
    def test_diplomatic_ai_turn_processing(self):
        """Test the diplomacy AI processing a game turn"""
        # Set up the game state for the turn
        self.game_state.current_turn = 5
        self.game_state.current_year = 2025
        
        # Process the turn
        actions = self.diplomacy_ai.process_turn(self.game_state)
        
        # Should have generated some diplomatic actions
        self.assertGreater(len(actions), 0)
        
        # Check action structure
        for action in actions:
            self.assertIn('type', action)
            self.assertIn('proposing_country', action)
            
            if action['type'] in ['trade_deal', 'defense_pact', 'sanction']:
                self.assertIn('target_country', action)
            
            if action['type'] == 'trade_deal':
                self.assertIn('details', action)
                self.assertIn('tariff_reduction', action['details'])
            
            if action['type'] == 'sanction':
                self.assertIn('intensity', action['details'])
                self.assertIn('sectors', action['details'])

class TestDiplomacyAPI(unittest.TestCase):
    """Test suite for diplomacy API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        from backend.routes.diplomacy import diplomacy_blueprint
        from flask import Flask
        from unittest.mock import MagicMock
        
        # Create Flask app
        cls.app = Flask(__name__)
        cls.app.register_blueprint(diplomacy_blueprint)
        cls.client = cls.app.test_client()
        
        # Mock diplomacy AI for API tests
        cls.mock_diplomacy_ai = MagicMock()
        
        # Setup mock relations
        cls.mock_diplomacy_ai.get_diplomatic_relation.return_value = {
            'opinion': 75,
            'trade_volume': 5000,
            'trade_deals': [],
            'agreements': []
        }
        
        # Setup mock active deals
        cls.mock_diplomacy_ai.get_active_deals.return_value = [
            {
                'id': 'deal-123',
                'type': 'trade_deal',
                'proposing_country': 'USA',
                'target_country': 'DEU',
                'status': 'active',
                'creation_date': '2025-01-15',
                'details': {
                    'tariff_reduction': 5,
                    'duration': 10
                }
            }
        ]
        
        # Setup mock sanctions
        cls.mock_diplomacy_ai.get_active_sanctions.return_value = [
            {
                'id': 'sanction-456',
                'type': 'sanction',
                'proposing_country': 'USA',
                'target_country': 'CHN',
                'status': 'active',
                'intensity': 0.5,
                'sectors': ['electronics'],
                'creation_date': '2025-02-10'
            }
        ]
        
        # Patch main module to use mock diplomacy AI
        patcher = patch('backend.routes.diplomacy.diplomacy_ai', cls.mock_diplomacy_ai)
        cls.mock_module_diplomacy_ai = patcher.start()
        cls.addClassCleanup(patcher.stop)
    
    def test_get_diplomatic_relations(self):
        """Test GET endpoint for diplomatic relations"""
        # Make request
        response = self.client.get('/api/diplomacy/relations/USA/DEU')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['opinion'], 75)
        
        # Test invalid countries
        response = self.client.get('/api/diplomacy/relations/INVALID/DEU')
        self.assertEqual(response.status_code, 404)
    
    def test_get_country_relations(self):
        """Test GET endpoint for all relations of a country"""
        # Setup mock result
        self.mock_diplomacy_ai.get_country_relations.return_value = {
            'DEU': {'opinion': 75},
            'JPN': {'opinion': 70},
            'CHN': {'opinion': 30}
        }
        
        # Make request
        response = self.client.get('/api/diplomacy/country/USA/relations')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data['DEU']['opinion'], 75)
        
        # Test invalid country
        response = self.client.get('/api/diplomacy/country/INVALID/relations')
        self.assertEqual(response.status_code, 404)
    
    def test_get_active_deals(self):
        """Test GET endpoint for active diplomatic deals"""
        # Make request for all deals
        response = self.client.get('/api/diplomacy/deals')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 'deal-123')
        
        # Make request for country-specific deals
        response = self.client.get('/api/diplomacy/country/USA/deals')
        self.assertEqual(response.status_code, 200)
    
    def test_propose_deal(self):
        """Test POST endpoint for proposing a diplomatic deal"""
        # Setup mock response
        self.mock_diplomacy_ai.create_trade_deal.return_value = {
            'id': 'new-deal-789',
            'type': 'trade_deal',
            'proposing_country': 'USA',
            'target_country': 'JPN',
            'status': 'proposed',
            'details': {
                'tariff_reduction': 10,
                'duration': 8,
                'sectors': ['technology', 'automotive']
            }
        }
        
        # Make request
        request_data = {
            'type': 'trade_deal',
            'target_country': 'JPN',
            'details': {
                'tariff_reduction': 10,
                'duration': 8,
                'sectors': ['technology', 'automotive']
            }
        }
        response = self.client.post(
            '/api/diplomacy/country/USA/deals',
            json=request_data,
            content_type='application/json'
        )
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 'new-deal-789')
        self.assertEqual(data['status'], 'proposed')
        
        # Verify diplomacy AI was called
        self.mock_diplomacy_ai.create_trade_deal.assert_called_with(
            'USA', 'JPN', request_data['details'])
        
        # Test invalid request
        response = self.client.post(
            '/api/diplomacy/country/USA/deals',
            json={'bad_field': 'value'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_respond_to_deal(self):
        """Test PUT endpoint for responding to a diplomatic deal"""
        # Setup mock response
        self.mock_diplomacy_ai.respond_to_deal.return_value = {
            'success': True,
            'deal_id': 'deal-123',
            'new_status': 'active',
            'relation_changes': {
                'USA': {'DEU': 5}
            }
        }
        
        # Make request
        request_data = {
            'response': 'accept',
            'message': 'We accept your generous offer.'
        }
        response = self.client.put(
            '/api/diplomacy/deals/deal-123',
            json=request_data,
            content_type='application/json'
        )
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['new_status'], 'active')
        
        # Verify diplomacy AI was called
        self.mock_diplomacy_ai.respond_to_deal.assert_called_with('deal-123', 'accept')
        
        # Test invalid request
        response = self.client.put(
            '/api/diplomacy/deals/bad-id',
            json={'response': 'invalid'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_get_sanctions(self):
        """Test GET endpoint for sanctions"""
        # Make request
        response = self.client.get('/api/diplomacy/sanctions')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 'sanction-456')
        
        # Make request for country-specific sanctions
        response = self.client.get('/api/diplomacy/country/USA/sanctions')
        self.assertEqual(response.status_code, 200)
    
    def test_create_sanction(self):
        """Test POST endpoint for creating a sanction"""
        # Setup mock response
        self.mock_diplomacy_ai.create_sanction.return_value = {
            'id': 'new-sanction-789',
            'type': 'sanction',
            'proposing_country': 'USA',
            'target_country': 'CHN',
            'status': 'active',
            'intensity': 0.3,
            'sectors': ['automotive'],
            'creation_date': '2025-04-23'
        }
        
        # Make request
        request_data = {
            'target_country': 'CHN',
            'intensity': 0.3,
            'sectors': ['automotive'],
            'duration': 5
        }
        response = self.client.post(
            '/api/diplomacy/country/USA/sanctions',
            json=request_data,
            content_type='application/json'
        )
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 'new-sanction-789')
        
        # Verify diplomacy AI was called
        self.mock_diplomacy_ai.create_sanction.assert_called_with(
            'USA', 'CHN', request_data)
        
        # Test invalid request
        response = self.client.post(
            '/api/diplomacy/country/USA/sanctions',
            json={'bad_field': 'value'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_lift_sanction(self):
        """Test DELETE endpoint for lifting sanctions"""
        # Setup mock response
        self.mock_diplomacy_ai.lift_sanction.return_value = {
            'success': True,
            'sanction_id': 'sanction-456',
            'message': 'Sanction lifted successfully',
            'relation_changes': {
                'USA': {'CHN': 5}
            }
        }
        
        # Make request
        response = self.client.delete('/api/diplomacy/sanctions/sanction-456')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify diplomacy AI was called
        self.mock_diplomacy_ai.lift_sanction.assert_called_with('sanction-456')

if __name__ == "__main__":
    unittest.main()