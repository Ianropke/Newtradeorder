import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import '../styles/BNPHistoryPanel.css';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const BNPHistoryPanel = ({ countryData, gameYear, selectedCountry }) => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: []
  });
  
  const [viewMode, setViewMode] = useState('absolute'); // 'absolute', 'growth', 'compare'
  const [comparisonCountries, setComparisonCountries] = useState([]);
  const [yearsToShow, setYearsToShow] = useState(10);
  
  // Generate chart colors
  const generateChartColor = (index, opacity = 1) => {
    const colors = [
      `rgba(45, 127, 249, ${opacity})`, // Blue
      `rgba(63, 152, 70, ${opacity})`,  // Green
      `rgba(251, 140, 0, ${opacity})`,  // Orange
      `rgba(229, 57, 53, ${opacity})`,  // Red
      `rgba(156, 39, 176, ${opacity})`, // Purple
      `rgba(0, 188, 212, ${opacity})`,  // Cyan
      `rgba(121, 85, 72, ${opacity})`,  // Brown
    ];
    return colors[index % colors.length];
  };

  useEffect(() => {
    if (!selectedCountry || !countryData || !gameYear) return;
    
    // Generate labels (years)
    const currentYear = parseInt(gameYear);
    const startYear = Math.max(currentYear - yearsToShow, 2000);
    const years = Array.from({ length: currentYear - startYear + 1 }, (_, i) => startYear + i);
    
    // Prepare datasets
    const datasets = [];
    
    // Format data for the selected country
    if (selectedCountry && countryData[selectedCountry.iso_code]) {
      const countryInfo = countryData[selectedCountry.iso_code];
      const historicalData = countryInfo.gdp_history || {};
      
      // Extract GDP values for each year (or 0 if not available)
      let values = years.map(year => historicalData[year] || null);
      
      // If we're in growth mode, calculate percentage changes
      if (viewMode === 'growth') {
        values = values.map((value, index, array) => {
          if (index === 0 || !value || !array[index - 1]) return null;
          return ((value / array[index - 1]) - 1) * 100; // Percentage change
        });
      }
      
      // Add dataset for selected country
      datasets.push({
        label: countryInfo.name,
        data: values,
        borderColor: generateChartColor(0),
        backgroundColor: generateChartColor(0, 0.1),
        borderWidth: 3,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: generateChartColor(0),
        tension: 0.3,
        fill: true
      });
      
      // Add comparison countries if in compare mode
      if (viewMode === 'compare') {
        comparisonCountries.forEach((isoCode, index) => {
          if (countryData[isoCode] && isoCode !== selectedCountry.iso_code) {
            const comparisonInfo = countryData[isoCode];
            const comparisonHistory = comparisonInfo.gdp_history || {};
            
            const comparisonValues = years.map(year => comparisonHistory[year] || null);
            
            datasets.push({
              label: comparisonInfo.name,
              data: comparisonValues,
              borderColor: generateChartColor(index + 1),
              backgroundColor: generateChartColor(index + 1, 0.1),
              borderWidth: 2,
              pointRadius: 3,
              pointHoverRadius: 5,
              pointBackgroundColor: generateChartColor(index + 1),
              tension: 0.3,
              fill: false
            });
          }
        });
      }
    }
    
    // Update chart data
    setChartData({
      labels: years,
      datasets
    });
  }, [selectedCountry, countryData, gameYear, viewMode, comparisonCountries, yearsToShow]);

  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animations: {
      tension: {
        duration: 1000,
        easing: 'easeOutQuad',
        from: 0.3,
        to: 0.3,
        loop: false
      }
    },
    scales: {
      y: {
        ticks: {
          callback: function(value) {
            if (viewMode === 'growth') {
              return value.toFixed(1) + '%';
            } else {
              // Format large numbers with k, M, B
              if (Math.abs(value) >= 1000000) {
                return (value / 1000000).toFixed(1) + 'M';
              } else if (Math.abs(value) >= 1000) {
                return (value / 1000).toFixed(1) + 'k';
              }
              return value;
            }
          }
        },
        grid: {
          color: 'rgba(200, 200, 200, 0.15)',
        },
        title: {
          display: true,
          text: viewMode === 'growth' ? 'Growth Rate (%)' : 'GDP (Million USD)',
          color: '#666'
        }
      },
      x: {
        grid: {
          color: 'rgba(200, 200, 200, 0.15)',
        },
        title: {
          display: true,
          text: 'Year',
          color: '#666'
        }
      }
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          boxWidth: 6
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              if (viewMode === 'growth') {
                label += context.parsed.y.toFixed(2) + '%';
              } else {
                label += context.parsed.y.toLocaleString() + ' Million USD';
              }
            }
            return label;
          }
        }
      }
    }
  };

  // Handle adding comparison countries
  const addComparisonCountry = (isoCode) => {
    if (
      isoCode !== selectedCountry.iso_code && 
      !comparisonCountries.includes(isoCode) &&
      comparisonCountries.length < 5
    ) {
      setComparisonCountries([...comparisonCountries, isoCode]);
    }
  };

  // Handle removing comparison countries
  const removeComparisonCountry = (isoCode) => {
    setComparisonCountries(comparisonCountries.filter(code => code !== isoCode));
  };

  return (
    <div className="bnp-history-panel">
      <div className="bnp-history-header">
        <h3>Economic History</h3>
        
        <div className="bnp-view-controls">
          <div className="view-selector">
            <button 
              className={`view-btn ${viewMode === 'absolute' ? 'active' : ''}`}
              onClick={() => setViewMode('absolute')}
            >
              Absolute
            </button>
            <button 
              className={`view-btn ${viewMode === 'growth' ? 'active' : ''}`}
              onClick={() => setViewMode('growth')}
            >
              Growth Rate
            </button>
            <button 
              className={`view-btn ${viewMode === 'compare' ? 'active' : ''}`}
              onClick={() => setViewMode('compare')}
            >
              Compare
            </button>
          </div>
          
          <div className="year-range-selector">
            <label>Years:</label>
            <select 
              value={yearsToShow}
              onChange={(e) => setYearsToShow(parseInt(e.target.value))}
            >
              <option value="5">5 Years</option>
              <option value="10">10 Years</option>
              <option value="20">20 Years</option>
              <option value="50">All Data</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* Comparison country selector */}
      {viewMode === 'compare' && (
        <div className="comparison-controls">
          <label>Compare with:</label>
          <div className="comparison-tags">
            {comparisonCountries.map(isoCode => (
              countryData[isoCode] ? (
                <div key={isoCode} className="comparison-tag">
                  <span>{countryData[isoCode].name}</span>
                  <button onClick={() => removeComparisonCountry(isoCode)}>×</button>
                </div>
              ) : null
            ))}
            
            {comparisonCountries.length < 5 && (
              <select 
                value=""
                onChange={(e) => {
                  if (e.target.value) {
                    addComparisonCountry(e.target.value);
                    e.target.value = "";
                  }
                }}
              >
                <option value="">+ Add country</option>
                {Object.entries(countryData)
                  .filter(([isoCode]) => 
                    isoCode !== selectedCountry.iso_code && 
                    !comparisonCountries.includes(isoCode)
                  )
                  .map(([isoCode, country]) => (
                    <option key={isoCode} value={isoCode}>
                      {country.name}
                    </option>
                  ))
                }
              </select>
            )}
          </div>
        </div>
      )}
      
      <div className="chart-container">
        <Line data={chartData} options={chartOptions} />
      </div>
      
      {/* Economic indicators */}
      {selectedCountry && countryData[selectedCountry.iso_code] && (
        <div className="economic-indicators">
          <div className="indicator">
            <span className="indicator-label">Current GDP:</span>
            <span className="indicator-value">
              {countryData[selectedCountry.iso_code].gdp?.toLocaleString()} Million USD
            </span>
          </div>
          
          <div className="indicator">
            <span className="indicator-label">Growth Rate:</span>
            <span className="indicator-value" style={{ 
              color: calculateGrowthRate() >= 0 ? 'var(--success)' : 'var(--danger)'
            }}>
              {calculateGrowthRate() >= 0 ? '+' : ''}{calculateGrowthRate().toFixed(2)}%
            </span>
          </div>
          
          <div className="indicator">
            <span className="indicator-label">Per Capita:</span>
            <span className="indicator-value">
              {calculatePerCapita().toLocaleString()} USD
            </span>
          </div>
          
          <div className="indicator">
            <span className="indicator-label">Global Rank:</span>
            <span className="indicator-value">
              #{calculateGlobalRank()}
            </span>
          </div>
        </div>
      )}
    </div>
  );
  
  // Helper function to calculate current growth rate
  function calculateGrowthRate() {
    if (!selectedCountry || !countryData[selectedCountry.iso_code]) return 0;
    
    const countryInfo = countryData[selectedCountry.iso_code];
    const history = countryInfo.gdp_history || {};
    const currentYear = parseInt(gameYear);
    const lastYear = currentYear - 1;
    
    if (!history[currentYear] || !history[lastYear]) return 0;
    
    return ((history[currentYear] / history[lastYear]) - 1) * 100;
  }
  
  // Helper function to calculate GDP per capita
  function calculatePerCapita() {
    if (!selectedCountry || !countryData[selectedCountry.iso_code]) return 0;
    
    const countryInfo = countryData[selectedCountry.iso_code];
    const gdp = countryInfo.gdp || 0;
    const population = countryInfo.population || 1;
    
    // Convert GDP from millions to actual value
    return Math.round((gdp * 1000000) / population);
  }
  
  // Helper function to calculate global GDP rank
  function calculateGlobalRank() {
    if (!selectedCountry || !countryData[selectedCountry.iso_code]) return 'N/A';
    
    const sortedCountries = Object.values(countryData)
      .filter(country => country.gdp)
      .sort((a, b) => b.gdp - a.gdp);
    
    const rankIndex = sortedCountries.findIndex(country => 
      country.iso_code === selectedCountry.iso_code
    );
    
    return rankIndex !== -1 ? rankIndex + 1 : 'N/A';
  }
};

export default BNPHistoryPanel;
