import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar } from 'recharts';

function DiplomacyPanel({ diplomacy, countries, selectedIso }) {
  const [activeTab, setActiveTab] = useState('relations');
  const [recentEvents, setRecentEvents] = useState([]);
  const [tradeData, setTradeData] = useState({});
  const [relationHistory, setRelationHistory] = useState({});
  const [showDependencyVisualization, setShowDependencyVisualization] = useState(false);
  const [selectedCountryForSanction, setSelectedCountryForSanction] = useState(null);
  const [sanctionSimulationResults, setSanctionSimulationResults] = useState(null);
  const [diplomaticRecommendations, setDiplomaticRecommendations] = useState([]);
  const [proposedAgreementImpact, setProposedAgreementImpact] = useState(null);
  const [tradeAgreementSimulation, setTradeAgreementSimulation] = useState({
    country: "",
    type: "FTA",
    showResults: false
  });

  useEffect(() => {
    if (!selectedIso) return;

    fetch(`/api/events/recent`)
      .then(res => res.json())
      .then(data => {
        setRecentEvents(data.events || []);
      })
      .catch(err => console.error("Fejl ved hentning af begivenheder:", err));

    fetch(`/api/trade/${selectedIso}`)
      .then(res => res.json())
      .then(data => {
        setTradeData(data || {});
      })
      .catch(err => console.error("Fejl ved hentning af handelsdata:", err));

    fetch(`/api/diplomacy/history/${selectedIso}`)
      .then(res => res.json())
      .then(data => {
        setRelationHistory(data || {});
      })
      .catch(err => console.error("Fejl ved hentning af relationshistorik:", err));

    fetch(`/api/diplomacy/recommendations/${selectedIso}`)
      .then(res => res.json())
      .then(data => {
        setDiplomaticRecommendations(data?.recommendations || []);
      })
      .catch(err => console.error("Fejl ved hentning af diplomatiske anbefalinger:", err));
  }, [selectedIso]);

  if (!diplomacy || !diplomacy.relations) {
    return (
      <div className="widget">
        <h3>Diplomati & Alliancer</h3>
        <p>Ingen diplomatiske data tilgængelige.</p>
      </div>
    );
  }

  const myRelations = diplomacy.relations.filter(rel =>
    rel.country_a === selectedIso || rel.country_b === selectedIso
  );

  const groupedRelations = {
    allies: [],
    friendly: [],
    neutral: [],
    tense: [],
    hostile: []
  };

  myRelations.forEach(rel => {
    const otherCountry = rel.country_a === selectedIso ? rel.country_b : rel.country_a;
    const countryName = countries && countries[otherCountry] ? countries[otherCountry].name : otherCountry;

    const tradeDependency = tradeData.dependencies ?
      tradeData.dependencies.find(dep => dep.iso === otherCountry) : null;

    const relationInfo = {
      iso: otherCountry,
      name: countryName,
      level: rel.relation_level,
      lastEvent: rel.last_event || 'N/A',
      tradeDependency: tradeDependency ? tradeDependency.level : 0,
      tradeVolume: tradeDependency ? tradeDependency.volume : 0
    };

    if (rel.relation_level > 0.7) {
      groupedRelations.allies.push(relationInfo);
    } else if (rel.relation_level > 0.3) {
      groupedRelations.friendly.push(relationInfo);
    } else if (rel.relation_level > -0.3) {
      groupedRelations.neutral.push(relationInfo);
    } else if (rel.relation_level > -0.7) {
      groupedRelations.tense.push(relationInfo);
    } else {
      groupedRelations.hostile.push(relationInfo);
    }
  });

  Object.keys(groupedRelations).forEach(key => {
    groupedRelations[key].sort((a, b) => b.tradeDependency - a.tradeDependency);
  });

  const tradeAgreements = diplomacy.agreements || [
    {
      id: "dummy-trade-1",
      name: "Frihandelsaftale med USA",
      parties: ["USA", selectedIso],
      type: "FTA",
      terms: "Reducerer told med 50% på industrielle varer",
      benefit: "Øget eksport af 15%",
      duration: "Ubegrænset",
      isProposed: false
    },
    {
      id: "dummy-trade-2",
      name: "Handelspartnerskab med EU",
      parties: ["EU", selectedIso],
      type: "Præferenceaftale",
      terms: "Reducerer told med 25% på landbrugsvarer",
      benefit: "Forbedrede diplomatiske relationer",
      duration: "10 år",
      isProposed: true
    }
  ];

  const handleTradeAgreementSimulation = () => {
    if (!tradeAgreementSimulation.country) return;

    fetch(`/api/trade/simulate_agreement`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        country_a: selectedIso,
        country_b: tradeAgreementSimulation.country,
        agreement_type: tradeAgreementSimulation.type
      }),
    })
      .then(res => res.json())
      .then(data => {
        setProposedAgreementImpact(data);
        setTradeAgreementSimulation({
          ...tradeAgreementSimulation,
          showResults: true
        });
      })
      .catch(err => console.error("Fejl ved simulation af handelsaftale:", err));
  };

  const simulateSanctions = (targetCountryIso) => {
    fetch(`/api/diplomacy/simulate_sanctions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        source_country: selectedIso,
        target_country: targetCountryIso,
        severity: "moderate"
      }),
    })
      .then(res => res.json())
      .then(data => {
        setSanctionSimulationResults(data);
        setSelectedCountryForSanction(targetCountryIso);
      })
      .catch(err => console.error("Fejl ved simulation af sanktioner:", err));
  };

  const prepareHistoricalChartData = (isoCode) => {
    if (!relationHistory[isoCode] || relationHistory[isoCode].length === 0) {
      return [];
    }

    return relationHistory[isoCode].map(entry => ({
      date: entry.date,
      level: entry.level,
      event: entry.event
    }));
  };

  const DiplomaticRiskAnalysis = ({ countryRelations, tradeData, selectedIso }) => {
    const calculateRisks = () => {
      const risks = {
        diplomaticIsolation: 0,
        tradeDependency: 0,
        conflictPotential: 0,
        sanctionVulnerability: 0,
        overallScore: 0
      };

      const hostileCount = countryRelations.hostile.length;
      const tenseCount = countryRelations.tense.length;
      const alliesCount = countryRelations.allies.length;

      risks.diplomaticIsolation = Math.min(
        1.0,
        ((hostileCount * 0.15) + (tenseCount * 0.05)) / Math.max(1, (alliesCount * 0.1 + 0.5))
      );

      if (tradeData && tradeData.dependencies) {
        const highDependencies = tradeData.dependencies.filter(dep => dep.level > 0.4).length;
        risks.tradeDependency = Math.min(1.0, highDependencies * 0.2);

        const hostileIsos = countryRelations.hostile.map(rel => rel.iso);
        const hostileDependencies = tradeData.dependencies
          .filter(dep => hostileIsos.includes(dep.iso))
          .reduce((sum, dep) => sum + dep.level, 0);

        risks.sanctionVulnerability = Math.min(1.0, hostileDependencies * 1.5);
      }

      if (tradeData && tradeData.dependencies) {
        const tenseIsos = countryRelations.tense.map(rel => rel.iso);
        const tenseDependencies = tradeData.dependencies
          .filter(dep => tenseIsos.includes(dep.iso))
          .reduce((sum, dep) => sum + dep.level, 0);

        risks.conflictPotential = Math.min(1.0, tenseDependencies * 1.2);
      }

      risks.overallScore = (
        risks.diplomaticIsolation * 0.3 +
        risks.tradeDependency * 0.25 +
        risks.conflictPotential * 0.25 +
        risks.sanctionVulnerability * 0.2
      );

      return risks;
    };

    const risks = calculateRisks();

    const getRiskLevel = (score) => {
      if (score < 0.3) return { text: 'Lav', color: '#4CAF50' };
      if (score < 0.6) return { text: 'Moderat', color: '#FF9800' };
      return { text: 'Høj', color: '#F44336' };
    };

    return (
      <div className="diplomatic-risk-analysis">
        <h5>Risikoevaluering</h5>

        <div className="risk-score-summary">
          <div className="overall-risk">
            <span className="risk-label">Samlet diplomatisk risiko:</span>
            <div className="risk-meter">
              <div
                className="risk-fill"
                style={{
                  width: `${Math.min(100, risks.overallScore * 100)}%`,
                  backgroundColor: getRiskLevel(risks.overallScore).color
                }}
              ></div>
            </div>
            <span className="risk-value" style={{ color: getRiskLevel(risks.overallScore).color }}>
              {getRiskLevel(risks.overallScore).text} ({(risks.overallScore * 100).toFixed(1)}%)
            </span>
          </div>
        </div>

        <div className="risk-breakdown">
          <div className="risk-factor">
            <span className="factor-label">Diplomatisk Isolation:</span>
            <div className="risk-meter-small">
              <div
                className="risk-fill"
                style={{
                  width: `${Math.min(100, risks.diplomaticIsolation * 100)}%`,
                  backgroundColor: getRiskLevel(risks.diplomaticIsolation).color
                }}
              ></div>
            </div>
            <span className="factor-value">{(risks.diplomaticIsolation * 100).toFixed(1)}%</span>
          </div>

          <div className="risk-factor">
            <span className="factor-label">Handelsafhængighed:</span>
            <div className="risk-meter-small">
              <div
                className="risk-fill"
                style={{
                  width: `${Math.min(100, risks.tradeDependency * 100)}%`,
                  backgroundColor: getRiskLevel(risks.tradeDependency).color
                }}
              ></div>
            </div>
            <span className="factor-value">{(risks.tradeDependency * 100).toFixed(1)}%</span>
          </div>

          <div className="risk-factor">
            <span className="factor-label">Konfliktpotentiale:</span>
            <div className="risk-meter-small">
              <div
                className="risk-fill"
                style={{
                  width: `${Math.min(100, risks.conflictPotential * 100)}%`,
                  backgroundColor: getRiskLevel(risks.conflictPotential).color
                }}
              ></div>
            </div>
            <span className="factor-value">{(risks.conflictPotential * 100).toFixed(1)}%</span>
          </div>

          <div className="risk-factor">
            <span className="factor-label">Sanktionssårbarhed:</span>
            <div className="risk-meter-small">
              <div
                className="risk-fill"
                style={{
                  width: `${Math.min(100, risks.sanctionVulnerability * 100)}%`,
                  backgroundColor: getRiskLevel(risks.sanctionVulnerability).color
                }}
              ></div>
            </div>
            <span className="factor-value">{(risks.sanctionVulnerability * 100).toFixed(1)}%</span>
          </div>
        </div>

        {risks.overallScore > 0.5 && (
          <div className="risk-recommendations">
            <h6>Anbefalinger til risikoreduktion</h6>
            <ul>
              {risks.diplomaticIsolation > 0.5 && (
                <li>Prioritér diplomatiske missioner til anspændte lande</li>
              )}
              {risks.tradeDependency > 0.5 && (
                <li>Diversificér handel med nye markeder</li>
              )}
              {risks.conflictPotential > 0.5 && (
                <li>Styrk diplomatiske bånd med vigtige handelspartnere</li>
              )}
              {risks.sanctionVulnerability > 0.5 && (
                <li>Reducér afhængighed af fjendtlige handelspartnere</li>
              )}
            </ul>
          </div>
        )}
      </div>
    );
  };

  const StrategicAdvicePanel = ({ countryData, relations, worldEvents, economicTrends }) => {
    const calculateStrategicOptions = () => {
      if (!countryData || !relations) return [];
      
      const options = [];
      const alliesCount = relations.allies ? relations.allies.length : 0;
      const friendlyCount = relations.friendly ? relations.friendly.length : 0;
      const tenseCount = relations.tense ? relations.tense.length : 0;
      const hostileCount = relations.hostile ? relations.hostile.length : 0;
      
      if (alliesCount < 2 && friendlyCount > 3) {
        options.push({
          type: 'alliance',
          title: 'Styrk Alliancer',
          description: 'Du har få formelle alliancer, men flere venligtsindede relationer. Overvej at opgradere nogle af disse til formelle alliancer.',
          benefit: 'Øget diplomatisk støtte og sikkerhed',
          cost: 'Forpligtelser til at støtte allierede i konflikter',
          recommendedTargets: relations.friendly?.slice(0, 3).map(rel => rel.iso) || []
        });
      }
      
      if (hostileCount > 2 && tenseCount > 3) {
        options.push({
          type: 'de-escalation',
          title: 'Afspændings-diplomati',
          description: 'Du har flere fjendtlige og anspændte forhold. Overvej en diplomatisk indsats for at reducere spændinger.',
          benefit: 'Reduceret risiko for konflikter og handelskrig',
          cost: 'Potentielle indrømmelser og prestige-tab',
          recommendedTargets: relations.tense?.slice(0, 3).map(rel => rel.iso) || []
        });
      }
      
      if (countryData.economy && countryData.economy.growth < 2.0) {
        options.push({
          type: 'economic_partnerships',
          title: 'Økonomiske Partnerskaber',
          description: 'Din økonomiske vækst er lav. Søg nye handelspartnerskaber for at stimulere væksten.',
          benefit: 'Øget økonomisk vækst og nye markeder',
          cost: 'Mulig øget konkurrence for lokale producenter',
          recommendedTargets: relations.friendly?.filter(rel => rel.tradeDependency < 0.2).slice(0, 3).map(rel => rel.iso) || []
        });
      }
      
      const majorPowers = ['USA', 'CHN', 'RUS', 'EU'];
      const alignmentScores = {};
      
      majorPowers.forEach(power => {
        const relation = [...relations.allies, ...relations.friendly, ...relations.neutral, ...relations.tense, ...relations.hostile]
          .find(rel => rel.iso === power);
        
        if (relation) {
          alignmentScores[power] = relation.level;
        }
      });
      
      const dominantAlignment = Object.entries(alignmentScores)
        .reduce((max, [power, score]) => (score > max.score ? {power, score} : max), {power: null, score: -2});
      
      if (dominantAlignment.power && dominantAlignment.score > 0.3) {
        const alignedPower = dominantAlignment.power;
        const rivalPowers = majorPowers.filter(p => p !== alignedPower);
        
        options.push({
          type: 'geopolitical_bloc',
          title: `Styrk ${alignedPower}-blokken`,
          description: `Du har en stærk relation med ${alignedPower}. Udnyt dette ved at styrke forbindelser med deres allierede.`,
          benefit: 'Styrket diplomatisk position gennem blokdannelse',
          cost: 'Potentielt forværrede relationer med rivaliserende blokke',
          recommendedTargets: [] 
        });
      }
      
      if (economicTrends && economicTrends.globalGrowthSectors) {
        options.push({
          type: 'trade_focus',
          title: 'Specialiseret Handelsstrategi',
          description: `Fokusér på handelsaftaler inden for ${economicTrends.globalGrowthSectors.join(', ')}, som er voksende globale sektorer.`,
          benefit: 'Maksimeret økonomisk vækst gennem målrettede handelsaftaler',
          cost: 'Øget sårbarhed over for sektorspecifikke økonomiske chok',
          recommendedTargets: relations.friendly?.filter(rel => rel.tradeDependency < 0.4).slice(0, 3).map(rel => rel.iso) || []
        });
      }
      
      return options;
    };
    
    const analyzeWorldEvents = () => {
      if (!worldEvents || worldEvents.length === 0) return [];
      
      const opportunityScores = {};
      const analyzed = [];
      
      worldEvents.forEach(event => {
        const relevantCountries = event.countriesInvolved || [];
        let relevanceScore = 0;
        let opportunityType = null;
        
        if (event.type === 'economic_crisis' && relevantCountries.some(iso => 
          relations.hostile?.find(rel => rel.iso === iso) || relations.tense?.find(rel => rel.iso === iso))) {
          opportunityType = 'leverage_crisis';
          relevanceScore = 0.8;
        } else if (event.type === 'trade_conflict' && !relevantCountries.includes(countryData.iso)) {
          opportunityType = 'redirect_trade';
          relevanceScore = 0.6;
        } else if (event.type === 'diplomatic_initiative' && 
          relevantCountries.some(iso => relations.friendly?.find(rel => rel.iso === iso) || relations.allies?.find(rel => rel.iso === iso))) {
          opportunityType = 'join_initiative';
          relevanceScore = 0.7;
        }
        
        if (opportunityType) {
          analyzed.push({
            event: event.title,
            type: opportunityType,
            description: getOpportunityDescription(opportunityType, event),
            relevanceScore,
            relatedCountries: relevantCountries
          });
        }
      });
      
      return analyzed.sort((a, b) => b.relevanceScore - a.relevanceScore).slice(0, 3);
    };
    
    const getOpportunityDescription = (type, event) => {
      switch(type) {
        case 'leverage_crisis':
          return `Udnyt den økonomiske krise i ${event.countriesInvolved.join(', ')} til at forbedre din relative forhandlingsposition.`;
        case 'redirect_trade':
          return `Handelskonflikten mellem ${event.countriesInvolved.join(' og ')} giver mulighed for at omdirigere handelsstrømme til din fordel.`;
        case 'join_initiative':
          return `Deltag i det diplomatiske initiativ fra ${event.countriesInvolved.join(', ')} for at styrke dine regionale bånd.`;
        default:
          return 'Analyser denne begivenhed for potentielle diplomatiske muligheder.';
      }
    };
    
    const strategies = calculateStrategicOptions();
    const eventOpportunities = analyzeWorldEvents();
    
    const mockEconomicTrends = {
      globalGrowthSectors: ['Grøn energi', 'Bioteknologi', 'Digital infrastruktur']
    };
    
    const mockWorldEvents = [
      {
        title: 'Amerikansk-Kinesisk handelsspænding',
        type: 'trade_conflict',
        countriesInvolved: ['USA', 'CHN']
      },
      {
        title: 'EU Green Deal Initiative',
        type: 'diplomatic_initiative',
        countriesInvolved: ['EU', 'FRA', 'DEU']
      }
    ];
    
    const actualEconomicTrends = economicTrends || mockEconomicTrends;
    const actualWorldEvents = worldEvents || mockWorldEvents;
    
    return (
      <div className="strategic-advice-panel">
        <h4>Strategisk Rådgivning</h4>
        
        <div className="strategy-section">
          <h5>Anbefalede Diplomatiske Strategier</h5>
          {strategies.length === 0 ? (
            <p>Ingen strategiske anbefalinger tilgængelige.</p>
          ) : (
            <div className="strategy-cards">
              {strategies.map((strategy, index) => (
                <div key={index} className="strategy-card">
                  <div className="card-header">
                    <h6>{strategy.title}</h6>
                    <span className="strategy-type">{strategy.type}</span>
                  </div>
                  <p>{strategy.description}</p>
                  <div className="strategy-details">
                    <div className="detail-row">
                      <span className="detail-label">Fordele:</span>
                      <span className="detail-value">{strategy.benefit}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Omkostninger:</span>
                      <span className="detail-value">{strategy.cost}</span>
                    </div>
                    {strategy.recommendedTargets.length > 0 && (
                      <div className="detail-row">
                        <span className="detail-label">Anbefalede mål:</span>
                        <span className="detail-value">{strategy.recommendedTargets.join(', ')}</span>
                      </div>
                    )}
                  </div>
                  <button className="implement-strategy-btn">Implementer Strategi</button>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="events-section">
          <h5>Diplomatiske Muligheder fra Verdensbegivenheder</h5>
          {eventOpportunities.length === 0 ? (
            <p>Ingen relevante verdensbegivenheder at kapitalisere på.</p>
          ) : (
            <div className="event-opportunities">
              {eventOpportunities.map((opportunity, index) => (
                <div key={index} className="event-opportunity">
                  <div className="event-header">
                    <h6>{opportunity.event}</h6>
                    <span className="relevance-badge" style={{
                      backgroundColor: opportunity.relevanceScore > 0.7 ? '#4CAF50' : 
                                      opportunity.relevanceScore > 0.5 ? '#FF9800' : '#2196F3'
                    }}>
                      {opportunity.relevanceScore > 0.7 ? 'Høj Relevans' : 
                       opportunity.relevanceScore > 0.5 ? 'Moderat Relevans' : 'Lav Relevans'}
                    </span>
                  </div>
                  <p>{opportunity.description}</p>
                  <div className="opportunity-footer">
                    <span className="countries-involved">
                      Involverede lande: {opportunity.relatedCountries.join(', ')}
                    </span>
                    <button className="act-on-opportunity-btn">Udnyt Mulighed</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="global-trends-section">
          <h5>Globale Økonomiske Tendenser</h5>
          <div className="trends-summary">
            <div className="growth-sectors">
              <h6>Voksende Sektorer Globalt</h6>
              <ul>
                {actualEconomicTrends.globalGrowthSectors.map((sector, idx) => (
                  <li key={idx}>{sector}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="widget diplomacy-panel">
      <h3>Diplomati & Handel</h3>

      <div className="tabs">
        <button
          className={activeTab === 'relations' ? 'active-tab' : ''}
          onClick={() => setActiveTab('relations')}
        >
          Relationer
        </button>
        <button
          className={activeTab === 'alliances' ? 'active-tab' : ''}
          onClick={() => setActiveTab('alliances')}
        >
          Alliancer
        </button>
        <button
          className={activeTab === 'trade' ? 'active-tab' : ''}
          onClick={() => setActiveTab('trade')}
        >
          Handelsafhængighed
        </button>
        <button
          className={activeTab === 'agreements' ? 'active-tab' : ''}
          onClick={() => setActiveTab('agreements')}
        >
          Handelsaftaler
        </button>
        <button
          className={activeTab === 'history' ? 'active-tab' : ''}
          onClick={() => setActiveTab('history')}
        >
          Relationshistorik
        </button>
        <button
          className={activeTab === 'strategy' ? 'active-tab' : ''}
          onClick={() => setActiveTab('strategy')}
        >
          Strategi
        </button>
        <button
          className={activeTab === 'sanctions' ? 'active-tab' : ''}
          onClick={() => setActiveTab('sanctions')}
        >
          Sanktioner
        </button>
        <button
          className={activeTab === 'events' ? 'active-tab' : ''}
          onClick={() => setActiveTab('events')}
        >
          Begivenheder
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'relations' && (
          <div className="relations-container">
            <div className="relation-summary">
              <p>
                <span className="relation-dot allies"></span> Allierede: {groupedRelations.allies.length}
                <span className="relation-dot friendly"></span> Venlige: {groupedRelations.friendly.length}
                <span className="relation-dot neutral"></span> Neutrale: {groupedRelations.neutral.length}
                <span className="relation-dot tense"></span> Anspændte: {groupedRelations.tense.length}
                <span className="relation-dot hostile"></span> Fjendtlige: {groupedRelations.hostile.length}
              </p>
            </div>

            {Object.entries(groupedRelations).map(([type, relations]) => {
              if (relations.length === 0) return null;

              return (
                <div key={type} className={`relation-group ${type}`}>
                  <h4>
                    {type === 'allies' && 'Allierede'}
                    {type === 'friendly' && 'Venlige Forhold'}
                    {type === 'neutral' && 'Neutrale Forhold'}
                    {type === 'tense' && 'Anspændte Forhold'}
                    {type === 'hostile' && 'Fjendtlige Forhold'}
                  </h4>
                  <ul className="relation-list">
                    {relations.map((rel, idx) => (
                      <li key={idx} className="relation-item">
                        <div className="relation-country">
                          <strong>{rel.name}</strong> ({rel.iso})
                          {rel.tradeDependency > 0.5 && (
                            <span className="high-dependency" title="Høj handelsafhængighed">⚠️</span>
                          )}
                        </div>
                        <div className="relation-level">
                          <div className="relation-meter">
                            <div
                              className="relation-fill"
                              style={{
                                width: `${Math.abs(rel.level) * 100}%`,
                                backgroundColor: rel.level > 0 ? '#4CAF50' : '#F44336'
                              }}
                            ></div>
                          </div>
                          <span className="relation-value">{rel.level.toFixed(2)}</span>
                        </div>
                        <div className="relation-trade">
                          <small>
                            Handelsvolumen: {rel.tradeVolume ? `${rel.tradeVolume.toFixed(1)} mia. $` : 'N/A'}
                            {rel.tradeDependency > 0 && ` (${(rel.tradeDependency * 100).toFixed(1)}% afhængighed)`}
                          </small>
                        </div>
                        <div className="relation-event">
                          <small>Seneste begivenhed: {rel.lastEvent}</small>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}

            <StrategicAdvicePanel 
              countryData={countries[selectedIso]}
              relations={groupedRelations}
              worldEvents={gameState?.worldEvents || []}
              economicTrends={gameState?.economicTrends || {}}
            />
          </div>
        )}

        {activeTab === 'alliances' && (
          <div className="alliances-container">
            {(diplomacy.alliances && diplomacy.alliances.length > 0) ? (
              <div>
                <h4>Dine Alliancer</h4>
                <ul className="alliance-list">
                  {diplomacy.alliances
                    .filter(al => al.members.includes(selectedIso))
                    .map((al, i) => (
                      <li key={i} className="alliance-item">
                        <div className="alliance-header">
                          <strong>{al.name}</strong>
                          <span className="alliance-type">({al.type || 'Handelsforbund'})</span>
                        </div>
                        <div className="alliance-details">
                          <p><strong>Medlemmer:</strong> {al.members.map(m => countries[m]?.name || m).join(', ')}</p>
                          <p><strong>Stiftet:</strong> {al.date_formed || 'Ukendt'}</p>
                          {al.benefits && <p><strong>Fordele:</strong> {al.benefits}</p>}
                        </div>
                        <div className="alliance-actions">
                          <button className="small-button">Træd ud</button>
                        </div>
                      </li>
                    ))
                  }
                </ul>

                <h4>Andre Globale Alliancer</h4>
                <ul className="alliance-list other-alliances">
                  {diplomacy.alliances
                    .filter(al => !al.members.includes(selectedIso))
                    .map((al, i) => (
                      <li key={i} className="alliance-item">
                        <div className="alliance-header">
                          <strong>{al.name}</strong>
                          <span className="alliance-type">({al.type || 'Handelsforbund'})</span>
                        </div>
                        <div className="alliance-details">
                          <p><strong>Medlemmer:</strong> {al.members.map(m => countries[m]?.name || m).join(', ')}</p>
                          <p><strong>Stiftet:</strong> {al.date_formed || 'Ukendt'}</p>
                          {al.benefits && <p><strong>Fordele:</strong> {al.benefits}</p>}
                        </div>
                        <div className="alliance-actions">
                          <button className="small-button">Ansøg om medlemskab</button>
                        </div>
                      </li>
                    ))
                  }
                </ul>
              </div>
            ) : (
              <div>
                <h4>Vigtige Globale Handelsalliancer</h4>
                <ul className="alliance-list">
                  <li className="alliance-item">
                    <div className="alliance-header">
                      <strong>Nordamerikansk Frihandelsaftale (NAFTA/USMCA)</strong>
                    </div>
                    <div className="alliance-details">
                      <p><strong>Medlemmer:</strong> USA, Canada, Mexico</p>
                      <p><strong>Stiftet:</strong> 1994, opdateret 2020</p>
                      <p><strong>Fordele:</strong> Reducerede toldsatser, øget handel mellem medlemmerne</p>
                    </div>
                    <div className="alliance-actions">
                      <button className="small-button">Ansøg om tilknytning</button>
                    </div>
                  </li>
                  <li className="alliance-item">
                    <div className="alliance-header">
                      <strong>EU Single Market</strong>
                    </div>
                    <div className="alliance-details">
                      <p><strong>Medlemmer:</strong> 27 EU-lande</p>
                      <p><strong>Stiftet:</strong> 1993</p>
                      <p><strong>Fordele:</strong> Fri bevægelighed af varer, kapital, tjenester og personer</p>
                    </div>
                    <div className="alliance-actions">
                      <button className="small-button">Ansøg om handelspartnerskab</button>
                    </div>
                  </li>
                  <li className="alliance-item">
                    <div className="alliance-header">
                      <strong>Australia-USA Frihandelsaftale (AUSFTA)</strong>
                    </div>
                    <div className="alliance-details">
                      <p><strong>Medlemmer:</strong> Australien, USA</p>
                      <p><strong>Stiftet:</strong> 2005</p>
                      <p><strong>Fordele:</strong> Præferencetold, øget handel mellem de to lande</p>
                      <p><strong>Status:</strong> Stærk handel, specielt inden for landbrug og råvarer</p>
                    </div>
                  </li>
                  <li className="alliance-item">
                    <div className="alliance-header">
                      <strong>ASEAN Frihandelsområde</strong>
                    </div>
                    <div className="alliance-details">
                      <p><strong>Medlemmer:</strong> 10 sydøstasiatiske lande</p>
                      <p><strong>Stiftet:</strong> 1992</p>
                      <p><strong>Fordele:</strong> Reducerede toldsatser mellem medlemslande, styrket regional integration</p>
                    </div>
                    <div className="alliance-actions">
                      <button className="small-button">Ansøg om handelspartnerskab</button>
                    </div>
                  </li>
                </ul>

                <div className="alliance-info">
                  <p>
                    <i>Tip: Du kan indgå i alliancer gennem diplomatiske handlinger for at få fordele som
                      reducerede toldsatser eller øget handel med medlemslandene.</i>
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'trade' && (
          <div className="trade-dependency-container">
            <h4>Handelsafhængighed</h4>
            {tradeData.dependencies && tradeData.dependencies.length > 0 ? (
              <div>
                <div className="trade-overview">
                  <div className="overview-stat">
                    <span className="stat-title">Total Eksport</span>
                    <span className="stat-value">{tradeData.totalExport?.toFixed(1) || 0} mia. $</span>
                  </div>
                  <div className="overview-stat">
                    <span className="stat-title">Total Import</span>
                    <span className="stat-value">{tradeData.totalImport?.toFixed(1) || 0} mia. $</span>
                  </div>
                  <div className="overview-stat">
                    <span className="stat-title">Handelsbalance</span>
                    <span className="stat-value" style={{ color: (tradeData.balance || 0) >= 0 ? 'green' : 'red' }}>
                      {tradeData.balance?.toFixed(1) || 0} mia. $
                    </span>
                  </div>
                </div>

                <div className="action-buttons">
                  <button
                    className="toggle-button"
                    onClick={() => setShowDependencyVisualization(!showDependencyVisualization)}
                  >
                    {showDependencyVisualization ? 'Skjul Visualisering' : 'Vis Visualisering'}
                  </button>
                </div>

                {showDependencyVisualization && (
                  <div className="dependency-visualization">
                    <h5>Handelsafhængighed Visualisering</h5>
                    <div className="chart-container">
                      <BarChart width={600} height={300} data={tradeData.dependencies
                        .sort((a, b) => b.volume - a.volume)
                        .slice(0, 10)
                        .map(dep => ({
                          country: countries[dep.iso]?.name || dep.iso,
                          volume: dep.volume,
                          export: dep.export,
                          import: dep.import,
                          dependency: dep.level * 100
                        }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="country" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="export" name="Eksport (mia. $)" fill="#2196F3" />
                        <Bar dataKey="import" name="Import (mia. $)" fill="#4CAF50" />
                      </BarChart>
                    </div>

                    <div className="chart-container">
                      <BarChart width={600} height={300} data={tradeData.dependencies
                        .sort((a, b) => b.level - a.level)
                        .slice(0, 10)
                        .map(dep => ({
                          country: countries[dep.iso]?.name || dep.iso,
                          dependency: dep.level * 100
                        }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="country" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="dependency" name="Afhængighed (%)" fill="#FF9800" />
                      </BarChart>
                    </div>
                  </div>
                )}

                <h5>Top Handelspartnere</h5>
                <div className="trade-partners">
                  {tradeData.dependencies
                    .sort((a, b) => b.volume - a.volume)
                    .slice(0, 5)
                    .map((dep, i) => (
                      <div key={i} className="trade-partner">
                        <div className="partner-name">
                          <strong>{countries[dep.iso]?.name || dep.iso}</strong>
                          {dep.level > 0.5 && <span className="high-dependency-warning" title="Høj afhængighed">⚠️</span>}
                        </div>
                        <div className="partner-volume">
                          <span>Handelsvolumen: {dep.volume?.toFixed(1) || 0} mia. $</span>
                        </div>
                        <div className="partner-dependency">
                          <div className="dependency-meter">
                            <div
                              className="dependency-fill"
                              style={{
                                width: `${Math.min(100, dep.level * 100)}%`,
                                backgroundColor: dep.level > 0.5 ? '#ff9800' : '#2196F3'
                              }}
                            ></div>
                          </div>
                          <span className="dependency-value">{(dep.level * 100).toFixed(1)}% afhængighed</span>
                        </div>
                        <div className="partner-details">
                          <span>Eksport: {dep.export?.toFixed(1) || 0} mia. $ ({Math.round((dep.export / tradeData.totalExport) * 100) || 0}% af total)</span>
                          <span>Import: {dep.import?.toFixed(1) || 0} mia. $ ({Math.round((dep.import / tradeData.totalImport) * 100) || 0}% af total)</span>
                        </div>
                      </div>
                    ))
                  }
                </div>

                <div className="trade-risk-analysis">
                  <h5>Handelsrisiko Analyse</h5>
                  <div className="risk-indicators">
                    {tradeData.dependencies.filter(dep => dep.level > 0.4).length > 0 ? (
                      <div className="risk-indicator warning">
                        <span className="risk-icon">⚠️</span>
                        <div className="risk-detail">
                          <strong>Høj Handelsafhængighed</strong>
                          <p>Du har høj afhængighed af {tradeData.dependencies.filter(dep => dep.level > 0.4).length} lande,
                            hvilket gør din økonomi sårbar over for handelskonflikter.</p>
                        </div>
                      </div>
                    ) : (
                      <div className="risk-indicator good">
                        <span className="risk-icon">✅</span>
                        <div className="risk-detail">
                          <strong>Diversificeret Handel</strong>
                          <p>Din handel er godt fordelt på forskellige lande uden kritiske afhængigheder.</p>
                        </div>
                      </div>
                    )}

                    {tradeData.balance < 0 ? (
                      <div className="risk-indicator warning">
                        <span className="risk-icon">📉</span>
                        <div className="risk-detail">
                          <strong>Handelsunderskud</strong>
                          <p>Dit handelsunderskud kan påvirke økonomisk vækst og valutakurser på længere sigt.</p>
                        </div>
                      </div>
                    ) : (
                      <div className="risk-indicator good">
                        <span className="risk-icon">📈</span>
                        <div className="risk-detail">
                          <strong>Handelsoverskud</strong>
                          <p>Dit handelsoverskud styrker din økonomiske position og valuta.</p>
                        </div>
                      </div>
                    )}

                    {tradeData.diversificationIndex < 0.5 ? (
                      <div className="risk-indicator warning">
                        <span className="risk-icon">🔍</span>
                        <div className="risk-detail">
                          <strong>Lav Handelsdiversificering</strong>
                          <p>Din handel er koncentreret på få markeder, hvilket øger din sårbarhed.</p>
                        </div>
                      </div>
                    ) : (
                      <div className="risk-indicator good">
                        <span className="risk-icon">🔍</span>
                        <div className="risk-detail">
                          <strong>God Handelsdiversificering</strong>
                          <p>Din handel er spredt over mange markeder, hvilket reducerer din sårbarhed.</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-trade-data">
                <p>Ingen detaljeret handelsdata tilgængelig endnu.</p>
                <p>Efterhånden som spillet skrider frem, vil du kunne se:</p>
                <ul>
                  <li>Hvor meget du eksporterer og importerer fra hvert land</li>
                  <li>Hvilke lande din økonomi er mest afhængig af</li>
                  <li>Risikofaktorer baseret på handelskoncentration</li>
                  <li>Konkurrenter inden for samme eksportmarkeder</li>
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === 'agreements' && (
          <div className="agreements-container">
            <h4>Dine Handelsaftaler</h4>

            <ul className="agreement-list">
              {tradeAgreements
                .filter(a => a.parties.includes(selectedIso) && !a.isProposed)
                .map((agreement, i) => (
                  <li key={i} className="agreement-item">
                    <div className="agreement-header">
                      <strong>{agreement.name}</strong>
                      <span className="agreement-type">({agreement.type})</span>
                    </div>
                    <div className="agreement-details">
                      <p><strong>Parter:</strong> {agreement.parties.map(p => countries[p]?.name || p).join(', ')}</p>
                      <p><strong>Betingelser:</strong> {agreement.terms}</p>
                      <p><strong>Fordele:</strong> {agreement.benefit}</p>
                      <p><strong>Varighed:</strong> {agreement.duration}</p>
                    </div>
                    <div className="agreement-actions">
                      <button className="small-button danger-btn">Ophæv aftale</button>
                    </div>
                  </li>
                ))
              }
            </ul>

            <h4>Foreslåede Aftaler</h4>
            <ul className="agreement-list proposed">
              {tradeAgreements
                .filter(a => a.parties.includes(selectedIso) && a.isProposed)
                .map((agreement, i) => (
                  <li key={i} className="agreement-item">
                    <div className="agreement-header">
                      <strong>{agreement.name}</strong>
                      <span className="agreement-type">({agreement.type})</span>
                    </div>
                    <div className="agreement-details">
                      <p><strong>Parter:</strong> {agreement.parties.map(p => countries[p]?.name || p).join(', ')}</p>
                      <p><strong>Betingelser:</strong> {agreement.terms}</p>
                      <p><strong>Fordele:</strong> {agreement.benefit}</p>
                      <p><strong>Varighed:</strong> {agreement.duration}</p>
                    </div>
                    <div className="agreement-actions">
                      <button className="small-button accept-btn">Accepter</button>
                      <button className="small-button reject-btn">Afvis</button>
                    </div>
                  </li>
                ))
              }
            </ul>

            <div className="new-agreement">
              <h4>Handelsaftale Analyse</h4>
              <div className="agreement-simulation-form">
                <div className="form-group">
                  <label>Land:</label>
                  <select
                    className="agreement-country-select"
                    value={tradeAgreementSimulation.country}
                    onChange={(e) => setTradeAgreementSimulation({
                      ...tradeAgreementSimulation,
                      country: e.target.value,
                      showResults: false
                    })}
                  >
                    <option value="">Vælg land</option>
                    {Object.values(countries || {})
                      .filter(c => c.iso_code !== selectedIso)
                      .map(c => (
                        <option key={c.iso_code} value={c.iso_code}>{c.name}</option>
                      ))
                    }
                  </select>
                </div>
                <div className="form-group">
                  <label>Type:</label>
                  <select
                    className="agreement-type-select"
                    value={tradeAgreementSimulation.type}
                    onChange={(e) => setTradeAgreementSimulation({
                      ...tradeAgreementSimulation,
                      type: e.target.value,
                      showResults: false
                    })}
                  >
                    <option value="FTA">Frihandelsaftale</option>
                    <option value="Præferenceaftale">Toldpræference</option>
                    <option value="Partnerskab">Strategisk Partnerskab</option>
                  </select>
                </div>
                <button
                  className="small-button"
                  onClick={handleTradeAgreementSimulation}
                  disabled={!tradeAgreementSimulation.country}
                >
                  Analysér Virkning
                </button>
              </div>

              {tradeAgreementSimulation.showResults && proposedAgreementImpact && (
                <div className="agreement-impact-analysis">
                  <h5>Anslået Virkning af Handelsaftale</h5>

                  <div className="impact-metrics">
                    <div className="impact-metric">
                      <span className="metric-label">Eksportstigning:</span>
                      <span className="metric-value" style={{ color: 'green' }}>
                        +{proposedAgreementImpact.export_growth.toFixed(1)}%
                      </span>
                    </div>
                    <div className="impact-metric">
                      <span className="metric-label">Importstigning:</span>
                      <span className="metric-value" style={{ color: 'blue' }}>
                        +{proposedAgreementImpact.import_growth.toFixed(1)}%
                      </span>
                    </div>
                    <div className="impact-metric">
                      <span className="metric-label">BNP Påvirkning:</span>
                      <span className="metric-value" style={{
                        color: proposedAgreementImpact.gdp_impact >= 0 ? 'green' : 'red'
                      }}>
                        {proposedAgreementImpact.gdp_impact > 0 ? '+' : ''}
                        {proposedAgreementImpact.gdp_impact.toFixed(2)}%
                      </span>
                    </div>
                    <div className="impact-metric">
                      <span className="metric-label">Relation Ændring:</span>
                      <span className="metric-value" style={{ color: 'green' }}>
                        +{proposedAgreementImpact.relation_change.toFixed(2)}
                      </span>
                    </div>
                    <div className="impact-metric">
                      <span className="metric-label">Handelsafhængighed:</span>
                      <span className="metric-value" style={{
                        color: proposedAgreementImpact.dependency_risk > 0.3 ? 'orange' : 'green'
                      }}>
                        {(proposedAgreementImpact.dependency_risk * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div className="impact-summary">
                    <h6>Opsummering</h6>
                    <p>{proposedAgreementImpact.summary}</p>
                  </div>

                  <div className="agreement-actions">
                    <button className="small-button">Foreslå Aftale</button>
                    <button
                      className="small-button secondary-btn"
                      onClick={() => setTradeAgreementSimulation({ ...tradeAgreementSimulation, showResults: false })}
                    >
                      Luk Analyse
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="relations-history-container">
            <h4>Diplomatisk Relationshistorik</h4>

            <div className="country-selector">
              <label>Vælg land:</label>
              <select
                onChange={(e) => setShowDependencyVisualization(e.target.value)}
                value={showDependencyVisualization || ''}
              >
                <option value="">Vælg land for at se relationshistorik</option>
                {myRelations.map(rel => {
                  const otherIso = rel.country_a === selectedIso ? rel.country_b : rel.country_a;
                  return (
                    <option key={otherIso} value={otherIso}>
                      {countries[otherIso]?.name || otherIso}
                    </option>
                  );
                })}
              </select>
            </div>

            {showDependencyVisualization && (
              <div className="relation-history-visualization">
                <h5>Historisk Relation med {countries[showDependencyVisualization]?.name || showDependencyVisualization}</h5>

                {relationHistory[showDependencyVisualization] && relationHistory[showDependencyVisualization].length > 0 ? (
                  <div className="chart-container">
                    <LineChart width={600} height={300} data={prepareHistoricalChartData(showDependencyVisualization)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis domain={[-1, 1]} />
                      <Tooltip
                        formatter={(value, name, props) => [
                          `${value.toFixed(2)}`,
                          'Relationsniveau'
                        ]}
                        labelFormatter={(label) => `Dato: ${label}`}
                      />
                      <Legend />
                      <Line type="monotone" dataKey="level" name="Relationsniveau" stroke="#8884d8" activeDot={{ r: 8 }} />
                    </LineChart>
                  </div>
                ) : (
                  <p>Ingen historisk data tilgængelig for dette land.</p>
                )}

                <div className="relation-history-events">
                  <h6>Vigtige Begivenheder</h6>
                  {relationHistory[showDependencyVisualization] && relationHistory[showDependencyVisualization].length > 0 ? (
                    <ul className="history-events-list">
                      {relationHistory[showDependencyVisualization]
                        .filter(entry => entry.event)
                        .map((entry, i) => (
                          <li key={i} className="history-event-item">
                            <span className="event-date">{entry.date}</span>
                            <span className="event-content">{entry.event}</span>
                            <span className="event-impact" style={{
                              color: entry.impact > 0 ? 'green' : entry.impact < 0 ? 'red' : 'gray'
                            }}>
                              {entry.impact > 0 ? '+' : ''}{entry.impact.toFixed(2)}
                            </span>
                          </li>
                        ))
                      }
                    </ul>
                  ) : (
                    <p>Ingen begivenheder registreret for dette land.</p>
                  )}
                </div>
              </div>
            )}

            {!showDependencyVisualization && (
              <div className="history-overview">
                <p>Vælg et land fra dropdown-menuen for at se en detaljeret historik over jeres diplomatiske relation.</p>
                <p>Historikken viser:</p>
                <ul>
                  <li>Hvordan relationen har udviklet sig over tid</li>
                  <li>Vigtige begivenheder der har påvirket relationen</li>
                  <li>Handelsudvikling mellem landene</li>
                  <li>Kriser og højdepunkter i det diplomatiske forhold</li>
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === 'strategy' && (
          <div className="strategy-container">
            <h4>Diplomatiske Strategianbefalinger</h4>

            {diplomaticRecommendations && diplomaticRecommendations.length > 0 ? (
              <div className="recommendations-list">
                {diplomaticRecommendations.map((rec, i) => (
                  <div key={i} className="recommendation-item">
                    <div className="recommendation-header">
                      <span className="recommendation-priority" style={{
                        backgroundColor:
                          rec.priority === 'high' ? '#e53935' :
                            rec.priority === 'medium' ? '#fb8c00' : '#43a047'
                      }}>
                        {rec.priority === 'high' ? 'Høj' : rec.priority === 'medium' ? 'Medium' : 'Lav'}
                      </span>
                      <h5>{rec.title}</h5>
                    </div>
                    <div className="recommendation-body">
                      <p>{rec.description}</p>
                      {rec.reasoning && (
                        <div className="recommendation-reasoning">
                          <strong>Begrundelse:</strong> {rec.reasoning}
                        </div>
                      )}
                      {rec.benefit && (
                        <div className="recommendation-benefit">
                          <strong>Fordele:</strong> {rec.benefit}
                        </div>
                      )}
                      {rec.risk && (
                        <div className="recommendation-risk">
                          <strong>Risici:</strong> {rec.risk}
                        </div>
                      )}
                    </div>
                    {rec.actions && rec.actions.length > 0 && (
                      <div className="recommendation-actions">
                        <strong>Anbefalede handlinger:</strong>
                        <ul>
                          {rec.actions.map((action, j) => (
                            <li key={j}>{action}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-recommendations">
                <p>Ingen strategiske anbefalinger tilgængelige på nuværende tidspunkt.</p>
                <p>Anbefalinger genereres baseret på:</p>
                <ul>
                  <li>Dine aktuelle diplomatiske relationer</li>
                  <li>Økonomiske afhængigheder og sårbarheder</li>
                  <li>Globale begivenheder og spændinger</li>
                  <li>Muligheder for nye alliancer og handelsaftaler</li>
                </ul>
              </div>
            )}

            <div className="strategy-insights">
              <h5>Diplomatisk Overblik</h5>
              <div className="strategy-metrics">
                <div className="strategy-metric">
                  <span className="metric-label">Allierede:</span>
                  <span className="metric-value">{groupedRelations.allies.length}</span>
                </div>
                <div className="strategy-metric">
                  <span className="metric-label">Venlige:</span>
                  <span className="metric-value">{groupedRelations.friendly.length}</span>
                </div>
                <div className="strategy-metric">
                  <span className="metric-label">Neutrale:</span>
                  <span className="metric-value">{groupedRelations.neutral.length}</span>
                </div>
                <div className="strategy-metric">
                  <span className="metric-label">Anspændte:</span>
                  <span className="metric-value">{groupedRelations.tense.length}</span>
                </div>
                <div className="strategy-metric">
                  <span className="metric-label">Fjendtlige:</span>
                  <span className="metric-value">{groupedRelations.hostile.length}</span>
                </div>
              </div>

              <div className="diplomatic-focus-areas">
                <h6>Fokusområder</h6>
                <ul>
                  {groupedRelations.tense.length > 0 && (
                    <li>
                      <strong>Reducer spændinger:</strong> Overvej diplomatiske handlinger for at forbedre
                      relationer med {groupedRelations.tense.length} anspændte partnere.
                    </li>
                  )}
                  {tradeData.dependencies && tradeData.dependencies.filter(d => d.level > 0.4).length > 0 && (
                    <li>
                      <strong>Diversificér handel:</strong> Reducer afhængighed af høj-koncentrerede
                      handelspartnere for at mindske risiko.
                    </li>
                  )}
                  {groupedRelations.friendly.length > 2 && (
                    <li>
                      <strong>Konsolidér alliancer:</strong> Undersøg muligheder for at opgradere venlige
                      relationer til formelle alliancer.
                    </li>
                  )}
                  {tradeData.balance && tradeData.balance < 0 && (
                    <li>
                      <strong>Styrk eksport:</strong> Søg nye eksportmuligheder for at forbedre handelsbalancen.
                    </li>
                  )}
                </ul>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'sanctions' && (
          <div className="sanctions-container">
            <h4>Sanktioner & Handelskonflikter</h4>

            <DiplomaticRiskAnalysis
              countryRelations={groupedRelations}
              tradeData={tradeData}
              selectedIso={selectedIso}
            />

            <div className="sanctions-section">
              <h5>Aktive Sanktioner</h5>
              {diplomacy.sanctions && diplomacy.sanctions.length > 0 ? (
                <ul className="sanctions-list">
                  {diplomacy.sanctions
                    .filter(sanc => sanc.source === selectedIso || sanc.target === selectedIso)
                    .map((sanction, i) => {
                      const isSource = sanction.source === selectedIso;
                      const otherCountry = isSource ? sanction.target : sanction.source;
                      return (
                        <li key={i} className={`sanction-item ${isSource ? 'outgoing' : 'incoming'}`}>
                          <div className="sanction-header">
                            <strong>
                              {isSource ? 'Pålagt af dig mod ' : 'Pålagt mod dig af '}
                              {countries[otherCountry]?.name || otherCountry}
                            </strong>
                            <span className="sanction-severity"
                              style={{
                                backgroundColor:
                                  sanction.severity === 'high' ? '#e53935' :
                                    sanction.severity === 'medium' ? '#fb8c00' : '#ffb300'
                              }}>
                              {sanction.severity === 'high' ? 'Hård' :
                                sanction.severity === 'medium' ? 'Moderat' : 'Let'}
                            </span>
                          </div>
                          <div className="sanction-details">
                            <p><strong>Type:</strong> {sanction.type}</p>
                            <p><strong>Indført:</strong> {sanction.date}</p>
                            <p><strong>Effekt:</strong> {sanction.effect}</p>
                            <p><strong>Begrundelse:</strong> {sanction.reason}</p>
                          </div>
                          {isSource && (
                            <div className="sanction-actions">
                              <button className="small-button danger-btn">Ophæv sanktioner</button>
                            </div>
                          )}
                        </li>
                      );
                    })}
                </ul>
              ) : (
                <p>Der er ingen aktive sanktioner for dit land på nuværende tidspunkt.</p>
              )}
            </div>

            <div className="sanctions-simulation">
              <h5>Simulér Sanktioner</h5>
              <div className="simulation-form">
                <div className="form-group">
                  <label>Land:</label>
                  <select
                    value={selectedCountryForSanction || ''}
                    onChange={(e) => {
                      setSelectedCountryForSanction(e.target.value);
                      setSanctionSimulationResults(null);
                    }}
                  >
                    <option value="">Vælg land</option>
                    {Object.values(countries || {})
                      .filter(c => c.iso_code !== selectedIso)
                      .map(c => (
                        <option key={c.iso_code} value={c.iso_code}>{c.name}</option>
                      ))
                    }
                  </select>
                </div>
                <button
                  className="small-button"
                  onClick={() => simulateSanctions(selectedCountryForSanction)}
                  disabled={!selectedCountryForSanction}
                >
                  Simulér Konsekvenser
                </button>
              </div>

              {sanctionSimulationResults && (
                <div className="sanction-simulation-results">
                  <h6>Estimerede konsekvenser af sanktioner mod {countries[selectedCountryForSanction]?.name}</h6>

                  <div className="simulation-metrics">
                    <div className="simulation-metric">
                      <span className="metric-label">Økonomisk Påvirkning (Dig):</span>
                      <span className="metric-value" style={{ color: 'red' }}>
                        {sanctionSimulationResults.own_economic_impact.toFixed(2)}%
                      </span>
                    </div>
                    <div className="simulation-metric">
                      <span className="metric-label">Økonomisk Påvirkning (Dem):</span>
                      <span className="metric-value" style={{ color: 'red' }}>
                        {sanctionSimulationResults.target_economic_impact.toFixed(2)}%
                      </span>
                    </div>
                    <div className="simulation-metric">
                      <span className="metric-label">Handelsvolumentab:</span>
                      <span className="metric-value">
                        {sanctionSimulationResults.trade_volume_loss.toFixed(1)} mia. $
                      </span>
                    </div>
                    <div className="simulation-metric">
                      <span className="metric-label">Relationspåvirkning:</span>
                      <span className="metric-value" style={{ color: 'red' }}>
                        {sanctionSimulationResults.relation_impact.toFixed(2)}
                      </span>
                    </div>
                    <div className="simulation-metric">
                      <span className="metric-label">Globalt Omdømme:</span>
                      <span className="metric-value" style={{
                        color: sanctionSimulationResults.global_reputation_impact < 0 ? 'red' : 'green'
                      }}>
                        {sanctionSimulationResults.global_reputation_impact.toFixed(2)}
                      </span>
                    </div>
                  </div>

                  <div className="simulation-summary">
                    <h6>Analyse</h6>
                    <p>{sanctionSimulationResults.analysis}</p>
                  </div>

                  <div className="simulation-actions">
                    <button className="small-button danger-btn">Indfør Sanktioner</button>
                    <button
                      className="small-button secondary-btn"
                      onClick={() => setSanctionSimulationResults(null)}
                    >
                      Afbryd
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'events' && (
          <div className="global-events-container">
            <h4>Seneste Globale Begivenheder</h4>

            {recentEvents && recentEvents.length > 0 ? (
              <ul className="events-list">
                {recentEvents.map((event, i) => (
                  <li key={i} className="event-item">
                    <div className="event-header">
                      <span className="event-date">{event.date}</span>
                      <span className="event-type" style={{
                        backgroundColor:
                          event.impact === 'major' ? '#e53935' :
                            event.impact === 'moderate' ? '#fb8c00' : '#2196F3'
                      }}>
                        {event.type}
                      </span>
                    </div>
                    <div className="event-content">{event.description}</div>
                    <div className="event-countries">
                      {event.countries && event.countries.length > 0 && (
                        <small>Involverede lande: {event.countries.map(c => countries[c]?.name || c).join(', ')}</small>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p>Ingen globale begivenheder registreret.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default DiplomacyPanel;