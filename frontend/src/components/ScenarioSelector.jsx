import React, { useState, useEffect, useRef } from 'react';
import '../styles/ScenarioSelector.css';

const scenarios = [
  {
    id: 'standard',
    name: 'Standardspil',
    description: 'Start et standard handelsspil med ligevægtige økonomiske forhold på den globale scene.',
    difficulty: 'Normal',
    year: '2025',
    image: '/scenarios/standard.jpg',
    themes: ['Balance', 'Frihandel'],
    category: 'Standard'
  },
  {
    id: 'trade_war_2020',
    name: 'Handelskrig 2020',
    description: 'Start under USA-Kina handelskrigen fra 2020 med øgede spændinger og ustabilitet i de globale forsyningskæder.',
    difficulty: 'Medium',
    year: '2020',
    image: '/scenarios/trade_war.jpg',
    themes: ['Konflikt', 'Protektionisme', 'Geopolitik'],
    category: 'Historisk'
  },
  {
    id: 'pandemic_recovery',
    name: 'Pandemi-genopretning',
    description: 'Navigér gennem de økonomiske følger af en global pandemi, hvor lande skal balancere økonomisk genopretning med sundhedshensyn.',
    difficulty: 'Svær',
    year: '2023',
    image: '/scenarios/pandemic.jpg',
    themes: ['Sundhed', 'Krise', 'Genopbygning'],
    category: 'Krise'
  },
  {
    id: 'resource_crisis',
    name: 'Ressourcekrise',
    description: 'Global ressourcemangel skaber højere priser og konkurrence. Lande må udvikle nye handelsstrategier for at sikre vitale forsyninger.',
    difficulty: 'Meget svær',
    year: '2027',
    image: '/scenarios/resource_crisis.jpg',
    themes: ['Ressourcer', 'Krise', 'Konkurrence'],
    category: 'Krise'
  },
  {
    id: 'green_transition',
    name: 'Grøn Omstilling',
    description: 'Lande implementerer grønne politikker og CO2-afgifter. Balancér økonomisk vækst med miljømæssig bæredygtighed.',
    difficulty: 'Medium',
    year: '2026',
    image: '/scenarios/green_transition.jpg',
    themes: ['Miljø', 'Bæredygtighed', 'Innovation'],
    category: 'Fremtid'
  },
  {
    id: 'regional_bloc',
    name: 'Regionale Blokke',
    description: 'Verden er opdelt i konkurrerende handelsblokke. Styrk din blok eller forsøg at balancere mellem dem.',
    difficulty: 'Svær',
    year: '2028',
    image: '/scenarios/regional_blocs.jpg',
    themes: ['Allianser', 'Geopolitik', 'Protektionisme'],
    category: 'Fremtid'
  }
];

