import { useState, useEffect, useRef } from 'react';
import './App.css';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import CountryInfoPanel from './components/CountryInfoPanel';
import BNPHistoryPanel from './components/BNPHistoryPanel';
import DiplomacyPanel from './components/DiplomacyPanel';
import EventFeedPanel from './components/EventFeedPanel';
import PolicyPanel from './components/PolicyPanel';
import TutorialPanel from './components/TutorialPanel';
import MapPanel from './components/MapPanel';
import GamePhaseController from './components/GamePhaseController';
import CountryAnalysisPanel from './components/CountryAnalysisPanel';
import DecisionImpactPanel from './components/DecisionImpactPanel';

function App() {
  // --- State ---
  const [countries, setCountries] = useState({});
  const [selectedIso, setSelectedIso] = useState('');
  const [targetCountry, setTargetCountry] = useState(null); // Land valgt for handelspolitik
  const [countryData, setCountryData] = useState(null);
  const [bnpHistory, setBnpHistory] = useState([]);
  const [eventFeed, setEventFeed] = useState([]);
  const [diplomacy, setDiplomacy] = useState({ relations: [], alliances: [] });
  const [loading, setLoading] = useState(false);
  const [gameStarted, setGameStarted] = useState(false);
  const [currentPhase, setCurrentPhase] = useState(0);
  const [currentTurn, setCurrentTurn] = useState(0);
  const [showTutorial, setShowTutorial] = useState(false);
  const [lastDecisions, setLastDecisions] = useState([]);
  const [policyRanges, setPolicyRanges] = useState({
    tariff: { min: 0, max: 50, normal: 10, description: "Toldsatser er ekstra afgifter på importvarer. Normal told er omkring 5-15%, høj told over 20%." },
    tax: { min: 10, max: 60, normal: 30, description: "Skattesatser påvirker din økonomi og befolkningens tilfredshed. Normal skat er 25-35%, høj skat over 40%." },
    subsidy: { min: 0, max: 30, normal: 5, description: "Subsidier er støtte til din industri. Normal subsidie er 2-8%, høj subsidie over 10%." }
  });
  
  // Refs
  const mapRef = useRef(null);
  const leafletMap = useRef(null);

  // --- Fetch countries on mount ---
  useEffect(() => {
    fetch('/api/countries')
      .then(res => res.json())
      .then(data => {
        // Konverter array til objekt med iso_code som nøgle for lettere opslag
        const countriesObj = {};
        // Kontroller at data er et array, ellers konverter
        const countriesArray = Array.isArray(data) ? data : data.countries || [data];
        
        if (countriesArray.length > 0) {
          countriesArray.forEach(country => {
            if (country && country.iso_code) {
              countriesObj[country.iso_code] = country;
            }
          });
          setCountries(countriesObj);
          if (Object.values(countriesObj).length > 0) {
            setSelectedIso(Object.values(countriesObj)[0].iso_code);
          }
        } else {
          console.error("Ingen lande fundet i API-svaret:", data);
        }
      })
      .catch(error => {
        console.error("Fejl ved hentning af lande:", error);
      });

    // Hent spil status
    fetch('/api/game_state')
      .then(res => res.json())
      .then(data => {
        if (data.current_turn) {
          setCurrentTurn(data.current_turn);
          if (data.player_country_iso) {
            setSelectedIso(data.player_country_iso);
            setGameStarted(true);
          }
        }
      })
      .catch(error => {
        console.error("Fejl ved hentning af spilstatus:", error);
      });
  }, []);

  // --- Fetch country data when selectedIso changes ---
  useEffect(() => {
    if (!selectedIso) return;
    setLoading(true);
    fetch(`/api/countries/${selectedIso}`)
      .then(res => res.json())
      .then(data => {
        // Berig data med relationsinformation
        setCountryData({...data, relations: diplomacy.relations});
        setLoading(false);
        // BNP historik (kun eksempel, kan udvides)
        setBnpHistory(hist => [...hist, { turn: hist.length + 1, gdp: data.gdp }].slice(-40));
      });
    // Diplomati
    fetch(`/api/diplomacy/${selectedIso}`)
      .then(res => res.json())
      .then(data => {
        setDiplomacy(data);
        // Opdater countryData med de nye relationer, hvis den allerede eksisterer
        setCountryData(prev => prev ? {...prev, relations: data.relations} : prev);
      });
  }, [selectedIso]);

  // --- Event feed eksempel ---
  useEffect(() => {
    if (!gameStarted) {
      setEventFeed(feed => [
        { text: 'Velkommen til Trade War Simulator! Vælg dit land og start spillet.', ts: new Date().toLocaleTimeString() },
        ...feed.slice(0, 9)
      ]);
    }
  }, [gameStarted]);

  // --- Handlers ---
  const handleCountryChange = e => setSelectedIso(e.target.value);

  const handleMapCountrySelect = (iso) => {
    // Når et land vælges på kortet, sæt det som målland for handelspolitik
    if (iso !== selectedIso) {
      setTargetCountry(iso);
      
      // Find landeoplysninger
      const country = countries[iso];
      if (country) {
        setEventFeed(feed => [
          { text: `${country.name} valgt som handelsmål.`, ts: new Date().toLocaleTimeString() },
          ...feed.slice(0, 9)
        ]);
      }
    }
  };

  const handleStartGame = () => {
    if (!selectedIso) {
      setEventFeed(feed => [
        { text: 'Du skal vælge et land først!', ts: new Date().toLocaleTimeString() },
        ...feed.slice(0, 9)
      ]);
      return;
    }
    
    setGameStarted(true);
    setCurrentPhase(0);
    setCurrentTurn(1);
    setEventFeed(feed => [
      { text: `Spillet er startet! Du spiller som ${countryData?.name}. God fornøjelse!`, ts: new Date().toLocaleTimeString() },
      ...feed.slice(0, 9)
    ]);
    
    // Send player choice to backend
    fetch('/api/next_turn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ playerCountry: selectedIso })
    })
    .then(res => res.json())
    .then(data => {
      console.log('Game started', data);
    });
  };

  const handleNextTurn = () => {
    if (!gameStarted) return;
    
    setLoading(true);
    fetch('/api/next_turn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ playerCountry: selectedIso }) // Sørg for at sende data altid
    })
    .then(res => {
      if (!res.ok) {
        console.error("Fejl ved next_turn:", res.status);
        throw new Error(`Server returnerede ${res.status}`);
      }
      return res.json();
    })
    .then(data => {
      setCurrentTurn(data.turn || currentTurn + 1);
      setCurrentPhase(0);
      setEventFeed(feed => [
        { text: `Tur ${data.turn || currentTurn + 1} er begyndt!`, ts: new Date().toLocaleTimeString() },
        ...feed.slice(0, 9)
      ]);
      
      // Opdater landets data
      return fetch(`/api/countries/${selectedIso}`);
    })
    .then(res => {
      if (!res.ok) throw new Error(`Kunne ikke hente landedata: ${res.status}`);
      return res.json();
    })
    .then(data => {
      setCountryData(prev => ({...data, relations: prev?.relations || []}));
      setBnpHistory(hist => [...hist, { turn: currentTurn + 1, gdp: data.gdp }].slice(-40));
      setLoading(false);
      
      // Hent feedback for denne tur
      return fetch(`/api/turn_feedback/${selectedIso}`);
    })
    .then(res => {
      if (!res.ok) return null; // Ignorerer fejl her
      return res.json();
    })
    .then(data => {
      if (data && data.feedback && data.feedback !== 'ok') {
        setEventFeed(feed => [
          { text: `Feedback: ${data.feedback}`, ts: new Date().toLocaleTimeString() },
          ...feed.slice(0, 9)
        ]);
      }
    })
    .catch(error => {
      console.error("Fejl under tur-skift:", error);
      setLoading(false);
      setEventFeed(feed => [
        { text: `Fejl: ${error.message}`, ts: new Date().toLocaleTimeString() },
        ...feed.slice(0, 9)
      ]);
    });
  };

  const handlePhaseChange = (phase) => {
    setCurrentPhase(phase);
    setEventFeed(feed => [
      { text: `Fasen er ændret til: ${["Forberedelse", "Handelsvalg", "Simulering", "Resultater", "Afslutning"][phase]}`, ts: new Date().toLocaleTimeString() },
      ...feed.slice(0, 9)
    ]);
  };
  
  const handlePolicyAction = (feed) => {
    // Udover at opdatere feed, registrerer vi også beslutningen til konsekvensanalyse
    const lastAction = feed && feed.length > 0 ? feed[0] : null;
    
    if (lastAction && lastAction.text && (lastAction.text.includes("ændret") || lastAction.text.includes("indført"))) {
      // Forsøg at udtrække informationen fra beskeden
      const policyMatch = lastAction.text.match(/(Told|Skat|Subsidie)/i);
      const valueMatch = lastAction.text.match(/(\d+(?:\.\d+)?)%/);
      const targetMatch = lastAction.text.match(/mod (\w+)/i);
      
      if (policyMatch && valueMatch) {
        const policy = policyMatch[0].toLowerCase();
        const value = parseFloat(valueMatch[1]);
        const target = targetMatch ? targetMatch[1] : 'all';
        
        setLastDecisions([
          { 
            policy: { policy, value, target },
            timestamp: new Date().toISOString()
          },
          ...lastDecisions.slice(0, 4)
        ]);
      }
    }
    
    // Opdater feed som normalt
    setEventFeed(feed || []);
  };

  const toggleTutorial = () => {
    setShowTutorial(!showTutorial);
  };

  // --- Render ---
  return (
    <div className="app-container">
      <h1>Trade War Simulator</h1>
      
      {!gameStarted ? (
        <div className="game-start-screen">
          <h2>Vælg dit land og start handelskrigs-simulatoren</h2>
          <div className="country-selection">
            <label>
              Vælg land:
              <select value={selectedIso} onChange={handleCountryChange}>
                {Object.values(countries).map(c => (
                  <option key={c.iso_code} value={c.iso_code}>{c.name}</option>
                ))}
              </select>
            </label>
            <button className="start-button" onClick={handleStartGame}>Start Spillet</button>
            <button className="tutorial-button" onClick={toggleTutorial}>
              {showTutorial ? "Skjul Tutorial" : "Vis Tutorial"}
            </button>
          </div>
          {showTutorial && <TutorialPanel />}
          <div className="preview-info">
            {countryData && (
              <div>
                <h3>Forhåndsvisning af {countryData.name}</h3>
                <p>BNP: {countryData.gdp} mia. $</p>
                <p>Befolkning: {countryData.population} mio.</p>
                <p>Regeringsform: {countryData.government_type}</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="main-layout">
          <div className="game-controls">
            <div className="turn-info">
              <h3>Tur: {currentTurn}</h3>
              <button className="next-turn-button" onClick={handleNextTurn}>Næste Tur</button>
              <button className="tutorial-button" onClick={toggleTutorial}>
                {showTutorial ? "Skjul Tutorial" : "Vis Tutorial"}
              </button>
            </div>
            <GamePhaseController currentPhase={currentPhase} onPhaseChange={handlePhaseChange} />
          </div>
          
          <div className="game-content">
            <div className="sidebar">
              <h3>Dit land: {countryData?.name}</h3>
              <CountryInfoPanel country={countryData} loading={loading} />
              <CountryAnalysisPanel 
                country={countryData} 
                allCountries={countries} 
                diplomacy={diplomacy} 
              />
              <BNPHistoryPanel history={bnpHistory} />
              <DiplomacyPanel diplomacy={diplomacy} />
            </div>
            <div className="content">
              <MapPanel 
                countryData={countryData} 
                countries={countries} 
                selectedIso={selectedIso}
                onCountrySelect={handleMapCountrySelect} 
              />
              <div className="interactive-panels">
                <div className="policy-section">
                  <PolicyPanel 
                    iso={selectedIso} 
                    targetCountry={targetCountry}
                    policyRanges={policyRanges}
                    onAction={handlePolicyAction} 
                  />
                </div>
                <div className="impact-section">
                  <DecisionImpactPanel 
                    country={countryData}
                    targetCountry={targetCountry}
                    lastDecisions={lastDecisions}
                    allCountries={countries}
                    policyRanges={policyRanges}
                  />
                </div>
              </div>
              <EventFeedPanel feed={eventFeed} />
              {showTutorial && <TutorialPanel />}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
