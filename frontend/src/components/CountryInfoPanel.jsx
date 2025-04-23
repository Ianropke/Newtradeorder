import React, { useState } from 'react';

function CountryInfoPanel({ country, loading, onSelectPolicy }) {
  const [showDetails, setShowDetails] = useState(false);
  
  if (loading) return <div className="widget loading-widget">Indlæser...</div>;
  if (!country) return <div className="widget empty-widget">Vælg et land for at se detaljer</div>;
  
  // Calculate economic health indicator (just an example calculation)
  const economicHealth = ((country.gdp || 0) / (country.population || 1)) * 
                        (1 - (country.unemployment_rate || 0) / 100);
  
  // Get appropriate color for indicators
  const getIndicatorColor = (value, type) => {
    if (type === 'approval') {
      if (value > 75) return '#4CAF50'; // Green
      if (value > 50) return '#8BC34A'; // Light green
      if (value > 30) return '#FFC107'; // Amber
      return '#F44336'; // Red
    } else if (type === 'unemployment') {
      if (value < 5) return '#4CAF50'; // Green
      if (value < 8) return '#8BC34A'; // Light green
      if (value < 12) return '#FFC107'; // Amber
      return '#F44336'; // Red
    }
    return '#888'; // Default gray
  };

  return (
    <div className="widget country-info-panel">
      <div className="country-header">
        <h3>{country.name} <span className="country-code">({country.iso_code})</span></h3>
        <div className="country-flag">{country.flag_emoji || '🏳️'}</div>
      </div>
      
      <div className="country-key-stats">
        <div className="stat-item">
          <span className="stat-label">BNP:</span>
          <span className="stat-value">{country.gdp?.toLocaleString() ?? 'N/A'} mio. USD</span>
        </div>
        
        <div className="stat-item">
          <span className="stat-label">Befolkning:</span>
          <span className="stat-value">{country.population?.toLocaleString() ?? 'N/A'}</span>
        </div>
        
        <div className="stat-item indicator">
          <span className="stat-label">Arbejdsløshed:</span>
          <div className="indicator-bar-container">
            <div className="indicator-bar" 
                style={{ 
                  width: `${Math.min(country.unemployment_rate || 0, 20) * 5}%`,
                  backgroundColor: getIndicatorColor(country.unemployment_rate, 'unemployment')
                }} 
            />
            <span className="indicator-value">{country.unemployment_rate?.toFixed(1) ?? 'N/A'}%</span>
          </div>
        </div>
        
        <div className="stat-item indicator">
          <span className="stat-label">Godkendelsesrate:</span>
          <div className="indicator-bar-container">
            <div className="indicator-bar" 
                style={{
                  width: `${country.approval_rating || 0}%`,
                  backgroundColor: getIndicatorColor(country.approval_rating, 'approval')
                }} 
            />
            <span className="indicator-value">{country.approval_rating?.toFixed(1) ?? 'N/A'}%</span>
          </div>
        </div>
      </div>
      
      <div className="country-actions">
        <button 
          className="details-toggle" 
          onClick={() => setShowDetails(!showDetails)}
        >
          {showDetails ? 'Skjul detaljer' : 'Vis flere detaljer'}
        </button>
        
        <button 
          className="policy-button"
          onClick={() => onSelectPolicy && onSelectPolicy(country.iso_code)}
        >
          Håndter politik
        </button>
      </div>
      
      {showDetails && (
        <div className="country-details">
          <div className="details-section">
            <h4>Politik & Økonomi</h4>
            <p><strong>Regeringstype:</strong> {country.government_type || 'N/A'}</p>
            <p><strong>EU-medlem:</strong> {country.is_eu_member ? 'Ja' : 'Nej'}</p>
            <p><strong>Økonomisk sundhed:</strong> {economicHealth.toFixed(2)}</p>
          </div>
          
          {country.major_exports && (
            <div className="details-section">
              <h4>Top Eksportvarer</h4>
              <ul className="export-list">
                {country.major_exports.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          
          {country.trading_partners && (
            <div className="details-section">
              <h4>Handelspartnere</h4>
              <ul className="partners-list">
                {country.trading_partners.map((partner, i) => (
                  <li key={i}>{partner.country}: {partner.volume} mio. USD</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default CountryInfoPanel;
