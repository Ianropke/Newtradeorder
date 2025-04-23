import React, { useState, useEffect } from 'react';
import './PolicyPanel.css'; // Adding CSS import

function PolicyPanel({ iso, targetCountry, policyRanges, onAction }) {
  const [policy, setPolicy] = useState('');
  const [value, setValue] = useState('');
  const [appliesTo, setAppliesTo] = useState('all');
  const [showGuidelines, setShowGuidelines] = useState(false);
  const [feedback, setFeedback] = useState(null);
  
  // Reset værdi ved politikændring
  useEffect(() => {
    setValue('');
  }, [policy]);
  
  // Reset appliesTo når targetCountry ændres
  useEffect(() => {
    if (targetCountry) {
      setAppliesTo('target');
    }
  }, [targetCountry]);
  
  const handleSubmit = async e => {
    e.preventDefault();
    if (!policy) return;
    
    try {
      // Konstruer policy-objekt
      const policyObj = { 
        type: policy,
        value: Number(value),
        target: appliesTo === 'target' ? targetCountry : 'all'
      };
      
      // Vis visuel feedback under API-kald
      setFeedback({ type: 'loading', message: 'Anvender politik...' });
      
      const res = await fetch(`/api/policy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          iso_code: iso,
          policy: { [policy]: policyObj }
        })
      });
      
      if (res.ok) {
        const data = await res.json();
        
        // Feedback baseret på politiktypen
        let message;
        let feedbackType = 'success';
        const currentRange = policyRanges[policy] || {};
        
        if (policy === 'tariff') {
          const targetText = appliesTo === 'target' ? ` mod ${targetCountry}` : ' (mod alle lande)';
          if (Number(value) > (currentRange.normal * 1.5)) {
            message = `Høj told på ${value}%${targetText} indført. Dette kan starte en handelskrig!`;
            feedbackType = 'warning';
          } else {
            message = `Told ændret til ${value}%${targetText}`;
          }
        } else if (policy === 'tax') {
          if (Number(value) > currentRange.normal + 10) {
            message = `Høj skat på ${value}% indført. Dette vil påvirke din popularitet negativt.`;
            feedbackType = 'warning';
          } else if (Number(value) < currentRange.normal - 10) {
            message = `Lav skat på ${value}% indført. Dette vil reducere statsindtægter.`;
            feedbackType = 'warning';
          } else {
            message = `Skat ændret til ${value}%`;
          }
        } else if (policy === 'subsidy') {
          if (Number(value) > currentRange.normal + 5) {
            message = `Høj subsidie på ${value}% indført. Dette er dyrt for statskassen.`;
            feedbackType = 'warning';
          } else {
            message = `Subsidie ændret til ${value}%`;
          }
        } else {
          message = `Politik ændret: ${policy} → ${value}`;
        }
        
        // Vis visuel feedback
        setFeedback({ type: feedbackType, message });
        
        // Gem besked i hændelseslog
        onAction(feed => [{ text: message, ts: new Date().toLocaleTimeString() }, ...feed.slice(0, 9)]);
        
        // Reset form efter succesfuldt API-kald
        setTimeout(() => {
          setPolicy(''); 
          setValue('');
          setAppliesTo('all');
          setFeedback(null);
        }, 3000);
      } else {
        const errorData = await res.text();
        console.error("Policy fejl:", errorData);
        setFeedback({ type: 'error', message: `Fejl ved policy-ændring: ${res.status}` });
        onAction(feed => [{ text: `Fejl ved policy-ændring: ${res.status}`, ts: new Date().toLocaleTimeString() }, ...feed.slice(0, 9)]);
      }
    } catch (error) {
      console.error("Policy fejl:", error);
      setFeedback({ type: 'error', message: `Fejl ved policy-ændring: ${error.message}` });
      onAction(feed => [{ text: `Fejl ved policy-ændring: ${error.message}`, ts: new Date().toLocaleTimeString() }, ...feed.slice(0, 9)]);
    }
  };
  
  // Få den aktuelle politiks anbefalede værdier
  const getCurrentRange = () => {
    if (!policy || !policyRanges[policy]) return null;
    return policyRanges[policy];
  };
  
  const currentRange = getCurrentRange();
  
  // Beregn risiko-niveau baseret på værdien
  const calculateRiskLevel = () => {
    if (!policy || !currentRange || !value) return 'normal';
    
    const numValue = Number(value);
    if (policy === 'tariff') {
      if (numValue > currentRange.normal * 1.5) return 'high';
      if (numValue > currentRange.normal * 1.2) return 'medium';
    } else if (policy === 'tax') {
      if (numValue > currentRange.normal + 10) return 'high';
      if (numValue < currentRange.normal - 10) return 'medium';
    } else if (policy === 'subsidy') {
      if (numValue > currentRange.normal + 5) return 'high';
      if (numValue > currentRange.normal + 2) return 'medium';
    }
    return 'normal';
  };
  
  const riskLevel = calculateRiskLevel();
  
  return (
    <div className="widget policy-panel">
      <h3>Ændr politik</h3>
      
      {feedback && (
        <div className={`policy-feedback policy-feedback-${feedback.type}`}>
          {feedback.message}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="policy-controls">
          <div className="policy-selection">
            <select 
              value={policy} 
              onChange={e => setPolicy(e.target.value)} 
              required
              className="policy-dropdown"
            >
              <option value="">Vælg politik</option>
              <option value="tariff">Told</option>
              <option value="tax">Skat</option>
              <option value="subsidy">Subsidie</option>
            </select>
            
            {policy === 'tariff' && (
              <select 
                value={appliesTo} 
                onChange={e => setAppliesTo(e.target.value)}
                className="policy-target"
              >
                <option value="all">Alle lande</option>
                {targetCountry && <option value="target">Målrettet mod {targetCountry}</option>}
              </select>
            )}
          </div>
          
          <div className="policy-value-container">
            {currentRange && (
              <div className="range-info">
                <div className="range-slider">
                  <span className="range-min">{currentRange.min}</span>
                  <div className="slider-track">
                    <div 
                      className="normal-zone" 
                      style={{
                        left: `${(currentRange.normal - currentRange.min) / (currentRange.max - currentRange.min) * 100 - 10}%`,
                        width: '20%'
                      }}
                    ></div>
                  </div>
                  <span className="range-max">{currentRange.max}</span>
                </div>
                <input 
                  type="range" 
                  min={currentRange.min} 
                  max={currentRange.max} 
                  value={value || currentRange.normal}
                  onChange={e => setValue(e.target.value)} 
                  className={`policy-slider risk-${riskLevel}`}
                />
              </div>
            )}
            
            <div className="value-input-container">
              <input 
                type="number" 
                value={value} 
                onChange={e => setValue(e.target.value)} 
                placeholder="Værdi" 
                min={currentRange?.min || 0}
                max={currentRange?.max || 100}
                required 
                className={`policy-value risk-${riskLevel}`}
              />
              {value && <span className="value-unit">%</span>}
            </div>
          </div>
          
          <button type="submit" className={`policy-submit risk-${riskLevel}`} disabled={!policy || !value}>
            Anvend politik
          </button>
        </div>
        
        <div className="policy-info">
          <button 
            type="button" 
            onClick={() => setShowGuidelines(!showGuidelines)}
            className="guidelines-toggle"
          >
            {showGuidelines ? "Skjul retningslinjer" : "Vis retningslinjer"}
          </button>
          
          {showGuidelines && currentRange && (
            <div className="guidelines-panel">
              <p>{currentRange.description}</p>
              <ul>
                <li>Normal værdi: <strong>{currentRange.normal}%</strong></li>
                <li>Minimum: {currentRange.min}%</li>
                <li>Maksimum: {currentRange.max}%</li>
              </ul>
              {policy === 'tariff' && (
                <p>
                  <strong>Bemærk:</strong> Høje toldsatser kan føre til handelskrige og gengældelsestold fra andre lande.
                </p>
              )}
              {policy === 'tax' && (
                <p>
                  <strong>Bemærk:</strong> Høje skatter påvirker økonomisk vækst og popularitet negativt. Lave skatter reducerer statens indtægter.
                </p>
              )}
              {policy === 'subsidy' && (
                <p>
                  <strong>Bemærk:</strong> Høje subsidier er dyrt for statskassen, men kan booste produktion og konkurrenceevne.
                </p>
              )}
            </div>
          )}
          
          {riskLevel !== 'normal' && value && (
            <div className={`risk-warning risk-${riskLevel}`}>
              {riskLevel === 'high' && <span>⚠️ Høj risiko: Denne værdi kan have alvorlige konsekvenser!</span>}
              {riskLevel === 'medium' && <span>⚠️ Moderat risiko: Denne værdi afviger betydeligt fra normalen.</span>}
            </div>
          )}
        </div>
      </form>
    </div>
  );
}

export default PolicyPanel;
