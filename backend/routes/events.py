from flask import Blueprint, jsonify, request
import uuid
import event_types

events_bp = Blueprint('events', __name__)
event_system = None  # Will be initialized in main.py

@events_bp.route('/events', methods=['GET'])
def get_events():
    """Get all active events or filter by country"""
    country_iso = request.args.get('country')
    include_resolved = request.args.get('include_resolved', 'false').lower() == 'true'
    
    events = []
    
    if event_system:
        if country_iso:
            # Get events for specific country
            events = event_system.get_events_for_country(country_iso, include_resolved)
        else:
            # Get all events
            events = event_system.events
            if include_resolved:
                events = events + event_system.event_history
    
    return jsonify({
        'events': [event if isinstance(event, dict) else event.to_dict() for event in events]
    })

@events_bp.route('/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get details for a specific event"""
    if not event_system:
        return jsonify({'error': 'Event system not initialized'}), 500
        
    # Search in active events
    for event in event_system.events:
        if isinstance(event, dict) and event.get('event_id') == event_id:
            return jsonify(event)
        elif hasattr(event, 'event_id') and event.event_id == event_id:
            return jsonify(event.to_dict())
    
    # Search in event history
    for event in event_system.event_history:
        if isinstance(event, dict) and event.get('event_id') == event_id:
            return jsonify(event)
        elif hasattr(event, 'event_id') and event.event_id == event_id:
            return jsonify(event.to_dict())
    
    return jsonify({'error': 'Event not found'}), 404

@events_bp.route('/events', methods=['POST'])
def create_event():
    """Create a new event manually (typically used for testing or scripted scenarios)"""
    data = request.json
    
    # Validate required fields
    required_fields = ['event_type', 'title', 'description', 'affected_countries']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create event ID if not provided
    if 'event_id' not in data:
        data['event_id'] = str(uuid.uuid4())
    
    # Add the event to the system
    if event_system:
        event_system.add_event(data)
    
    return jsonify({
        'message': 'Event created successfully',
        'event': data
    }), 201

@events_bp.route('/events/<event_id>/resolve', methods=['POST'])
def resolve_event(event_id):
    """Resolve an event with a chosen option and apply its effects"""
    data = request.json or {}
    option_id = data.get('option_id')
    
    # Get game state reference from main app
    from main import game_state, game_engine
    
    # Find the event
    event = None
    for e in event_system.events:
        event_id_value = e.get('event_id') if isinstance(e, dict) else getattr(e, 'event_id', None)
        if event_id_value == event_id:
            event = e
            break
    
    if not event:
        return jsonify({'error': 'Event not found or already resolved'}), 404
    
    # Process AI responses to this event
    ai_responses = {}
    if hasattr(game_state, 'diplomacy') and hasattr(game_state.diplomacy, 'ai'):
        # Get affected countries that aren't the player
        affected_countries = event.get('affected_countries', []) if isinstance(event, dict) else getattr(event, 'affected_countries', [])
        player_country = getattr(game_state, 'player_country_iso', None)
        
        for country_iso in affected_countries:
            if country_iso != player_country:
                # Generate AI response for this country
                ai_profile = game_state.diplomacy.ai.country_personalities.get(country_iso)
                if ai_profile:
                    reaction = None
                    if hasattr(ai_profile, 'react_to_event'):
                        reaction = ai_profile.react_to_event(event)
                    ai_responses[country_iso] = {
                        'reaction': reaction or ["Landet følger udviklingen."],
                        'opinion_change': -0.05 if option_id == 'decline' else 0.05 # Simple example
                    }
    
    # Apply event effects based on chosen option
    effects_applied = []
    if option_id and event_system:
        if isinstance(event, dict):
            # Handle dict-style events
            for option in event.get('options', []):
                if option.get('id') == option_id:
                    effects = option.get('effects', [])
                    # Mark as resolved
                    event['is_resolved'] = True
                    event['resolution_option'] = option_id
                    event['resolution_effects'] = effects
                    
                    # Apply effects through game engine
                    for effect in effects:
                        game_engine._apply_event_effects([event])
                        effects_applied.append(effect)
        else:
            # Handle class-style events
            event_system.apply_event_effects(event, game_state, option_id)
    
    # Convert event to dict for response if it isn't already
    event_dict = event if isinstance(event, dict) else event.to_dict()
    
    return jsonify({
        'message': 'Event resolved successfully',
        'event': event_dict,
        'effects_applied': effects_applied,
        'ai_responses': ai_responses
    })

@events_bp.route('/events/generate', methods=['POST'])
def generate_event():
    """
    Manually trigger event generation (normally happens automatically each turn)
    Used primarily for testing.
    """
    from main import game_state
    
    data = request.json or {}
    turn = data.get('turn', game_state.current_turn or 1)
    
    # Use our new event generation system
    new_events = event_types.check_and_trigger_events(game_state)
    
    if not new_events:
        return jsonify({'message': 'No events generated this time'}), 200
    
    # Add all generated events
    if event_system:
        for event in new_events:
            event_system.add_event(event)
    
    return jsonify({
        'message': f'{len(new_events)} events generated successfully',
        'events': new_events
    }), 201

@events_bp.route('/events/history', methods=['GET'])
def get_event_history():
    """Get historical events"""
    country_iso = request.args.get('country')
    
    history = []
    if event_system:
        if country_iso:
            # Filter history by country
            history = []
            for event in event_system.event_history:
                affected = (event.get('affected_countries', []) if isinstance(event, dict) 
                           else getattr(event, 'affected_countries', []))
                if country_iso in affected:
                    history.append(event if isinstance(event, dict) else event.to_dict())
        else:
            history = [event if isinstance(event, dict) else event.to_dict() 
                      for event in event_system.event_history]
    
    return jsonify({
        'history': history
    })

@events_bp.route('/events/ai-response/<event_id>', methods=['GET'])
def get_ai_response(event_id):
    """Get AI country responses to a specific event"""
    from main import game_state
    
    # Find the event
    event = None
    if event_system:
        for e in event_system.events + event_system.event_history:
            event_id_value = e.get('event_id') if isinstance(e, dict) else getattr(e, 'event_id', None)
            if event_id_value == event_id:
                event = e
                break
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Get AI responses for affected countries
    ai_responses = {}
    if hasattr(game_state, 'diplomacy') and hasattr(game_state.diplomacy, 'ai'):
        affected_countries = event.get('affected_countries', []) if isinstance(event, dict) else getattr(event, 'affected_countries', [])
        player_country = getattr(game_state, 'player_country_iso', None)
        
        for country_iso in affected_countries:
            if country_iso != player_country:
                # Generate AI response
                ai_profile = game_state.diplomacy.ai.country_personalities.get(country_iso)
                if ai_profile:
                    reaction = None
                    if hasattr(ai_profile, 'react_to_event'):
                        reaction = ai_profile.react_to_event(event)
                    ai_responses[country_iso] = {
                        'country_name': game_state.countries[country_iso].name if country_iso in game_state.countries else country_iso,
                        'reaction': reaction or ["Landet følger udviklingen."]
                    }
    
    return jsonify({
        'event_id': event_id,
        'ai_responses': ai_responses
    })