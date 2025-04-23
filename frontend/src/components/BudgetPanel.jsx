import React, { useState, useEffect, useRef } from 'react';
import './BudgetPanel.css';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const BudgetPanel = ({ countryId, gameYear, onBudgetUpdate }) => {
  const [budgetData, setBudgetData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Editing states
  const [editingItem, setEditingItem] = useState(null);
  const [editValue, setEditValue] = useState(0);
  
  // Subsidy states
  const [subsidies, setSubsidies] = useState([]);
  const [showAddSubsidyForm, setShowAddSubsidyForm] = useState(false);
  const [newSubsidy, setNewSubsidy] = useState({
    sector: 'agriculture',
    percentage: 5,
    duration: 2
  });
  
  // New subsidy preview state
  const [subsidyPreview, setSubsidyPreview] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);

  // Simulation state
  const [showEffects, setShowEffects] = useState(false);
  const [simulatedEffects, setSimulatedEffects] = useState(null);
  
  // Calibration states
  const [isCalibrating, setIsCalibrating] = useState(false);
  const [calibrationResult, setCalibrationResult] = useState(null);
  const [showCalibrationReport, setShowCalibrationReport] = useState(false);
  const [calibrationMetrics, setCalibrationMetrics] = useState({
    gdp_growth: true,
    inflation: true,
    unemployment: true
  });
  
  // Chart references
  const revenueChartRef = useRef(null);
  const expenditureChartRef = useRef(null);
  const historicalChartRef = useRef(null);
  
  // Historical data
  const [historicalBudgets, setHistoricalBudgets] = useState([]);
  const [showHistoricalData, setShowHistoricalData] = useState(false);
  
  // Advanced view toggle
  const [showAdvancedView, setShowAdvancedView] = useState(false);
  
  // Fetch budget data when country or year changes
  useEffect(() => {
    if (!countryId) return;
    
    fetchBudgetData();
    fetchSubsidies();
    fetchHistoricalBudgets();
  }, [countryId, gameYear]);

  const fetchBudgetData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/budget/${countryId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch budget data');
      }
      const data = await response.json();
      setBudgetData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching budget data:', err);
      setError('Failed to load budget data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const fetchSubsidies = async () => {
    try {
      const response = await fetch(`/api/budget/${countryId}/subsidies`);
      if (!response.ok) {
        throw new Error('Failed to fetch subsidies');
      }
      const data = await response.json();
      setSubsidies(data.subsidies || []);
    } catch (err) {
      console.error('Error fetching subsidies:', err);
    }
  };

  const fetchHistoricalBudgets = async () => {
    try {
      const response = await fetch(`/api/budget/${countryId}/historical`);
      if (!response.ok) {
        return; // Historical data may not be available, that's okay
      }
      const data = await response.json();
      setHistoricalBudgets(data.history || []);
    } catch (err) {
      console.error('Error fetching historical budget data:', err);
    }
  };

  const handleEditClick = (item, currentValue) => {
    setEditingItem(item);
    setEditValue(currentValue);
  };

  const handleEditCancel = () => {
    setEditingItem(null);
    setEditValue(0);
    setSimulatedEffects(null);
  };

  const handleEditSave = async () => {
    if (!editingItem) return;
    
    try {
      const response = await fetch(`/api/budget/${countryId}/allocate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category: editingItem,
          value: parseFloat(editValue)
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update budget allocation');
      }
      
      // Refresh budget data
      fetchBudgetData();
      
      // Notify parent component
      if (onBudgetUpdate) {
        onBudgetUpdate();
      }
      
    } catch (err) {
      console.error('Error updating budget allocation:', err);
      setError('Failed to update budget. Please try again.');
    } finally {
      setEditingItem(null);
      setSimulatedEffects(null);
    }
  };

  const handleSubsidyChange = (e) => {
    const { name, value } = e.target;
    const updatedSubsidy = {
      ...newSubsidy,
      [name]: name === 'percentage' || name === 'duration' 
        ? parseFloat(value) 
        : value
    };
    
    setNewSubsidy(updatedSubsidy);
    
    // Preview effects when subsidy parameters change
    previewSubsidyEffects(updatedSubsidy);
  };

  const previewSubsidyEffects = async (subsidyData) => {
    if (!subsidyData || !subsidyData.sector) return;
    
    setLoadingPreview(true);
    try {
      const response = await fetch(`/api/budget/${countryId}/subsidies/preview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(subsidyData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to preview subsidy effects');
      }
      
      const previewData = await response.json();
      setSubsidyPreview(previewData);
      
    } catch (err) {
      console.error('Error previewing subsidy effects:', err);
      setSubsidyPreview(null);
    } finally {
      setLoadingPreview(false);
    }
  };

  const addSubsidy = async () => {
    try {
      const response = await fetch(`/api/budget/${countryId}/subsidies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newSubsidy),
      });
      
      if (!response.ok) {
        throw new Error('Failed to add subsidy');
      }
      
      // Refresh subsidies
      fetchSubsidies();
      // Reset form
      setShowAddSubsidyForm(false);
      setNewSubsidy({
        sector: 'agriculture',
        percentage: 5,
        duration: 2
      });
      setSubsidyPreview(null);
      
      // Refresh budget data as subsidies affect budget
      fetchBudgetData();
      
      // Notify parent component
      if (onBudgetUpdate) {
        onBudgetUpdate();
      }
      
    } catch (err) {
      console.error('Error adding subsidy:', err);
      setError('Failed to add subsidy. Please try again.');
    }
  };

  const removeSubsidy = async (subsidyId) => {
    try {
      const response = await fetch(`/api/budget/${countryId}/subsidies/${subsidyId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error('Failed to remove subsidy');
      }
      
      // Update subsidies list
      setSubsidies(subsidies.filter(subsidy => subsidy.id !== subsidyId));
      
      // Refresh budget data as subsidies affect budget
      fetchBudgetData();
      
      // Notify parent component
      if (onBudgetUpdate) {
        onBudgetUpdate();
      }
      
    } catch (err) {
      console.error('Error removing subsidy:', err);
      setError('Failed to remove subsidy. Please try again.');
    }
  };

  const simulateBudgetEffects = async () => {
    if (!editingItem) return;
    
    try {
      const response = await fetch(`/api/budget/${countryId}/simulate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category: editingItem,
          value: parseFloat(editValue)
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to simulate budget effects');
      }
      
      const effects = await response.json();
      setSimulatedEffects(effects);
      setShowEffects(true);
      
    } catch (err) {
      console.error('Error simulating budget effects:', err);
      setError('Failed to simulate budget effects. Please try again.');
    }
  };

  const getBudgetHealthClass = () => {
    if (!budgetData) return 'budget-neutral';
    
    const balanceRatio = budgetData.balance / budgetData.gdp * 100;
    const debtRatio = budgetData.debt / budgetData.gdp * 100;
    
    if (balanceRatio < -3 || debtRatio > 90) {
      return 'budget-critical';
    } else if (balanceRatio < -1 || debtRatio > 60) {
      return 'budget-warning';
    } else {
      return 'budget-healthy';
    }
  };
  
  const getHealthText = () => {
    if (!budgetData) return 'Loading...';
    
    const balanceRatio = budgetData.balance / budgetData.gdp * 100;
    const debtRatio = budgetData.debt / budgetData.gdp * 100;
    
    if (balanceRatio < -3 || debtRatio > 90) {
      return 'Critical: High deficit or debt';
    } else if (balanceRatio < -1 || debtRatio > 60) {
      return 'Warning: Deficit or debt concerns';
    } else {
      return 'Healthy: Sustainable fiscal position';
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
      notation: 'compact',
      compactDisplay: 'short'
    }).format(value);
  };

  const formatPercentage = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    }).format(value / 100);
  };

  const handleCalibrationMetricChange = (e) => {
    const { name, checked } = e.target;
    setCalibrationMetrics({
      ...calibrationMetrics,
      [name]: checked
    });
  };
  
  const startCalibration = async () => {
    setIsCalibrating(true);
    setCalibrationResult(null);
    
    // Get selected metrics
    const targetMetrics = Object.keys(calibrationMetrics).filter(
      metric => calibrationMetrics[metric]
    );
    
    try {
      const response = await fetch(`/api/countries/${countryId}/calibrate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          target_metrics: targetMetrics
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to calibrate economic parameters');
      }
      
      const result = await response.json();
      setCalibrationResult(result);
      setShowCalibrationReport(true);
      
      // Refresh budget data as calibration may affect economic indicators
      fetchBudgetData();
      
      // Notify parent component
      if (onBudgetUpdate) {
        onBudgetUpdate();
      }
      
    } catch (err) {
      console.error('Error calibrating economic parameters:', err);
      setError('Failed to calibrate economic parameters. Please try again.');
    } finally {
      setIsCalibrating(false);
    }
  };
  
  // Function to generate charts data
  const getRevenueChartData = () => {
    if (!budgetData || !budgetData.revenue) return null;
    
    const labels = Object.keys(budgetData.revenue);
    const values = Object.values(budgetData.revenue);
    
    const backgroundColor = [
      'rgba(54, 162, 235, 0.8)',
      'rgba(75, 192, 192, 0.8)',
      'rgba(153, 102, 255, 0.8)',
      'rgba(255, 159, 64, 0.8)',
      'rgba(255, 99, 132, 0.8)',
    ];
    
    return {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor,
          borderWidth: 1,
        },
      ],
    };
  };
  
  const getExpenditureChartData = () => {
    if (!budgetData || !budgetData.expenses) return null;
    
    const labels = Object.keys(budgetData.expenses);
    const values = Object.values(budgetData.expenses);
    
    const backgroundColor = [
      'rgba(255, 99, 132, 0.8)',
      'rgba(255, 159, 64, 0.8)',
      'rgba(255, 205, 86, 0.8)',
      'rgba(75, 192, 192, 0.8)',
      'rgba(54, 162, 235, 0.8)',
      'rgba(153, 102, 255, 0.8)',
    ];
    
    return {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor,
          borderWidth: 1,
        },
      ],
    };
  };
  
  const getHistoricalChartData = () => {
    if (!historicalBudgets || historicalBudgets.length === 0) return null;
    
    const sortedBudgets = [...historicalBudgets].sort((a, b) => a.year - b.year);
    const labels = sortedBudgets.map(budget => budget.year);
    
    return {
      labels,
      datasets: [
        {
          label: 'Revenue',
          data: sortedBudgets.map(budget => budget.totalRevenue),
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
        },
        {
          label: 'Expenditure',
          data: sortedBudgets.map(budget => budget.totalExpenditure),
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1,
        },
        {
          label: 'Balance',
          data: sortedBudgets.map(budget => budget.balance),
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1,
          type: 'line',
        },
      ],
    };
  };

  if (loading) {
    return <div className="budget-panel loading">Loading budget data...</div>;
  }

  if (error) {
    return <div className="budget-panel error">{error}</div>;
  }

  if (!budgetData) {
    return <div className="budget-panel error">No budget data available</div>;
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.raw;
            return `${label}: ${formatCurrency(value)}`;
          }
        }
      }
    }
  };
  
  const historicalChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: 'Historical Budget Trends'
      },
      legend: {
        position: 'top',
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: 'Amount'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Year'
        }
      }
    }
  };

  return (
    <div className={`budget-panel ${getBudgetHealthClass()}`}>
      <h2>National Budget</h2>
      
      <div className="panel-controls">
        <div className="budget-health-indicator">
          {getHealthText()}
        </div>
        
        <div className="view-toggles">
          <button 
            className={`view-toggle ${showAdvancedView ? 'active' : ''}`}
            onClick={() => setShowAdvancedView(!showAdvancedView)}
          >
            {showAdvancedView ? 'Simple View' : 'Advanced View'}
          </button>
          
          <button 
            className={`view-toggle ${showHistoricalData ? 'active' : ''}`}
            onClick={() => setShowHistoricalData(!showHistoricalData)}
            disabled={historicalBudgets.length === 0}
          >
            {showHistoricalData ? 'Hide History' : 'Show History'}
          </button>
        </div>
      </div>
      
      <div className="budget-summary">
        <div className="budget-balance">
          <h3>Budget Balance</h3>
          <div className={`balance-value ${budgetData.balance >= 0 ? 'positive' : 'negative'}`}>
            {formatCurrency(budgetData.balance)}
          </div>
          <div>
            ({formatPercentage(budgetData.balance / budgetData.gdp * 100)} of GDP)
          </div>
        </div>
        
        <div className="debt-information">
          <div className="debt-metric">
            <h4>National Debt</h4>
            <div>{formatCurrency(budgetData.debt)}</div>
          </div>
          
          <div className="debt-metric">
            <h4>Debt-to-GDP Ratio</h4>
            <div className={`debt-ratio ${
              budgetData.debt / budgetData.gdp > 0.9 ? 'critical' : 
              budgetData.debt / budgetData.gdp > 0.6 ? 'warning' : 'healthy'
            }`}>
              {formatPercentage(budgetData.debt / budgetData.gdp * 100)}
            </div>
          </div>
        </div>
      </div>
      
      {showHistoricalData && historicalBudgets.length > 0 && (
        <div className="historical-chart-container">
          <Bar 
            data={getHistoricalChartData()}
            options={historicalChartOptions}
            ref={historicalChartRef}
          />
        </div>
      )}
      
      <div className={`budget-content ${showAdvancedView ? 'advanced-view' : 'simple-view'}`}>
        <div className="budget-column">
          <div className="budget-section">
            <h3>Government Revenue</h3>
            
            {showAdvancedView && (
              <div className="chart-container">
                <Pie 
                  data={getRevenueChartData()}
                  options={chartOptions}
                  ref={revenueChartRef}
                />
              </div>
            )}
            
            <div className="budget-items">
              {Object.entries(budgetData.revenue).map(([name, value]) => (
                <div key={name} className="budget-item">
                  <div className="budget-item-name">{name}</div>
                  <div className="budget-item-value">
                    {formatCurrency(value)}
                    <span style={{ marginLeft: '10px', color: '#7f8c8d', fontSize: '0.9em' }}>
                      ({formatPercentage(value / budgetData.gdp * 100)} of GDP)
                    </span>
                  </div>
                </div>
              ))}
              
              <div className="budget-item total">
                <div className="budget-item-name">Total Revenue</div>
                <div className="budget-item-value">
                  {formatCurrency(budgetData.totalRevenue)}
                  <span style={{ marginLeft: '10px', color: '#7f8c8d', fontSize: '0.9em' }}>
                    ({formatPercentage(budgetData.totalRevenue / budgetData.gdp * 100)} of GDP)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="budget-column">
          <div className="budget-section">
            <h3>Government Expenditure</h3>
            
            {showAdvancedView && (
              <div className="chart-container">
                <Pie 
                  data={getExpenditureChartData()}
                  options={chartOptions}
                  ref={expenditureChartRef}
                />
              </div>
            )}
            
            <div className="budget-items">
              {Object.entries(budgetData.expenses).map(([name, value]) => (
                <div key={name} className={`budget-item ${budgetData.editableCategories?.includes(name) ? 'editable' : ''} ${editingItem === name ? 'editing' : ''}`}>
                  <div className="budget-item-name">{name}</div>
                  
                  {editingItem === name ? (
                    <div className="budget-edit-controls">
                      <input
                        type="number"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        min="0"
                        step="100000000"
                      />
                      <button className="apply-button" onClick={handleEditSave}>Apply</button>
                      <button className="cancel-button" onClick={handleEditCancel}>Cancel</button>
                      <button className="edit-button" onClick={simulateBudgetEffects}>
                        Simulate Effects
                      </button>
                    </div>
                  ) : (
                    <div className="budget-item-value">
                      {formatCurrency(value)}
                      <span style={{ marginLeft: '10px', color: '#7f8c8d', fontSize: '0.9em' }}>
                        ({formatPercentage(value / budgetData.gdp * 100)} of GDP)
                      </span>
                      
                      {budgetData.editableCategories?.includes(name) && (
                        <button 
                          className="edit-button"
                          onClick={() => handleEditClick(name, value)}
                        >
                          Edit
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
              
              <div className="budget-item total">
                <div className="budget-item-name">Total Expenditure</div>
                <div className="budget-item-value">
                  {formatCurrency(budgetData.totalExpenditure)}
                  <span style={{ marginLeft: '10px', color: '#7f8c8d', fontSize: '0.9em' }}>
                    ({formatPercentage(budgetData.totalExpenditure / budgetData.gdp * 100)} of GDP)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="budget-section">
        <h3>Subsidies and Economic Support</h3>
        
        {subsidies.length > 0 ? (
          <div className="budget-items">
            {subsidies.map(subsidy => (
              <div key={subsidy.id} className="budget-item subsidy-item">
                <div className="budget-item-name">
                  {subsidy.sector} Sector ({subsidy.percentage}% subsidy)
                  <div style={{ fontSize: '0.8em', color: '#7f8c8d' }}>
                    {subsidy.remainingYears} years remaining
                  </div>
                </div>
                <div className="budget-item-value">
                  {formatCurrency(subsidy.annualCost)}
                  <button 
                    className="remove-button"
                    onClick={() => removeSubsidy(subsidy.id)}
                  >
                    Remove
                  </button>
                </div>
                
                {showAdvancedView && subsidy.effects && (
                  <div className="subsidy-effects">
                    <div className="effect-header">Effects:</div>
                    <div className="effect-grid">
                      {subsidy.effects.output_increase_percentage && (
                        <div className="effect-item">
                          <span className="effect-label">Output:</span>
                          <span className="effect-value positive">+{subsidy.effects.output_increase_percentage.toFixed(1)}%</span>
                        </div>
                      )}
                      {subsidy.effects.unemployment_reduction && (
                        <div className="effect-item">
                          <span className="effect-label">Unemployment:</span>
                          <span className="effect-value positive">-{subsidy.effects.unemployment_reduction.toFixed(1)}%</span>
                        </div>
                      )}
                      {subsidy.effects.price_reduction_percentage && (
                        <div className="effect-item">
                          <span className="effect-label">Price:</span>
                          <span className="effect-value positive">-{subsidy.effects.price_reduction_percentage.toFixed(1)}%</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p>No active subsidies. Add subsidies to support economic sectors.</p>
        )}
        
        {showAddSubsidyForm ? (
          <div className="add-subsidy-form">
            <div className="form-group">
              <label>Sector:</label>
              <select 
                name="sector" 
                value={newSubsidy.sector}
                onChange={handleSubsidyChange}
              >
                <option value="agriculture">Agriculture</option>
                <option value="manufacturing">Manufacturing</option>
                <option value="technology">Technology</option>
                <option value="energy">Energy</option>
                <option value="services">Services</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Subsidy Percentage (%):</label>
              <input 
                type="number" 
                name="percentage"
                value={newSubsidy.percentage}
                onChange={handleSubsidyChange}
                min="1"
                max="50"
                step="1"
              />
            </div>
            
            <div className="form-group">
              <label>Duration (years):</label>
              <input 
                type="number" 
                name="duration"
                value={newSubsidy.duration}
                onChange={handleSubsidyChange}
                min="1"
                max="10"
                step="1"
              />
            </div>
            
            {subsidyPreview && !loadingPreview && (
              <div className="subsidy-preview">
                <h4>Projected Effects</h4>
                <div className="preview-grid">
                  <div className="preview-item">
                    <div className="preview-label">Output Increase:</div>
                    <div className="preview-value positive">+{subsidyPreview.output_increase_percentage.toFixed(1)}%</div>
                  </div>
                  <div className="preview-item">
                    <div className="preview-label">Unemployment Reduction:</div>
                    <div className="preview-value positive">-{subsidyPreview.unemployment_reduction.toFixed(1)}%</div>
                  </div>
                  <div className="preview-item">
                    <div className="preview-label">Annual Cost:</div>
                    <div className="preview-value">{formatCurrency(subsidyPreview.annual_cost)}</div>
                  </div>
                  <div className="preview-item">
                    <div className="preview-label">Export Boost:</div>
                    <div className="preview-value positive">+{subsidyPreview.export_increase_percentage?.toFixed(1) || '0.0'}%</div>
                  </div>
                </div>
              </div>
            )}
            
            {loadingPreview && (
              <div className="preview-loading">Calculating effects...</div>
            )}
            
            <div className="form-actions">
              <button className="apply-button" onClick={addSubsidy}>
                Add Subsidy
              </button>
              <button 
                className="cancel-button"
                onClick={() => {
                  setShowAddSubsidyForm(false);
                  setSubsidyPreview(null);
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <button 
            className="add-subsidy-button"
            onClick={() => setShowAddSubsidyForm(true)}
          >
            + Add New Subsidy
          </button>
        )}
      </div>
      
      <div className="budget-impact-section">
        <h3>Economic Impact</h3>
        
        <div className="impact-grid">
          <div className="impact-item">
            <div className="impact-label">Economic Growth Effect</div>
            <div className="impact-value">
              {budgetData.economicImpact?.growthEffect > 0 ? '+' : ''}
              {budgetData.economicImpact?.growthEffect.toFixed(2)}%
            </div>
          </div>
          
          <div className="impact-item">
            <div className="impact-label">Employment Effect</div>
            <div className="impact-value">
              {budgetData.economicImpact?.employmentEffect > 0 ? '+' : ''}
              {budgetData.economicImpact?.employmentEffect.toFixed(2)}%
            </div>
          </div>
          
          <div className="impact-item">
            <div className="impact-label">Investment Effect</div>
            <div className="impact-value">
              {budgetData.economicImpact?.investmentEffect > 0 ? '+' : ''}
              {budgetData.economicImpact?.investmentEffect.toFixed(2)}%
            </div>
          </div>
          
          <div className="impact-item">
            <div className="impact-label">Public Approval</div>
            <div className="impact-value">
              {budgetData.economicImpact?.publicApproval > 0 ? '+' : ''}
              {budgetData.economicImpact?.publicApproval.toFixed(2)}%
            </div>
          </div>
        </div>
      </div>
      
      {showAdvancedView && (
        <div className="budget-section calibration-section">
          <h3>Economic Parameter Calibration</h3>
          <p className="calibration-description">
            Calibrate economic model parameters based on historical data to improve economic 
            forecasting accuracy. This process fine-tunes your country's economic model.
          </p>
          
          <div className="calibration-metrics">
            <div className="metrics-label">Select metrics to calibrate:</div>
            <div className="metrics-options">
              <label className="metric-option">
                <input 
                  type="checkbox"
                  name="gdp_growth"
                  checked={calibrationMetrics.gdp_growth}
                  onChange={handleCalibrationMetricChange}
                />
                GDP Growth
              </label>
              <label className="metric-option">
                <input 
                  type="checkbox"
                  name="inflation"
                  checked={calibrationMetrics.inflation}
                  onChange={handleCalibrationMetricChange}
                />
                Inflation
              </label>
              <label className="metric-option">
                <input 
                  type="checkbox"
                  name="unemployment"
                  checked={calibrationMetrics.unemployment}
                  onChange={handleCalibrationMetricChange}
                />
                Unemployment
              </label>
            </div>
          </div>
          
          <button 
            className="calibrate-button"
            onClick={startCalibration}
            disabled={isCalibrating || !Object.values(calibrationMetrics).some(v => v)}
          >
            {isCalibrating ? 'Calibrating...' : 'Calibrate Economic Parameters'}
          </button>
          
          {calibrationResult && (
            <div className="calibration-result">
              <h4>Calibration Complete</h4>
              <p>{calibrationResult.message}</p>
              
              <button
                className="view-report-button"
                onClick={() => setShowCalibrationReport(!showCalibrationReport)}
              >
                {showCalibrationReport ? 'Hide Detailed Report' : 'View Detailed Report'}
              </button>
              
              {showCalibrationReport && calibrationResult.report && (
                <div className="calibration-report">
                  <h4>Calibration Report</h4>
                  
                  <div className="report-metrics">
                    {Object.entries(calibrationResult.report.metrics || {}).map(([metric, value]) => (
                      <div key={metric} className="report-metric">
                        <div className="metric-name">{metric.replace('_', ' ')}</div>
                        <div className="metric-value">
                          <div className="before-value">
                            Before: {typeof value.before === 'number' ? value.before.toFixed(2) : value.before}
                          </div>
                          <div className="after-value">
                            After: {typeof value.after === 'number' ? value.after.toFixed(2) : value.after}
                          </div>
                          <div className={`change-value ${value.change > 0 ? 'positive' : value.change < 0 ? 'negative' : ''}`}>
                            Change: {value.change > 0 ? '+' : ''}{typeof value.change === 'number' ? value.change.toFixed(2) : value.change}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="calibration-parameters">
                    <h5>Updated Economic Parameters</h5>
                    <div className="parameters-grid">
                      {Object.entries(calibrationResult.calibrated_params || {}).map(([param, value]) => (
                        <div key={param} className="parameter-item">
                          <div className="parameter-name">{param.replace('_', ' ')}</div>
                          <div className="parameter-value">
                            {typeof value === 'number' ? value.toFixed(4) : value}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
      
      {/* Budget Effects Simulation Popup */}
      {showEffects && simulatedEffects && (
        <div className="budget-effects-overlay">
          <div className="budget-effects-popup">
            <h3>Budget Change Simulation</h3>
            <h4>Effects of changing {editingItem} to {formatCurrency(editValue)}</h4>
            
            <p className="effects-description">
              These are the estimated effects if you apply this budget change.
              Effects may vary based on current economic conditions and other policies.
            </p>
            
            <ul className="effects-list">
              <li>
                <span className="effect-name">GDP Growth</span>
                <span className={`effect-value ${simulatedEffects.gdpGrowthChange > 0 ? 'positive' : 'negative'}`}>
                  {simulatedEffects.gdpGrowthChange > 0 ? '+' : ''}
                  {simulatedEffects.gdpGrowthChange.toFixed(2)}%
                </span>
              </li>
              <li>
                <span className="effect-name">Unemployment</span>
                <span className={`effect-value ${simulatedEffects.unemploymentChange < 0 ? 'positive' : 'negative'}`}>
                  {simulatedEffects.unemploymentChange > 0 ? '+' : ''}
                  {simulatedEffects.unemploymentChange.toFixed(2)}%
                </span>
              </li>
              <li>
                <span className="effect-name">Inflation</span>
                <span className={`effect-value ${simulatedEffects.inflationChange < 0 ? 'positive' : 'negative'}`}>
                  {simulatedEffects.inflationChange > 0 ? '+' : ''}
                  {simulatedEffects.inflationChange.toFixed(2)}%
                </span>
              </li>
              <li>
                <span className="effect-name">Public Approval</span>
                <span className={`effect-value ${simulatedEffects.approvalChange > 0 ? 'positive' : 'negative'}`}>
                  {simulatedEffects.approvalChange > 0 ? '+' : ''}
                  {simulatedEffects.approvalChange.toFixed(2)}%
                </span>
              </li>
              <li>
                <span className="effect-name">New Budget Balance</span>
                <span className={`effect-value ${simulatedEffects.newBalance >= 0 ? 'positive' : 'negative'}`}>
                  {formatCurrency(simulatedEffects.newBalance)}
                </span>
              </li>
            </ul>
            
            {simulatedEffects.description && (
              <div className="effects-description expert-opinion">
                <h5>Economic Analysis</h5>
                <p>{simulatedEffects.description}</p>
              </div>
            )}
            
            <div className="budget-effects-actions">
              <button 
                className="apply-button"
                onClick={() => {
                  handleEditSave();
                  setShowEffects(false);
                }}
              >
                Apply Changes
              </button>
              <button 
                className="cancel-button"
                onClick={() => setShowEffects(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BudgetPanel;