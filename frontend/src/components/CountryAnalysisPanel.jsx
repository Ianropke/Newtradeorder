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

// Add the missing debounce function
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

  // Helper function for getting human-readable metric labels
  const getMetricLabel = (metricKey) => {
    const metricLabels = {
      'gdp_growth': 'BNP Vækst',
      'inflation': 'Inflation',
      'unemployment': 'Arbejdsløshed',
      'trade_balance': 'Handelsbalance',
      'government_debt': 'Offentlig Gæld',
      'fdi': 'Udenlandske Investeringer',
      'industrial_production': 'Industriproduktion'
    };
    
    return metricLabels[metricKey] || metricKey;
  };

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
            // General retry
            debouncedFetch(() => fetchAllData());
          }
        }
      }, Math.pow(2, retryCount) * 1000); // Exponential backoff: 2s, 4s, 8s
    } else {
      setError(userMessage);
      
      // If we've exhausted retries, generate mock data
      if (endpoint.includes('historical') && country) {
        generateMockHistoricalData(country.iso_code);
      } else if (endpoint.includes('trade') && country) {
        generateMockTradeData(country.iso_code);
      }
    }
  };

  const fetchTradeData = async (countryIso) => {
    try {
      const response = await fetch(`/api/trade_partners/${countryIso}`);
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => `${response.status} ${response.statusText}`);
        throw new Error(`Server returned ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      if (data.partners) {
        setTradePartners(data.partners);
        
        // Calculate trade dependency
        const totalTradeVolume = data.partners.reduce((sum, partner) => sum + partner.tradeVolume, 0);
        const countryGdp = country?.gdp || 1;
        const dependencyRatio = totalTradeVolume / countryGdp;
        setTradeDependency(dependencyRatio);
      } else {
        setTradePartners([]);
        setTradeDependency(0);
      }
      
      // Reset retry count on success
      setRetryCount(0);
      setError(null);
    } catch (error) {
      console.error("Trade data fetch error:", error);
      handleFetchError(error, 'trade partners');
    }
  };

  const generateMockTradeData = (countryIso) => {
    console.log("Generating mock trade data as fallback");
    const mockPartners = [];
    
    // Use existing countries data to generate realistic mock trade partners
    if (allCountries && allCountries.length > 0) {
      const partnerCount = Math.min(5, allCountries.length - 1);
      
      for (let i = 0; i < partnerCount; i++) {
        const partner = allCountries[i];
        if (partner.iso_code === countryIso) continue;
        
        const importVolume = Math.floor(Math.random() * 5000) + 1000;
        const exportVolume = Math.floor(Math.random() * 5000) + 1000;
        
        mockPartners.push({
          country: {
            name: partner.name,
            iso_code: partner.iso_code,
            region: partner.region
          },
          iso_code: partner.iso_code,
          importVolume,
          exportVolume,
          tradeVolume: importVolume + exportVolume,
          tradeBalance: exportVolume - importVolume,
          dependencyScore: (importVolume + exportVolume) / (country?.gdp || 10000),
          isCritical: Math.random() > 0.7
        });
      }
    }
    
    setTradePartners(mockPartners);
    setTradeDependency(0.15 + Math.random() * 0.1);
  };

  const fetchHistoricalBenchmarks = async (iso) => {
    setIsLoading(true);
    try {
      // Clear existing data before fetching new data
      setHistoricalBenchmarks(null);
      setEconomicTrends([]);
      
      // Fetch from our historical benchmarks endpoint with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      const response = await fetch(`/api/countries/${iso}/historical-benchmarks`, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => `${response.status} ${response.statusText}`);
        throw new Error(`Status ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      
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
      setError(null);
    } catch (error) {
      console.error("Historical data fetch error:", error);
      if (error.name === 'AbortError') {
        handleFetchError(new Error('Request timed out after 10 seconds'), 'historiske data');
      } else {
        handleFetchError(error, 'historiske data');
      }
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

  // Mock data generation functions
  const generateDummyTradeData = () => {
    // Create mock trade partners data
    const mockPartners = [];
    const partnerCount = 5 + Math.floor(Math.random() * 4);
    
    const possiblePartners = Object.values(allCountries || {})
      .filter(c => c.iso_code !== country.iso_code)
      .slice(0, 10);
    
    for(let i = 0; i < partnerCount && i < possiblePartners.length; i++) {
      const partner = possiblePartners[i];
      const importVolume = Math.random() * 100;
      const exportVolume = Math.random() * 100;
      
      mockPartners.push({
        country: partner,
        iso_code: partner.iso_code,
        importVolume,
        exportVolume,
        tradeBalance: exportVolume - importVolume,
        dependencyScore: (importVolume + exportVolume) / (country.gdp || 1000),
        isCritical: Math.random() > 0.7
      });
    }
    
    setTradePartners(mockPartners);
    
    // Calculate trade dependency
    const totalTrade = mockPartners.reduce((sum, partner) => 
      sum + partner.importVolume + partner.exportVolume, 0);
    setTradeDependency(totalTrade / (country.gdp || 1000));
  };
  
  const generateDummyCompetitors = () => {
    // Create mock competitor data
    const mockCompetitors = [];
    const competitorCount = 3 + Math.floor(Math.random() * 3);
    
    const possibleCompetitors = Object.values(allCountries || {})
      .filter(c => c.iso_code !== country.iso_code)
      .slice(0, 8);
    
    const industries = [
      'Agriculture', 'Manufacturing', 'Services', 'Technology', 
      'Mining', 'Energy', 'Finance', 'Tourism'
    ];
    
    for(let i = 0; i < competitorCount && i < possibleCompetitors.length; i++) {
      const competitor = possibleCompetitors[i];
      
      // Create random overlapping industries
      const mainIndustries = {};
      const industryCount = 2 + Math.floor(Math.random() * 3);
      
      for(let j = 0; j < industryCount; j++) {
        const industry = industries[Math.floor(Math.random() * industries.length)];
        mainIndustries[industry] = 0.3 + Math.random() * 0.6;
      }
      
      mockCompetitors.push({
        country: competitor,
        mainIndustries,
        competitionIntensity: 0.3 + Math.random() * 0.6,
        markets: ['Domestic', 'Regional', 'Global'].filter(() => Math.random() > 0.3)
      });
    }
    
    setCompetitorData(mockCompetitors);
  };
  
  const generateMockHistoricalData = () => {
    const years = [];
    const currentYear = new Date().getFullYear();
    
    // Generate last 10 years
    for(let i = 0; i < 10; i++) {
      years.push(currentYear - 9 + i);
    }
    
    // Generate metrics with country, regional and global values
    const metrics = {
      gdp_growth: {
        country_values: years.map(() => (Math.random() * 6) - 0.5),
        regional_values: years.map(() => (Math.random() * 4) + 0.5),
        global_values: years.map(() => (Math.random() * 3) + 1)
      },
      inflation: {
        country_values: years.map(() => (Math.random() * 5) + 0.5),
        regional_values: years.map(() => (Math.random() * 3) + 1),
        global_values: years.map(() => (Math.random() * 2) + 1.5)
      },
      unemployment: {
        country_values: years.map(() => (Math.random() * 8) + 2),
        regional_values: years.map(() => (Math.random() * 5) + 3),
        global_values: years.map(() => (Math.random() * 3) + 4)
      },
      trade_balance: {
        country_values: years.map(() => (Math.random() * 14) - 7),
        regional_values: years.map(() => (Math.random() * 10) - 5),
        global_values: years.map(() => (Math.random() * 6) - 3)
      }
    };
    
    // Generate performance metrics
    const performance = {
      gdp_growth: metrics.gdp_growth.country_values[years.length - 1],
      region_gdp_growth: metrics.gdp_growth.regional_values[years.length - 1],
      relative_performance: metrics.gdp_growth.country_values[years.length - 1] - 
                           metrics.gdp_growth.regional_values[years.length - 1],
      unemployment: metrics.unemployment.country_values[years.length - 1],
      region_unemployment: metrics.unemployment.regional_values[years.length - 1],
      unemployment_performance: metrics.unemployment.regional_values[years.length - 1] - 
                               metrics.unemployment.country_values[years.length - 1]
    };
    
    // Generate key events
    const keyEvents = [
      {
        year: years[2],
        event: 'Handelspolitisk reform',
        impact: 'Positive',
        magnitude: 'Medium'
      },
      {
        year: years[5],
        event: 'Global finanskrise',
        impact: 'Negative',
        magnitude: 'Very High'
      },
      {
        year: years[8],
        event: 'Teknologisk gennembrud',
        impact: 'Positive',
        magnitude: 'High'
      }
    ];
    
    // Set the historical data
    setHistoricalBenchmarks({
      country_name: country.name,
      region: country.region,
      years,
      metrics,
      performance,
      key_events: keyEvents
    });
    
    // Process trends data
    const trends = [
      {
        metric: 'gdp_growth',
        years,
        countryValues: metrics.gdp_growth.country_values,
        regionalValues: metrics.gdp_growth.regional_values,
        globalValues: metrics.gdp_growth.global_values
      },
      {
        metric: 'inflation',
        years,
        countryValues: metrics.inflation.country_values,
        regionalValues: metrics.inflation.regional_values,
        globalValues: metrics.inflation.global_values
      },
      {
        metric: 'unemployment',
        years,
        countryValues: metrics.unemployment.country_values,
        regionalValues: metrics.unemployment.regional_values,
        globalValues: metrics.unemployment.global_values
      },
      {
        metric: 'trade_balance',
        years,
        countryValues: metrics.trade_balance.country_values,
        regionalValues: metrics.trade_balance.regional_values,
        globalValues: metrics.trade_balance.global_values
      }
    ];
    setEconomicTrends(trends);
    
    // Generate trend summaries for the overview tab
    generateTrendSummaries({years, metrics});
    
    // Set key events
    setKeyEvents(keyEvents);
  };
  
  // Calculate performance metrics if not provided by the backend
  const calculatePerformanceMetrics = (data) => {
    if (!data.metrics || !data.years || data.years.length === 0) return;
    
    const latestYearIndex = data.years.length - 1;
    
    const performance = {
      gdp_growth: data.metrics.gdp_growth?.country_values?.[latestYearIndex] || 0,
      region_gdp_growth: data.metrics.gdp_growth?.regional_values?.[latestYearIndex] || 0,
      relative_performance: (data.metrics.gdp_growth?.country_values?.[latestYearIndex] || 0) - 
                           (data.metrics.gdp_growth?.regional_values?.[latestYearIndex] || 0),
      unemployment: data.metrics.unemployment?.country_values?.[latestYearIndex] || 0,
      region_unemployment: data.metrics.unemployment?.regional_values?.[latestYearIndex] || 0,
      unemployment_performance: (data.metrics.unemployment?.regional_values?.[latestYearIndex] || 0) - 
                               (data.metrics.unemployment?.country_values?.[latestYearIndex] || 0)
    };
    
    // Update the historical benchmarks with the calculated performance
    setHistoricalBenchmarks(prev => ({ ...prev, performance }));
  };
  
  // Generate trend summaries for the overview tab
  const generateTrendSummaries = (data) => {
    if (!data.metrics || !data.years || data.years.length === 0) return;
    
    const latestYearIndex = data.years.length - 1;
    const fiveYearsAgoIndex = Math.max(0, latestYearIndex - 5);
    
    const trendSummaries = [
      {
        trend: 'BNP Vækst',
        current: data.metrics.gdp_growth?.country_values?.[latestYearIndex]?.toFixed(1) + '%' || 'N/A',
        last_5_years: calculateAverage(
          data.metrics.gdp_growth?.country_values?.slice(fiveYearsAgoIndex, latestYearIndex + 1) || []
        ).toFixed(1) + '%',
        outlook: generateOutlook(data.metrics.gdp_growth?.country_values)
      },
      {
        trend: 'Inflation',
        current: data.metrics.inflation?.country_values?.[latestYearIndex]?.toFixed(1) + '%' || 'N/A',
        last_5_years: calculateAverage(
          data.metrics.inflation?.country_values?.slice(fiveYearsAgoIndex, latestYearIndex + 1) || []
        ).toFixed(1) + '%',
        outlook: generateOutlook(data.metrics.inflation?.country_values, false)
      },
      {
        trend: 'Arbejdsløshed',
        current: data.metrics.unemployment?.country_values?.[latestYearIndex]?.toFixed(1) + '%' || 'N/A',
        last_5_years: calculateAverage(
          data.metrics.unemployment?.country_values?.slice(fiveYearsAgoIndex, latestYearIndex + 1) || []
        ).toFixed(1) + '%',
        outlook: generateOutlook(data.metrics.unemployment?.country_values, false)
      },
      {
        trend: 'Handelsbalance',
        current: data.metrics.trade_balance?.country_values?.[latestYearIndex]?.toFixed(1) + '%' || 'N/A',
        last_5_years: calculateAverage(
          data.metrics.trade_balance?.country_values?.slice(fiveYearsAgoIndex, latestYearIndex + 1) || []
        ).toFixed(1) + '%',
        outlook: generateOutlook(data.metrics.trade_balance?.country_values)
      }
    ];
    
    setEconomicTrends(prev => [...prev, ...trendSummaries]);
  };
  
  // Helper function to calculate average
  const calculateAverage = (values) => {
    if (!values || values.length === 0) return 0;
    return values.reduce((sum, val) => sum + val, 0) / values.length;
  };
  
  // Helper function to generate outlook descriptions
  const generateOutlook = (values, isPositiveBetter = true) => {
    if (!values || values.length < 3) return 'Utilstrækkelige data';
    
    const lastThree = values.slice(-3);
    const trend = (lastThree[2] - lastThree[0]) / lastThree[0] * 100;
    
    // For metrics where lower is better (like unemployment, inflation)
    if (!isPositiveBetter) {
      if (trend < -10) return 'Stærk forbedring';
      if (trend < -5) return 'Moderat forbedring';
      if (trend < 0) return 'Let forbedring';
      if (trend < 5) return 'Stabil';
      if (trend < 10) return 'Let forværring';
      return 'Betydelig forværring';
    }
    
    // For metrics where higher is better (like GDP growth)
    if (trend > 10) return 'Stærk positiv';
    if (trend > 5) return 'Moderat positiv';
    if (trend > 0) return 'Let positiv';
    if (trend > -5) return 'Stabil';
    if (trend > -10) return 'Let negativ';
    return 'Betydelig negativ';
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