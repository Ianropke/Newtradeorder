import React, { useState, useEffect } from 'react';

function GlobalActionsPanel({ countries, selectedIso, currentTurn, alliances = [] }) {
  const [globalActions, setGlobalActions] = useState([]);
  const [competitors, setCompetitors] = useState([]);
  const [tradeDependencies, setTradeDependencies] = useState([]);
  const [activeTab, setActiveTab] = useState('actions');

  // Simulerer handlinger fra andre lande
  useEffect(() => {
    if (!countries || Object.keys(countries).length === 0 || !selectedIso || currentTurn === 0) return;
    
    // Simuler nye handlinger når turen ændres
    const topCountries = Object.values(countries)
      .filter(c => c.iso_code !== selectedIso)
      .sort((a, b) => b.gdp - a.gdp)
      .slice(0, 10);
    
    // Generér tilfældige handlinger fra andre lande
    const newActions = [];
    
    // Mellem 1-3 handlinger per tur
    const actionCount = Math.floor(Math.random() * 3) + 1;
    
    for (let i = 0; i < actionCount; i++) {
      const actionType = ['toll', 'subsidy', 'alliance', 'sanction'][Math.floor(Math.random() * 4)];
      const actorCountry = topCountries[Math.floor(Math.random() * topCountries.length)];
      let targetCountry;
      
      // Vælg et andet land som mål, måske spillerens land
      do {
        const usePlayerCountry = Math.random() < 0.3; // 30% chance for at målrette spilleren
        if (usePlayerCountry) {
          targetCountry = countries[selectedIso];
        } else {
          targetCountry = topCountries[Math.floor(Math.random() * topCountries.length)];
        }
      } while (targetCountry.iso_code === actorCountry.iso_code);
      
      let action;
      switch (actionType) {
        case 'toll':
          const tollRate = Math.floor(Math.random() * 30) + 5;
          action = {
            type: 'toll',
            actor: actorCountry,
            target: targetCountry,
            value: tollRate,
            turn: currentTurn,
            description: `${actorCountry.name} indfører ${tollRate}% told på import fra ${targetCountry.name}`,
            impact: targetCountry.iso_code === selectedIso ? 'negativ' : 'neutral',
            date: new Date().toLocaleDateString()
          };
          break;
        case 'subsidy':
          const subsidyRate = Math.floor(Math.random() * 20) + 5;
          const sector = ['landbrug', 'produktion', 'teknologi', 'tjenester'][Math.floor(Math.random() * 4)];
          action = {
            type: 'subsidy',
            actor: actorCountry,
            target: null,
            value: subsidyRate,
            sector: sector,
            turn: currentTurn,
            description: `${actorCountry.name} indfører ${subsidyRate}% subsidie til ${sector}sektoren`,
            impact: 'neutral',
            date: new Date().toLocaleDateString()
          };
          break;
        case 'alliance':
          action = {
            type: 'alliance',
            actor: actorCountry,
            target: targetCountry,
            turn: currentTurn,
            description: `${actorCountry.name} indgår handelsaftale med ${targetCountry.name}`,
            impact: targetCountry.iso_code === selectedIso ? 'positiv' : 'neutral',
            date: new Date().toLocaleDateString()
          };
          break;
        case 'sanction':
          action = {
            type: 'sanction',
            actor: actorCountry,
            target: targetCountry,
            turn: currentTurn,
            description: `${actorCountry.name} indfører handelssanktioner mod ${targetCountry.name}`,
            impact: targetCountry.iso_code === selectedIso ? 'kritisk' : 'neutral',
            date: new Date().toLocaleDateString()
          };
          break;
      }
      
      if (action) {
        newActions.push(action);
      }
    }
    
    setGlobalActions(prev => [...newActions, ...prev].slice(0, 15));
    
    // Beregn konkurrenter baseret på industri-overlap
    if (countries[selectedIso] && countries[selectedIso].industries) {
      const playerCountry = countries[selectedIso];
      const playerTopIndustries = Object.entries(playerCountry.industries)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map(([key]) => key);
      
      const newCompetitors = Object.values(countries)
        .filter(c => c.iso_code !== selectedIso && c.industries)
        .map(country => {
          // Beregn industri-overlap
          const countryTopIndustries = Object.entries(country.industries || {})
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3)
            .map(([key]) => key);
          
          const overlap = playerTopIndustries.filter(ind => countryTopIndustries.includes(ind)).length;
          const competitionScore = overlap * (country.gdp / playerCountry.gdp);
          
          return {
            country,
            overlap,
            competitionScore,
            commonIndustries: playerTopIndustries.filter(ind => countryTopIndustries.includes(ind))
          };
        })
        .filter(c => c.overlap > 0)
        .sort((a, b) => b.competitionScore - a.competitionScore)
        .slice(0, 5);
      
      setCompetitors(newCompetitors);
    }
    
    // Beregn handelsafhængigheder
    const myTradePartners = Object.values(countries)
      .filter(c => c.iso_code !== selectedIso)
      .map(country => {
        // Simuler handelsvolumen (i virkeligheden ville dette komme fra backend)
        const importVol = Math.random() * country.gdp * 0.2;
        const exportVol = Math.random() * country.gdp * 0.15;
        const totalTrade = importVol + exportVol;
        const tradeBalance = exportVol - importVol;
        
        // Simuler afhængighedsgrad (0-1)
        const dependencyScore = totalTrade / (countries[selectedIso].gdp * 0.3);
        
        return {
          country,
          importVolume: importVol,
          exportVolume: exportVol,
          totalTrade,
          tradeBalance,
          dependencyScore,
          isKeyPartner: totalTrade > (countries[selectedIso].gdp * 0.05) // Over 5% af BNP
        };
      })
      .sort((a, b) => b.totalTrade - a.totalTrade)
      .slice(0, 8);
    
    setTradeDependencies(myTradePartners);
    
  }, [countries, selectedIso, currentTurn]);

  return (
    <div className="widget global-actions-panel">
      <h3>Internationale Relationer</h3>

      <div className="tabs">
        <button 
          className={activeTab === 'actions' ? 'active-tab' : ''} 
          onClick={() => setActiveTab('actions')}
        >
          Globale Handlinger
        </button>
        <button 
          className={activeTab === 'dependencies' ? 'active-tab' : ''} 
          onClick={() => setActiveTab('dependencies')}
        >
          Handelsafhængigheder
        </button>
        <button 
          className={activeTab === 'competitors' ? 'active-tab' : ''} 
          onClick={() => setActiveTab('competitors')}
        >
          Konkurrenter
        </button>
        <button 
          className={activeTab === 'alliances' ? 'active-tab' : ''} 
          onClick={() => setActiveTab('alliances')}
        >
          Alliancer
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'actions' && (
          <div className="actions-container">
            <h4>Seneste Internationale Handlinger</h4>
            {globalActions.length === 0 ? (
              <p>Ingen handlinger at vise endnu.</p>
            ) : (
              <ul className="actions-list">
                {globalActions.map((action, idx) => (
                  <li key={`action-${idx}`} className={`action-item ${action.impact}`}>
                    <div className="action-header">
                      <span className="action-turn">Tur {action.turn}</span>
                      <span className="action-date">{action.date}</span>
                    </div>
                    <div className="action-content">
                      <p>{action.description}</p>
                      {action.impact !== 'neutral' && (
                        <p className="impact-indicator">
                          <strong>Påvirkning på din økonomi:</strong> {
                            action.impact === 'positiv' ? 'Positiv 📈' :
                            action.impact === 'negativ' ? 'Negativ 📉' :
                            action.impact === 'kritisk' ? 'Kritisk ⚠️' : 'Neutral'
                          }
                        </p>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {activeTab === 'dependencies' && (
          <div className="dependencies-container">
            <h4>Dine Handelsafhængigheder</h4>
            {tradeDependencies.length === 0 ? (
              <p>Ingen handelsafhængigheder at vise endnu.</p>
            ) : (
              <div>
                <table className="dependencies-table">
                  <thead>
                    <tr>
                      <th>Land</th>
                      <th>Import (mia.)</th>
                      <th>Eksport (mia.)</th>
                      <th>Handelsbalance</th>
                      <th>Afhængighed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tradeDependencies.map((dep, idx) => (
                      <tr key={`dep-${idx}`} className={dep.isKeyPartner ? 'key-partner' : ''}>
                        <td>{dep.country.name}</td>
                        <td>{dep.importVolume.toFixed(1)}</td>
                        <td>{dep.exportVolume.toFixed(1)}</td>
                        <td className={dep.tradeBalance > 0 ? 'positive' : 'negative'}>
                          {dep.tradeBalance.toFixed(1)}
                        </td>
                        <td>
                          <div className="dependency-bar" title={`${(dep.dependencyScore * 100).toFixed(1)}% af dit BNP`}>
                            <div 
                              className="dependency-fill" 
                              style={{width: `${Math.min(100, dep.dependencyScore * 100)}%`}}
                            ></div>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div className="dependencies-summary">
                  <p><strong>Nøgleafhængigheder:</strong></p>
                  <ul>
                    {tradeDependencies.filter(d => d.isKeyPartner).slice(0, 3).map((dep, idx) => (
                      <li key={`key-dep-${idx}`}>
                        {dep.country.name}: {(dep.dependencyScore * 100).toFixed(1)}% af dit BNP
                        {dep.tradeBalance < 0 ? 
                          ` (negativ handelsbalance: ${dep.tradeBalance.toFixed(1)} mia.)` : 
                          ` (positiv handelsbalance: +${dep.tradeBalance.toFixed(1)} mia.)`}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'competitors' && (
          <div className="competitors-container">
            <h4>Dine Hovedkonkurrenter</h4>
            {competitors.length === 0 ? (
              <p>Ingen konkurrenter at vise endnu.</p>
            ) : (
              <div>
                <table className="competitors-table">
                  <thead>
                    <tr>
                      <th>Land</th>
                      <th>Fælles Industrier</th>
                      <th>Konkurrenceniveau</th>
                    </tr>
                  </thead>
                  <tbody>
                    {competitors.map((comp, idx) => (
                      <tr key={`comp-${idx}`}>
                        <td>{comp.country.name}</td>
                        <td>{comp.commonIndustries.join(', ')}</td>
                        <td>
                          <div className="competition-meter">
                            <div 
                              className="competition-fill" 
                              style={{width: `${Math.min(100, comp.competitionScore * 20)}%`}}
                            ></div>
                          </div>
                          {comp.competitionScore > 2 ? 'Høj' : comp.competitionScore > 1 ? 'Medium' : 'Lav'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div className="competition-insight">
                  <p><strong>Indsigt:</strong></p>
                  <p>
                    Høj konkurrence med andre lande kan føre til handelskonflikter.
                    Overvej beskyttende politikker for dine nøgleindustrier eller differentiering
                    gennem subsidier til at blive mere konkurrencedygtig.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'alliances' && (
          <div className="alliances-container">
            <h4>Etablerede Handelsalliancer</h4>
            {alliances.length === 0 ? (
              <div>
                <p>Eksisterende globale handelsalliancer:</p>
                <ul className="alliances-list">
                  <li className="alliance-item">
                    <h5>Nordamerikansk Frihandelsaftale (NAFTA)</h5>
                    <p>Medlemmer: USA, Canada, Mexico</p>
                    <p>Fordele: Reducerede toldsatser, øget handel mellem medlemmerne</p>
                  </li>
                  <li className="alliance-item">
                    <h5>EU Single Market</h5>
                    <p>Medlemmer: 27 EU-lande</p>
                    <p>Fordele: Fri bevægelighed af varer, kapital, tjenester og personer</p>
                  </li>
                  <li className="alliance-item">
                    <h5>ASEAN Free Trade Area</h5>
                    <p>Medlemmer: Thailand, Indonesien, Singapore, m.fl.</p>
                    <p>Fordele: Reducerede told, regional økonomisk integration</p>
                  </li>
                  <li className="alliance-item">
                    <h5>Australia-USA Frihandelsaftale</h5>
                    <p>Medlemmer: Australien, USA</p>
                    <p>Fordele: Præferencetold, øget handel mellem de to lande</p>
                  </li>
                </ul>
              </div>
            ) : (
              <ul className="alliances-list">
                {alliances.map((alliance, idx) => (
                  <li key={`alliance-${idx}`} className="alliance-item">
                    <h5>{alliance.name}</h5>
                    <p>Medlemmer: {alliance.members.join(', ')}</p>
                    <p>Type: {alliance.type}</p>
                    <p>Stiftet: {alliance.date_formed}</p>
                    <p>Primær fordel: {alliance.benefits}</p>
                  </li>
                ))}
                <li className="alliance-item">
                  <h5>Nordamerikansk Frihandelsaftale (NAFTA)</h5>
                  <p>Medlemmer: USA, Canada, Mexico</p>
                  <p>Stiftet: 1994</p>
                  <p>Primær fordel: Reducerede toldsatser, øget handel mellem medlemmerne</p>
                </li>
                <li className="alliance-item">
                  <h5>Australia-USA Frihandelsaftale</h5>
                  <p>Medlemmer: Australien, USA</p>
                  <p>Stiftet: 2005</p>
                  <p>Primær fordel: Præferencetold, øget handel mellem de to lande</p>
                </li>
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default GlobalActionsPanel;