import React, { useState, useEffect, useCallback, useRef } from 'react';
import '../styles/CountryAnalysisPanel.css';
import { Line, Bar } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend, 
  TimeScale,
  Filler
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import annotationPlugin from 'chartjs-plugin-annotation';

// Register Chart.js components including annotations for key events
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend, 
  TimeScale,
  Filler,
  ChartDataLabels,
  annotationPlugin
);

function CountryAnalysisPanel({ country, allCountries, diplomacy, historicalData }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [competitorData, setCompetitorData] = useState([]);
  const [tradePartners, setTradePartners] = useState([]);
  const [tradeDependency, setTradeDependency] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [historicalBenchmarks, setHistoricalBenchmarks] = useState(null);
  const [economicTrends, setEconomicTrends] = useState([]);
  const [selectedBenchmarkMetric, setSelectedBenchmarkMetric] = useState('gdp_growth');
  const [dataSource, setDataSource] = useState('real'); // 'real' or 'mock'
  const [keyEvents, setKeyEvents] = useState([]);
  const [comparisonCountries, setComparisonCountries] = useState([]); // Multiple countries comparison
  const [error, setError] = useState(null);
  const [exportLoading, setExportLoading] = useState(false);
  const [showAnnotations, setShowAnnotations] = useState(true);
  const [viewMode, setViewMode] = useState('line'); // 'line' or 'bar'
  const [retryCount, setRetryCount] = useState(0);
  const chartRef = useRef(null);
  const maxRetries = 3;

  // Debounced data fetching to prevent excessive API calls
  const debouncedFetch = useCallback(
    debounce((func) => {
      func();
    }, 300),
    []
  );

  useEffect(() => {
    if (!country || !country.iso_code) return;

    setIsLoading(true);
    setError(null);

    // Fetch data with enhanced error handling
    const fetchAllData = async () => {
      try {
        await Promise.all([
          fetchTradeData(country.iso_code),
          fetchHistoricalBenchmarks(country.iso_code)
        ]);
      } catch (error) {
        console.error("Error in main data fetch:", error);
        handleFetchError(error);
      } finally {
        setIsLoading(false);
      }
    };
    
    debouncedFetch(fetchAllData);
    
    return () => {
      // Cleanup
    };
  }, [country]);

  // Improved error handling with retry mechanism
  const handleFetchError = (error, endpoint = '') => {
    // Create a more user-friendly error message
    const userMessage = `Kunne ikke hente data${endpoint ? ` for ${endpoint}` : ''}: ${error.message || 'Ukendt fejl'}`;
    
    // Log the detailed error for debugging
    console.error(`API Error (${endpoint || 'unknown endpoint'})`, error);
    
    // Decide if we should retry
    if (retryCount < maxRetries) {
      setRetryCount(count => count + 1);
      setError(`${userMessage} - Prøver igen (${retryCount + 1}/${maxRetries})...`);
      
      // Retry with exponential backoff
      setTimeout(() => {
        if (country && country.iso_code) {
          if (endpoint.includes('trade')) {
            fetchTradeData(country.iso_code);
          } else if (endpoint.includes('historical')) {
            fetchHistoricalBenchmarks(country.iso_code);
          } else {
            // Retry all
            fetchTradeData(country.iso_code);
            fetchHistoricalBenchmarks(country.iso_code);
          }
        }
      }, 1000 * Math.pow(2, retryCount));
    } else {
      // Max retries reached, show final error and fallback to mock data
      setError(`${userMessage} - Bruger simulerede data i stedet.`);
      setRetryCount(0);
      
      // Generate mock data as fallback
      if (endpoint.includes('trade') || !endpoint) {
        generateDummyTradeData();
        generateDummyCompetitors();
      }
      
      if (endpoint.includes('historical') || !endpoint) {
        generateMockHistoricalData();
        setDataSource('mock');
      }
    }
  };

  const fetchTradeData = async (iso) => {
    try {
      const partnersRes = await fetch(`/api/trade_partners/${iso}`);
      
      if (!partnersRes.ok) {
        throw new Error(`Status ${partnersRes.status}: ${await partnersRes.text().catch(() => 'Ukendt fejl')}`);
      }
      
      const partnersData = await partnersRes.json();

      if (partnersData.partners) {
        setTradePartners(partnersData.partners);

        const totalTrade = partnersData.partners.reduce((sum, partner) =>
          sum + (partner.importVolume || 0) + (partner.exportVolume || 0), 0);
        setTradeDependency(totalTrade / (country.gdp || 1));
      }

      const competitorsRes = await fetch(`/api/competitors/${iso}`);
      
      if (!competitorsRes.ok) {
        throw new Error(`Status ${competitorsRes.status}: ${await competitorsRes.text().catch(() => 'Ukendt fejl')}`);
      }
      
      const competitorsData = await competitorsRes.json();
      
      if (competitorsData.competitors) {
        setCompetitorData(competitorsData.competitors);
      }
      
      // Reset retry count on success
      setRetryCount(0);
    } catch (error) {
      handleFetchError(error, 'handelsdata');
    }
  };

  const fetchHistoricalBenchmarks = async (iso) => {
    setIsLoading(true);
    try {
      // Clear existing data before fetching new data
      setHistoricalBenchmarks(null);
      setEconomicTrends([]);
      
      // Fetch from our new historical benchmarks endpoint
      const response = await fetch(`/api/countries/${iso}/historical-benchmarks`);
      
      if (!response.ok) {
        const errorMessage = await response.text().catch(() => 'Ukendt fejl');
        throw new Error(`Status ${response.status}: ${errorMessage}`);
      }
      
      const data = await response.json();
      console.log("Received historical data:", data);
      
      if (data.status === 'mock') {
        console.info("Using mock historical data from server:", data.message);
        setDataSource('mock');
      } else {
        setDataSource('real');
      }
      
      setHistoricalBenchmarks(data);

      // Process the trends data
      if (data.metrics && data.years) {
        processHistoricalTrends(data);
      }
      
      // Extract key historical events if available
      if (data.key_events) {
        setKeyEvents(data.key_events);
      }
      
      // Reset retry count on success
      setRetryCount(0);
    } catch (error) {
      handleFetchError(error, 'historiske data');
    } finally {
      setIsLoading(false);
    }
  };

  // Process historical trends data from the API
  const processHistoricalTrends = (data) => {
    if (!data.metrics || !data.years || data.years.length === 0) return;
    
    const trends = [];
    
    // Define the metrics we want to process
    const metricsToProcess = ['gdp_growth', 'inflation', 'unemployment', 'trade_balance'];
    
    metricsToProcess.forEach(metric => {
      if (data.metrics[metric]) {
        // Format the trend data for the chart
        trends.push({
          metric: metric,
          years: data.years,
          countryValues: data.metrics[metric].country_values || [],
          regionalValues: data.metrics[metric].regional_values || [],
          globalValues: data.metrics[metric].global_values || []
        });
      }
    });
    
    setEconomicTrends(trends);
    
    // Calculate performance metrics if not provided by the backend
    if (!data.performance) {
      calculatePerformanceMetrics(data);
    }
    
    // Generate summary trends for overview tab
    generateTrendSummaries(data);
  };

  const renderBenchmarkChart = () => {
    if (!historicalBenchmarks || !economicTrends.length) {
      return <div className="loading-placeholder">Indlæser historiske data...</div>;
    }
    
    // Find the selected trend data
    const selectedTrend = economicTrends.find(trend => trend.metric === selectedBenchmarkMetric);
    if (!selectedTrend) {
      return <div className="error-message">Ingen data tilgængelig for valgte metrik.</div>;
    }
    
    // Prepare chart data
    const labels = selectedTrend.years;
    
    const countryName = historicalBenchmarks.country_name || country.name;
    const regionName = historicalBenchmarks.region || 'Region';
    
    const datasets = [
      {
        label: countryName,
        data: selectedTrend.countryValues,
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.5)',
        borderWidth: 2,
        fill: showAnnotations ? 'origin' : false,
      },
      {
        label: `${regionName} gennemsnit`,
        data: selectedTrend.regionalValues,
        borderColor: '#2ecc71',
        backgroundColor: 'rgba(46, 204, 113, 0.3)',
        borderWidth: 2,
        borderDash: [5, 5],
        fill: false,
      },
      {
        label: 'Globalt gennemsnit',
        data: selectedTrend.globalValues,
        borderColor: '#e74c3c',
        backgroundColor: 'rgba(231, 76, 60, 0.3)',
        borderWidth: 1,
        borderDash: [2, 2],
        fill: false,
      }
    ];
    
    // Add annotations for key events if available and annotations are enabled
    const annotations = {};
    if (showAnnotations && keyEvents && keyEvents.length > 0) {
      keyEvents.forEach((event, index) => {
        const yearIndex = labels.indexOf(event.year);
        if (yearIndex > -1) {
          annotations[`event-${index}`] = {
            type: 'line',
            scaleID: 'x',
            value: event.year,
            borderColor: event.impact === 'Negative' ? 'rgba(231, 76, 60, 0.7)' : 'rgba(46, 204, 113, 0.7)',
            borderWidth: event.magnitude === 'Very High' ? 2 : 1,
            label: {
              content: event.event,
              enabled: true,
              position: 'top',
              backgroundColor: event.impact === 'Negative' ? 'rgba(231, 76, 60, 0.9)' : 'rgba(46, 204, 113, 0.9)',
              fontColor: 'white',
              yAdjust: -10,
            }
          };
        }
      });
    }
    
    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          title: {
            display: true,
            text: getMetricLabel(selectedBenchmarkMetric) + ' (%)'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'År'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        }
      },
      plugins: {
        legend: {
          position: 'top',
        },
        annotation: {
          annotations: annotations
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || '';
              if (label) {
                label += ': ';
              }
              if (context.parsed.y !== null) {
                label += context.parsed.y.toFixed(1) + '%';
              }
              return label;
            }
          }
        }
      }
    };
    
    if (viewMode === 'line') {
      return (
        <Line ref={chartRef} data={{ labels, datasets }} options={chartOptions} />
      );
    } else {
      return (
        <Bar ref={chartRef} data={{ labels, datasets }} options={chartOptions} />
      );
    }
  };

  const renderBenchmarkControls = () => {
    return (
      <div className="benchmark-controls">
        <div className="metric-selector">
          <label htmlFor="metric-select">Vælg Økonomisk Indikator:</label>
          <select 
            id="metric-select" 
            value={selectedBenchmarkMetric}
            onChange={(e) => setSelectedBenchmarkMetric(e.target.value)}
          >
            <option value="gdp_growth">BNP Vækst</option>
            <option value="inflation">Inflation</option>
            <option value="unemployment">Arbejdsløshed</option>
            <option value="trade_balance">Handelsbalance</option>
          </select>
        </div>
        
        <div className="view-toggles">
          <button 
            className={`view-toggle ${viewMode === 'line' ? 'active' : ''}`}
            onClick={() => setViewMode('line')}
          >
            Linjediagram
          </button>
          <button 
            className={`view-toggle ${viewMode === 'bar' ? 'active' : ''}`}
            onClick={() => setViewMode('bar')}
          >
            Søjlediagram
          </button>
          <button 
            className={`annotation-toggle ${showAnnotations ? 'active' : ''}`}
            onClick={() => setShowAnnotations(!showAnnotations)}
          >
            {showAnnotations ? 'Skjul begivenheder' : 'Vis begivenheder'}
          </button>
        </div>
        
        {dataSource === 'mock' && (
          <div className="data-source-notice">
            <i className="fas fa-info-circle"></i> Anvender simulerede historiske data
          </div>
        )}
      </div>
    );
  };

  // Utility function for debouncing
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  if (!country) {
    return (
      <div className="widget">
        <h3>Landeanalyse</h3>
        <p>Vælg et land for at se analysen.</p>
      </div>
    );
  }

  return (
    <div className="widget country-analysis-panel">
      <h3>Landeanalyse: {country.name}</h3>
      
      {isLoading && <div className="loading-indicator">Indlæser data...</div>}
      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <span className="error-text">{error}</span>
          <button className="dismiss-error" onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <div className="tabs">
        <button
          className={activeTab === 'overview' ? 'active-tab' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overblik
        </button>
        <button
          className={activeTab === 'trade' ? 'active-tab' : ''}
          onClick={() => setActiveTab('trade')}
        >
          Handelsafhængighed
        </button>
        <button
          className={activeTab === 'competitors' ? 'active-tab' : ''}
          onClick={() => setActiveTab('competitors')}
        >
          Konkurrenter
        </button>
        <button
          className={activeTab === 'historical' ? 'active-tab' : ''}
          onClick={() => setActiveTab('historical')}
        >
          Historisk Benchmark
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-container">
            <div className="key-indicators">
              <div className="indicator">
                <span className="indicator-label">BNP (mia.):</span>
                <span className="indicator-value">{country.gdp ? country.gdp.toFixed(1) : 'N/A'}</span>
              </div>
              <div className="indicator">
                <span className="indicator-label">Befolkning:</span>
                <span className="indicator-value">{country.population ? (country.population / 1000000).toFixed(1) + ' mio.' : 'N/A'}</span>
              </div>
              <div className="indicator">
                <span className="indicator-label">BNP per capita:</span>
                <span className="indicator-value">
                  {country.gdp && country.population ? (country.gdp * 1000000000 / country.population).toFixed(0) : 'N/A'}
                </span>
              </div>
              <div className="indicator">
                <span className="indicator-label">Handelsafhængighed:</span>
                <span className="indicator-value">
                  {tradeDependency ? (tradeDependency * 100).toFixed(1) + '%' : 'N/A'}
                </span>
              </div>
            </div>

            <div className="country-industries">
              <h4>Nøgleindustrier</h4>
              {country.industries ? (
                <ul className="industry-list">
                  {Object.entries(country.industries)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 5)
                    .map(([industry, value], index) => (
                      <li key={index} className="industry-item">
                        <span className="industry-name">{industry}</span>
                        <div className="industry-bar-container">
                          <div
                            className="industry-bar"
                            style={{ width: `${value * 100}%` }}
                          ></div>
                          <span className="industry-value">{(value * 100).toFixed(1)}%</span>
                        </div>
                      </li>
                    ))
                  }
                </ul>
              ) : (
                <p>Ingen industridata tilgængelige.</p>
              )}
            </div>

            <div className="economic-trends">
              <h4>Økonomiske nøgletal</h4>
              <table className="trends-table">
                <thead>
                  <tr>
                    <th>Indikator</th>
                    <th>Aktuel</th>
                    <th>Seneste 5 år</th>
                    <th>Vurdering</th>
                  </tr>
                </thead>
                <tbody>
                  {economicTrends.filter(trend => typeof trend.trend === 'string').map((trend, index) => (
                    <tr key={index}>
                      <td>{trend.trend}</td>
                      <td>{trend.current}</td>
                      <td>{trend.last_5_years}</td>
                      <td className={trend.outlook.toLowerCase().includes('positiv') || 
                                      trend.outlook.toLowerCase().includes('stærk') ? 
                                      'positive-outlook' : 
                                      trend.outlook.toLowerCase().includes('stabil') ? 
                                      'neutral-outlook' : 'negative-outlook'}>
                        {trend.outlook}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {historicalBenchmarks && historicalBenchmarks.performance && (
              <div className="performance-summary">
                <h4>Performance vs. region</h4>
                <div className="performance-metrics">
                  <div className="performance-metric">
                    <div className="metric-label">BNP Vækst</div>
                    <div className="metric-values">
                      <div>{historicalBenchmarks.performance.gdp_growth?.toFixed(1)}%</div>
                      <div className="region-value">Region: {historicalBenchmarks.performance.region_gdp_growth?.toFixed(1)}%</div>
                    </div>
                    <div className={`performance-indicator ${historicalBenchmarks.performance.relative_performance > 0 ? 'positive' : 'negative'}`}>
                      {historicalBenchmarks.performance.relative_performance > 0 ? '+' : ''}
                      {historicalBenchmarks.performance.relative_performance?.toFixed(1)}%
                    </div>
                  </div>
                  
                  <div className="performance-metric">
                    <div className="metric-label">Arbejdsløshed</div>
                    <div className="metric-values">
                      <div>{historicalBenchmarks.performance.unemployment?.toFixed(1)}%</div>
                      <div className="region-value">Region: {historicalBenchmarks.performance.region_unemployment?.toFixed(1)}%</div>
                    </div>
                    <div className={`performance-indicator ${historicalBenchmarks.performance.unemployment_performance > 0 ? 'positive' : 'negative'}`}>
                      {historicalBenchmarks.performance.unemployment_performance > 0 ? '+' : ''}
                      {historicalBenchmarks.performance.unemployment_performance?.toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'trade' && (
          <div className="trade-tab">
            <div className="trade-analysis">
              <h4>Handelspartnere</h4>
              {tradePartners.length > 0 ? (
                <div className="partners-table-container">
                  <table className="partners-table">
                    <thead>
                      <tr>
                        <th>Land</th>
                        <th>Import (mia.)</th>
                        <th>Eksport (mia.)</th>
                        <th>Balance</th>
                        <th>Afhængighed</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tradePartners.map((partner, index) => (
                        <tr key={index} className={partner.isCritical ? 'critical-partner' : ''}>
                          <td>{partner.country?.name || partner.iso_code}</td>
                          <td>{partner.importVolume?.toFixed(1)}</td>
                          <td>{partner.exportVolume?.toFixed(1)}</td>
                          <td className={partner.tradeBalance > 0 ? 'positive-balance' : 'negative-balance'}>
                            {partner.tradeBalance?.toFixed(1)}
                          </td>
                          <td>{(partner.dependencyScore * 100)?.toFixed(1)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p>Ingen handelspartnerdata tilgængelige.</p>
              )}
            </div>
            
            {historicalBenchmarks && historicalBenchmarks.metrics && historicalBenchmarks.metrics.trade_balance && (
              <div className="trade-trends">
                <h4>Handelsbalance udvikling</h4>
                <div className="chart-container trade-chart">
                  <Line 
                    data={{
                      labels: historicalBenchmarks.years || [],
                      datasets: [
                        {
                          label: 'Handelsbalance (% af BNP)',
                          data: historicalBenchmarks.metrics.trade_balance.country_values || [],
                          borderColor: '#3f51b5',
                          backgroundColor: 'rgba(63, 81, 181, 0.1)',
                          tension: 0.3,
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: {
                          title: {
                            display: true,
                            text: '% af BNP'
                          },
                          grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                          }
                        },
                        x: {
                          title: {
                            display: true,
                            text: 'År'
                          },
                          grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                          }
                        }
                      }
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'competitors' && (
          <div className="competitors-tab">
            <h4>Væsentlige konkurrenter</h4>
            {competitorData.length > 0 ? (
              <div className="competitors-container">
                <table className="competitors-table">
                  <thead>
                    <tr>
                      <th>Land</th>
                      <th>Overlappende Industrier</th>
                      <th>Konkurrenceintensitet</th>
                    </tr>
                  </thead>
                  <tbody>
                    {competitorData.map((competitor, index) => (
                      <tr key={index}>
                        <td>{competitor.country?.name}</td>
                        <td>
                          {Object.entries(competitor.mainIndustries)
                            .sort((a, b) => b[1] - a[1])
                            .slice(0, 2)
                            .map(([industry]) => industry)
                            .join(', ')}
                        </td>
                        <td>
                          <div className="intensity-bar-container">
                            <div
                              className="intensity-bar"
                              style={{ width: `${competitor.competitionIntensity * 100}%` }}
                            ></div>
                            <span className="intensity-label">
                              {(competitor.competitionIntensity * 100).toFixed(0)}%
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>Ingen konkurrentdata tilgængelige.</p>
            )}
          </div>
        )}

        {activeTab === 'historical' && (
          <div className="historical-tab">
            <div className="historical-controls">
              <div className="data-source">
                <span className="source-label">Datakilde: </span>
                <span className={`source-indicator ${dataSource}`}>
                  {dataSource === 'real' ? 'Faktiske data' : 'Simulerede data'}
                </span>
              </div>
              
              <div className="metrics-visualization-container">
                <div className="metric-selector">
                  <label htmlFor="metric-select">Metrik:</label>
                  <select 
                    id="metric-select"
                    value={selectedBenchmarkMetric}
                    onChange={(e) => setSelectedBenchmarkMetric(e.target.value)}
                    disabled={isLoading}
                  >
                    <option value="gdp_growth">BNP Vækst</option>
                    <option value="inflation">Inflation</option>
                    <option value="unemployment">Arbejdsløshed</option>
                    <option value="trade_balance">Handelsbalance</option>
                  </select>
                </div>
                
                {renderBenchmarkControls()}
              </div>
            </div>
            
            <div className="chart-and-events-container">
              {renderBenchmarkChart()}
            </div>
            
            {isLoading && (
              <div className="loading-overlay">
                <div className="loading-spinner"></div>
                <div className="loading-text">Indlæser data...</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default CountryAnalysisPanel;