import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { geoMercator, geoPath } from 'd3-geo';
import { zoom } from 'd3-zoom';
import '../styles/MapPanel.css';

const MapPanel = ({ countries, selectedCountry, setSelectedCountry, gameData }) => {
  const mapRef = useRef(null);
  const svgRef = useRef(null);
  const tooltipRef = useRef(null);
  const [worldData, setWorldData] = useState(null);
  const [mapMode, setMapMode] = useState('political'); // political, economic, trade, diplomatic
  const [highlightedRegions, setHighlightedRegions] = useState([]);
  const [zoomLevel, setZoomLevel] = useState(1);

  // Fetch world map data
  useEffect(() => {
    const fetchWorldData = async () => {
      try {
        console.log('World map data would be loaded here');
        setWorldData({ type: 'FeatureCollection', features: [] });

        setTimeout(() => {
          createPlaceholderMap();
        }, 500);
      } catch (err) {
        console.error('Error loading map data:', err);
      }
    };

    fetchWorldData();
  }, []);

  // Map visualization modes
  const getCountryColor = (countryCode) => {
    if (!countries || !countries[countryCode]) return '#e0e0e0';

    const country = countries[countryCode];

    switch (mapMode) {
      case 'economic':
        const gdpValue = country.gdp || 0;
        const gdpMax = Object.values(countries).reduce((max, c) => Math.max(max, c.gdp || 0), 1);
        const gdpIntensity = Math.max(0.2, Math.min(0.9, (gdpValue / gdpMax) * 0.9));
        return `rgba(21, 101, 192, ${gdpIntensity})`;

      case 'trade':
        const tradeBalance = (country.exports || 0) - (country.imports || 0);
        if (tradeBalance > 0) {
          const intensity = Math.min(0.9, (tradeBalance / 1000) * 0.5 + 0.4);
          return `rgba(46, 125, 50, ${intensity})`;
        } else {
          const intensity = Math.min(0.9, (Math.abs(tradeBalance) / 1000) * 0.5 + 0.4);
          return `rgba(198, 40, 40, ${intensity})`;
        }

      case 'diplomatic':
        if (selectedCountry) {
          const relations = selectedCountry.relations?.[countryCode] || 0;
          if (relations > 50) return `rgba(25, 118, 210, ${0.3 + (relations - 50) / 100 * 0.6})`;
          if (relations >= 0) return `rgba(251, 192, 45, ${0.3 + relations / 100 * 0.6})`;
          return `rgba(211, 47, 47, ${0.3 + Math.abs(relations) / 100 * 0.6})`;
        }
        return '#e0e0e0';

      case 'political':
      default:
        const regionColors = {
          'North America': '#5D9CEC',
          'South America': '#A0D568',
          'Europe': '#AC92EB',
          'Africa': '#FFCE54',
          'Asia': '#FC6E51',
          'Oceania': '#48CFAD',
        };

        return regionColors[country.region] || '#e0e0e0';
    }
  };

  // Create placeholder map
  const createPlaceholderMap = () => {
    if (!svgRef.current) return;

    const width = mapRef.current.clientWidth;
    const height = 500;

    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height])
      .attr('style', 'width: 100%; height: auto; max-height: 500px;');

    const g = svg.append('g');

    if (countries) {
      const projection = geoMercator()
        .scale(width / 6.28)
        .translate([width / 2, height / 1.5]);

      Object.entries(countries).forEach(([countryCode, country]) => {
        let lat, lng;

        switch (country.region) {
          case 'North America':
            lat = 40 + Math.random() * 15;
            lng = -100 - Math.random() * 20;
            break;
          case 'South America':
            lat = -20 - Math.random() * 15;
            lng = -60 - Math.random() * 10;
            break;
          case 'Europe':
            lat = 50 + Math.random() * 10;
            lng = 10 + Math.random() * 20;
            break;
          case 'Africa':
            lat = 0 - Math.random() * 20;
            lng = 20 + Math.random() * 20;
            break;
          case 'Asia':
            lat = 30 + Math.random() * 20;
            lng = 100 + Math.random() * 30;
            break;
          case 'Oceania':
            lat = -25 - Math.random() * 10;
            lng = 135 + Math.random() * 20;
            break;
          default:
            lat = Math.random() * 60 - 30;
            lng = Math.random() * 360 - 180;
        }

        const [x, y] = projection([lng, lat]);
        const size = 10 + (country.gdp ? Math.sqrt(country.gdp) / 10 : 5);

        g.append('circle')
          .attr('cx', x)
          .attr('cy', y)
          .attr('r', size)
          .attr('fill', getCountryColor(countryCode))
          .attr('stroke', selectedCountry && selectedCountry.iso_code === countryCode ? '#000' : '#fff')
          .attr('stroke-width', selectedCountry && selectedCountry.iso_code === countryCode ? 3 : 1)
          .attr('class', 'country-marker')
          .attr('data-country', countryCode)
          .on('mouseover', function (event) {
            d3.select(this).attr('stroke-width', 2);

            const tooltip = d3.select(tooltipRef.current);
            tooltip.style('display', 'block')
              .html(`
                <strong>${country.name}</strong><br/>
                Population: ${country.population?.toLocaleString() || 'N/A'}<br/>
                GDP: ${country.gdp?.toLocaleString() || 'N/A'} M USD
              `)
              .style('left', `${event.pageX + 15}px`)
              .style('top', `${event.pageY - 28}px`);
          })
          .on('mouseout', function () {
            d3.select(this).attr('stroke-width',
              selectedCountry && selectedCountry.iso_code === countryCode ? 3 : 1);

            d3.select(tooltipRef.current).style('display', 'none');
          })
          .on('click', function () {
            if (countries[countryCode]) {
              setSelectedCountry(countries[countryCode]);
            }
          });

        if (country.gdp > 1000 || (country.population && country.population > 50000000)) {
          g.append('text')
            .attr('x', x)
            .attr('y', y + size + 10)
            .attr('text-anchor', 'middle')
            .attr('font-size', '9px')
            .attr('fill', '#333')
            .attr('class', 'country-label')
            .text(country.name);
        }
      });

      const zoomBehavior = zoom()
        .scaleExtent([0.5, 8])
        .on('zoom', (event) => {
          g.attr('transform', event.transform);
          setZoomLevel(event.transform.k);
        });

      svg.call(zoomBehavior);

      const regions = [...new Set(Object.values(countries).map(c => c.region))];
      regions.forEach(region => {
        let x, y;
        switch (region) {
          case 'North America': x = width * 0.2; y = height * 0.3; break;
          case 'South America': x = width * 0.3; y = height * 0.6; break;
          case 'Europe': x = width * 0.5; y = height * 0.3; break;
          case 'Africa': x = width * 0.5; y = height * 0.5; break;
          case 'Asia': x = width * 0.7; y = height * 0.4; break;
          case 'Oceania': x = width * 0.8; y = height * 0.7; break;
          default: x = width * 0.5; y = height * 0.5;
        }

        svg.append('text')
          .attr('x', x)
          .attr('y', y)
          .attr('text-anchor', 'middle')
          .attr('font-size', '20px')
          .attr('font-weight', 'bold')
          .attr('fill', 'rgba(0,0,0,0.07)')
          .attr('class', 'region-label')
          .text(region);
      });
    }
  };

  const captureMapScreenshot = () => {
    console.log('Screenshot functionality would be implemented here');
  };

  useEffect(() => {
    const handleResize = () => {
      if (countries) {
        createPlaceholderMap();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [countries, selectedCountry, mapMode]);

  useEffect(() => {
    if (countries) {
      createPlaceholderMap();
    }
  }, [countries, selectedCountry, mapMode]);

  useEffect(() => {
    if (!svgRef.current || !highlightedRegions.length) return;

    const svg = d3.select(svgRef.current);

    svg.selectAll('.country-marker').attr('stroke-width', c => {
      const code = d3.select(c).attr('data-country');
      return selectedCountry && selectedCountry.iso_code === code ? 3 : 1;
    });

    highlightedRegions.forEach(region => {
      svg.selectAll('.country-marker')
        .filter(function () {
          const code = d3.select(this).attr('data-country');
          return countries[code] && countries[code].region === region;
        })
        .attr('stroke', '#FFD700')
        .attr('stroke-width', 3);
    });
  }, [highlightedRegions, countries, selectedCountry]);

  return (
    <div className="map-panel" ref={mapRef}>
      <div className="map-controls">
        <div className="map-mode-selector">
          <button 
            className={`mode-btn ${mapMode === 'political' ? 'active' : ''}`} 
            onClick={() => setMapMode('political')}
          >
            <i className="fas fa-globe-americas"></i>
            <span>Political</span>
          </button>
          <button 
            className={`mode-btn ${mapMode === 'economic' ? 'active' : ''}`} 
            onClick={() => setMapMode('economic')}
          >
            <i className="fas fa-chart-line"></i>
            <span>Economic</span>
          </button>
          <button 
            className={`mode-btn ${mapMode === 'trade' ? 'active' : ''}`} 
            onClick={() => setMapMode('trade')}
          >
            <i className="fas fa-exchange-alt"></i>
            <span>Trade</span>
          </button>
          <button 
            className={`mode-btn ${mapMode === 'diplomatic' ? 'active' : ''}`} 
            onClick={() => setMapMode('diplomatic')}
            disabled={!selectedCountry}
          >
            <i className="fas fa-handshake"></i>
            <span>Diplomatic</span>
          </button>
        </div>
        
        <div className="map-navigation">
          <button className="nav-btn zoom-in" onClick={() => 
            d3.select(svgRef.current).transition().call(
              d3.zoom().scaleBy, 1.5
            )
          } title="Zoom In">
            <i className="fas fa-search-plus"></i>
          </button>
          <button className="nav-btn zoom-out" onClick={() => 
            d3.select(svgRef.current).transition().call(
              d3.zoom().scaleBy, 0.75
            )
          } title="Zoom Out">
            <i className="fas fa-search-minus"></i>
          </button>
          <button className="nav-btn reset" onClick={() => 
            d3.select(svgRef.current).transition().call(
              d3.zoom().transform, d3.zoomIdentity
            )
          } title="Reset View">
            <i className="fas fa-expand"></i>
          </button>
          <button className="nav-btn screenshot" onClick={() => captureMapScreenshot()} title="Take Screenshot">
            <i className="fas fa-camera"></i>
          </button>
        </div>
      </div>
      
      <div className="map-container">
        <div className="map-backdrop"></div>
        <svg ref={svgRef}></svg>
        <div className="map-tooltip" ref={tooltipRef}></div>
        <div className="map-overlay-effects"></div>
        
        {/* Map legend */}
        <div className="map-legend">
          <h4>{mapMode.charAt(0).toUpperCase() + mapMode.slice(1)} Map</h4>
          {mapMode === 'economic' && (
            <div className="legend-items">
              <div className="legend-item">
                <span className="color-sample" style={{background: 'linear-gradient(to right, rgba(21, 101, 192, 0.2), rgba(21, 101, 192, 0.9))'}}></span>
                <div className="legend-labels">
                  <span>Low GDP</span>
                  <span>High GDP</span>
                </div>
              </div>
            </div>
          )}
          
          {mapMode === 'trade' && (
            <div className="legend-items">
              <div className="legend-item">
                <span className="color-sample" style={{background: 'linear-gradient(to right, rgba(198, 40, 40, 0.7), rgba(46, 125, 50, 0.7))'}}></span>
                <div className="legend-labels">
                  <span>Trade Deficit</span>
                  <span>Trade Surplus</span>
                </div>
              </div>
            </div>
          )}
          
          {mapMode === 'diplomatic' && selectedCountry && (
            <div className="legend-items">
              <div className="legend-item">
                <span className="color-sample" style={{background: 'linear-gradient(to right, rgba(211, 47, 47, 0.7), rgba(251, 192, 45, 0.7), rgba(25, 118, 210, 0.7))'}}></span>
                <div className="legend-labels">
                  <span>Hostile</span>
                  <span>Neutral</span>
                  <span>Allied</span>
                </div>
              </div>
            </div>
          )}
          
          {mapMode === 'political' && (
            <div className="legend-items">
              {['North America', 'South America', 'Europe', 'Africa', 'Asia', 'Oceania'].map(region => (
                <div className="legend-item" key={region}>
                  <span className="color-sample" style={{
                    backgroundColor: {
                      'North America': '#5D9CEC',
                      'South America': '#A0D568',
                      'Europe': '#AC92EB',
                      'Africa': '#FFCE54',
                      'Asia': '#FC6E51',
                      'Oceania': '#48CFAD'
                    }[region]
                  }}></span>
                  <span className="legend-label">{region}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Map stats overlay */}
        <div className="map-stats-overlay">
          <div className="zoom-level-indicator">
            <span>Zoom: {Math.round(zoomLevel * 100)}%</span>
          </div>
          {selectedCountry && (
            <div className="selected-country-info">
              <img 
                src={`/flags/${selectedCountry.iso_code.toLowerCase()}.png`} 
                alt="" 
                className="country-flag"
                onError={(e) => { e.target.style.display = 'none' }}
              />
              <span>{selectedCountry.name}</span>
            </div>
          )}
        </div>
      </div>
      
      {/* Game event notification overlay */}
      {gameData && gameData.currentEvent && (
        <div className="map-event-notification">
          <div className="event-icon">
            <i className={`fas ${
              gameData.currentEvent.type === 'economic' ? 'fa-chart-line' :
              gameData.currentEvent.type === 'political' ? 'fa-landmark' :
              gameData.currentEvent.type === 'natural' ? 'fa-cloud-showers-heavy' :
              gameData.currentEvent.type === 'technological' ? 'fa-microchip' :
              'fa-exclamation-circle'
            }`}></i>
          </div>
          <div className="event-content">
            <h4>Global Event: {gameData.currentEvent.title}</h4>
            <p>{gameData.currentEvent.description}</p>
            <div className="event-impact">
              {gameData.currentEvent.impactedRegions?.map(region => (
                <span 
                  key={region} 
                  className="region-tag"
                  onClick={() => {
                    setHighlightedRegions([region]);
                    setTimeout(() => setHighlightedRegions([]), 3000);
                  }}
                >
                  <i className="fas fa-map-marker-alt"></i>
                  {region}
                </span>
              ))}
            </div>
          </div>
          <button className="close-event-btn" onClick={() => {
            console.log('Event dismissed');
          }}>
            <i className="fas fa-times"></i>
          </button>
        </div>
      )}
    </div>
  );
};

export default MapPanel;
