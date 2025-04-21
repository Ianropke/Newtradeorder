document.addEventListener('DOMContentLoaded', () => {
    const countrySelect = document.getElementById('country-select');
    const nextTurnButton = document.getElementById('next-turn');
    const countryInfoDiv = document.getElementById('country-info');
    const mapContainer = document.getElementById('map-container');

    let allCountriesData = {}; // Store all country data fetched initially
    let bnpHistory = {}; // BNP-historik for valgte land
    let eventFeed = []; // Event feed

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
        const response = await fetch('/api/v1/countries');
        if (!response.ok) return;
        const countries = await response.json();
        select.innerHTML = '';
        countries.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.iso_code;
            opt.textContent = c.name;
            select.appendChild(opt);
        });
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
        const success = await advanceTurn();
        if (success) {
            addEventToFeed('Ny tur gennemført. Økonomien er opdateret.');
            // Refresh the displayed country info after the turn advances
            await displayCountryInfo(); 
            // TODO: Update map visualization if needed
        }
    }

    function initializeMap() {
        // TODO: Implement map visualization using a library like Leaflet or D3.js
        mapContainer.innerHTML = '<p>World Map Placeholder (Library Needed)</p>';
    }

    // Funktion til at hente og vise lande- og sektordata fra backend
    async function fetchCountryData(isoCode) {
        const response = await fetch(`/api/v1/countries/${isoCode}`);
        if (!response.ok) return;
        const data = await response.json();
        renderCountryInfo(data);
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
        const response = await fetch(`/api/v1/turn_feedback/${isoCode}`);
        if (!response.ok) return;
        const feedbackData = await response.json();
        showTurnFeedback(feedbackData);
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

    // Event handler for landvalg
    if (countrySelect) {
        countrySelect.addEventListener('change', (e) => {
            fetchCountryData(e.target.value);
        });
    }

    // Event handler for næste tur
    const nextTurnBtn = document.getElementById('next-turn');
    if (nextTurnBtn) {
        nextTurnBtn.addEventListener('click', async () => {
            await fetch('/api/v1/next_turn', { method: 'POST' });
            if (countrySelect) {
                fetchCountryData(countrySelect.value);
                fetchAndShowTurnFeedback(countrySelect.value);
            }
        });
    }

    // Initial load
    if (countrySelect) fetchCountryData(countrySelect.value);

    // Initial feedback visning
    if (countrySelect) fetchAndShowTurnFeedback(countrySelect.value);

    // --- Initialization ---
    populateCountrySelect(); // Initial population of the dropdown
    initializeMap();
    nextTurnButton.addEventListener('click', handleNextTurn);
    renderPolicyPanel(); // Render policy panel

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
});
