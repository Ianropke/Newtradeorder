import React, { useState } from 'react';
import './EventFeedPanel.css'; // Antager at vi har en CSS-fil for dette panel

function EventFeedPanel({ events = [], onEventAction }) {
  const [expandedEvents, setExpandedEvents] = useState({});
  
  // Toggle event expansion
  const toggleEventExpansion = (eventId) => {
    setExpandedEvents(prev => ({
      ...prev,
      [eventId]: !prev[eventId]
    }));
  };

  // Map event categories to colors and icons
  const getCategoryStyle = (category) => {
    const styles = {
      'economic': { color: '#4CAF50', icon: '💰' },
      'political': { color: '#2196F3', icon: '🏛️' },
      'environmental': { color: '#8BC34A', icon: '🌍' },
      'technological': { color: '#9C27B0', icon: '🔬' },
      'diplomatic': { color: '#FF9800', icon: '🤝' },
      'social': { color: '#795548', icon: '👥' },
      'default': { color: '#888', icon: 'ℹ️' }
    };
    
    return styles[category] || styles.default;
  };

  // Format effect for readability
  const formatEffect = (effect) => {
    let target = effect.target || 'unknown';
    let attribute = effect.attribute || '';
    let change = effect.change || 0;
    let duration = effect.duration || 1;
    let sign = change >= 0 ? '+' : '';
    
    // Oversæt attributter til brugervenlige navne
    const attributeNames = {
      'growth_rate': 'Vækstrate',
      'approval_rating': 'Tilslutning',
      'unemployment_rate': 'Arbejdsløshed',
      'gdp': 'BNP',
      'output': 'Produktion',
      'price': 'Pris',
      'inflation': 'Inflation',
      'relation_level': 'Diplomatisk relation',
      'productivity_modifier': 'Produktivitet',
      'investment_modifier': 'Investeringer',
      'stability_modifier': 'Stabilitet'
    };
    
    let displayAttribute = attributeNames[attribute] || attribute;
    
    // Format effect based on target type
    if (target === 'country') {
      return `${displayAttribute}: ${sign}${(change * 100).toFixed(1)}% i ${duration} runder`;
    } else if (target === 'sector') {
      let sectorName = effect.sector_name || "ukendt sektor";
      return `${sectorName} ${displayAttribute}: ${sign}${(change * 100).toFixed(1)}% i ${duration} runder`;
    } else if (target === 'relation') {
      return `Diplomatiske relationer: ${sign}${(change * 100).toFixed(1)}% i ${duration} runder`;
    }
    
    return `${target} ${attribute}: ${sign}${change} (${duration} runder)`;
  };

  // Format date and turn info
  const formatTurnInfo = (turn) => {
    return `Runde ${turn}`;
  };

  return (
    <div className="event-feed-panel">
      <h3>Begivenheder</h3>
      {events.length === 0 ? (
        <p className="no-events-message">Ingen begivenheder at vise endnu.</p>
      ) : (
        <div className="events-list">
          {events.map((event) => {
            const isExpanded = expandedEvents[event.event_id] || false;
            const { color, icon } = getCategoryStyle(event.category);
            
            return (
              <div 
                key={event.event_id} 
                className={`event-item ${isExpanded ? 'expanded' : ''}`}
                style={{ borderLeftColor: color }}
              >
                <div 
                  className="event-header" 
                  onClick={() => toggleEventExpansion(event.event_id)}
                >
                  <span className="event-icon">{icon}</span>
                  <span className="event-title">{event.title}</span>
                  <span className="event-turn">{formatTurnInfo(event.turn)}</span>
                  <span className="expand-toggle">{isExpanded ? '▼' : '►'}</span>
                </div>
                
                {isExpanded && (
                  <div className="event-details">
                    <p className="event-description">{event.description}</p>
                    
                    {event.effects && event.effects.length > 0 && (
                      <div className="event-effects">
                        <h4>Effekter:</h4>
                        <ul>
                          {event.effects.map((effect, index) => (
                            <li key={index} className="event-effect">
                              {formatEffect(effect)}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {event.options && event.options.length > 0 && (
                      <div className="event-options">
                        <h4>Valgmuligheder:</h4>
                        {event.options.map((option) => (
                          <button 
                            key={option.id}
                            className="event-option-button"
                            onClick={() => onEventAction(event.event_id, option.id)}
                          >
                            {option.text}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default EventFeedPanel;
