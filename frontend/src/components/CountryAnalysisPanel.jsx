import React, { useState, useEffect } from 'react';
import '../styles/CountryAnalysisPanel.css';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, AnnotationPlugin } from 'chart.js';

// Register Chart.js components including annotations for key events
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, AnnotationPlugin);

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

  useEffect(() => {
    if (!country || !country.iso_code) return;

    setIsLoading(true);
    setError(null);

    fetchTradeData(country.iso_code);
    fetchHistoricalBenchmarks(country.iso_code);
  }, [country]);

  const fetchTradeData = async (iso) => {
    try {
      const partnersRes = await fetch(`/api/trade_partners/${iso}`);
      if (partnersRes.ok) {
        const partnersData = await partnersRes.json();

        if (partnersData.partners) {
          setTradePartners(partnersData.partners);

          const totalTrade = partnersData.partners.reduce((sum, partner) =>
            sum + (partner.importVolume || 0) + (partner.exportVolume || 0), 0);
          setTradeDependency(totalTrade / (country.gdp || 1));
        }
      } else {
        console.warn("Kunne ikke hente handelspartnerdata");
        generateDummyTradeData();
      }

      const competitorsRes = await fetch(`/api/competitors/${iso}`);
      if (competitorsRes.ok) {
        const competitorsData = await competitorsRes.json();
        if (competitorsData.competitors) {
          setCompetitorData(competitorsData.competitors);
        }
      } else {
        console.warn("Kunne ikke hente konkurrentdata");
        generateDummyCompetitors();
      }
    } catch (error) {
      console.error("Fejl ved hentning af handelsdata:", error);
      setError(`Fejl ved hentning af handelsdata: ${error.message}`);
      generateDummyTradeData();
      generateDummyCompetitors();
    } finally {
      setIsLoading(false);
    }
  };

  const fetchHistoricalBenchmarks = async (iso) => {
    setIsLoading(true);
    setError(null);
    try {
      // Clear existing data before fetching new data
      setHistoricalBenchmarks(null);
      setEconomicTrends([]);
      
      // Fetch historical benchmarks data from backend
      const response = await fetch(`/api/countries/${iso}/historical-benchmarks`);
      if (response.ok) {
        const data = await response.json();
        console.log("Received historical data:", data);
        
        if (data.status === 'mock') {
          console.info("Using mock historical data from server:", data.message);
          setDataSource('mock');
        } else {
          setDataSource('real');
        }
        
        setHistoricalBenchmarks(data);

        // Process the trends data from the backend API
        if (data.metrics && data.years) {
          processHistoricalTrends(data);
        }
        
        // Extract key historical events if available
        if (data.key_events) {
          setKeyEvents(data.key_events);
        } else {
          // Set default key events if not provided by the backend
          setKeyEvents([
            { year: 2008, event: "Global finanskrise", impact: "Negativ", magnitude: "Høj" },
            { year: 2020, event: "COVID-19 pandemi", impact: "Negativ", magnitude: "Meget høj" }
          ]);
        }
      } else {
        const errorData = await response.json().catch(() => ({ error: 'Ukendt fejl' }));
        console.warn("Could not fetch historical benchmarks:", errorData.error || 'Unknown error');
        setError(`Kunne ikke hente historiske data: ${errorData.error || 'Ukendt fejl'}`);
        generateMockHistoricalData();
        setDataSource('mock');
      }
    } catch (error) {
      console.error("Error fetching historical benchmarks:", error);
      setError(`Fejl ved hentning af historiske data: ${error.message}`);
      generateMockHistoricalData();
      setDataSource('mock');
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
  
  // Generate summary trends for the overview tab
  const generateTrendSummaries = (data) => {
    if (!data.metrics || !data.years || data.years.length === 0) return;
    
    const years = data.years;
    const latestYearIndex = years.length - 1;
    const fiveYearsAgoIndex = Math.max(0, latestYearIndex - 4);
    
    // Calculate current GDP growth and 5-year average
    const currentGdpGrowth = data.metrics.gdp_growth?.country_values?.[latestYearIndex] || 0;
    const gdpGrowthLast5Years = data.metrics.gdp_growth?.country_values?.slice(fiveYearsAgoIndex, latestYearIndex + 1) || [];
    const avgGdpGrowth5Years = gdpGrowthLast5Years.length > 0 
      ? gdpGrowthLast5Years.reduce((sum, val) => sum + val, 0) / gdpGrowthLast5Years.length
      : 0;
    
    // Calculate current unemployment and 5-year average
    const currentUnemployment = data.metrics.unemployment?.country_values?.[latestYearIndex] || 0;
    const unemploymentLast5Years = data.metrics.unemployment?.country_values?.slice(fiveYearsAgoIndex, latestYearIndex + 1) || [];
    const avgUnemployment5Years = unemploymentLast5Years.length > 0
      ? unemploymentLast5Years.reduce((sum, val) => sum + val, 0) / unemploymentLast5Years.length
      : 0;
    
    // Calculate trade balance trend
    const currentTradeBalance = data.metrics.trade_balance?.country_values?.[latestYearIndex] || 0;
    const tradeBalanceLast5Years = data.metrics.trade_balance?.country_values?.slice(fiveYearsAgoIndex, latestYearIndex + 1) || [];
    const avgTradeBalance5Years = tradeBalanceLast5Years.length > 0
      ? tradeBalanceLast5Years.reduce((sum, val) => sum + val, 0) / tradeBalanceLast5Years.length
      : 0;
    
    // Generate overall economic trend summaries
    const summaryTrends = [
      {
        trend: "BNP Vækst",
        current: currentGdpGrowth.toFixed(1) + "%",
        last_5_years: avgGdpGrowth5Years.toFixed(1) + "%",
        historical_avg: (data.metrics.gdp_growth?.global_values?.reduce((sum, val) => sum + val, 0) / 
                         data.metrics.gdp_growth?.global_values?.length || 0).toFixed(1) + "%",
        outlook: currentGdpGrowth > 2.5 ? "Positiv" : currentGdpGrowth > 1 ? "Stabil" : "Udfordrende"
      },
      {
        trend: "Arbejdsløshed",
        current: currentUnemployment.toFixed(1) + "%",
        last_5_years: avgUnemployment5Years.toFixed(1) + "%",
        historical_avg: (data.metrics.unemployment?.global_values?.reduce((sum, val) => sum + val, 0) / 
                         data.metrics.unemployment?.global_values?.length || 0).toFixed(1) + "%",
        outlook: currentUnemployment < 4 ? "Stærk" : currentUnemployment < 6 ? "Stabil" : "Bekymrende"
      },
      {
        trend: "Handelsbalance",
        current: currentTradeBalance.toFixed(1) + "%",
        last_5_years: avgTradeBalance5Years.toFixed(1) + "%",
        historical_avg: (data.metrics.trade_balance?.global_values?.reduce((sum, val) => sum + val, 0) / 
                         data.metrics.trade_balance?.global_values?.length || 0).toFixed(1) + "%",
        outlook: currentTradeBalance > 2 ? "Stærk eksportør" : 
                 currentTradeBalance > 0 ? "Positiv" : 
                 currentTradeBalance > -2 ? "Balanceret" : "Importafhængig"
      }
    ];
    
    // Set economic trends for overview tab
    setEconomicTrends(prevTrends => {
      // Keep the detailed metric data and add these summary trends
      return [...prevTrends.filter(t => t.metric), ...summaryTrends];
    });
  };
  
  const calculatePerformanceMetrics = (data) => {
    // Only calculate if we have the necessary data
    if (!data.metrics || !data.years || data.years.length === 0) return;
    
    const years = data.years;
    const latestYear = Math.max(...years);
    const latestYearIndex = years.indexOf(latestYear);
    
    // If we don't have data for the latest year, we can't calculate performance
    if (latestYearIndex === -1) return;
    
    const prevYearIndex = latestYearIndex > 0 ? latestYearIndex - 1 : latestYearIndex;
    
    // Calculate performance metrics
    const gdpGrowth = data.metrics.gdp_growth?.country_values?.[latestYearIndex] || 0;
    const regionGdpGrowth = data.metrics.gdp_growth?.regional_values?.[latestYearIndex] || 0;
    const relativePerformance = gdpGrowth - regionGdpGrowth;
    
    const unemployment = data.metrics.unemployment?.country_values?.[latestYearIndex] || 0;
    const regionUnemployment = data.metrics.unemployment?.regional_values?.[latestYearIndex] || 0;
    const unemploymentPerformance = regionUnemployment - unemployment;
    
    const tradeBalance = data.metrics.trade_balance?.country_values?.[latestYearIndex] || 0;
    
    data.performance = {
      gdp_growth: gdpGrowth,
      region_gdp_growth: regionGdpGrowth,
      relative_performance: relativePerformance,
      unemployment: unemployment,
      region_unemployment: regionUnemployment,
      unemployment_performance: unemploymentPerformance,
      trade_balance: tradeBalance
    };
    
    setHistoricalBenchmarks(data);
  };

  // Generate mock historical data for when the backend fails or isn't available
  const generateMockHistoricalData = () => {
    if (!country) return;

    const currentYear = new Date().getFullYear();
    const years = Array.from({length: 10}, (_, i) => currentYear - 10 + i + 1);
    
    // Generate mock data for each metric
    const gdpGrowthValues = years.map((_, i) => {
      const cycleFactor = Math.sin(i / 3) * 0.5;
      return 2 + cycleFactor * 2;
    });
    
    const inflationValues = years.map((_, i) => {
      const cycleFactor = Math.sin((i + 1) / 3) * 0.5;
      return 1.5 + cycleFactor * 1.5;
    });
    
    const unemploymentValues = years.map((_, i) => {
      const cycleFactor = Math.sin((i + 2) / 3) * 0.5;
      return 5 + cycleFactor * 3;
    });
    
    const tradeBalanceValues = years.map((_, i) => {
      const cycleFactor = Math.sin((i + 1.5) / 3) * 0.5;
      return cycleFactor * 6;
    });
    
    // Add financial crisis and COVID effects
    const crisisIndex = years.indexOf(2008);
    if (crisisIndex >= 0) {
      gdpGrowthValues[crisisIndex] = -2.5;
      unemploymentValues[crisisIndex] += 2;
    }
    
    const covidIndex = years.indexOf(2020);
    if (covidIndex >= 0) {
      gdpGrowthValues[covidIndex] = -3.5;
      unemploymentValues[covidIndex] += 3;
    }
    
    // Create mock data structure similar to backend API
    const mockData = {
      status: 'mock',
      message: 'Using generated mock data',
      years: years,
      metrics: {
        gdp_growth: {
          country_values: gdpGrowthValues,
          regional_values: gdpGrowthValues.map(v => v + (Math.random() * 1 - 0.5)),
          global_values: gdpGrowthValues.map(v => v * 0.8 + 0.5)
        },
        inflation: {
          country_values: inflationValues,
          regional_values: inflationValues.map(v => v + (Math.random() * 0.8 - 0.4)),
          global_values: inflationValues.map(v => v * 0.9 + 0.3)
        },
        unemployment: {
          country_values: unemploymentValues,
          regional_values: unemploymentValues.map(v => v + (Math.random() * 1.5 - 0.75)),
          global_values: unemploymentValues.map(v => v * 0.9 + 0.5)
        },
        trade_balance: {
          country_values: tradeBalanceValues,
          regional_values: tradeBalanceValues.map(v => v * 0.6 + (Math.random() * 2 - 1)),
          global_values: tradeBalanceValues.map(v => v * 0.3)
        }
      },
      key_events: [
        { year: 2008, event: "Global finanskrise", impact: "Negativ", magnitude: "Høj", description: "Finansiel krise der ramte globale økonomier" },
        { year: 2020, event: "COVID-19 pandemi", impact: "Negativ", magnitude: "Meget høj", description: "Pandemi der førte til nedlukninger og økonomisk nedgang" }
      ]
    };
    
    setHistoricalBenchmarks(mockData);
    processHistoricalTrends(mockData);
  };

  // Generate dummy trade partner data
  const generateDummyTradeData = () => {
    if (!country || !allCountries) return;

    const relationBasedPartners = Object.values(allCountries)
      .filter(c => c.iso_code !== country.iso_code)
      .map(c => {
        const relation = diplomacy?.relations?.find(r =>
          (r.country_a === c.iso_code && r.country_b === country.iso_code) ||
          (r.country_b === c.iso_code && r.country_a === country.iso_code)
        );

        const relationLevel = relation ? relation.relation_level : 0;
        const relationFactor = 0.5 + (relationLevel + 1) * 0.25;

        const sizeFactor = Math.pow((c.gdp || 10) / (country.gdp || 10), 0.7) * 0.5;

        const tradeFactor = relationFactor * sizeFactor;
        const importVolume = (c.gdp || 10) * 0.05 * tradeFactor;
        const exportVolume = (country.gdp || 10) * 0.05 * tradeFactor;

        const randomFactor = 0.7 + Math.random() * 0.6;

        return {
          country: c,
          iso_code: c.iso_code,
          importVolume: importVolume * randomFactor,
          exportVolume: exportVolume * randomFactor,
          get tradeVolume() { return this.importVolume + this.exportVolume; },
          get tradeBalance() { return this.exportVolume - this.importVolume; },
          get dependencyScore() { return this.tradeVolume / (country.gdp || 100); },
          get isCritical() { return this.dependencyScore > 0.05; }
        };
      })
      .sort((a, b) => b.tradeVolume - a.tradeVolume)
      .slice(0, 8);

    setTradePartners(relationBasedPartners);

    const totalTrade = relationBasedPartners.reduce((sum, partner) =>
      sum + partner.tradeVolume, 0);
    setTradeDependency(totalTrade / (country.gdp || 1));
  };

  // Generate dummy competitor data
  const generateDummyCompetitors = () => {
    if (!country || !allCountries) return;

    const similarCountries = Object.values(allCountries)
      .filter(c => c.iso_code !== country.iso_code)
      .map(c => {
        let industryOverlap = 0;

        if (country.industries && c.industries) {
          const commonIndustries = Object.keys(country.industries)
            .filter(ind => c.industries[ind])
            .map(ind => ({
              name: ind,
              overlapValue: Math.min(country.industries[ind], c.industries[ind])
            }));

          industryOverlap = commonIndustries.reduce((sum, ind) => sum + ind.overlapValue, 0);
        } else {
          const gdpRatio = Math.min(c.gdp || 10, country.gdp || 10) /
            Math.max(c.gdp || 10, country.gdp || 10);
          industryOverlap = gdpRatio * 0.5;
        }

        const competitionIntensity = industryOverlap * Math.min(1, (c.gdp || 10) / (country.gdp || 10));

        return {
          country: c,
          overlapScore: industryOverlap,
          competitionIntensity: competitionIntensity,
          mainIndustries: c.industries || {
            "Landbrug": Math.random() * 0.5,
            "Industri": Math.random() * 0.6,
            "Service": 0.3 + Math.random() * 0.5
          }
        };
      })
      .sort((a, b) => b.competitionIntensity - a.competitionIntensity)
      .slice(0, 5);

    setCompetitorData(similarCountries);
  };

  // Export historical data to CSV
  const exportHistoricalData = (isoCode, benchmarks) => {
    if (!benchmarks || !benchmarks.metrics || !benchmarks.years) {
      setError("Ingen data tilgængelig til eksport");
      return;
    }

    try {
      setExportLoading(true);
      
      const years = benchmarks.years;
      const metrics = benchmarks.metrics;
      
      // Base CSV headers
      const headers = ['År', 'BNP Vækst (%)', 'Regional BNP Vækst (%)', 'Global BNP Vækst (%)'];
      
      // Add comparison countries headers if any
      comparisonCountries.forEach(country => {
        headers.push(`${country.name} BNP Vækst (%)`);
      });
      
      // Continue with other metrics
      headers.push(
        'Inflation (%)', 'Regional Inflation (%)', 
        'Arbejdsløshed (%)', 'Regional Arbejdsløshed (%)',
        'Handelsbalance (% af BNP)', 'Regional Handelsbalance (%)'
      );
      
      const csvRows = [headers];
      
      // Add data rows
      years.forEach((year, index) => {
        const row = [
          year,
          metrics.gdp_growth?.country_values?.[index]?.toFixed(2) || '',
          metrics.gdp_growth?.regional_values?.[index]?.toFixed(2) || '',
          metrics.gdp_growth?.global_values?.[index]?.toFixed(2) || ''
        ];
        
        // Add comparison countries data
        comparisonCountries.forEach(country => {
          const countryValue = country.metrics?.gdp_growth?.country_values?.[index]?.toFixed(2) || '';
          row.push(countryValue);
        });
        
        // Continue with other metrics
        row.push(
          metrics.inflation?.country_values?.[index]?.toFixed(2) || '',
          metrics.inflation?.regional_values?.[index]?.toFixed(2) || '',
          metrics.unemployment?.country_values?.[index]?.toFixed(2) || '',
          metrics.unemployment?.regional_values?.[index]?.toFixed(2) || '',
          metrics.trade_balance?.country_values?.[index]?.toFixed(2) || '',
          metrics.trade_balance?.regional_values?.[index]?.toFixed(2) || ''
        );
        
        csvRows.push(row);
      });
      
      // Also add a section for key events if available
      if (keyEvents && keyEvents.length > 0) {
        csvRows.push([]);  // Empty row as separator
        csvRows.push(['Vigtige historiske begivenheder']);
        csvRows.push(['År', 'Begivenhed', 'Effekt', 'Betydning', 'Beskrivelse']);
        
        keyEvents.forEach(event => {
          csvRows.push([
            event.year,
            event.event,
            event.impact,
            event.magnitude,
            event.description || ''
          ]);
        });
      }
      
      const csvContent = csvRows.map(row => row.join(',')).join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.setAttribute('download', `${isoCode}_historical_data_${new Date().toISOString().slice(0,10)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Fejl ved eksport af data:", error);
      setError(`Fejl ved eksport af data: ${error.message}`);
    } finally {
      setExportLoading(false);
    }
  };

  // Add a country to the comparison list
  const addCountryComparison = async (isoCode) => {
    if (!isoCode || !allCountries || !historicalBenchmarks) {
      setError("Kan ikke tilføje landet til sammenligning");
      return;
    }
    
    if (comparisonCountries.some(c => c.iso_code === isoCode)) {
      setError("Dette land er allerede tilføjet til sammenligningen");
      return; // Already added
    }
    
    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch comparison country's historical data
      const response = await fetch(`/api/countries/${isoCode}/historical-benchmarks`);
      if (response.ok) {
        const data = await response.json();
        
        // Create comparison country object with all necessary data
        const comparisonData = {
          iso_code: isoCode,
          name: allCountries[isoCode]?.name || isoCode,
          color: getRandomColor(),
          metrics: data.metrics || {},
          years: data.years || []
        };
        
        // Add to comparison countries list
        setComparisonCountries(prev => [...prev, comparisonData]);
      } else {
        const errorData = await response.json().catch(() => ({ error: 'Ukendt fejl' }));
        console.error("Failed to fetch comparison country data:", errorData.error);
        setError(`Kunne ikke hente data for sammenligningslandet: ${errorData.error || 'Ukendt fejl'}`);
        
        // Try with mock data instead
        const mockData = generateMockDataForCountry(isoCode);
        const comparisonData = {
          iso_code: isoCode,
          name: allCountries[isoCode]?.name || isoCode,
          color: getRandomColor(),
          metrics: mockData.metrics || {},
          years: mockData.years || [],
          isMock: true
        };
        
        setComparisonCountries(prev => [...prev, comparisonData]);
      }
    } catch (error) {
      console.error("Error adding comparison country:", error);
      setError(`Fejl ved tilføjelse af sammenligningsland: ${error.message}`);
      
      // Try with mock data in case of error
      const mockData = generateMockDataForCountry(isoCode);
      const comparisonData = {
        iso_code: isoCode,
        name: allCountries[isoCode]?.name || isoCode,
        color: getRandomColor(),
        metrics: mockData.metrics || {},
        years: mockData.years || [],
        isMock: true
      };
      
      setComparisonCountries(prev => [...prev, comparisonData]);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Generate mock data for a specific country
  const generateMockDataForCountry = (isoCode) => {
    if (!historicalBenchmarks || !historicalBenchmarks.years) {
      return generateDefaultMockData();
    }
    
    const years = historicalBenchmarks.years;
    const targetCountry = allCountries[isoCode];
    
    // Create variations based on the main country data
    const gdpVariation = targetCountry && country ? 
      (targetCountry.gdp || 10) / (country.gdp || 10) : 
      0.8 + Math.random() * 0.4;
    
    const mockData = {
      status: 'mock',
      years: years,
      metrics: {}
    };
    
    // Generate mock metrics with slight variations from the main country
    if (historicalBenchmarks.metrics.gdp_growth) {
      mockData.metrics.gdp_growth = {
        country_values: historicalBenchmarks.metrics.gdp_growth.country_values.map(
          v => v * (0.8 + gdpVariation * 0.4) + (Math.random() * 1 - 0.5)
        )
      };
    }
    
    if (historicalBenchmarks.metrics.inflation) {
      mockData.metrics.inflation = {
        country_values: historicalBenchmarks.metrics.inflation.country_values.map(
          v => v * (0.9 + Math.random() * 0.2) + (Math.random() * 0.8 - 0.4)
        )
      };
    }
    
    if (historicalBenchmarks.metrics.unemployment) {
      mockData.metrics.unemployment = {
        country_values: historicalBenchmarks.metrics.unemployment.country_values.map(
          v => v * (0.9 + Math.random() * 0.2) + (Math.random() * 1.5 - 0.75)
        )
      };
    }
    
    if (historicalBenchmarks.metrics.trade_balance) {
      mockData.metrics.trade_balance = {
        country_values: historicalBenchmarks.metrics.trade_balance.country_values.map(
          v => v * (0.7 + Math.random() * 0.6) + (Math.random() * 2 - 1)
        )
      };
    }
    
    return mockData;
  };
  
  // Default mock data if no reference data is available
  const generateDefaultMockData = () => {
    const currentYear = new Date().getFullYear();
    const years = Array.from({length: 10}, (_, i) => currentYear - 10 + i + 1);
    
    return {
      status: 'mock',
      years: years,
      metrics: {
        gdp_growth: {
          country_values: years.map(() => (Math.random() * 4) - 0.5)
        },
        inflation: {
          country_values: years.map(() => (Math.random() * 3) + 0.5)
        },
        unemployment: {
          country_values: years.map(() => (Math.random() * 6) + 3)
        },
        trade_balance: {
          country_values: years.map(() => (Math.random() * 8) - 4)
        }
      }
    };
  };
  
  // Remove a country from the comparison list
  const removeCountryComparison = (isoCode) => {
    setComparisonCountries(prev => prev.filter(c => c.iso_code !== isoCode));
  };
  
  // Generate a random color for comparison countries
  const getRandomColor = () => {
    const colors = [
      '#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3', 
      '#009688', '#4caf50', '#8bc34a', '#cddc39', '#ffc107', 
      '#ff9800', '#ff5722', '#795548', '#607d8b'
    ];
    
    // Find a color that's not already used
    const usedColors = comparisonCountries.map(c => c.color);
    const availableColors = colors.filter(c => !usedColors.includes(c));
    
    if (availableColors.length > 0) {
      return availableColors[Math.floor(Math.random() * availableColors.length)];
    }
    
    // If all colors are used, generate a completely random color
    return `#${Math.floor(Math.random() * 16777215).toString(16)}`;
  };

  // Render chart for selected historical metric with annotations for key events
  const renderHistoricalChart = () => {
    const metric = selectedBenchmarkMetric || 'gdp_growth';
    
    // Find the trend data for the selected metric
    const selectedTrend = economicTrends.find(trend => trend.metric === metric);
    
    if (!selectedTrend || !historicalBenchmarks) {
      return <p className="no-data-message">Ingen data tilgængelig for denne metrik.</p>;
    }
    
    // Create chart datasets
    const datasets = [
      {
        label: `${country?.name || 'Land'}`,
        data: selectedTrend.countryValues || [],
        borderColor: '#3f51b5',
        backgroundColor: 'rgba(63, 81, 181, 0.1)',
        tension: 0.3,
        borderWidth: 2,
      },
      {
        label: 'Regional Benchmark',
        data: selectedTrend.regionalValues || [],
        borderColor: '#ff9800',
        backgroundColor: 'rgba(255, 152, 0, 0.1)',
        tension: 0.3,
        borderDash: [5, 5],
        borderWidth: 1.5,
      },
      {
        label: 'Global Benchmark',
        data: selectedTrend.globalValues || [],
        borderColor: '#4caf50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.3,
        borderDash: [2, 2],
        borderWidth: 1.5,
      }
    ];
    
    // Add comparison countries to the chart
    comparisonCountries.forEach(compCountry => {
      if (compCountry.metrics && compCountry.metrics[metric] && compCountry.metrics[metric].country_values) {
        datasets.push({
          label: `${compCountry.name}${compCountry.isMock ? ' (estimeret)' : ''}`,
          data: compCountry.metrics[metric].country_values,
          borderColor: compCountry.color,
          backgroundColor: `${compCountry.color}20`, // Add transparency
          tension: 0.3,
          borderWidth: 2,
        });
      }
    });
    
    const chartData = {
      labels: selectedTrend.years || historicalBenchmarks.years || [],
      datasets: datasets
    };

    // Create annotations for key events
    const annotations = {};
    if (keyEvents && keyEvents.length > 0) {
      keyEvents.forEach((event, index) => {
        const eventYear = event.year.toString();
        const yearIndex = chartData.labels.findIndex(year => year.toString() === eventYear);
        
        if (yearIndex >= 0) {
          annotations[`event-${index}`] = {
            type: 'line',
            borderColor: event.impact === 'Negativ' ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 128, 0, 0.5)',
            borderWidth: 2,
            borderDash: [6, 6],
            label: {
              content: event.event,
              enabled: true,
              position: 'top',
              backgroundColor: 'rgba(0, 0, 0, 0.7)',
              font: {
                size: 10
              }
            },
            scaleID: 'x',
            value: yearIndex
          };
        }
      });
    }

    const getMetricTitle = (metricName) => {
      const titles = {
        'gdp_growth': 'BNP Vækst (%)',
        'inflation': 'Inflation (%)',
        'unemployment': 'Arbejdsløshed (%)',
        'trade_balance': 'Handelsbalance (% af BNP)'
      };
      return titles[metricName] || metricName;
    };

    return (
      <div className="trend-chart">
        <h5>{getMetricTitle(metric)}</h5>
        <div className="chart-container">
          <Line 
            data={chartData}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              interaction: {
                mode: 'index',
                intersect: false,
              },
              scales: {
                y: {
                  beginAtZero: metric !== 'trade_balance',
                  title: {
                    display: true,
                    text: '%'
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
                  labels: {
                    usePointStyle: true,
                    boxWidth: 10
                  }
                },
                tooltip: {
                  callbacks: {
                    label: function(context) {
                      return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
                    }
                  }
                },
                annotation: {
                  annotations: annotations
                }
              }
            }}
          />
        </div>
      </div>
    );
  };
  
  // Render country comparison selector
  const renderComparisonSelector = () => {
    if (!allCountries) return null;
    
    const availableCountries = Object.values(allCountries)
      .filter(c => c.iso_code !== country?.iso_code && 
                !comparisonCountries.some(comp => comp.iso_code === c.iso_code));
    
    if (availableCountries.length === 0) return null;
    
    return (
      <div className="comparison-selector">
        <h5>Sammenlign med andre lande</h5>
        <div className="comparison-controls">
          <select 
            className="country-select"
            onChange={(e) => {
              if (e.target.value) {
                addCountryComparison(e.target.value);
                e.target.value = '';  // Reset after selection
              }
            }}
            value=""
            disabled={isLoading}
          >
            <option value="">Vælg land til sammenligning...</option>
            {availableCountries.map(c => (
              <option key={c.iso_code} value={c.iso_code}>{c.name}</option>
            ))}
          </select>
        </div>
        
        {comparisonCountries.length > 0 && (
          <div className="comparison-list">
            {comparisonCountries.map(c => (
              <div key={c.iso_code} className="comparison-item">
                <div className="color-indicator" style={{ backgroundColor: c.color }}></div>
                <span>{c.name}{c.isMock ? ' (estimeret)' : ''}</span>
                <button 
                  className="remove-btn"
                  onClick={() => removeCountryComparison(c.iso_code)}
                  aria-label={`Fjern ${c.name} fra sammenligning`}
                >
                  ✕
                </button>
              </div>
            ))}
            {comparisonCountries.length > 1 && (
              <button 
                className="clear-all-btn"
                onClick={() => setComparisonCountries([])}
                aria-label="Fjern alle sammenligninger"
              >
                Fjern alle
              </button>
            )}
          </div>
        )}
      </div>
    );
  };
  
  // Render key historical events
  const renderKeyEvents = () => {
    if (!keyEvents || keyEvents.length === 0) return null;
    
    return (
      <div className="key-events">
        <h5>Vigtige historiske begivenheder</h5>
        <ul className="event-list">
          {keyEvents.map((event, index) => (
            <li key={index} className="event-item">
              <div className="event-year">{event.year}</div>
              <div className="event-content">
                <div className="event-title">{event.event}</div>
                <div className="event-impact">
                  <span className={`impact-label ${event.impact.toLowerCase()}`}>
                    {event.impact}
                  </span>
                  <span className="impact-magnitude">{event.magnitude}</span>
                </div>
                {event.description && (
                  <div className="event-description">{event.description}</div>
                )}
              </div>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  // Clear error message after a timeout
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError(null);
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [error]);

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
      {error && <div className="error-message">{error}</div>}

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
              
              <div className="metrics-export-container">
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
                
                <button 
                  className="export-button"
                  onClick={() => exportHistoricalData(country.iso_code, historicalBenchmarks)}
                  disabled={!historicalBenchmarks || isLoading || exportLoading}
                >
                  <span className="export-icon">📊</span>
                  {exportLoading ? 'Eksporterer...' : 'Eksportér data (CSV)'}
                </button>
              </div>
            </div>
            
            {renderComparisonSelector()}
            
            <div className="chart-and-events-container">
              {renderHistoricalChart()}
              
              {renderKeyEvents()}
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