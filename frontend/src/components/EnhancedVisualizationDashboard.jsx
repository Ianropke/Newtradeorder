import React, { useState, useEffect, useRef } from 'react';
import { 
  AreaChart, Area, BarChart, Bar, LineChart, Line, PieChart, Pie, 
  Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ScatterChart, Scatter, ZAxis, ComposedChart
} from 'recharts';
import { scaleLinear } from 'd3-scale';
// Import additional visualization libraries
import { ForceGraph2D } from 'react-force-graph';
// Add CSV export functionality
import { CSVLink } from 'react-csv';
// Add date picker for time series comparison
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

const EnhancedVisualizationDashboard = ({ 
  country, 
  allCountries, 
  tradeData, 
  historicalData,
  policyChanges,
  diplomaticRelations
}) => {
  const [activeDashboard, setActiveDashboard] = useState('trade');
  const [tradeFlowData, setTradeFlowData] = useState([]);
  const [economicImpactData, setEconomicImpactData] = useState([]);
  const [tariffImpactData, setTariffImpactData] = useState([]);
  const [diplomaticHeatmapData, setDiplomaticHeatmapData] = useState([]);
  // New state variables for enhanced features
  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [selectedCountries, setSelectedCountries] = useState([]);
  const [selectedIndicator, setSelectedIndicator] = useState('gdp');
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [networkData, setNetworkData] = useState({ nodes: [], links: [] });
  // Export data state
  const [exportData, setExportData] = useState([]);
  const [showTimeSeriesComparison, setShowTimeSeriesComparison] = useState(false);
  // Reference to the network graph
  const networkRef = useRef();
  
  useEffect(() => {
    if (!country || !allCountries) return;
    
    // Process trade flow data
    processTradeData();
    
    // Process economic impact data
    processEconomicImpactData();
    
    // Process diplomatic relations data for heatmap
    processDiplomaticData();
    
    // Process time series data for comparison feature
    processTimeSeriesData();
    
    // Process network graph data for diplomatic relations
    processNetworkData();
  }, [country, allCountries, tradeData, historicalData, policyChanges, diplomaticRelations, selectedCountries, selectedIndicator]);
  
  const processTradeData = () => {
    if (!country || !tradeData) return;
    
    const tradePartners = Object.keys(tradeData || {}).map(partnerCode => {
      const partnerCountry = allCountries[partnerCode];
      if (!partnerCountry) return null;
      
      return {
        name: partnerCountry.name,
        code: partnerCode,
        exports: tradeData[partnerCode]?.exports || 0,
        imports: tradeData[partnerCode]?.imports || 0,
        balance: (tradeData[partnerCode]?.exports || 0) - (tradeData[partnerCode]?.imports || 0),
        gdp: partnerCountry.gdp,
        ratio: partnerCountry.gdp / country.gdp
      };
    }).filter(Boolean);
    
    tradePartners.sort((a, b) => (b.imports + b.exports) - (a.imports + a.exports));
    
    setTradeFlowData(tradePartners.slice(0, 10));
  };
  
  const processEconomicImpactData = () => {
    if (!policyChanges || !historicalData) return;
    
    const impacts = [];
    const indicators = ['gdp', 'unemployment', 'inflation', 'approval'];
    
    policyChanges.forEach(change => {
      const dataPoint = historicalData.find(d => 
        Math.abs(new Date(d.date) - new Date(change.date)) < 1000*60*60*24*30
      );
      
      if (dataPoint) {
        impacts.push({
          date: change.date,
          policy: change.policy,
          value: change.value,
          target: change.target,
          gdpChange: dataPoint.gdpChange,
          unemploymentChange: dataPoint.unemploymentChange,
          inflationChange: dataPoint.inflationChange,
          approvalChange: dataPoint.approvalChange,
          combinedIndex: (dataPoint.gdpChange * 2) - 
                         (dataPoint.unemploymentChange * 0.5) - 
                         (dataPoint.inflationChange * 0.5) +
                         (dataPoint.approvalChange * 0.3)
        });
      }
    });
    
    setEconomicImpactData(impacts);
    
    const tariffData = policyChanges
      .filter(change => change.policy === 'tariff')
      .map(change => {
        const matchingData = impacts.find(i => i.date === change.date);
        return {
          date: change.date,
          value: change.value,
          target: change.target === 'all' ? 'Global' : allCountries[change.target]?.name || change.target,
          economicImpact: matchingData?.combinedIndex || 0,
          tradeVolumeChange: matchingData?.tradeVolumeChange || 0
        };
      });
    
    setTariffImpactData(tariffData);
  };
  
  const processDiplomaticData = () => {
    if (!diplomaticRelations || !allCountries) return;
    
    const heatmapData = diplomaticRelations.map(relation => {
      const countryA = allCountries[relation.country_a];
      const countryB = allCountries[relation.country_b];
      
      if (!countryA || !countryB) return null;
      
      return {
        countryA: countryA.name,
        countryB: countryB.name,
        relationLevel: relation.relation_level,
        tradeVolume: relation.trade_volume || 0,
        agreements: relation.agreements || []
      };
    }).filter(Boolean);
    
    setDiplomaticHeatmapData(heatmapData);
  };
  
  const processTimeSeriesData = () => {
    if (!historicalData || !allCountries) return;
    
    const countriesToCompare = selectedCountries.length > 0 
      ? selectedCountries 
      : [country?.code];
      
    let filteredData = [...historicalData];
    if (startDate && endDate) {
      filteredData = filteredData.filter(data => {
        const dataDate = new Date(data.date);
        return dataDate >= startDate && dataDate <= endDate;
      });
    }
    
    const timeSeriesDataPoints = filteredData.map(dataPoint => {
      const point = { date: dataPoint.date };
      
      countriesToCompare.forEach(countryCode => {
        if (dataPoint[countryCode]) {
          const countryName = allCountries[countryCode]?.name || countryCode;
          point[countryName] = dataPoint[countryCode][selectedIndicator];
        }
      });
      
      return point;
    });
    
    setTimeSeriesData(timeSeriesDataPoints);
    
    setExportData(timeSeriesDataPoints);
  };
  
  const processNetworkData = () => {
    if (!diplomaticRelations || !allCountries) return;
    
    const nodes = Object.entries(allCountries).map(([code, countryData]) => ({
      id: code,
      name: countryData.name,
      gdp: countryData.gdp,
      val: Math.log(countryData.gdp || 1000) / 10,
      color: code === country?.code ? '#ff5722' : '#1976d2'
    }));
    
    const links = diplomaticRelations.map(relation => ({
      source: relation.country_a,
      target: relation.country_b,
      value: relation.trade_volume ? Math.log(relation.trade_volume) / 10 : 1,
      color: relation.relation_level >= 0 ? 
        `rgba(76, 175, 80, ${0.3 + relation.relation_level * 0.7})` : 
        `rgba(244, 67, 54, ${0.3 + Math.abs(relation.relation_level) * 0.7})`
    }));
    
    setNetworkData({ nodes, links });
  };
  
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];
  
  const getRelationColor = (level) => {
    const colorScale = scaleLinear()
      .domain([-1, -0.5, 0, 0.5, 1])
      .range(['#d32f2f', '#f57c00', '#ffd54f', '#66bb6a', '#388e3c']);
    
    return colorScale(level);
  };
  
  const renderTradeFlowDashboard = () => {
    if (!tradeFlowData || tradeFlowData.length === 0) {
      return <div className="loading-placeholder">Loading trade data...</div>;
    }
    
    const totalExports = tradeFlowData.reduce((sum, partner) => sum + partner.exports, 0);
    const totalImports = tradeFlowData.reduce((sum, partner) => sum + partner.imports, 0);
    
    return (
      <div className="dashboard-content">
        <h3>Global Trade Flows</h3>
        <div className="dashboard-row">
          <div className="chart-container half-width">
            <h4>Top Trading Partners</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={tradeFlowData}
                margin={{ top: 20, right: 30, left: 20, bottom: 70 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip formatter={(value) => `$${(value/1000).toFixed(1)} billion`} />
                <Legend />
                <Bar dataKey="exports" name="Exports" stackId="a" fill="#4CAF50" />
                <Bar dataKey="imports" name="Imports" stackId="a" fill="#2196F3" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="chart-container half-width">
            <h4>Trade Balance</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={tradeFlowData}
                margin={{ top: 20, right: 30, left: 20, bottom: 70 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip 
                  formatter={(value) => `$${(value/1000).toFixed(1)} billion`}
                  labelFormatter={(label) => `Balance with ${label}`}
                />
                <Bar 
                  dataKey="balance" 
                  name="Trade Balance" 
                  fill={(data) => data.balance >= 0 ? '#4CAF50' : '#F44336'}
                >
                  {tradeFlowData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.balance >= 0 ? '#4CAF50' : '#F44336'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="dashboard-row">
          <div className="chart-container half-width">
            <h4>Export Distribution</h4>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={tradeFlowData}
                  dataKey="exports"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  label={({name, percent}) => `${name}: ${(percent * 100).toFixed(1)}%`}
                >
                  {tradeFlowData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${(value/1000).toFixed(1)} billion`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div className="chart-container half-width">
            <h4>Import Distribution</h4>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={tradeFlowData}
                  dataKey="imports"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  label={({name, percent}) => `${name}: ${(percent * 100).toFixed(1)}%`}
                >
                  {tradeFlowData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${(value/1000).toFixed(1)} billion`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="dashboard-row">
          <div className="chart-container full-width">
            <h4>Trade Flow Heat Map</h4>
            <div className="heat-map-container" style={{ height: '400px' }}>
              <div className="heat-map-placeholder">
                <p>Interactive trade flow heat map showing global trade connections</p>
                <div className="heat-map-legend">
                  <div className="legend-item">
                    <div className="color-box" style={{ backgroundColor: '#e3f2fd' }}></div>
                    <span>Low trade volume</span>
                  </div>
                  <div className="legend-item">
                    <div className="color-box" style={{ backgroundColor: '#2196f3' }}></div>
                    <span>Medium trade volume</span>
                  </div>
                  <div className="legend-item">
                    <div className="color-box" style={{ backgroundColor: '#0d47a1' }}></div>
                    <span>High trade volume</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  const renderEconomicImpactDashboard = () => {
    if (!economicImpactData || economicImpactData.length === 0) {
      return <div className="loading-placeholder">Loading economic impact data...</div>;
    }
    
    const latestData = economicImpactData[economicImpactData.length - 1];
    const radarData = [
      { subject: 'GDP Growth', A: latestData?.gdpChange || 0, fullMark: 5 },
      { subject: 'Employment', A: -1 * (latestData?.unemploymentChange || 0), fullMark: 5 },
      { subject: 'Price Stability', A: -1 * (latestData?.inflationChange || 0), fullMark: 5 },
      { subject: 'Approval', A: latestData?.approvalChange || 0, fullMark: 5 },
      { subject: 'Trade Balance', A: latestData?.tradeBalanceChange || 0, fullMark: 5 }
    ];
    
    return (
      <div className="dashboard-content">
        <h3>Economic Impact Analysis</h3>
        
        <div className="dashboard-row">
          <div className="chart-container half-width">
            <h4>Policy Impact on Economic Indicators</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={economicImpactData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="gdpChange" name="GDP Change %" stroke="#4CAF50" />
                <Line type="monotone" dataKey="unemploymentChange" name="Unemployment Δ" stroke="#F44336" />
                <Line type="monotone" dataKey="inflationChange" name="Inflation Δ" stroke="#FF9800" />
                <Line type="monotone" dataKey="approvalChange" name="Approval Δ" stroke="#2196F3" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <div className="chart-container half-width">
            <h4>Current Economic Health</h4>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart outerRadius={100} width={500} height={300} data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis angle={30} domain={[-5, 5]} />
                <Radar name="Economic Health" dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="dashboard-row">
          <div className="chart-container full-width">
            <h4>Tariff Impact Analysis</h4>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart
                data={tariffImpactData}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="value" name="Tariff Rate %" stroke="#8884d8" fill="#8884d8" />
                <Area type="monotone" dataKey="economicImpact" name="Economic Impact" stroke="#82ca9d" fill="#82ca9d" />
                <Area type="monotone" dataKey="tradeVolumeChange" name="Trade Volume Δ" stroke="#ffc658" fill="#ffc658" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="dashboard-row">
          <div className="chart-container full-width">
            <h4>Policy Change Distribution</h4>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'Tariff Policies', value: policyChanges.filter(p => p.policy === 'tariff').length },
                    { name: 'Tax Policies', value: policyChanges.filter(p => p.policy === 'tax').length },
                    { name: 'Subsidy Policies', value: policyChanges.filter(p => p.policy === 'subsidy').length },
                    { name: 'Other Policies', value: policyChanges.filter(p => !['tariff', 'tax', 'subsidy'].includes(p.policy)).length }
                  ]}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  label
                >
                  {[0, 1, 2, 3].map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  };
  
  const renderDiplomaticDashboard = () => {
    if (!diplomaticHeatmapData || diplomaticHeatmapData.length === 0) {
      return <div className="loading-placeholder">Loading diplomatic data...</div>;
    }
    
    const countryRelationData = diplomaticHeatmapData
      .filter(relation => relation.countryA === country.name || relation.countryB === country.name)
      .map(relation => {
        const otherCountry = relation.countryA === country.name ? relation.countryB : relation.countryA;
        return {
          country: otherCountry,
          relationLevel: relation.relationLevel,
          tradeVolume: relation.tradeVolume,
          agreements: relation.agreements
        };
      })
      .sort((a, b) => b.relationLevel - a.relationLevel);
    
    return (
      <div className="dashboard-content">
        <h3>Diplomatic Relations Analysis</h3>
        
        <div className="dashboard-row">
          <div className="chart-container full-width">
            <h4>Global Diplomatic Network</h4>
            <div className="network-controls">
              <button 
                onClick={() => networkRef.current && networkRef.current.zoomToFit(400)}
                className="control-button"
              >
                Zoom to Fit
              </button>
              <div className="network-legend">
                <div className="legend-item">
                  <div className="color-dot" style={{backgroundColor: '#ff5722'}}></div>
                  <span>Current Country</span>
                </div>
                <div className="legend-item">
                  <div className="color-dot" style={{backgroundColor: '#1976d2'}}></div>
                  <span>Other Countries</span>
                </div>
                <div className="legend-item">
                  <div className="color-line" style={{backgroundColor: 'rgba(76, 175, 80, 0.7)'}}></div>
                  <span>Positive Relations</span>
                </div>
                <div className="legend-item">
                  <div className="color-line" style={{backgroundColor: 'rgba(244, 67, 54, 0.7)'}}></div>
                  <span>Negative Relations</span>
                </div>
              </div>
            </div>
            <div style={{ height: '500px', width: '100%' }}>
              {networkData.nodes.length > 0 && (
                <ForceGraph2D
                  ref={networkRef}
                  graphData={networkData}
                  nodeLabel={node => `${node.name}: GDP $${(node.gdp/1000).toFixed(1)} billion`}
                  linkLabel={link => {
                    const sourceCountry = allCountries[link.source.id || link.source]?.name;
                    const targetCountry = allCountries[link.target.id || link.target]?.name;
                    return `${sourceCountry} — ${targetCountry}`;
                  }}
                  linkWidth={link => link.value}
                  linkColor={link => link.color}
                  nodeCanvasObject={(node, ctx, globalScale) => {
                    const label = node.name;
                    const fontSize = 12/globalScale;
                    ctx.font = `${fontSize}px Sans-Serif`;
                    const textWidth = ctx.measureText(label).width;
                    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);
                    
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, node.val, 0, 2 * Math.PI, false);
                    ctx.fillStyle = node.color;
                    ctx.fill();
                    
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                    ctx.fillRect(
                      node.x - bckgDimensions[0] / 2,
                      node.y + node.val + 2,
                      bckgDimensions[0],
                      bckgDimensions[1]
                    );
                    
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#000';
                    ctx.fillText(
                      label,
                      node.x,
                      node.y + node.val + 2 + bckgDimensions[1]/2
                    );
                  }}
                  cooldownTicks={100}
                  onEngineStop={() => networkRef.current && networkRef.current.zoomToFit(400)}
                />
              )}
            </div>
          </div>
        </div>
        
        <div className="dashboard-row">
          <div className="chart-container full-width">
            <h4>Diplomatic Relations Heat Map</h4>
            <div className="diplomatic-heat-map">
              <div className="heat-map-legend">
                <div className="legend-title">Relation Level</div>
                <div className="legend-scale">
                  <div className="legend-item">
                    <div className="color-box" style={{ backgroundColor: '#d32f2f' }}></div>
                    <span>Hostile (-1.0)</span>
                  </div>
                  <div className="legend-item">
                    <div className="color-box" style={{ backgroundColor: '#f57c00' }}></div>
                    <span>Tense (-0.5)</span>
                  </div>
                  <div className="legend-item">
                    <div className="color-box" style={{ backgroundColor: '#ffd54f' }}></div>
                    <span>Neutral (0.0)</span>
                  </div>
                  <div className="legend-item">
                    <div className="color-box" style={{ backgroundColor: '#66bb6a' }}></div>
                    <span>Friendly (0.5)</span>
                  </div>
                  <div className="legend-item">
                    <div className="color-box" style={{ backgroundColor: '#388e3c' }}></div>
                    <span>Allied (1.0)</span>
                  </div>
                </div>
              </div>
              
              <div className="heat-map-grid">
                {countryRelationData.slice(0, 15).map((relation, index) => (
                  <div 
                    key={`relation-${index}`}
                    className="heat-map-cell"
                    style={{ 
                      backgroundColor: getRelationColor(relation.relationLevel),
                      opacity: 0.7 + (relation.tradeVolume / 10000) * 0.3
                    }}
                    title={`${relation.country}: Relation Level ${relation.relationLevel.toFixed(2)}, Trade Volume: $${(relation.tradeVolume/1000).toFixed(1)} billion`}
                  >
                    <div className="heat-map-cell-content">
                      <div className="country-name">{relation.country}</div>
                      <div className="relation-value">{relation.relationLevel.toFixed(2)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        
        <div className="dashboard-row">
          <div className="chart-container half-width">
            <h4>Relations Distribution</h4>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'Allied (0.5 to 1.0)', value: countryRelationData.filter(r => r.relationLevel >= 0.5).length },
                    { name: 'Friendly (0 to 0.5)', value: countryRelationData.filter(r => r.relationLevel >= 0 && r.relationLevel < 0.5).length },
                    { name: 'Neutral (-0.2 to 0)', value: countryRelationData.filter(r => r.relationLevel >= -0.2 && r.relationLevel < 0).length },
                    { name: 'Tense (-0.5 to -0.2)', value: countryRelationData.filter(r => r.relationLevel >= -0.5 && r.relationLevel < -0.2).length },
                    { name: 'Hostile (-1.0 to -0.5)', value: countryRelationData.filter(r => r.relationLevel < -0.5).length }
                  ]}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  label
                >
                  <Cell fill="#388e3c" />
                  <Cell fill="#66bb6a" />
                  <Cell fill="#ffd54f" />
                  <Cell fill="#f57c00" />
                  <Cell fill="#d32f2f" />
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div className="chart-container half-width">
            <h4>Trade Agreements</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={[
                  { name: 'Free Trade', count: countryRelationData.filter(r => r.agreements.includes('free_trade')).length },
                  { name: 'Preferential', count: countryRelationData.filter(r => r.agreements.includes('preferential')).length },
                  { name: 'Customs Union', count: countryRelationData.filter(r => r.agreements.includes('customs_union')).length },
                  { name: 'Military', count: countryRelationData.filter(r => r.agreements.includes('military')).length },
                  { name: 'Cultural', count: countryRelationData.filter(r => r.agreements.includes('cultural')).length }
                ]}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" name="Number of Agreements" fill="#4CAF50" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  };
  
  const renderTimeSeriesComparison = () => {
    if (!timeSeriesData || timeSeriesData.length === 0) {
      return <div className="loading-placeholder">No time series data available</div>;
    }
    
    const availableCountries = Object.entries(allCountries)
      .filter(([code]) => code !== country?.code)
      .map(([code, countryData]) => ({
        code,
        name: countryData.name
      }));
    
    const indicators = [
      { value: 'gdp', label: 'GDP Growth' },
      { value: 'unemployment', label: 'Unemployment Rate' },
      { value: 'inflation', label: 'Inflation Rate' },
      { value: 'approval', label: 'Approval Rating' },
      { value: 'trade_balance', label: 'Trade Balance' }
    ];
    
    const generateCountryColor = (index) => {
      const colors = ['#4CAF50', '#2196F3', '#F44336', '#FF9800', '#9C27B0', '#3F51B5', '#00BCD4', '#009688'];
      return colors[index % colors.length];
    };
    
    return (
      <div className="dashboard-content">
        <h3>Time Series Comparison</h3>
        
        <div className="comparison-controls">
          <div className="control-group">
            <label>Select Indicator:</label>
            <select 
              value={selectedIndicator} 
              onChange={(e) => setSelectedIndicator(e.target.value)}
              className="indicator-select"
            >
              {indicators.map(indicator => (
                <option key={indicator.value} value={indicator.value}>
                  {indicator.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="control-group">
            <label>Date Range:</label>
            <div className="date-pickers">
              <DatePicker
                selected={startDate}
                onChange={date => setStartDate(date)}
                selectsStart
                startDate={startDate}
                endDate={endDate}
                placeholderText="Start Date"
                className="date-picker"
              />
              <DatePicker
                selected={endDate}
                onChange={date => setEndDate(date)}
                selectsEnd
                startDate={startDate}
                endDate={endDate}
                minDate={startDate}
                placeholderText="End Date"
                className="date-picker"
              />
            </div>
          </div>
          
          <div className="control-group">
            <label>Compare Countries:</label>
            <div className="country-select-container">
              <select 
                multiple
                value={selectedCountries}
                onChange={(e) => {
                  const selected = Array.from(e.target.selectedOptions, option => option.value);
                  setSelectedCountries(selected);
                }}
                className="country-multi-select"
              >
                {availableCountries.map(country => (
                  <option key={country.code} value={country.code}>
                    {country.name}
                  </option>
                ))}
              </select>
              <div className="select-helper-text">Hold Ctrl/Cmd to select multiple countries</div>
            </div>
          </div>
          
          <div className="control-group">
            <button 
              onClick={() => processTimeSeriesData()}
              className="update-button"
            >
              Update Comparison
            </button>
            
            <CSVLink 
              data={exportData}
              filename={`trade-data-${selectedIndicator}-${new Date().toISOString().slice(0,10)}.csv`}
              className="export-button"
            >
              Export to CSV
            </CSVLink>
          </div>
        </div>
        
        <div className="dashboard-row">
          <div className="chart-container full-width">
            <h4>{indicators.find(i => i.value === selectedIndicator)?.label || 'Economic Indicator'} Comparison</h4>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart
                data={timeSeriesData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                {Object.keys(timeSeriesData[0] || {})
                  .filter(key => key !== 'date')
                  .map((country, index) => (
                    <Line 
                      key={country}
                      type="monotone" 
                      dataKey={country} 
                      name={country} 
                      stroke={generateCountryColor(index)}
                      activeDot={{ r: 8 }}
                      strokeWidth={2}
                    />
                  ))
                }
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="dashboard-row">
          <div className="chart-container full-width">
            <h4>Comparative Analysis</h4>
            <ResponsiveContainer width="100%" height={400}>
              <ComposedChart
                data={timeSeriesData.filter((_, i) => i % 3 === 0)}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                {Object.keys(timeSeriesData[0] || {})
                  .filter(key => key !== 'date')
                  .map((country, index) => (
                    index === 0 ? (
                      <Area 
                        key={country}
                        type="monotone" 
                        dataKey={country} 
                        name={`${country} (Area)`}
                        fill={generateCountryColor(index)}
                        stroke={generateCountryColor(index)}
                        fillOpacity={0.3}
                      />
                    ) : (
                      <Line 
                        key={country}
                        type="monotone" 
                        dataKey={country} 
                        name={country}
                        stroke={generateCountryColor(index)}
                        dot={{ r: 4 }}
                      />
                    )
                  ))
                }
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="widget enhanced-visualization-dashboard">
      <div className="dashboard-header">
        <h3>Enhanced Visualization Dashboard</h3>
        <div className="dashboard-tabs">
          <button 
            className={`tab-button ${activeDashboard === 'trade' ? 'active' : ''}`}
            onClick={() => setActiveDashboard('trade')}
          >
            Global Trade Flows
          </button>
          <button 
            className={`tab-button ${activeDashboard === 'economic' ? 'active' : ''}`}
            onClick={() => setActiveDashboard('economic')}
          >
            Economic Impacts
          </button>
          <button 
            className={`tab-button ${activeDashboard === 'diplomatic' ? 'active' : ''}`}
            onClick={() => setActiveDashboard('diplomatic')}
          >
            Diplomatic Relations
          </button>
          <button 
            className={`tab-button ${activeDashboard === 'timeseries' ? 'active' : ''}`}
            onClick={() => setActiveDashboard('timeseries')}
          >
            Time Series Comparison
          </button>
        </div>
      </div>
      
      <div className="dashboard-container">
        {activeDashboard === 'trade' && renderTradeFlowDashboard()}
        {activeDashboard === 'economic' && renderEconomicImpactDashboard()}
        {activeDashboard === 'diplomatic' && renderDiplomaticDashboard()}
        {activeDashboard === 'timeseries' && renderTimeSeriesComparison()}
      </div>
    </div>
  );
};

export default EnhancedVisualizationDashboard;