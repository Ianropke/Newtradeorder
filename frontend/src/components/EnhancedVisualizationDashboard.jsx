import React, { useState, useEffect } from 'react';
import '../styles/EnhancedVisualizationDashboard.css';
import BNPHistoryPanel from './BNPHistoryPanel';
import CountryAnalysisPanel from './CountryAnalysisPanel';

const EnhancedVisualizationDashboard = ({ gameState, countries, tradeData, diplomaticRelations }) => {
  const [activeTab, setActiveTab] = useState('economic');
  const [timeRange, setTimeRange] = useState('all');
  const [viewMode, setViewMode] = useState('detailed');

  // Filter data based on timeRange
  const filterDataByTimeRange = (data) => {
    if (timeRange === 'all') return data;

    const currentTurn = gameState?.currentTurn || 0;
    const turnThreshold =
      timeRange === 'last5' ? 5 :
      timeRange === 'last10' ? 10 :
      timeRange === 'last20' ? 20 : 0;

    return data.filter(item => (currentTurn - item.turn) <= turnThreshold);
  };

  // Prepare data for different visualizations
  const prepareEconomicData = () => {
    return countries.map(country => ({
      name: country.name,
      gdp: country.economy.gdp,
      growthRate: country.economy.growthRate,
      inflation: country.economy.inflation,
      unemployment: country.economy.unemployment,
      debt: country.economy.publicDebt,
      history: filterDataByTimeRange(country.economy.history || [])
    }));
  };

  const prepareDiplomaticData = () => {
    return diplomaticRelations.map(relation => ({
      source: relation.source,
      target: relation.target,
      status: relation.status,
      tradeAgreements: relation.tradeAgreements,
      sanctions: relation.sanctions,
      tension: relation.tension,
      history: filterDataByTimeRange(relation.history || [])
    }));
  };

  const prepareTradeData = () => {
    return tradeData.map(item => ({
      exporter: item.exporter,
      importer: item.importer,
      volume: item.volume,
      balance: item.balance,
      products: item.products,
      history: filterDataByTimeRange(item.history || [])
    }));
  };

  const prepareCoalitionData = () => {
    // Extract coalition data from countries and diplomatic relations
    const coalitions = [];
    const coalitionMap = new Map();

    countries.forEach(country => {
      if (country.coalitions && country.coalitions.length) {
        country.coalitions.forEach(coalitionId => {
          if (!coalitionMap.has(coalitionId)) {
            coalitionMap.set(coalitionId, {
              id: coalitionId,
              name: `Coalition ${coalitionId}`,
              members: [],
              strength: 0,
              gdpShare: 0,
              tradeVolume: 0
            });
            coalitions.push(coalitionMap.get(coalitionId));
          }

          coalitionMap.get(coalitionId).members.push(country.name);
          coalitionMap.get(coalitionId).strength += country.economy.gdp * 0.8 + country.military.strength * 0.2;
          coalitionMap.get(coalitionId).gdpShare += country.economy.gdp;
        });
      }
    });

    return coalitions;
  };

  const preparePredictionData = () => {
    // Generate prediction data based on historical trends
    return countries.map(country => {
      const history = country.economy.history || [];
      const lastFive = history.slice(-5);

      const avgGrowthRate = lastFive.reduce((sum, item) => sum + item.growthRate, 0) / lastFive.length || 0;
      const growthTrend = lastFive.length > 1 ?
        (lastFive[lastFive.length - 1].growthRate - lastFive[0].growthRate) / lastFive.length :
        0;

      return {
        name: country.name,
        currentGdp: country.economy.gdp,
        predictedGrowth: avgGrowthRate + growthTrend * 0.5,
        confidenceInterval: [avgGrowthRate - 0.5, avgGrowthRate + 0.5],
        riskFactor: country.economy.inflation > 5 ? 'high' : country.economy.inflation > 2 ? 'medium' : 'low',
        stabilityIndex: 10 - (country.economy.unemployment + country.economy.inflation / 2) / 2
      };
    });
  };

  // Render different dashboard content based on active tab
  const renderDashboardContent = () => {
    switch (activeTab) {
      case 'economic':
        const economicData = prepareEconomicData();
        return (
          <div className="economic-dashboard">
            <div className="economic-indicators">
              <h3>Economic Indicators</h3>
              <div className="indicators-grid">
                {economicData.map(country => (
                  <div key={country.name} className="country-indicator">
                    <h4>{country.name}</h4>
                    <div>GDP: ${country.gdp.toLocaleString()} billion</div>
                    <div>Growth: {country.growthRate.toFixed(1)}%</div>
                    <div>Inflation: {country.inflation.toFixed(1)}%</div>
                    <div>Unemployment: {country.unemployment.toFixed(1)}%</div>
                  </div>
                ))}
              </div>
            </div>
            <BNPHistoryPanel countries={countries} />
          </div>
        );

      case 'diplomatic':
        const diplomaticData = prepareDiplomaticData();
        return (
          <div className="diplomatic-dashboard">
            <div className="relation-analysis">
              <h3>Diplomatic Relations</h3>
              <div className="relation-grid">
                {diplomaticData.map((relation, index) => (
                  <div key={index} className={`relation-card ${relation.status.toLowerCase()}`}>
                    <div className="relation-header">
                      <span>{relation.source} ↔ {relation.target}</span>
                      <span className={`status-badge ${relation.status.toLowerCase()}`}>{relation.status}</span>
                    </div>
                    <div className="relation-details">
                      <div>Tension: <span className={relation.tension > 70 ? 'high' : relation.tension > 30 ? 'medium' : 'low'}>
                        {relation.tension}%
                      </span></div>
                      <div>Trade agreements: {relation.tradeAgreements?.length || 0}</div>
                      <div>Sanctions: {relation.sanctions?.length || 0}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="tension-map">
              <h3>Global Tension Map</h3>
              <div className="map-container">
                {/* This would be integrated with a map visualization library */}
                <div className="placeholder-map">Map Visualization Placeholder</div>
              </div>
            </div>
          </div>
        );

      case 'trade':
        const tradeData = prepareTradeData();
        return (
          <div className="trade-dashboard">
            <div className="trade-flow-visualization">
              <h3>Global Trade Flows</h3>
              <div className="trade-flow-chart">
                {/* This would be integrated with a sankey diagram or similar flow visualization */}
                <div className="placeholder-chart">Trade Flow Visualization Placeholder</div>
              </div>
            </div>
            <div className="trade-balances">
              <h3>Trade Balances</h3>
              {countries.map(country => (
                <div key={country.name} className="trade-balance-card">
                  <h4>{country.name}</h4>
                  <div className={`balance-value ${country.economy.tradeBalance > 0 ? 'positive' : 'negative'}`}>
                    {country.economy.tradeBalance > 0 ? '+' : ''}{country.economy.tradeBalance.toFixed(1)}B USD
                  </div>
                  <div className="trade-partners">
                    <strong>Top partners:</strong>
                    <ul>
                      {country.economy.topTradePartners?.slice(0, 3).map((partner, idx) => (
                        <li key={idx}>{partner.name} (${partner.volume}B)</li>
                      )) || <li>No data available</li>}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'coalitions':
        const coalitionData = prepareCoalitionData();
        return (
          <div className="coalitions-dashboard">
            <div className="coalition-network">
              <h3>Coalition Network</h3>
              <div className="network-visualization">
                {/* This would be integrated with a network graph visualization */}
                <div className="placeholder-network">Coalition Network Visualization Placeholder</div>
              </div>
            </div>
            <div className="coalition-strength">
              <h3>Coalition Strength Analysis</h3>
              {coalitionData.map(coalition => (
                <div key={coalition.id} className="coalition-card">
                  <h4>{coalition.name}</h4>
                  <div className="coalition-stats">
                    <div>Members: {coalition.members.length}</div>
                    <div>Combined GDP: ${Math.round(coalition.gdpShare).toLocaleString()}B</div>
                    <div>Relative Strength: {Math.round(coalition.strength / (Math.max(...coalitionData.map(c => c.strength)) || 1) * 100)}%</div>
                  </div>
                  <div className="coalition-members">
                    <strong>Members:</strong> {coalition.members.join(', ')}
                  </div>
                </div>
              ))}
              {coalitionData.length === 0 && (
                <div className="no-data-message">No active coalitions in the current game state</div>
              )}
            </div>
          </div>
        );

      case 'predictions':
        const predictionData = preparePredictionData();
        return (
          <div className="predictions-dashboard">
            <div className="trend-predictions">
              <h3>Economic Trend Predictions</h3>
              <div className="prediction-cards">
                {predictionData.map(country => (
                  <div key={country.name} className="prediction-card">
                    <h4>{country.name}</h4>
                    <div className="prediction-detail">
                      <div>Current GDP: ${country.currentGdp.toLocaleString()}B</div>
                      <div>Predicted Growth: <span className={
                        country.predictedGrowth > 3 ? 'positive' : 
                        country.predictedGrowth < 0 ? 'negative' : 'neutral'
                      }>{country.predictedGrowth.toFixed(1)}%</span></div>
                      <div>Confidence Interval: {country.confidenceInterval[0].toFixed(1)}% to {country.confidenceInterval[1].toFixed(1)}%</div>
                      <div>Risk Factor: <span className={country.riskFactor}>{country.riskFactor}</span></div>
                      <div>Stability Index: <span className={
                        country.stabilityIndex > 7 ? 'positive' : 
                        country.stabilityIndex < 4 ? 'negative' : 'neutral'
                      }>{country.stabilityIndex.toFixed(1)}/10</span></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="ai-analysis">
              <h3>AI Strategic Analysis</h3>
              <div className="analysis-content">
                <div className="analysis-section">
                  <h4>Global Economic Outlook</h4>
                  <p>Based on current trends, the global economy is expected to {
                    predictionData.reduce((sum, country) => sum + country.predictedGrowth, 0) / predictionData.length > 2 
                    ? 'grow steadily over the next few turns' 
                    : predictionData.reduce((sum, country) => sum + country.predictedGrowth, 0) / predictionData.length > 0
                    ? 'experience modest growth with regional variations'
                    : 'face challenges with potential recession risks'
                  }.</p>
                </div>
                <div className="analysis-section">
                  <h4>Potential Crisis Points</h4>
                  <ul>
                    {predictionData
                      .filter(country => country.riskFactor === 'high' || country.stabilityIndex < 4)
                      .map(country => (
                        <li key={country.name}>{country.name}: {
                          country.riskFactor === 'high' && country.stabilityIndex < 4
                            ? 'High inflation and political instability'
                            : country.riskFactor === 'high'
                            ? 'Inflation risks'
                            : 'Political instability'
                        }</li>
                      ))}
                    {predictionData.filter(country => country.riskFactor === 'high' || country.stabilityIndex < 4).length === 0 && (
                      <li>No major crisis points detected at this time</li>
                    )}
                  </ul>
                </div>
                <div className="analysis-section">
                  <h4>Strategic Recommendations</h4>
                  <ul>
                    <li>Focus on strengthening trade relations with stable economies</li>
                    <li>Consider diplomatic initiatives to reduce global tensions</li>
                    <li>Monitor high-risk countries for potential market impacts</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        );
      
      default:
        return <div>Select a tab to view data</div>;
    }
  };

  return (
    <div className="enhanced-visualization-dashboard">
      <div className="visualization-header">
        <h2>Enhanced Analytics Dashboard</h2>
        <div className="visualization-controls">
          <div className="time-range-selector">
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value)}
              aria-label="Select time range"
            >
              <option value="all">All Time</option>
              <option value="last5">Last 5 Turns</option>
              <option value="last10">Last 10 Turns</option>
              <option value="last20">Last 20 Turns</option>
            </select>
          </div>
          <div className="mode-selector">
            <select 
              value={viewMode} 
              onChange={(e) => setViewMode(e.target.value)}
              aria-label="Select view mode"
            >
              <option value="detailed">Detailed View</option>
              <option value="summary">Summary View</option>
              <option value="comparative">Comparative View</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="visualization-tabs">
        <button 
          className={activeTab === 'economic' ? 'active' : ''} 
          onClick={() => setActiveTab('economic')}
        >
          Economic
        </button>
        <button 
          className={activeTab === 'diplomatic' ? 'active' : ''} 
          onClick={() => setActiveTab('diplomatic')}
        >
          Diplomatic
        </button>
        <button 
          className={activeTab === 'trade' ? 'active' : ''} 
          onClick={() => setActiveTab('trade')}
        >
          Trade
        </button>
        <button 
          className={activeTab === 'coalitions' ? 'active' : ''} 
          onClick={() => setActiveTab('coalitions')}
        >
          Coalitions
        </button>
        <button 
          className={activeTab === 'predictions' ? 'active' : ''} 
          onClick={() => setActiveTab('predictions')}
        >
          Predictions
        </button>
      </div>
      
      <div className="visualization-content">
        {renderDashboardContent()}
      </div>
      
      <div className="visualization-footer">
        <div className="data-timestamp">
          Data as of Turn {gameState?.currentTurn || 0} | {new Date().toLocaleDateString()}
        </div>
        <div className="visualization-actions">
          <button className="action-button export">Export Data</button>
          <button className="action-button refresh">Refresh</button>
        </div>
      </div>
    </div>
  );
};

export default EnhancedVisualizationDashboard;