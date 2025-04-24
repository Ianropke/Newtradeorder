import unittest
import os
import json
from unittest.mock import MagicMock, patch
from backend.models import GameState, Country, Event
from backend.engine import GameEngine
from backend.event_types import EventType

class TestEventSystem(unittest.TestCase):
    """Test suite for the event system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        data_path = os.path.join(os.path.dirname(__file__), '../data/countries.json')
        cls.engine = GameEngine(data_path)
        cls.game_state = cls.engine.game_state
    
    def setUp(self):
        """Set up before each test"""
        # Create a fresh event system for each test
        self.event_system = self.engine.event_system
        
        # Ensure we have some sample events for testing
        self.sample_events = [
            Event(
                id='event-1',
                name='Trade Dispute',
                description='A trade dispute has erupted between countries.',
                type=EventType.TRADE,
                affected_countries=['USA', 'CHN'],
                magnitude=0.6,
                duration=3,
                options=[
                    {
                        'id': 'option-1',
                        'text': 'Negotiate a resolution',
                        'effects': {
                            'relation': 5,
                            'economic': -2
                        }
                    },
                    {
                        'id': 'option-2',
                        'text': 'Impose additional tariffs',
                        'effects': {
                            'relation': -10,
                            'economic': -5,
                            'gdp_impact': -0.01
                        }
                    }
                ]
            ),
            Event(
                id='event-2',
                name='Technological Breakthrough',
                description='A major technological breakthrough has occurred.',
                type=EventType.TECHNOLOGY,
                affected_countries=['USA'],
                magnitude=0.8,
                duration=5,
                options=[
                    {
                        'id': 'option-1',
                        'text': 'Invest heavily in the technology',
                        'effects': {
                            'economic': 10,
                            'gdp_impact': 0.02,
                            'research': 15
                        }
                    },
                    {
                        'id': 'option-2',
                        'text': 'Share the technology with allies',
                        'effects': {
                            'relation': 15,
                            'economic': 5,
                            'research': 5
                        }
                    }
                ]
            ),
            Event(
                id='event-3',
                name='Natural Disaster',
                description='A natural disaster has struck.',
                type=EventType.DISASTER,
                affected_countries=['JPN'],
                magnitude=0.9,
                duration=4,
                options=[
                    {
                        'id': 'option-1',
                        'text': 'Focus on domestic recovery',
                        'effects': {
                            'economic': -5,
                            'stability': -10,
                            'gdp_impact': -0.03
                        }
                    },
                    {
                        'id': 'option-2',
                        'text': 'Request international aid',
                        'effects': {
                            'relation': 5,
                            'economic': -3,
                            'stability': -5,
                            'gdp_impact': -0.02
                        }
                    }
                ]
            )
        ]
        
        # Register the sample events
        for event in self.sample_events:
            self.event_system.register_event(event)
    
    def test_event_registration(self):
        """Test event registration and retrieval"""
        # Test that events were properly registered
        self.assertEqual(len(self.event_system.available_events), 3)
        
        # Test retrieving a specific event
        event = self.event_system.get_event('event-1')
        self.assertIsNotNone(event)
        self.assertEqual(event.name, 'Trade Dispute')
        
        # Test event type
        self.assertEqual(event.type, EventType.TRADE)
        
        # Test registering a new event
        new_event = Event(
            id='event-4',
            name='Political Scandal',
            description='A political scandal has erupted.',
            type=EventType.POLITICAL,
            affected_countries=['DEU'],
            magnitude=0.5,
            duration=2,
            options=[
                {
                    'id': 'option-1',
                    'text': 'Address the scandal directly',
                    'effects': {
                        'stability': -5,
                        'relation': 0
                    }
                },
                {
                    'id': 'option-2',
                    'text': 'Cover up the scandal',
                    'effects': {
                        'stability': -2,
                        'relation': -5
                    }
                }
            ]
        )
        
        self.event_system.register_event(new_event)
        self.assertEqual(len(self.event_system.available_events), 4)
        
        # Test retrieving the new event
        retrieved_event = self.event_system.get_event('event-4')
        self.assertEqual(retrieved_event.name, 'Political Scandal')
    
    def test_event_generation(self):
        """Test event generation based on game state"""
        # Setup game state for testing
        self.game_state.current_turn = 5
        self.game_state.current_year = 2025
        
        # Force trade tension between USA and CHN
        usa = self.engine.countries['USA']
        chn = self.engine.countries['CHN']
        usa.relations['CHN'] = {'opinion': 20, 'trade_tension': 0.7}
        chn.relations['USA'] = {'opinion': 20, 'trade_tension': 0.7}
        
        # Generate events for the turn
        generated_events = self.event_system.generate_events(self.game_state)
        
        # Should have generated at least some events
        self.assertGreater(len(generated_events), 0)
        
        # Check that generated events have all required fields
        for event in generated_events:
            self.assertIsNotNone(event.id)
            self.assertIsNotNone(event.name)
            self.assertIsNotNone(event.description)
            self.assertIsNotNone(event.type)
            self.assertGreater(len(event.affected_countries), 0)
            self.assertGreater(len(event.options), 0)
            
            # Check options structure
            for option in event.options:
                self.assertIn('id', option)
                self.assertIn('text', option)
                self.assertIn('effects', option)
    
    def test_event_probability(self):
        """Test event probability calculation"""
        # Setup game state for testing different scenarios
        self.game_state.current_turn = 5
        
        # Get base probabilities
        base_probs = self.event_system.calculate_event_probabilities(self.game_state)
        
        # Simulate trade war condition
        usa = self.engine.countries['USA']
        chn = self.engine.countries['CHN']
        usa.relations['CHN'] = {'opinion': 10, 'trade_tension': 0.9}
        chn.relations['USA'] = {'opinion': 10, 'trade_tension': 0.9}
        
        # Trade war should increase trade event probability
        trade_war_probs = self.event_system.calculate_event_probabilities(self.game_state)
        self.assertGreater(trade_war_probs[EventType.TRADE], base_probs[EventType.TRADE])
        
        # Simulate economic boom
        for country in self.engine.countries.values():
            country.gdp_growth = 0.07  # Strong growth
        
        # Economic boom should reduce disaster probability
        boom_probs = self.event_system.calculate_event_probabilities(self.game_state)
        self.assertLess(boom_probs[EventType.DISASTER], base_probs[EventType.DISASTER])
        
        # Simulate late game
        self.game_state.current_turn = 20
        
        # Late game should increase political and technology event probability
        late_probs = self.event_system.calculate_event_probabilities(self.game_state)
        self.assertGreater(late_probs[EventType.POLITICAL], base_probs[EventType.POLITICAL])
        self.assertGreater(late_probs[EventType.TECHNOLOGY], base_probs[EventType.TECHNOLOGY])
    
    def test_event_filtering(self):
        """Test event filtering based on game state"""
        # Setup game state for testing
        self.game_state.current_turn = 5
        
        # Modify countries' state to test filtering
        usa = self.engine.countries['USA']
        usa.gdp = 25000000  # Very high GDP
        usa.technology_level = 0.9  # High tech level
        
        jpn = self.engine.countries['JPN']
        jpn.stability = 0.2  # Low stability
        
        # Filter events for USA
        usa_events = self.event_system.filter_events_for_country(
            self.sample_events, 'USA', self.game_state)
        
        # USA has high tech, so should get tech events
        has_tech_event = any(e.type == EventType.TECHNOLOGY for e in usa_events)
        self.assertTrue(has_tech_event)
        
        # Filter events for JPN
        jpn_events = self.event_system.filter_events_for_country(
            self.sample_events, 'JPN', self.game_state)
        
        # JPN has low stability, so should get disaster events
        has_disaster_event = any(e.type == EventType.DISASTER for e in jpn_events)
        self.assertTrue(has_disaster_event)
    
    def test_event_resolution(self):
        """Test event resolution and effects application"""
        # Get a sample event
        event = self.event_system.get_event('event-1')  # Trade Dispute
        
        # Test resolving the event with option 1
        affected_countries = event.affected_countries
        option_id = event.options[0]['id']  # 'Negotiate a resolution'
        
        # Get countries' state before resolution
        usa = self.engine.countries['USA']
        chn = self.engine.countries['CHN']
        usa_original_relation = usa.relations.get('CHN', {}).get('opinion', 50)
        usa_original_econ = usa.economic_strength
        
        # Resolve the event
        resolution_result = self.event_system.resolve_event(
            event.id, option_id, self.game_state)
        
        # Check resolution result
        self.assertTrue(resolution_result['success'])
        self.assertEqual(resolution_result['event_id'], event.id)
        self.assertEqual(resolution_result['option_id'], option_id)
        
        # Check that effects were applied
        self.assertIn('applied_effects', resolution_result)
        applied_effects = resolution_result['applied_effects']
        
        # Option 1 increases relations but decreases economic strength
        self.assertGreater(usa.relations['CHN']['opinion'], usa_original_relation)
        self.assertLess(usa.economic_strength, usa_original_econ)
        
        # Test other effects like GDP impact
        # Get a sample event with GDP impact
        event = self.event_system.get_event('event-3')  # Natural Disaster
        
        # Test resolving the event with option 2
        option_id = event.options[1]['id']  # 'Request international aid'
        
        # Get Japan's original GDP and GDP growth
        jpn = self.engine.countries['JPN']
        original_gdp = jpn.gdp
        original_gdp_growth = jpn.gdp_growth
        
        # Resolve the event
        resolution_result = self.event_system.resolve_event(
            event.id, option_id, self.game_state)
        
        # Check GDP impact was applied
        self.assertLess(jpn.gdp_growth, original_gdp_growth)
    
    def test_event_duration(self):
        """Test handling of events with duration over multiple turns"""
        # Get a sample event with duration
        event = self.event_system.get_event('event-2')  # Technological Breakthrough
        
        # Resolve the event
        option_id = event.options[0]['id']  # 'Invest heavily'
        resolution_result = self.event_system.resolve_event(
            event.id, option_id, self.game_state)
        
        # Check active events
        active_events = self.event_system.get_active_events()
        self.assertGreater(len(active_events), 0)
        
        # The event we just resolved should be in active events
        event_ids = [e['event_id'] for e in active_events]
        self.assertIn(event.id, event_ids)
        
        # Get active event details
        active_event = next(e for e in active_events if e['event_id'] == event.id)
        self.assertEqual(active_event['duration_remaining'], event.duration)
        self.assertEqual(active_event['option_id'], option_id)
        
        # Simulate advancing the game by processing active events
        self.event_system.process_active_events(self.game_state)
        
        # Duration should have decreased
        active_events = self.event_system.get_active_events()
        active_event = next(e for e in active_events if e['event_id'] == event.id)
        self.assertEqual(active_event['duration_remaining'], event.duration - 1)
        
        # Simulate advancing the game to the end of the event's duration
        for _ in range(event.duration - 1):
            self.event_system.process_active_events(self.game_state)
        
        # Event should no longer be active
        active_events = self.event_system.get_active_events()
        self.assertFalse(any(e['event_id'] == event.id for e in active_events))
    
    def test_event_conditions(self):
        """Test event condition checking"""
        # Create a conditional event
        conditional_event = Event(
            id='conditional-event',
            name='Economic Recession',
            description='An economic recession is affecting the country.',
            type=EventType.ECONOMIC,
            affected_countries=['USA'],
            magnitude=0.7,
            duration=4,
            conditions={
                'gdp_growth_below': 0.01,
                'stability_below': 0.6
            },
            options=[
                {
                    'id': 'option-1',
                    'text': 'Implement austerity measures',
                    'effects': {
                        'economic': -5,
                        'stability': -10,
                        'gdp_impact': -0.01
                    }
                },
                {
                    'id': 'option-2',
                    'text': 'Increase government spending',
                    'effects': {
                        'economic': 5,
                        'stability': 5,
                        'gdp_impact': 0.01,
                        'debt_impact': 0.05
                    }
                }
            ]
        )
        
        self.event_system.register_event(conditional_event)
        
        # Test condition not met
        usa = self.engine.countries['USA']
        usa.gdp_growth = 0.03  # Good growth
        usa.stability = 0.8  # High stability
        
        # Event should not be eligible
        is_eligible = self.event_system.check_event_conditions(conditional_event, 'USA', self.game_state)
        self.assertFalse(is_eligible)
        
        # Test condition met
        usa.gdp_growth = 0.005  # Recession
        usa.stability = 0.5  # Low stability
        
        # Event should be eligible
        is_eligible = self.event_system.check_event_conditions(conditional_event, 'USA', self.game_state)
        self.assertTrue(is_eligible)
    
    def test_event_history(self):
        """Test event history tracking"""
        # Clear event history
        self.event_system.event_history = []
        
        # Resolve multiple events
        event_ids = ['event-1', 'event-2', 'event-3']
        
        for event_id in event_ids:
            event = self.event_system.get_event(event_id)
            option_id = event.options[0]['id']
            self.event_system.resolve_event(event_id, option_id, self.game_state)
        
        # Check event history
        history = self.event_system.get_event_history()
        self.assertEqual(len(history), 3)
        
        # Check history structure
        for entry in history:
            self.assertIn('event_id', entry)
            self.assertIn('event_name', entry)
            self.assertIn('turn', entry)
            self.assertIn('resolution', entry)
            self.assertIn('affected_countries', entry)
        
        # Check filter by country
        usa_history = self.event_system.get_event_history_for_country('USA')
        self.assertGreater(len(usa_history), 0)
        
        # All events in USA history should affect USA
        for entry in usa_history:
            self.assertIn('USA', entry['affected_countries'])
        
        # Check filter by turn
        current_turn_history = self.event_system.get_event_history_by_turn(self.game_state.current_turn)
        self.assertEqual(len(current_turn_history), 3)
    
    def test_event_modifiers(self):
        """Test event modifiers on country metrics"""
        # Get a country
        usa = self.engine.countries['USA']
        
        # Store original values
        original_gdp_growth = usa.gdp_growth
        original_stability = usa.stability
        
        # Add event modifiers
        self.event_system.add_country_modifier('USA', {
            'gdp_growth': 0.02,
            'stability': -0.1,
            'duration': 3,
            'source': 'event-2',
            'description': 'Technological investment effects'
        })
        
        # Check modifiers are applied
        modifiers = self.event_system.get_country_modifiers('USA')
        self.assertEqual(len(modifiers), 1)
        
        # Check modifier values
        self.assertEqual(modifiers[0]['gdp_growth'], 0.02)
        self.assertEqual(modifiers[0]['stability'], -0.1)
        self.assertEqual(modifiers[0]['duration'], 3)
        
        # Apply modifiers and check country values
        self.event_system.apply_country_modifiers(self.game_state)
        
        # GDP growth should increase, stability should decrease
        self.assertGreater(usa.gdp_growth, original_gdp_growth)
        self.assertLess(usa.stability, original_stability)
        
        # Advance turns and check duration
        for _ in range(3):
            self.event_system.process_modifiers()
        
        # Modifier should expire after 3 turns
        modifiers = self.event_system.get_country_modifiers('USA')
        self.assertEqual(len(modifiers), 0)
        
        # Country values should revert to normal
        self.event_system.apply_country_modifiers(self.game_state)
        self.assertAlmostEqual(usa.gdp_growth, original_gdp_growth, places=6)
        self.assertAlmostEqual(usa.stability, original_stability, places=6)
    
    def test_event_option_requirements(self):
        """Test event option requirements"""
        # Create an event with option requirements
        event_with_reqs = Event(
            id='event-with-reqs',
            name='Diplomatic Summit',
            description='A diplomatic summit has been called.',
            type=EventType.POLITICAL,
            affected_countries=['USA', 'CHN', 'RUS'],
            magnitude=0.7,
            duration=2,
            options=[
                {
                    'id': 'option-1',
                    'text': 'Lead the summit',
                    'effects': {
                        'relation': 10,
                        'influence': 15
                    },
                    'requirements': {
                        'gdp_above': 20000000,
                        'stability_above': 0.6,
                        'relations_above': {'CHN': 30}
                    }
                },
                {
                    'id': 'option-2',
                    'text': 'Send a delegation',
                    'effects': {
                        'relation': 5,
                        'influence': 5
                    }
                }
            ]
        )
        
        self.event_system.register_event(event_with_reqs)
        
        # Set USA metrics to not meet requirements
        usa = self.engine.countries['USA']
        usa.gdp = 15000000
        usa.stability = 0.5
        usa.relations['CHN'] = {'opinion': 20}
        
        # Get available options
        available_options = self.event_system.get_available_options(
            'event-with-reqs', 'USA', self.game_state)
        
        # USA should only have option 2 available
        self.assertEqual(len(available_options), 1)
        self.assertEqual(available_options[0]['id'], 'option-2')
        
        # Update USA metrics to meet requirements
        usa.gdp = 25000000
        usa.stability = 0.7
        usa.relations['CHN'] = {'opinion': 40}
        
        # Now both options should be available
        available_options = self.event_system.get_available_options(
            'event-with-reqs', 'USA', self.game_state)
        self.assertEqual(len(available_options), 2)
    
    def test_event_chaining(self):
        """Test event chaining based on previous resolutions"""
        # Create a chain of events
        initial_event = Event(
            id='initial-event',
            name='Border Dispute',
            description='A border dispute has erupted.',
            type=EventType.POLITICAL,
            affected_countries=['DEU', 'FRA'],
            magnitude=0.6,
            duration=2,
            options=[
                {
                    'id': 'option-1',
                    'text': 'Negotiate peacefully',
                    'effects': {
                        'relation': 5,
                        'stability': 0
                    },
                    'next_event': 'follow-up-peaceful'
                },
                {
                    'id': 'option-2',
                    'text': 'Take a hard stance',
                    'effects': {
                        'relation': -10,
                        'stability': -5
                    },
                    'next_event': 'follow-up-conflict'
                }
            ]
        )
        
        peaceful_follow_up = Event(
            id='follow-up-peaceful',
            name='Diplomatic Resolution',
            description='The border dispute is being resolved diplomatically.',
            type=EventType.POLITICAL,
            affected_countries=['DEU', 'FRA'],
            magnitude=0.4,
            duration=1,
            options=[
                {
                    'id': 'option-1',
                    'text': 'Commit to a partnership',
                    'effects': {
                        'relation': 15,
                        'trade_bonus': 0.05
                    }
                },
                {
                    'id': 'option-2',
                    'text': 'Maintain status quo',
                    'effects': {
                        'relation': 5
                    }
                }
            ]
        )
        
        conflict_follow_up = Event(
            id='follow-up-conflict',
            name='Escalating Tensions',
            description='The border dispute is escalating.',
            type=EventType.POLITICAL,
            affected_countries=['DEU', 'FRA'],
            magnitude=0.7,
            duration=3,
            options=[
                {
                    'id': 'option-1',
                    'text': 'Seek international mediation',
                    'effects': {
                        'relation': 0,
                        'stability': -5
                    }
                },
                {
                    'id': 'option-2',
                    'text': 'Impose economic sanctions',
                    'effects': {
                        'relation': -20,
                        'economic': -10,
                        'stability': -10
                    }
                }
            ]
        )
        
        self.event_system.register_event(initial_event)
        self.event_system.register_event(peaceful_follow_up)
        self.event_system.register_event(conflict_follow_up)
        
        # Resolve initial event with peaceful option
        resolution_result = self.event_system.resolve_event(
            'initial-event', 'option-1', self.game_state)
        
        # Check that the next event is queued
        queued_events = self.event_system.get_queued_events()
        self.assertEqual(len(queued_events), 1)
        self.assertEqual(queued_events[0]['event_id'], 'follow-up-peaceful')
        
        # Process queued events
        new_events = self.event_system.process_queued_events(self.game_state)
        
        # New event should be activated
        self.assertEqual(len(new_events), 1)
        self.assertEqual(new_events[0].id, 'follow-up-peaceful')
        
        # Clear events and test conflict option
        self.event_system.queued_events = []
        
        # Resolve initial event with conflict option
        resolution_result = self.event_system.resolve_event(
            'initial-event', 'option-2', self.game_state)
        
        # Check that the different next event is queued
        queued_events = self.event_system.get_queued_events()
        self.assertEqual(len(queued_events), 1)
        self.assertEqual(queued_events[0]['event_id'], 'follow-up-conflict')

class TestEventAPI(unittest.TestCase):
    """Test suite for event API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        from backend.routes.events import events_blueprint
        from flask import Flask
        from unittest.mock import MagicMock
        
        # Create Flask app
        cls.app = Flask(__name__)
        cls.app.register_blueprint(events_blueprint)
        cls.client = cls.app.test_client()
        
        # Mock event system for API tests
        cls.mock_event_system = MagicMock()
        
        # Setup mock events
        cls.mock_event_system.get_events_for_country.return_value = [
            {
                'id': 'event-1',
                'name': 'Trade Dispute',
                'description': 'A trade dispute has erupted between countries.',
                'type': 'TRADE',
                'affected_countries': ['USA', 'CHN'],
                'magnitude': 0.6,
                'options': [
                    {
                        'id': 'option-1',
                        'text': 'Negotiate a resolution'
                    },
                    {
                        'id': 'option-2',
                        'text': 'Impose additional tariffs'
                    }
                ]
            }
        ]
        
        # Setup mock event history
        cls.mock_event_system.get_event_history_for_country.return_value = [
            {
                'event_id': 'event-2',
                'event_name': 'Technological Breakthrough',
                'turn': 3,
                'resolution': 'option-1',
                'affected_countries': ['USA'],
                'date': '2025-02-15'
            }
        ]
        
        # Setup mock event resolution
        cls.mock_event_system.resolve_event.return_value = {
            'success': True,
            'event_id': 'event-1',
            'option_id': 'option-1',
            'applied_effects': {
                'relation': 5,
                'economic': -2
            }
        }
        
        # Patch main module to use mock event system
        patcher = patch('backend.routes.events.event_system', cls.mock_event_system)
        cls.mock_module_event_system = patcher.start()
        cls.addClassCleanup(patcher.stop)
    
    def test_get_events(self):
        """Test GET endpoint for current events"""
        # Make request
        response = self.client.get('/api/events')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        
        # Make request for country events
        response = self.client.get('/api/events/country/USA')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 'event-1')
    
    def test_get_event_history(self):
        """Test GET endpoint for event history"""
        # Make request for all event history
        response = self.client.get('/api/events/history')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        
        # Make request for country event history
        response = self.client.get('/api/events/history/country/USA')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['event_id'], 'event-2')
    
    def test_resolve_event(self):
        """Test POST endpoint for resolving an event"""
        # Make request
        request_data = {
            'option_id': 'option-1'
        }
        response = self.client.post(
            '/api/events/resolve/event-1',
            json=request_data,
            content_type='application/json'
        )
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['event_id'], 'event-1')
        self.assertEqual(data['option_id'], 'option-1')
        
        # Verify event system was called
        self.mock_event_system.resolve_event.assert_called_with(
            'event-1', 'option-1', self.mock_event_system.game_state)
        
        # Test invalid request
        response = self.client.post(
            '/api/events/resolve/bad-id',
            json={'option_id': 'invalid'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_get_active_events(self):
        """Test GET endpoint for active events"""
        # Setup mock active events
        self.mock_event_system.get_active_events.return_value = [
            {
                'event_id': 'event-2',
                'option_id': 'option-1',
                'start_turn': 3,
                'duration_remaining': 2,
                'affected_countries': ['USA']
            }
        ]
        
        # Make request
        response = self.client.get('/api/events/active')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['event_id'], 'event-2')
        
        # Make request for country active events
        response = self.client.get('/api/events/active/country/USA')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
    
    def test_get_event_effects(self):
        """Test GET endpoint for viewing potential event effects"""
        # Setup mock event effects
        self.mock_event_system.get_option_effects.return_value = {
            'relation': 5,
            'economic': -2,
            'gdp_impact': 0,
            'stability': 0,
            'description': 'Improves relations but has a small economic cost.'
        }
        
        # Make request
        response = self.client.get('/api/events/event-1/option-1/effects/USA')
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['relation'], 5)
        self.assertEqual(data['economic'], -2)
        
        # Verify event system was called
        self.mock_event_system.get_option_effects.assert_called_with(
            'event-1', 'option-1', 'USA', self.mock_event_system.game_state)

if __name__ == "__main__":
    unittest.main()