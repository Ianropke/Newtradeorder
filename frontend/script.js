document.addEventListener('DOMContentLoaded', () => {
    const countrySelect = document.getElementById('country-select');
    const nextTurnButton = document.getElementById('next-turn');
    const countryInfoDiv = document.getElementById('country-info');
    const mapContainer = document.getElementById('map-container');

    let allCountriesData = {}; // Store all country data fetched initially
    let bnpHistory = {}; // BNP-historik for valgte land
    let eventFeed = []; // Event feed
    let worldMap; // Leaflet map reference
    let countryLayers = {}; // Lag med lande på kortet

    // --- API Fetch Functions ---
    async function fetchCountries() {
        try {
            const response = await fetch('/api/countries');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const countries = await response.json();
            return countries;
        } catch (error) {
            console.error('Error fetching countries:', error);
            countryInfoDiv.innerHTML = '<p style="color: red;">Error loading country list.</p>';
            return []; // Return empty array on error
        }
    }

    async function fetchCountryDetails(isoCode) {
        try {
            const response = await fetch(`/api/countries/${isoCode}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const details = await response.json();
            return details;
        } catch (error) {
            console.error(`Error fetching details for ${isoCode}:`, error);
            return null; // Return null on error
        }
    }

    async function advanceTurn() {
        try {
            const response = await fetch('/api/next_turn', { method: 'POST' });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            console.log('Turn advanced:', result);
            return true;
        } catch (error) {
            console.error('Error advancing turn:', error);
            alert('Error advancing turn. See console for details.');
            return false;
        }
    }

    // --- UI Update Functions ---
    async function populateCountrySelect() {
        const select = document.getElementById('country-select');
        if (!select) return;
        select.innerHTML = '<option disabled selected>Indlæser lande...</option>';
        try {
            const response = await fetch('/api/countries');
            if (!response.ok) {
                throw new Error('Kunne ikke hente lande fra API');
            }
            const countries = await response.json();
            processCountriesData(countries);
        } catch (error) {
            console.error('Error fetching countries:', error);
            select.innerHTML = '<option disabled selected>Fejl ved indlæsning</option>';
            countryInfoDiv.innerHTML = '<p style="color: red;">Error loading country list. Check server connection.</p>';
        }
    }

    function processCountriesData(countries) {
        const select = document.getElementById('country-select');
        if (!select) return;
        select.innerHTML = '';
        // Add placeholder option
        const placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.textContent = 'Vælg et land...';
        placeholder.disabled = true;
        placeholder.selected = true;
        select.appendChild(placeholder);
        countries.forEach(c => {
            allCountriesData[c.iso_code] = c;
            const opt = document.createElement('option');
            opt.value = c.iso_code;
            opt.textContent = c.name;
            select.appendChild(opt);
        });
        if (countries.length > 0) {
            fetchCountryData(countries[0].iso_code);
            loadWorldMapData();
        }
    }

    async function displayCountryInfo() {
        const selectedIsoCode = countrySelect.value;
        if (!selectedIsoCode) {
            countryInfoDiv.innerHTML = '<p>Select a country.</p>';
            return;
        }

        const selectedCountry = await fetchCountryDetails(selectedIsoCode);

        if (selectedCountry) {
            // Format industries nicely
            let industriesHtml = 'N/A';
            if (selectedCountry.industries && typeof selectedCountry.industries === 'object') {
                industriesHtml = Object.entries(selectedCountry.industries)
                    .map(([key, value]) => `${key}: ${value.toFixed(1)}%`)
                    .join(', ');
            }

            countryInfoDiv.innerHTML = `
                <h3>${selectedCountry.name} (${selectedCountry.iso_code})</h3>
                <p>GDP: ${selectedCountry.gdp ? selectedCountry.gdp.toFixed(2) : 'N/A'} B</p>
                <p>Population: ${selectedCountry.population ? selectedCountry.population.toLocaleString() : 'N/A'}</p>
                <p>Unemployment: ${selectedCountry.unemployment_rate ? selectedCountry.unemployment_rate.toFixed(1) : 'N/A'}%</p>
                <p>Growth Rate: ${selectedCountry.growth_rate ? selectedCountry.growth_rate.toFixed(1) : 'N/A'}%</p>
                <p>Approval: ${selectedCountry.approval_rating ? selectedCountry.approval_rating.toFixed(1) : 'N/A'}%</p>
                <p>Industries: ${industriesHtml}</p>
                <p>Government: ${selectedCountry.government_type || 'N/A'}</p>
                <p>EU Member: ${selectedCountry.is_eu_member ? 'Yes' : 'No'}</p>
                <!-- Add more details later -->
            `;

            updateBNPHistory(selectedCountry.iso_code, selectedCountry.gdp);
            renderBNPHistoryChart(selectedCountry.iso_code);
        } else {
            countryInfoDiv.innerHTML = '<p style="color: red;">Could not load details for selected country.</p>';
        }
    }

    async function handleNextTurn() {
        console.log('Next turn button clicked');
        addEventToFeed('Starter næste tur...');
        
        try {
            let response = await fetch('/api/next_turn', { method: 'POST' });
            if (!response.ok) {
                console.error('Kunne ikke udføre næste tur');
                addEventToFeed('Fejl: Kunne ikke udføre næste tur');
                return false;
            }
            
            const result = await response.json();
            console.log('Turn advanced:', result);
            addEventToFeed('Ny tur gennemført. Økonomien er opdateret.');
            
            // Opdater det valgte land
            if (countrySelect && countrySelect.value) {
                await fetchCountryData(countrySelect.value);
                await fetchAndShowTurnFeedback(countrySelect.value);
            }
            
            return true;
            
        } catch (error) {
            console.error('Error advancing turn:', error);
            addEventToFeed('Fejl under udfører af næste tur');
            return false;
        }
    }

    // --- World Map Functions ---
    function initializeMap() {
        if (worldMap) return; // Undgå dubleret initialisering
        
        const mapElement = document.getElementById('world-map');
        if (!mapElement) {
            console.error('Map element not found');
            return;
        }
        
        // Initialiser Leaflet kort
        worldMap = L.map('world-map', {
            center: [20, 0],
            zoom: 2,
            minZoom: 2,
            maxZoom: 10,
            worldCopyJump: true
        });
        
        // Tilføj base tile layer (OpenStreetMap)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            noWrap: false
        }).addTo(worldMap);
        
        // Tilføj Leaflet scale
        L.control.scale({imperial: false}).addTo(worldMap);
        
        // Efter kort er initialiseret, indlæs data
        loadWorldMapData();
    }
    
    async function loadWorldMapData() {
        if (!worldMap || Object.keys(allCountriesData).length === 0) return;
        
        try {
            // Hent GeoJSON-data fra en offentlig kilde
            const response = await fetch('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson');
            if (!response.ok) throw new Error('Kunne ikke hente kort-data');
            
            const geojsonData = await response.json();
            
            // Tilføj GeoJSON-lag med styling baseret på data
            L.geoJSON(geojsonData, {
                style: function(feature) {
                    const isoCode = feature.properties.ISO_A3;
                    const countryData = allCountriesData[isoCode];
                    
                    // Basis styling
                    const style = {
                        weight: 1,
                        opacity: 1,
                        color: '#888',
                        fillOpacity: 0.6
                    };
                    
                    // Hvis vi har data for dette land
                    if (countryData) {
                        // GDP-baseret farve (jo højere GDP, jo mørkere blå)
                        const gdp = countryData.gdp || 0;
                        let intensity = Math.min(1, Math.log(gdp/100) / 10);
                        intensity = Math.max(0.1, intensity); // Undgå helt hvide lande
                        
                        style.fillColor = `rgba(0, 60, 136, ${intensity})`;
                        style.fillOpacity = 0.7;
                    } else {
                        style.fillColor = '#ccc';
                    }
                    
                    return style;
                },
                onEachFeature: function(feature, layer) {
                    const isoCode = feature.properties.ISO_A3;
                    
                    // Gem en reference til laget for hvert land
                    countryLayers[isoCode] = layer;
                    
                    // Tilføj popup og event listeners
                    const name = feature.properties.ADMIN;
                    layer.bindPopup(`<b>${name}</b><br>Klik for at vælge`);
                    
                    layer.on({
                        mouseover: function(e) {
                            layer.setStyle({
                                weight: 3,
                                color: '#333'
                            });
                            layer.bringToFront();
                        },
                        mouseout: function(e) {
                            L.geoJSON.resetStyle(layer);
                        },
                        click: function(e) {
                            // Opdater valgt land i dropdown
                            if (countrySelect && allCountriesData[isoCode]) {
                                countrySelect.value = isoCode;
                                fetchCountryData(isoCode);
                            }
                        }
                    });
                }
            }).addTo(worldMap);
            
            // Highlight det valgte land, hvis der er et valgt
            highlightSelectedCountry();
            
        } catch (error) {
            console.error('Error loading map data:', error);
            addEventToFeed('Fejl ved indlæsning af kortdata');
        }
    }
    
    function highlightSelectedCountry() {
        if (!worldMap || !countrySelect) return;
        
        const selectedIsoCode = countrySelect.value;
        if (!selectedIsoCode || !countryLayers[selectedIsoCode]) return;
        
        // Nulstil stil på alle lande
        Object.values(countryLayers).forEach(layer => {
            L.geoJSON.resetStyle(layer);
        });
        
        // Highlight det valgte land
        countryLayers[selectedIsoCode].setStyle({
            weight: 3,
            color: '#f00',
            dashArray: '',
            fillOpacity: 0.7
        });
        
        countryLayers[selectedIsoCode].bringToFront();
        
        // Centrer kort på det valgte land
        worldMap.fitBounds(countryLayers[selectedIsoCode].getBounds(), {
            padding: [50, 50],
            maxZoom: 5
        });
    }

    // Funktion til at hente og vise lande- og sektordata fra backend
    async function fetchCountryData(isoCode) {
        if (!isoCode) return;
        
        try {
            const response = await fetch(`/api/countries/${isoCode}`);
            if (!response.ok) {
                console.error(`Kunne ikke hente data for ${isoCode}`);
                return;
            }
            
            const data = await response.json();
            allCountriesData[isoCode] = data; // Opdater data i vores cache
            renderCountryInfo(data);
            updateBNPHistory(isoCode, data.gdp);
            renderBNPHistoryChart(isoCode);
            highlightSelectedCountry(); // Fremhæv landet på kortet
            
        } catch (error) {
            console.error(`Error fetching details for ${isoCode}:`, error);
            addEventToFeed(`Fejl ved hentning af data for ${isoCode}`);
        }
    }

    // Udvid renderCountryInfo til at vise handelsblok med ikon og tooltip
    function renderCountryInfo(data) {
        const infoDiv = document.getElementById('country-info');
        if (!infoDiv) return;
        let tradeBloc = 'Ingen';
        let tradeBlocIcon = '';
        let tradeBlocTooltip = '';
        if (data.is_eu_member) {
            tradeBloc = 'EU';
            tradeBlocIcon = '🇪🇺';
            tradeBlocTooltip = 'Medlem af Den Europæiske Union. Fælles toldsatser og frihandel internt.';
        } else if (["USA","CAN","MEX"].includes(data.iso_code)) {
            tradeBloc = 'NAFTA';
            tradeBlocIcon = '🌎';
            tradeBlocTooltip = 'Medlem af NAFTA/USMCA. Lavere toldsatser mellem medlemslande.';
        }

        infoDiv.innerHTML = `
            <div class="widget">
                <h3>${data.name} (${data.iso_code})</h3>
                <div style="display: flex; gap: 18px; flex-wrap: wrap;">
                    <div><b>BNP:</b><br><span style="font-size:1.2em">${data.gdp?.toLocaleString() ?? 'N/A'}</span> mio. USD</div>
                    <div><b>Befolkning:</b><br><span style="font-size:1.2em">${data.population?.toLocaleString() ?? 'N/A'}</span> mio.</div>
                    <div><b>Arbejdsløshed:</b><br><span style="font-size:1.2em">${data.unemployment_rate?.toFixed(1) ?? 'N/A'}%</span></div>
                    <div><b>Godkendelsesrate:</b><br><span style="font-size:1.2em">${data.approval_rating?.toFixed(1) ?? 'N/A'}%</span></div>
                </div>
                <p style="margin-top:10px"><b>Regeringstype:</b> ${data.government_type || 'N/A'}</p>
                <p><b>Handelsblok:</b> <span style="font-weight:bold;color:#2d7ff9" title="${tradeBlocTooltip}">${tradeBlocIcon} ${tradeBloc}</span></p>
            </div>
            <div class="widget">
                <h4>Sektorfordeling (andel af BNP)</h4>
                <ul style="list-style:none;padding:0;">
                    <li><b>Industri:</b> ${(data.industries?.manufacturing*100).toFixed(1) ?? 'N/A'}%</li>
                    <li><b>Service:</b> ${(data.industries?.services*100).toFixed(1) ?? 'N/A'}%</li>
                    <li><b>Landbrug:</b> ${(data.industries?.agriculture*100).toFixed(1) ?? 'N/A'}%</li>
                </ul>
            </div>
            <div class="widget">
                <h4>Sektorer</h4>
                <table style="width:100%;border-collapse:collapse;font-size:0.98em;">
                    <thead><tr style="background:#f0f4fa"><th style="text-align:left">Sektor</th><th>Output</th><th>Beskæftigelse</th><th>Ledighed</th><th>Pris</th></tr></thead>
                    <tbody>
                    ${(data.sectors || []).map(s => `
                        <tr><td>${s.name}</td><td>${s.output?.toLocaleString() ?? 'N/A'}</td><td>${s.employment?.toLocaleString() ?? 'N/A'}</td><td>${s.unemployment_rate?.toFixed(1) ?? 'N/A'}%</td><td>${s.price?.toFixed(2) ?? 'N/A'}</td></tr>
                    `).join('')}
                    </tbody>
                </table>
            </div>
            <div class="widget" id="sector-charts">
                <h4>Visualisering: Output pr. sektor</h4>
                <canvas id="sectorOutputChart" height="120"></canvas>
            </div>
        `;
        // Tegn sektorgraf (bar chart) hvis Chart.js er loaded
        if (window.Chart && data.sectors && data.sectors.length > 0) {
            const ctx = document.getElementById('sectorOutputChart').getContext('2d');
            if (window.sectorChart) window.sectorChart.destroy();
            window.sectorChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.sectors.map(s => s.name),
                    datasets: [{
                        label: 'Output (mio. USD)',
                        data: data.sectors.map(s => s.output),
                        backgroundColor: '#2d7ff9',
                    }]
                },
                options: {
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true } }
                }
            });
            makeSectorChartInteractive();
        }
    }

    // Funktion til at vise feedback og økonomisk indsigt efter hver tur
    function showTurnFeedback(data) {
        const feedbackDiv = document.getElementById('turn-feedback');
        if (!feedbackDiv) return;
        let feedback = '';
        if (data.gdp_change) {
            feedback += `<div class="widget"><b>BNP ændring:</b> ${data.gdp_change > 0 ? '+' : ''}${data.gdp_change.toFixed(2)}%<br>`;
            feedback += data.gdp_change > 0 ? 'Økonomien voksede – typisk et resultat af øget efterspørgsel, investering eller eksport.' : 'Økonomien skrumpede – kan skyldes lavere forbrug, eksport eller negative chok.';
            feedback += '</div>';
        }
        if (data.unemployment_change) {
            feedback += `<div class="widget"><b>Arbejdsløshed ændring:</b> ${data.unemployment_change > 0 ? '+' : ''}${data.unemployment_change.toFixed(2)}%<br>`;
            feedback += data.unemployment_change < 0 ? 'Faldende arbejdsløshed – ofte drevet af vækst (Okuns lov).' : 'Stigende arbejdsløshed – typisk ved lav vækst eller negative shocks.';
            feedback += '</div>';
        }
        if (data.trust_change) {
            feedback += `<div class="widget"><b>Borgernes tillid:</b> ${data.trust_change > 0 ? '+' : ''}${data.trust_change.toFixed(2)}<br>`;
            feedback += data.trust_change > 0 ? 'Stigende tillid – stabile priser og lav ledighed styrker opbakningen.' : 'Faldende tillid – høj inflation eller arbejdsløshed svækker opbakningen.';
            feedback += '</div>';
        }
        if (data.policy_effects && data.policy_effects.length > 0) {
            feedback += '<div class="widget"><b>Effekter af dine valg:</b><ul>';
            data.policy_effects.forEach(eff => {
                feedback += `<li>${eff}</li>`;
            });
            feedback += '</ul></div>';
        }
        if (data.ai_feedback && data.ai_feedback.length > 0) {
            feedback += '<div class="widget" style="background:#f7faff"><b>AI-reaktioner:</b><ul>';
            data.ai_feedback.forEach(eff => {
                feedback += `<li>${eff}</li>`;
            });
            feedback += '</ul></div>';
        }
        // Økonomisk teori forklaring (eksempel)
        feedback += `<div class="widget" style="background:#eaf6ff"><b>Økonomisk indsigt:</b><br>
            <i>"Når du hæver tolden, stiger importpriserne. Det kan beskytte hjemlige sektorer, men forbrugerne betaler mere, og andre lande kan gengælde. Dette illustrerer teorien om handelsbarrierer og deres effekter på velfærd."</i>
        </div>`;
        feedbackDiv.innerHTML = feedback;
    }

    // Tilføj feedback-panel til HTML hvis det ikke findes
    if (!document.getElementById('turn-feedback')) {
        const feedbackDiv = document.createElement('div');
        feedbackDiv.id = 'turn-feedback';
        feedbackDiv.style.marginTop = '18px';
        feedbackDiv.style.maxWidth = '700px';
        feedbackDiv.style.marginLeft = 'auto';
        feedbackDiv.style.marginRight = 'auto';
        document.body.appendChild(feedbackDiv);
    }

    // Efter hver tur: hent feedback-data fra backend og vis det
    async function fetchAndShowTurnFeedback(isoCode) {
        if (!isoCode) return;
        
        try {
            const response = await fetch(`/api/turn_feedback/${isoCode}`);
            if (!response.ok) {
                console.error(`Kunne ikke hente feedback for ${isoCode}`);
                return;
            }
            
            const feedbackData = await response.json();
            showTurnFeedback(feedbackData);
            
        } catch (error) {
            console.error(`Error fetching feedback for ${isoCode}:`, error);
        }
    }

    // Tilføj interaktivt panel til politiske valg og handlinger
    function renderPolicyPanel() {
        let panel = document.getElementById('policy-panel');
        if (!panel) {
            panel = document.createElement('div');
            panel.id = 'policy-panel';
            panel.className = 'widget';
            panel.style.maxWidth = '700px';
            panel.style.margin = '18px auto';
            document.body.insertBefore(panel, document.getElementById('turn-feedback'));
        }
        panel.innerHTML = `
            <h4>Politiske valg</h4>
            <form id="policy-form">
                <label for="tariff-sector">Vælg sektor:</label>
                <select id="tariff-sector">
                    <option value="manufacturing">Industri</option>
                    <option value="services">Service</option>
                    <option value="agriculture">Landbrug</option>
                </select>
                <label for="tariff-rate">Toldsats (%):</label>
                <input type="number" id="tariff-rate" min="0" max="50" step="1" value="0">
                <br><label for="tax-rate">Skatteprocent (%):</label>
                <input type="number" id="tax-rate" min="0" max="60" step="1" value="20">
                <br><label for="gov-spending">Offentlige udgifter (% af BNP):</label>
                <input type="number" id="gov-spending" min="5" max="50" step="1" value="18">
                <br><label for="subsidy-sector">Sektor-subsidie:</label>
                <select id="subsidy-sector">
                    <option value="none">Ingen</option>
                    <option value="manufacturing">Industri</option>
                    <option value="services">Service</option>
                    <option value="agriculture">Landbrug</option>
                </select>
                <label for="subsidy-amount">Beløb (mio. USD):</label>
                <input type="number" id="subsidy-amount" min="0" max="100000" step="1000" value="0">
                <br><label for="interest-rate">Rente (%):</label>
                <input type="number" id="interest-rate" min="0" max="10" step="0.1" value="2.0">
                <br><button type="submit">Opdater politik</button>
            </form>
            <div id="policy-result" style="margin-top:10px;"></div>
        `;
        document.getElementById('policy-form').onsubmit = async function(e) {
            e.preventDefault();
            const sector = document.getElementById('tariff-sector').value;
            const rate = parseFloat(document.getElementById('tariff-rate').value) / 100;
            const tax = parseFloat(document.getElementById('tax-rate').value) / 100;
            const gov = parseFloat(document.getElementById('gov-spending').value) / 100;
            const subsidySector = document.getElementById('subsidy-sector').value;
            const subsidyAmount = parseFloat(document.getElementById('subsidy-amount').value);
            const interest = parseFloat(document.getElementById('interest-rate').value) / 100;
            const isoCode = countrySelect.value;
            // Send valg til backend
            const res = await fetch('/api/policy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    iso_code: isoCode,
                    policy: {
                        sector,
                        rate,
                        tax,
                        gov,
                        subsidySector,
                        subsidyAmount,
                        interest
                    }
                })
            });
            const resultDiv = document.getElementById('policy-result');
            if (res.ok) {
                const data = await res.json();
                resultDiv.textContent = 'Politik opdateret!';
                // Opdater landedata i UI
                if (data.country) {
                    renderCountryInfo(data.country);
                }
            } else {
                resultDiv.textContent = 'Fejl ved opdatering af politik.';
            }
        };
    }

    // --- BNP History Functions ---
    function updateBNPHistory(isoCode, gdp) {
        if (!bnpHistory[isoCode]) bnpHistory[isoCode] = [];
        bnpHistory[isoCode].push({ turn: bnpHistory[isoCode].length + 1, gdp });
        if (bnpHistory[isoCode].length > 40) bnpHistory[isoCode].shift(); // max 40 punkter
    }

    function renderBNPHistoryChart(isoCode) {
        const data = bnpHistory[isoCode] || [];
        const ctx = document.getElementById('bnpHistoryChart').getContext('2d');
        if (window.bnpChart) window.bnpChart.destroy();
        window.bnpChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.turn),
                datasets: [{
                    label: 'BNP (mio. USD)',
                    data: data.map(d => d.gdp),
                    borderColor: '#2d7ff9',
                    backgroundColor: 'rgba(45,127,249,0.1)',
                    fill: true,
                    tension: 0.2
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // --- Event Feed Functions ---
    function addEventToFeed(text) {
        eventFeed.unshift({ text, ts: new Date().toLocaleTimeString() });
        if (eventFeed.length > 10) eventFeed.pop();
        renderEventFeed();
    }

    function renderEventFeed() {
        const ul = document.getElementById('event-feed');
        if (!ul) return;
        ul.innerHTML = eventFeed.map(e => `<li><span style='color:#888'>[${e.ts}]</span> ${e.text}</li>`).join('');
    }

    // --- Sector Chart Interactivity ---
    function makeSectorChartInteractive() {
        if (!window.sectorChart) return;
        window.sectorChart.options.onClick = function(evt, elements) {
            if (elements.length > 0) {
                const idx = elements[0].index;
                const label = window.sectorChart.data.labels[idx];
                addEventToFeed('Du fremhævede sektoren: ' + label);
            }
        };
        window.sectorChart.options.plugins.tooltip = {
            callbacks: {
                label: function(context) {
                    return `${context.label}: ${context.parsed.y.toLocaleString()} mio. USD`;
                }
            }
        };
        window.sectorChart.update();
    }

    // --- Diplomati & Alliancer ---
    async function fetchDiplomacyData(isoCode) {
        try {
            const response = await fetch(`/api/diplomacy/${isoCode}`);
            if (!response.ok) throw new Error('Diplomati-data kunne ikke hentes');
            return await response.json();
        } catch (e) {
            console.error(e);
            return { relations: [], alliances: [] };
        }
    }

    async function renderDiplomacyPanel(isoCode) {
        const panel = document.getElementById('diplomacy-content');
        if (!panel) return;
        const data = await fetchDiplomacyData(isoCode);
        let html = '';
        html += '<b>Relationer:</b><ul>';
        if (data.relations.length === 0) {
            html += '<li>Ingen relationer registreret.</li>';
        } else {
            data.relations.forEach(rel => {
                html += `<li>${rel.country_a} ↔ ${rel.country_b}: <b>${rel.relation_level}</b> (sidste event: ${rel.last_event || 'N/A'})</li>`;
            });
        }
        html += '</ul>';
        html += '<b>Aktive alliancer:</b><ul>';
        if (data.alliances.length === 0) {
            html += '<li>Ingen alliancer.</li>';
        } else {
            data.alliances.forEach(al => {
                html += `<li><b>${al.name}</b> (${al.type}) – Medlemmer: ${al.members.join(', ')} (stiftet: ${al.date_formed})</li>`;
            });
        }
        html += '</ul>';
        panel.innerHTML = html;
    }

    // Håndter forslag til ny alliance
    document.getElementById('propose-alliance-btn').onclick = async function() {
        const name = document.getElementById('alliance-name').value.trim();
        const members = document.getElementById('alliance-members').value.split(',').map(s => s.trim().toUpperCase()).filter(Boolean);
        if (!name || members.length < 2) {
            alert('Angiv alliancenavn og mindst to medlemslande (ISO-koder, kommasepareret).');
            return;
        }
        const res = await fetch('/api/diplomacy/propose_alliance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, members })
        });
        if (res.ok) {
            alert('Alliance foreslået/indgået!');
            renderDiplomacyPanel(countrySelect.value);
        } else {
            alert('Fejl ved oprettelse af alliance.');
        }
    };

    // Håndter opløsning af alliance
    document.getElementById('disband-alliance-btn').onclick = async function() {
        const name = document.getElementById('disband-alliance-name').value.trim();
        if (!name) {
            alert('Angiv navnet på alliancen der skal opløses.');
            return;
        }
        const res = await fetch('/api/diplomacy/disband_alliance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (res.ok) {
            alert('Alliance opløst!');
            renderDiplomacyPanel(countrySelect.value);
        } else {
            alert('Fejl ved opløsning af alliance.');
        }
    };

    // Opdater diplomati-panel når land vælges
    if (countrySelect) {
        countrySelect.addEventListener('change', (e) => {
            renderDiplomacyPanel(e.target.value);
        });
    }
    // Initial visning
    if (countrySelect && countrySelect.value) {
        renderDiplomacyPanel(countrySelect.value);
    }

    // --- Event Handlers ---
    // Event handler for landvalg
    if (countrySelect) {
        countrySelect.addEventListener('change', (e) => {
            fetchCountryData(e.target.value);
            fetchAndShowTurnFeedback(e.target.value);
        });
    }

    // Event handler for næste tur
    if (nextTurnButton) {
        nextTurnButton.addEventListener('click', handleNextTurn);
    }
    
    // --- Initialization ---
    populateCountrySelect(); // Initial population of the dropdown
    initializeMap(); // Initialize the map
    renderPolicyPanel(); // Render policy panel

    // --- Tutorial System ---
    const tutorialSteps = [
        {
            title: "Velkommen til Trade War Simulator",
            text: "Denne tutorial vil guide dig gennem spillets grundlæggende funktioner og hvordan du kan anvende det internationale handelssystem til din fordel.",
            target: null, // No specific target for intro screen
            position: "center"
        },
        {
            title: "Vælg et land",
            text: "Start med at vælge et land fra dropdown-menuen. Hvert land har forskellige økonomiske egenskaber, handelspolitikker og ressourcer.",
            target: "#country-select",
            position: "bottom"
        },
        {
            title: "Udforsk landedata",
            text: "Her kan du se information om dit valgte land, inklusiv BNP, befolkning, arbejdsløshed og regeringsform. Disse data påvirker dine strategiske muligheder.",
            target: "#country-info",
            position: "right"
        },
        {
            title: "Verdenskortet",
            text: "Kortet viser alle lande i simulationen. Farveintensiteten indikerer BNP-størrelse. Klik på et land for at vælge det direkte fra kortet.",
            target: "#world-map",
            position: "left"
        },
        {
            title: "BNP Udvikling",
            text: "Dette diagram viser dit lands økonomiske udvikling over tid. Efter hver tur opdateres grafen med nye BNP-data.",
            target: "#bnp-history-panel",
            position: "top"
        },
        {
            title: "Næste Tur",
            text: "Klik på 'Next Turn' knappen for at simulere en tidsperiode. Dette vil opdatere økonomien, anvende dine politikker og generere events.",
            target: "#next-turn",
            position: "bottom"
        },
        {
            title: "Event Feed",
            text: "Her vil du se nyheder og begivenheder fra simulationen. Hold øje med denne feed for at reagere på ændringer i det globale handelsmiljø.",
            target: "#event-feed-panel",
            position: "top"
        },
        {
            title: "Tillykke!",
            text: "Du er nu klar til at spille Trade War Simulator. Brug din økonomiske viden til at træffe kloge beslutninger og opbygge en stærk økonomi!",
            target: null,
            position: "center"
        }
    ];

    // Initialize tutorial controls
    function initializeTutorial() {
        const toggleButton = document.getElementById('toggle-tutorial');
        const tutorialOverlay = document.getElementById('tutorial-overlay');
        const tutorialPrev = document.getElementById('tutorial-prev');
        const tutorialNext = document.getElementById('tutorial-next');
        const tutorialSkip = document.getElementById('tutorial-skip');
        
        // Toggle tutorial on/off
        toggleButton.addEventListener('click', () => {
            if (tutorialActive) {
                endTutorial();
            } else {
                startTutorial();
            }
        });
        
        // Navigation buttons
        tutorialPrev.addEventListener('click', showPreviousTutorialStep);
        tutorialNext.addEventListener('click', showNextTutorialStep);
        tutorialSkip.addEventListener('click', endTutorial);
    }
    
    // Start the tutorial
    function startTutorial() {
        tutorialActive = true;
        currentTutorialStep = 0;
        document.getElementById('toggle-tutorial').textContent = 'Exit Tutorial';
        document.getElementById('tutorial-overlay').classList.remove('hidden');
        showTutorialStep(currentTutorialStep);
    }
    
    // End the tutorial
    function endTutorial() {
        tutorialActive = false;
        document.getElementById('toggle-tutorial').textContent = 'Start Tutorial';
        document.getElementById('tutorial-overlay').classList.add('hidden');
        document.getElementById('tutorial-highlight').style.display = 'none';
    }
    
    // Show previous tutorial step
    function showPreviousTutorialStep() {
        if (currentTutorialStep > 0) {
            currentTutorialStep--;
            showTutorialStep(currentTutorialStep);
        }
    }
    
    // Show next tutorial step
    function showNextTutorialStep() {
        if (currentTutorialStep < tutorialSteps.length - 1) {
            currentTutorialStep++;
            showTutorialStep(currentTutorialStep);
        } else {
            endTutorial();
        }
    }
    
    // Show a specific tutorial step
    function showTutorialStep(stepIndex) {
        const step = tutorialSteps[stepIndex];
        
        // Update tutorial content
        document.getElementById('tutorial-title').textContent = step.title;
        document.getElementById('tutorial-text').textContent = step.text;
        document.getElementById('tutorial-step-indicator').textContent = `${stepIndex + 1} / ${tutorialSteps.length}`;
        
        // Enable/disable navigation buttons
        document.getElementById('tutorial-prev').disabled = stepIndex === 0;
        document.getElementById('tutorial-next').textContent = stepIndex === tutorialSteps.length - 1 ? 'Afslut' : 'Næste';
        
        // Position the tutorial container
        const tutorialContainer = document.getElementById('tutorial-container');
        const tutorialHighlight = document.getElementById('tutorial-highlight');
        
        // Reset position and highlighting
        tutorialContainer.style.top = '50%';
        tutorialContainer.style.left = '50%';
        tutorialContainer.style.transform = 'translate(-50%, -50%)';
        tutorialHighlight.style.display = 'none';
        
        // If there's a specific target, position relative to it
        if (step.target) {
            const targetElement = document.querySelector(step.target);
            if (targetElement) {
                const targetRect = targetElement.getBoundingClientRect();
                const containerWidth = 400; // Approximate width of tutorial container
                const containerHeight = 250; // Approximate height of tutorial container
                
                // Show and position the highlight
                tutorialHighlight.style.display = 'block';
                tutorialHighlight.style.top = `${targetRect.top - 5}px`;
                tutorialHighlight.style.left = `${targetRect.left - 5}px`;
                tutorialHighlight.style.width = `${targetRect.width + 10}px`;
                tutorialHighlight.style.height = `${targetRect.height + 10}px`;
                
                // Position the tutorial container based on position setting
                switch(step.position) {
                    case 'top':
                        tutorialContainer.style.top = `${targetRect.top - containerHeight - 20}px`;
                        tutorialContainer.style.left = `${targetRect.left + targetRect.width/2}px`;
                        tutorialContainer.style.transform = 'translateX(-50%)';
                        break;
                    case 'bottom':
                        tutorialContainer.style.top = `${targetRect.bottom + 20}px`;
                        tutorialContainer.style.left = `${targetRect.left + targetRect.width/2}px`;
                        tutorialContainer.style.transform = 'translateX(-50%)';
                        break;
                    case 'left':
                        tutorialContainer.style.top = `${targetRect.top + targetRect.height/2}px`;
                        tutorialContainer.style.left = `${targetRect.left - containerWidth - 20}px`;
                        tutorialContainer.style.transform = 'translateY(-50%)';
                        break;
                    case 'right':
                        tutorialContainer.style.top = `${targetRect.top + targetRect.height/2}px`;
                        tutorialContainer.style.left = `${targetRect.right + 20}px`;
                        tutorialContainer.style.transform = 'translateY(-50%)';
                        break;
                    default: // center or fallback
                        // Already set to center by default
                        break;
                }
                
                // Ensure the tutorial container stays within the viewport
                const containerRect = tutorialContainer.getBoundingClientRect();
                if (containerRect.top < 20) tutorialContainer.style.top = '20px';
                if (containerRect.bottom > window.innerHeight - 20) 
                    tutorialContainer.style.top = `${window.innerHeight - containerHeight - 20}px`;
                if (containerRect.left < 20) tutorialContainer.style.left = '20px';
                if (containerRect.right > window.innerWidth - 20)
                    tutorialContainer.style.left = `${window.innerWidth - containerWidth - 20}px`;
            }
        }
    }

    // Initialize tutorial when DOM is loaded
    initializeTutorial();
});