function ScenarioSelector({ onSelectScenario, onBack }) {
  const [selectedScenario, setSelectedScenario] = useState('standard');
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [yearRange, setYearRange] = useState([2020, 2030]);
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [showFilters, setShowFilters] = useState(false);
  const [categories, setCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [themes, setThemes] = useState([]);
  const [selectedThemes, setSelectedThemes] = useState([]);
  const [activeFilters, setActiveFilters] = useState([]);
  const [filterPresets, setFilterPresets] = useState([]);
  const [presetName, setPresetName] = useState('');
  const [showPresetModal, setShowPresetModal] = useState(false);
  const presetInputRef = useRef(null);

  const [filterAnimation, setFilterAnimation] = useState(false);
  const [lastAppliedFilter, setLastAppliedFilter] = useState(null);
  const [showFilterTooltip, setShowFilterTooltip] = useState(false);
  const [filterVisualization, setFilterVisualization] = useState({ active: false, count: 0 });
  const [showFilterStats, setShowFilterStats] = useState(false);

  useEffect(() => {
    const uniqueCategories = [...new Set(scenarios.map(s => s.category).filter(Boolean))];
    setCategories(uniqueCategories);

    const allThemes = scenarios.flatMap(s => s.themes || []);
    const uniqueThemes = [...new Set(allThemes)];
    setThemes(uniqueThemes);

    const savedPresets = localStorage.getItem('scenarioFilterPresets');
    if (savedPresets) {
      try {
        setFilterPresets(JSON.parse(savedPresets));
      } catch (e) {
        console.error('Failed to load saved filter presets', e);
      }
    }
  }, []);

  useEffect(() => {
    const newActiveFilters = [];

    if (filter !== 'all') {
      newActiveFilters.push({ type: 'difficulty', value: filter });
    }

    if (searchTerm) {
      newActiveFilters.push({ type: 'search', value: searchTerm });
    }

    if (yearRange[0] > 2020 || yearRange[1] < 2030) {
      newActiveFilters.push({ type: 'year', value: `${yearRange[0]}-${yearRange[1]}` });
    }

    selectedCategories.forEach(cat => {
      newActiveFilters.push({ type: 'category', value: cat });
    });

    selectedThemes.forEach(theme => {
      newActiveFilters.push({ type: 'theme', value: theme });
    });

    if (sortBy !== 'name' || sortOrder !== 'asc') {
      newActiveFilters.push({ type: 'sort', value: `${sortBy} ${sortOrder}` });
    }

    setActiveFilters(newActiveFilters);

    setFilterVisualization({
      active: newActiveFilters.length > 0,
      count: newActiveFilters.length,
      filterTypes: {
        difficulty: newActiveFilters.filter(f => f.type === 'difficulty').length,
        search: newActiveFilters.filter(f => f.type === 'search').length,
        year: newActiveFilters.filter(f => f.type === 'year').length,
        category: newActiveFilters.filter(f => f.type === 'category').length,
        theme: newActiveFilters.filter(f => f.type === 'theme').length,
        sort: newActiveFilters.filter(f => f.type === 'sort').length,
      }
    });
  }, [filter, searchTerm, yearRange, selectedCategories, selectedThemes, sortBy, sortOrder]);

  useEffect(() => {
    if (filterPresets.length > 0) {
      localStorage.setItem('scenarioFilterPresets', JSON.stringify(filterPresets));
    }
  }, [filterPresets]);

  useEffect(() => {
    if (activeFilters.length > 0) {
      setFilterAnimation(true);
      setTimeout(() => setFilterAnimation(false), 500);
    }
  }, [activeFilters.length]);

  useEffect(() => {
    if (showPresetModal && presetInputRef.current) {
      presetInputRef.current.focus();
    }
  }, [showPresetModal]);

  const trackFilterChange = (filterType, filterValue) => {
    setLastAppliedFilter({ type: filterType, value: filterValue });
    setShowFilterTooltip(true);
    setTimeout(() => setShowFilterTooltip(false), 3000);

    setShowFilterStats(true);
    setTimeout(() => setShowFilterStats(false), 4000);
  };

  const filteredScenarios = scenarios
    .filter(scenario => {
      if (filter !== 'all' && scenario.difficulty.toLowerCase() !== filter.toLowerCase()) {
        return false;
      }

      const scenarioYear = parseInt(scenario.year);
      if (scenarioYear < yearRange[0] || scenarioYear > yearRange[1]) {
        return false;
      }

      if (selectedCategories.length > 0 && scenario.category &&
        !selectedCategories.includes(scenario.category)) {
        return false;
      }

      if (selectedThemes.length > 0) {
        const scenarioThemes = scenario.themes || [];
        if (!selectedThemes.some(theme => scenarioThemes.includes(theme))) {
          return false;
        }
      }

      if (searchTerm && !scenario.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !scenario.description.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }

      return true;
    })
    .sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'difficulty':
          const difficultyOrder = { 'Normal': 1, 'Medium': 2, 'Svær': 3, 'Meget svær': 4 };
          comparison = difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty];
          break;
        case 'year':
          comparison = parseInt(a.year) - parseInt(b.year);
          break;
        default:
          comparison = 0;
      }

      return sortOrder === 'asc' ? comparison : -comparison;
    });

  const handleDifficultyFilter = (difficulty) => {
    setFilter(difficulty);
    trackFilterChange('difficulty', difficulty);
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    if (e.target.value) {
      trackFilterChange('search', e.target.value);
    }
  };

  const handleYearRangeChange = (index, value) => {
    const newYearRange = [...yearRange];
    newYearRange[index] = parseInt(value);
    setYearRange(newYearRange);
    trackFilterChange('year', `${newYearRange[0]}-${newYearRange[1]}`);
  };

  const handleCategoryToggle = (category) => {
    setSelectedCategories(prev => {
      const newCategories = prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category];

      trackFilterChange('category', category);
      return newCategories;
    });
  };

  const handleThemeToggle = (theme) => {
    setSelectedThemes(prev => {
      const newThemes = prev.includes(theme)
        ? prev.filter(t => t !== theme)
        : [...prev, theme];

      trackFilterChange('theme', theme);
      return newThemes;
    });
  };

  const handleSortChange = (e) => {
    setSortBy(e.target.value);
    trackFilterChange('sort', e.target.value);
  };

  const handleSortOrderToggle = () => {
    const newOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    setSortOrder(newOrder);
    trackFilterChange('sortOrder', newOrder);
  };

  const handleSelect = (scenarioId) => {
    setSelectedScenario(scenarioId);
  };

  const handleStart = () => {
    const scenario = scenarios.find(s => s.id === selectedScenario);
    onSelectScenario(scenario);
  };

  const toggleFilters = () => {
    setShowFilters(prev => !prev);
  };

  const resetFilters = () => {
    setFilter('all');
    setSearchTerm('');
    setYearRange([2020, 2030]);
    setSortBy('name');
    setSortOrder('asc');
    setSelectedCategories([]);
    setSelectedThemes([]);
  };

  const removeFilter = (filterType, filterValue) => {
    switch (filterType) {
      case 'difficulty':
        setFilter('all');
        break;
      case 'search':
        setSearchTerm('');
        break;
      case 'year':
        setYearRange([2020, 2030]);
        break;
      case 'category':
        setSelectedCategories(prev => prev.filter(c => c !== filterValue));
        break;
      case 'theme':
        setSelectedThemes(prev => prev.filter(t => t !== filterValue));
        break;
      case 'sort':
        setSortBy('name');
        setSortOrder('asc');
        break;
    }
  };

  const saveCurrentFiltersAsPreset = () => {
    if (!presetName.trim()) return;

    const newPreset = {
      id: Date.now().toString(),
      name: presetName,
      filters: {
        difficulty: filter,
        searchTerm,
        yearRange: [...yearRange],
        categories: [...selectedCategories],
        themes: [...selectedThemes],
        sortBy,
        sortOrder
      },
      dateCreated: new Date().toLocaleDateString(),
      filterCount: activeFilters.length
    };

    setFilterPresets(prev => [...prev, newPreset]);
    setPresetName('');
    setShowPresetModal(false);

    alert(`Filter preset "${presetName}" saved successfully!`);
  };

  const loadFilterPreset = (preset) => {
    setFilter(preset.filters.difficulty);
    setSearchTerm(preset.filters.searchTerm);
    setYearRange(preset.filters.yearRange);
    setSelectedCategories(preset.filters.categories);
    setSelectedThemes(preset.filters.themes);
    setSortBy(preset.filters.sortBy);
    setSortOrder(preset.filters.sortOrder);
  };

  const deleteFilterPreset = (presetId) => {
    setFilterPresets(prev => prev.filter(p => p.id !== presetId));
  };

  const openPresetModal = () => {
    setShowPresetModal(true);
  };

  const cancelPresetSave = () => {
    setShowPresetModal(false);
    setPresetName('');
  };

  const exportFilterPresets = () => {
    const presetData = JSON.stringify(filterPresets, null, 2);
    const blob = new Blob([presetData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'scenario-filter-presets.json';
    a.click();

    URL.revokeObjectURL(url);
  };

  const importFilterPresets = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const presets = JSON.parse(event.target.result);
        if (Array.isArray(presets)) {
          setFilterPresets(prev => [...prev, ...presets]);
          alert(`Successfully imported ${presets.length} filter presets`);
        }
      } catch (err) {
        alert('Failed to parse the imported presets file');
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className={`scenario-selector ${filterAnimation ? 'filter-animation' : ''}`}>
      <h2>Vælg scenario</h2>

      <div className="scenario-filters-basic">
        <div className="search-box">
          <input
            type="text"
            placeholder="Søg efter scenario..."
            value={searchTerm}
            onChange={handleSearch}
          />
          <button className="search-icon" title="Søg">
            🔍
          </button>
        </div>

        <div className="filter-buttons">
          <button
            className={`advanced-filters-toggle ${showFilters ? 'active' : ''}`}
            onClick={toggleFilters}
          >
            {showFilters ? 'Skjul avancerede filtre' : 'Vis avancerede filtre'} {showFilters ? '▲' : '▼'}
          </button>

          <button
            className="preset-button"
            onClick={openPresetModal}
            title="Gem nuværende filtre som forudindstilling"
          >
            <span className="button-icon">💾</span> Gem filtre
          </button>
        </div>
      </div>

      {showFilterTooltip && lastAppliedFilter && (
        <div className="filter-tooltip">
          <span>Filter anvendt: <strong>{lastAppliedFilter.value}</strong> ({lastAppliedFilter.type})</span>
          <span className="close-tooltip" onClick={() => setShowFilterTooltip(false)}>✕</span>
        </div>
      )}

      {showFilterStats && filterVisualization.active && (
        <div className={`filter-stats-visual ${filterAnimation ? 'pulse' : ''}`}>
          <div className="filter-count">
            {filterVisualization.count} aktive filtre
          </div>
          <div className="filter-type-distribution">
            {Object.entries(filterVisualization.filterTypes).map(([type, count]) => (
              count > 0 && (
                <div key={type} className={`filter-type-indicator ${type}`} style={{ flex: count }}>
                  {count > 1 && count}
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {activeFilters.length > 0 && (
        <div className={`active-filters-container ${filterAnimation ? 'animate' : ''}`}>
          <div className="active-filters-header">
            <h3>Aktive filtre</h3>
            <button className="reset-filters" onClick={resetFilters}>
              Nulstil alle
            </button>
          </div>
          <div className="active-filters-tags">
            {activeFilters.map((filter, index) => (
              <div
                key={`${filter.type}-${filter.value}-${index}`}
                className={`filter-tag ${filter.type}`}
                onClick={() => removeFilter(filter.type, filter.value)}
              >
                <span className="filter-tag-type">
                  {filter.type === 'difficulty' && 'Sværhedsgrad'}
                  {filter.type === 'search' && 'Søgning'}
                  {filter.type === 'year' && 'År'}
                  {filter.type === 'category' && 'Kategori'}
                  {filter.type === 'theme' && 'Tema'}
                  {filter.type === 'sort' && 'Sortering'}
                </span>
                <span className="filter-tag-value">{filter.value}</span>
                <span className="filter-tag-remove">×</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="filter-presets-manager">
        <div className="presets-header">
          <h4>Filter forudindstillinger</h4>
          <div className="preset-buttons">
            <button
              className="save-preset-button"
              onClick={openPresetModal}
              disabled={activeFilters.length === 0}
            >
              Gem nuværende filtre
            </button>
            <button className="export-presets-button" onClick={exportFilterPresets}>
              Eksportér
            </button>
            <label className="import-presets-button">
              Importér
              <input
                type="file"
                accept=".json"
                onChange={importFilterPresets}
                style={{ display: 'none' }}
              />
            </label>
          </div>
        </div>

        {filterPresets.length > 0 && (
          <div className="preset-list">
            {filterPresets.map(preset => (
              <div key={preset.id} className="preset-item">
                <div className="preset-info">
                  <span className="preset-name">{preset.name}</span>
                  <span className="preset-count">
                    {preset.filterCount} filtre
                  </span>
                  <span className="preset-date">{preset.dateCreated}</span>
                </div>
                <div className="preset-actions">
                  <button
                    className="load-preset"
                    onClick={() => loadFilterPreset(preset)}
                  >
                    Indlæs
                  </button>
                  <button
                    className="delete-preset"
                    onClick={() => deleteFilterPreset(preset.id)}
                  >
                    Slet
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showPresetModal && (
        <div className="preset-modal-overlay">
          <div className="preset-modal">
            <h3>Gem filter forudindstilling</h3>
            <p>Gem dine nuværende filtre for hurtig adgang senere:</p>
            <input
              type="text"
              placeholder="Navn på filter forudindstilling"
              value={presetName}
              onChange={(e) => setPresetName(e.target.value)}
              ref={presetInputRef}
            />
            <div className="preset-summary">
              <div className="active-filter-count">
                {activeFilters.length} aktive filtre
              </div>
              <div className="filter-types-summary">
                {Object.entries(filterVisualization.filterTypes)
                  .filter(([_, count]) => count > 0)
                  .map(([type, count]) => (
                    <div key={type} className={`filter-type-tag ${type}`}>
                      {type}: {count}
                    </div>
                  ))
                }
              </div>
            </div>
            <div className="preset-modal-actions">
              <button className="cancel-button" onClick={cancelPresetSave}>
                Annuller
              </button>
              <button
                className="save-button"
                onClick={saveCurrentFiltersAsPreset}
                disabled={!presetName.trim()}
              >
                Gem
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="filter-summary">
        <span>Viser {filteredScenarios.length} ud af {scenarios.length} scenarier</span>
      </div>

      <div className="scenarios-grid">
        {filteredScenarios.length > 0 ? (
          filteredScenarios.map(scenario => (
            <div
              key={scenario.id}
              className={`scenario-card ${selectedScenario === scenario.id ? 'selected' : ''}`}
              onClick={() => handleSelect(scenario.id)}
            >
              <div className="scenario-image">
                <img src={scenario.image} alt={scenario.name} />
                <div className="scenario-year">{scenario.year}</div>
                <div className="scenario-difficulty">{scenario.difficulty}</div>
                {scenario.category && (
                  <div className="scenario-category">{scenario.category}</div>
                )}
              </div>
              <div className="scenario-info">
                <h3>{scenario.name}</h3>
                <p>{scenario.description}</p>
                <div className="scenario-details">
                  <div className="detail-item">
                    <span className="detail-label">Startår:</span>
                    <span className="detail-value">{scenario.year}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Sværhedsgrad:</span>
                    <span className="detail-value">{scenario.difficulty}</span>
                  </div>
                </div>
                {scenario.themes && scenario.themes.length > 0 && (
                  <div className="scenario-themes">
                    {scenario.themes.map(theme => (
                      <span key={theme} className="theme-tag">{theme}</span>
                    ))}
                  </div>
                )}
              </div>
              <div className="scenario-preview-button">
                <button onClick={(e) => {
                  e.stopPropagation();
                  alert(`Forhåndsvisning af ${scenario.name} kommer snart!`);
                }}>
                  Forhåndsvisning
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="no-scenarios">
            <p>Ingen scenarier matcher dine filtre. Prøv at ændre søgningen eller vælg 'Alle' fra filtret.</p>
            <button onClick={resetFilters} className="reset-button">Nulstil filtre</button>
          </div>
        )}
      </div>

      <div className="scenario-actions">
        <button onClick={onBack} className="back-button">Tilbage</button>
        <div className="selection-info">
          {selectedScenario && (
            <span>Valgt: {scenarios.find(s => s.id === selectedScenario)?.name}</span>
          )}
        </div>
        <button
          onClick={handleStart}
          className="start-button"
          disabled={!selectedScenario}
        >
          Start spillet
        </button>
      </div>
    </div>
  );
}

export default ScenarioSelector;