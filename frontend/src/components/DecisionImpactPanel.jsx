import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

// Registrer ChartJS komponenter
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function DecisionImpactPanel({ country, targetCountry, lastDecisions, allCountries, policyRanges }) {
  const [impactData, setImpactData] = useState(null);
  
  // Generer konsekvensanalyse baseret på sidste beslutninger
  useEffect(() => {
    if (!country || !lastDecisions || lastDecisions.length === 0) {
      setImpactData(null);
      return;
    }
    
    // Beregn de forventede ændringer baseret på den seneste beslutning
    const latestDecision = lastDecisions[0];
    calculateImpact(latestDecision);
  }, [lastDecisions, country, targetCountry]);
  
  const calculateImpact = (decision) => {
    // I et rigtigt system ville dette komme fra serveren
    // Her simulerer vi det baseret på beslutningen
    
    if (!decision || !decision.policy) {
      setImpactData(null);
      return;
    }
    
    const { policy, value, target } = decision.policy;
    const isTargeted = target !== 'all';
    const targetName = isTargeted ? (allCountries[target]?.name || target) : 'Alle lande';
    
    let title = '';
    let impactScenarios = [];
    let diplomaticImpact = [];
    let gdpImpactData = {};
    let approvalImpact = 0;
    let economicRiskLevel = 'lav';
    let relationType = 'neutral';
    
    const normalValue = policyRanges[policy]?.normal || 0;
    const valueComparison = value > normalValue ? 'højere' : 'lavere';
    const valueDiff = Math.abs(value - normalValue);
    const valueDiffPercent = normalValue > 0 ? (valueDiff / normalValue * 100).toFixed(1) : 100;
    
    // Beregn handelspartnerens størrelse og relationer
    let partnerImportance = 'mindre';
    let relationLevel = 0;
    
    if (isTargeted && target && allCountries[target]) {
      const partnerGDP = allCountries[target].gdp || 0;
      if (partnerGDP > country.gdp * 0.8) partnerImportance = 'betydelig';
      else if (partnerGDP > country.gdp * 0.3) partnerImportance = 'moderat';
      
      // Find relation
      if (country.relations) {
        const relation = country.relations.find(r => 
          (r.country_a === target && r.country_b === country.iso_code) || 
          (r.country_b === target && r.country_a === country.iso_code)
        );
        if (relation) {
          relationLevel = relation.relation_level;
          if (relationLevel > 0.5) relationType = 'allieret';
          else if (relationLevel > 0) relationType = 'positiv';
          else if (relationLevel > -0.5) relationType = 'anspændt';
          else relationType = 'fjendtlig';
        }
      }
    }
    
    // Policy-specifikke konsekvenser
    if (policy === 'tariff') {
      title = `Konsekvensanalyse: ${value}% told på import ${isTargeted ? `fra ${targetName}` : ''}`;
      
      const tariffDiffDescription = valueDiff > 10 ? 'markant' : valueDiff > 5 ? 'moderat' : 'lille';
      const baseImpact = value / 100;
      
      // Økonomisk effect
      if (value > normalValue) {
        // Højere told
        impactScenarios.push({
          title: 'Kortsigtede effekter',
          effects: [
            `Din lokale industri oplever ${tariffDiffDescription} beskyttelse mod udenlandsk konkurrence`,
            `Forbrugerpriser vil stige med estimeret ${(baseImpact * 0.7).toFixed(1)}% på importvarer${isTargeted ? ` fra ${targetName}` : ''}`,
            `Statens toldindtægter vil stige med ${(baseImpact * 25).toFixed(1)}%${isTargeted ? ` fra import fra ${targetName}` : ''}`
          ]
        });
        
        impactScenarios.push({
          title: 'Langsigtede effekter',
          effects: [
            `Risiko for ${isTargeted ? 'målrettet gengældelsestold fra ' + targetName : 'internationale handelsrestriktioner'}`,
            `Din lokale industri kan blive mindre konkurrencedygtig på lang sigt pga. beskyttelse`,
            `Øget inflation på ${(baseImpact * 0.4).toFixed(1)}% over de næste år`
          ]
        });
        
        gdpImpactData = {
          // Højere told giver kortsigtede fordele men langsigtede ulemper
          shortTerm: [0, 0.2, 0.1, -0.1, -0.3],
          longTerm: [0, -0.1, -0.3, -0.5, -0.8],
          uncertaintyRange: [0.2, 0.3, 0.4, 0.5, 0.6]
        };
        
        approvalImpact = 0.2; // Kortsigtede fordele kan øge popularitet
        economicRiskLevel = isTargeted && partnerImportance === 'betydelig' ? 'høj' : 'moderat';
      } else {
        // Lavere told
        impactScenarios.push({
          title: 'Kortsigtede effekter',
          effects: [
            `Lavere forbrugerpriser på importvarer${isTargeted ? ` fra ${targetName}` : ''}`,
            `Øget konkurrence for din lokale industri`,
            `Reducerede toldindtægter for staten`
          ]
        });
        
        impactScenarios.push({
          title: 'Langsigtede effekter',
          effects: [
            `Forbedrede handelsforbindelser${isTargeted ? ` med ${targetName}` : ''}`,
            `Potentiel øget eksport på grund af gensidighed`,
            `Øget produktivitet gennem international konkurrence`
          ]
        });
        
        gdpImpactData = {
          shortTerm: [0, -0.1, 0, 0.2, 0.3],
          longTerm: [0, 0.1, 0.3, 0.4, 0.6],
          uncertaintyRange: [0.1, 0.2, 0.3, 0.4, 0.5]
        };
        
        approvalImpact = -0.1; // Kortsigtede udfordringer kan reducere popularitet
        economicRiskLevel = 'lav';
      }
      
      // Diplomatisk effect
      if (isTargeted) {
        const significantTariff = value > normalValue * 1.5;
        
        if (significantTariff) {
          diplomaticImpact.push({
            country: targetName,
            impact: `Betydelig forværring af relationer${relationLevel > 0 ? ' trods tidligere positive forhold' : ''}`,
            tradeImpact: `Reduceret handel med ${targetName} (estimeret -${(baseImpact * 50).toFixed(1)}%)`,
            riskOfRetaliation: partnerImportance === 'betydelig' ? 'Meget høj' : partnerImportance === 'moderat' ? 'Høj' : 'Moderat'
          });
        } else if (value > normalValue) {
          diplomaticImpact.push({
            country: targetName,
            impact: `Lettere forværring af relationer`,
            tradeImpact: `Lettere reduceret handel med ${targetName}`,
            riskOfRetaliation: partnerImportance === 'betydelig' ? 'Moderat' : 'Lav'
          });
        } else {
          diplomaticImpact.push({
            country: targetName,
            impact: `Forbedring af relationer`,
            tradeImpact: `Øget handel med ${targetName}`,
            riskOfRetaliation: 'Ingen'
          });
        }
      } else {
        // Ikke-målrettet told påvirker alle
        if (value > normalValue * 1.5) {
          diplomaticImpact.push({
            country: 'Globalt',
            impact: 'Generel forværring af internationale relationer',
            tradeImpact: 'Reduceret globalt handelsvolumen',
            riskOfRetaliation: 'Høj på tværs af handelspartnere'
          });
        } else if (value > normalValue) {
          diplomaticImpact.push({
            country: 'Globalt',
            impact: 'Lettere forværring af handelsrelationer',
            tradeImpact: 'Mindre reduktion i global handel',
            riskOfRetaliation: 'Moderat'
          });
        } else {
          diplomaticImpact.push({
            country: 'Globalt',
            impact: 'Forbedring af handelsrelationer',
            tradeImpact: 'Øget global handelsmængde',
            riskOfRetaliation: 'Ingen'
          });
        }
      }
      
    } else if (policy === 'tax') {
      title = `Konsekvensanalyse: ${value}% skat`;
      
      if (value > normalValue) {
        // Højere skat
        impactScenarios.push({
          title: 'Kortsigtede effekter',
          effects: [
            `Øgede statsindtægter (estimeret +${(valueDiffPercent * 0.8).toFixed(1)}%)`,
            `Reduceret privatforbrug (estimeret -${(valueDiffPercent * 0.4).toFixed(1)}%)`,
            `Lettere negativ effekt på økonomisk vækst`
          ]
        });
        
        impactScenarios.push({
          title: 'Langsigtede effekter',
          effects: [
            `Potentiel reduktion i investeringer på -${(valueDiffPercent * 0.3).toFixed(1)}%`,
            `Mulig udvandring af kapital og talent til lavere-skat områder`,
            `Øget offentlig service kan afbøde negative effekter`
          ]
        });
        
        gdpImpactData = {
          shortTerm: [0, -0.2, -0.3, -0.4, -0.3],
          longTerm: [0, -0.3, -0.4, -0.3, -0.1],
          uncertaintyRange: [0.1, 0.2, 0.3, 0.4, 0.4]
        };
        
        approvalImpact = -0.3 * (valueDiff / 10); // Højere skat er typisk upopulært
        economicRiskLevel = value > normalValue + 15 ? 'høj' : 'moderat';
      } else {
        // Lavere skat
        impactScenarios.push({
          title: 'Kortsigtede effekter',
          effects: [
            `Reducerede statsindtægter (estimeret -${(valueDiffPercent * 0.9).toFixed(1)}%)`,
            `Øget privatforbrug og økonomisk aktivitet`,
            `Potentiel nedskæring i offentlige ydelser, hvis der ikke kompenseres`
          ]
        });
        
        impactScenarios.push({
          title: 'Langsigtede effekter',
          effects: [
            `Potentielt øgede investeringer og økonomisk vækst`,
            `Muligt budgetunderskud hvis ikke ledsaget af vækst eller besparelser`,
            `Tiltrække international kapital og talent`
          ]
        });
        
        gdpImpactData = {
          shortTerm: [0, 0.3, 0.4, 0.3, 0.2],
          longTerm: [0, 0.2, 0.4, 0.6, 0.5],
          uncertaintyRange: [0.1, 0.2, 0.3, 0.4, 0.5]
        };
        
        approvalImpact = 0.4 * (valueDiff / 10); // Lavere skat er typisk populært
        economicRiskLevel = value < normalValue - 15 ? 'moderat' : 'lav';
      }
      
      // Skatten har primært intern effekt, mindre international
      diplomaticImpact.push({
        country: 'Internationalt',
        impact: 'Minimal direkte påvirkning af relationer',
        tradeImpact: value < normalValue ? 'Potentielt øget international konkurrenceevne' : 'Lettere reduceret international konkurrenceevne',
        riskOfRetaliation: 'Ingen'
      });
      
    } else if (policy === 'subsidy') {
      title = `Konsekvensanalyse: ${value}% subsidier til industri`;
      
      if (value > normalValue) {
        // Højere subsidier
        impactScenarios.push({
          title: 'Kortsigtede effekter',
          effects: [
            `Styrket konkurrenceevne for din lokale industri`,
            `Øgede statsudgifter (estimeret +${(valueDiffPercent * 1.2).toFixed(1)}%)`,
            `Potentielt øget produktion og beskæftigelse`
          ]
        });
        
        impactScenarios.push({
          title: 'Langsigtede effekter',
          effects: [
            `Risiko for ineffektivitet i beskyttede industrier`,
            `Potentielle internationale handelsklager over unfair konkurrence`,
            `Øget afhængighed af statslig støtte i visse sektorer`
          ]
        });
        
        gdpImpactData = {
          shortTerm: [0, 0.4, 0.5, 0.4, 0.2],
          longTerm: [0, 0.2, 0.0, -0.1, -0.3],
          uncertaintyRange: [0.1, 0.2, 0.3, 0.4, 0.5]
        };
        
        approvalImpact = 0.3 * (valueDiff / 5); // Subsidier er typisk populære indenlands
        economicRiskLevel = value > normalValue + 10 ? 'høj' : 'moderat';
      } else {
        // Lavere subsidier
        impactScenarios.push({
          title: 'Kortsigtede effekter',
          effects: [
            `Reducerede statsudgifter`,
            `Potentielt pres på visse industrier`,
            `Reduceret politisk interferens i markedet`
          ]
        });
        
        impactScenarios.push({
          title: 'Langsigtede effekter',
          effects: [
            `Øget effektivitet i tidligere subsiderede industrier`,
            `Potentielt tab af konkurrenceevne i forhold til mere subsiderede udenlandske industrier`,
            `Markedsdrevet innovation og udvikling`
          ]
        });
        
        gdpImpactData = {
          shortTerm: [0, -0.2, -0.1, 0.0, 0.1],
          longTerm: [0, -0.1, 0.1, 0.3, 0.4],
          uncertaintyRange: [0.1, 0.2, 0.3, 0.3, 0.4]
        };
        
        approvalImpact = -0.2 * (valueDiff / 5); // Reducerede subsidier kan være upopulære
        economicRiskLevel = 'lav';
      }
      
      // Subsidier har international effekt
      if (value > normalValue + 8) {
        diplomaticImpact.push({
          country: 'Internationalt',
          impact: 'Potentielt negative reaktioner fra handelspartnere',
          tradeImpact: 'Risiko for modforanstaltninger og handelsklager',
          riskOfRetaliation: 'Moderat til høj'
        });
      } else if (value > normalValue) {
        diplomaticImpact.push({
          country: 'Internationalt',
          impact: 'Mindre bekymring fra handelspartnere',
          tradeImpact: 'Begrænset risiko for modforanstaltninger',
          riskOfRetaliation: 'Lav'
        });
      } else {
        diplomaticImpact.push({
          country: 'Internationalt',
          impact: 'Positiv respons fra frihandelsorienterede partnere',
          tradeImpact: 'Potentielt forbedrede handelsrelationer',
          riskOfRetaliation: 'Ingen'
        });
      }
    }
    
    // Generer graf-data for GDP-effekt
    const timeLabels = ['Nu', 'År 1', 'År 2', 'År 3', 'År 5'];
    
    const lineData = {
      labels: timeLabels,
      datasets: [
        {
          label: 'Kortsigtet effekt',
          data: gdpImpactData.shortTerm,
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          tension: 0.2
        },
        {
          label: 'Langsigtet effekt',
          data: gdpImpactData.longTerm,
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          tension: 0.2
        }
      ]
    };
    
    setImpactData({
      title,
      policy,
      value,
      target: targetName,
      impactScenarios,
      diplomaticImpact,
      gdpImpactData: lineData,
      approvalImpact,
      economicRiskLevel
    });
  };
  
  if (!impactData) {
    return (
      <div className="widget decision-impact-panel">
        <h3>Konsekvensanalyse</h3>
        <p>Implementér en politik for at se dens forventede konsekvenser.</p>
      </div>
    );
  }
  
  return (
    <div className="widget decision-impact-panel">
      <h3>{impactData.title}</h3>
      
      <div className="impact-summary">
        <div className={`risk-indicator ${impactData.economicRiskLevel}-risk`}>
          <h4>Økonomisk Risiko</h4>
          <div className="risk-level">{impactData.economicRiskLevel.toUpperCase()}</div>
        </div>
        
        <div className="approval-indicator">
          <h4>Popularitetseffekt</h4>
          <div className={`approval-change ${impactData.approvalImpact > 0 ? 'positive' : impactData.approvalImpact < 0 ? 'negative' : 'neutral'}`}>
            {impactData.approvalImpact > 0 ? '+' : ''}{(impactData.approvalImpact * 100).toFixed(1)}%
          </div>
        </div>
      </div>
      
      <div className="gdp-impact-chart">
        <h4>BNP-effekt over tid (% ændring)</h4>
        <div className="chart-wrapper" style={{ height: '200px' }}>
          <Line data={impactData.gdpImpactData} options={{ 
            maintainAspectRatio: false,
            scales: {
              y: {
                title: {
                  display: true,
                  text: 'Ændring i BNP (%)'
                }
              }
            }
          }} />
        </div>
      </div>
      
      <div className="impact-scenarios">
        {impactData.impactScenarios.map((scenario, idx) => (
          <div key={`scenario-${idx}`} className="scenario">
            <h4>{scenario.title}</h4>
            <ul>
              {scenario.effects.map((effect, effectIdx) => (
                <li key={`effect-${idx}-${effectIdx}`}>{effect}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      
      <div className="diplomatic-impact">
        <h4>Diplomatiske konsekvenser</h4>
        {impactData.diplomaticImpact.map((dipImpact, idx) => (
          <div key={`dip-impact-${idx}`} className="diplomatic-impact-item">
            <h5>{dipImpact.country}</h5>
            <p><strong>Relationseffekt:</strong> {dipImpact.impact}</p>
            <p><strong>Handelseffekt:</strong> {dipImpact.tradeImpact}</p>
            <p><strong>Risiko for gengældelse:</strong> {dipImpact.riskOfRetaliation}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DecisionImpactPanel;