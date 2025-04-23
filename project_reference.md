# Projekt Reference Dokument

## STATUSOPDATERING (23. april 2025)

### Seneste fremskridt
- Frontend og backend integration er komplet og fungerer gnidningsfrit med turbaseret simulation
- Alle nødvendige API-endpoints er implementeret med fuld dokumentation (`backend/routes/`)
- Feedback-systemet efter hver tur er nu implementeret og giver pædagogisk vejledning til spilleren
- Interaktivt kortmodul visualiserer landedata og økonomiske indikatorer i realtid (`frontend/src/components/MapPanel.jsx`)
- Policy-panel i UI er fuldt integreret med backend og viser øjeblikkelige effekter af politiske beslutninger (`frontend/src/components/PolicyPanel.jsx`)
- AI-modstandere handler strategisk baseret på økonomiske indikatorer og spillerens handlinger (`backend/diplomacy_ai.py`)
- Den neoklassiske økonomiske model med sektorspecifik simulation er fuldt implementeret (`backend/engine.py`, `backend/models.py`)
- Datavisualisering med grafer og diagrammer for GDP, sektordata og økonomiske trends er implementeret
- Omfattende test suite validerer økonomiske modeller og invarianter (`backend/test_*.py`)
- Omfattende diplomatisystem med relationsvisualisering, handelsdependensanalyse og sanktionssimulation er nu implementeret (`backend/diplomacy_ai.py`, `frontend/src/components/DiplomacyPanel.jsx`)
- Event-feed visualisering af simulationsbegivenheder tilføjet til brugergrænsefladen (`frontend/src/components/EventFeedPanel.jsx`)
- BNP-historik og analysepanelet er færdigudviklet med interaktive grafer (`frontend/src/components/BNPHistoryPanel.jsx`)
- AI-system udvidet med detaljerede `CountryProfile` klasser, der inkluderer mange træk (økonomisk, diplomatisk, lederskab, teknologi) og kan genereres dynamisk baseret på landets data og justeres under kriser (`backend/diplomacy_ai.py`)
- DiplomacyPanel er udbygget med risiko- og sanktionsanalyseværktøjer (`frontend/src/components/DiplomacyPanel.jsx`)
- Robust event-system implementeret med strukturerede `EventType` og `EventOption` klasser, kategorier, effekt-processorer og flere komplekse, detaljerede events med specifikke triggere, muligheder og narrative følger (`backend/event_types.py`)
- ScenarioSelector-komponenten er betydeligt forbedret med avancerede UI/UX elementer, herunder animerede filter-tags, visuel feedback ved filterændringer, tilpasset scrollbardesign, gradient-effekter for visualisering af filterdistribution, forbedret præsentation af forudindstillede filtre, bedre tilgængelighed med fokustilstande, tooltips og tomtilstandsdesign når ingen filtre er anvendt (`frontend/src/styles/ScenarioSelector.css`)
- Komplet tutorial-system implementeret med kategoribaseret læring og interaktive elementer (`frontend/src/components/TutorialPanel.jsx`, `frontend/src/styles/TutorialPanel.css`):
  - Grundlæggende introduktion til spilmekanikker
  - Kategoribaseret system med detaljerede tutorials indenfor økonomi, diplomati, begivenheder og avancerede strategier
  - Interaktivt navigationssystem med fremskridt-sporing
  - Responsive design med mobile tilpasninger
  - Visuelle illustrationer med billeder der understøtter læring
  - Elegant UI med animerede overgange og visuelle effekter
  - Kontekstspecifikke forklaringer af spilmekanikker
  - Mulighed for at vende tilbage til specifikke tutorial-sektioner efter behov
- Implementeret avancerede scenarier og udvidet event-systemet med flere event-typer baseret på virkelige økonomiske situationer (`backend/event_types.py`):
  - Omfattende kategorisering af events (økonomiske, politiske, miljømæssige, teknologiske, diplomatiske, sociale, sikkerhedsmæssige og handelsrelaterede)
  - Detaljerede effekt-processorer til håndtering af forskellige påvirkninger (BNP-ændringer, godkendelsesændringer, relationsændringer, handelsvolumenændringer, osv.)
  - Avancerede trigger-mekanismer for events baseret på landespecifikke attributter, globale betingelser, relationer og koalitioner
  - Narrative følgeoplevelser der skaber sammenhængende storylines gennem spillets forløb
  - AI-præference-beregning der sikrer realistiske reaktioner fra AI-lande i krisesituationer
  - Implementering af naturkatastrofer, politiske kriser og teknologiske gennembrud som påvirker spillet på realistiske måder
- AI-strategi udvidet med flere handlingstyper, herunder:
  - Integration af budget og subsidiestyring i GameEngine klassen med detaljerede økonomiske effekter (`engine.py`)
  - Forbedret strategisk koalitionsdannelse og -anvendelse med avancerede evaluerings- og beslutningsalgoritmer (`backend/diplomacy_ai.py`)
  - Omfattende tests til validering af koalitionsfunktionalitet med simulerede lande og diplomatiske relationer (`backend/test_coalition.py`)
  - Implementering af BudgetPolicy klassen, der kan evaluere fiskal situation og beregne subsidieallokeringer baseret på landets økonomiske profil
  - Implementering af CoalitionStrategy klassen med dynamisk identifikation af handelspartnere, defensivpartnere og regionale partnere
  - Sofistikeret evaluering af potentielle og eksisterende koalitioner med cost-benefit analyse
- Udviklet avanceret `HistoricalDataset` klasse til indlæsning og benchmarking af økonomiske data (`backend/engine.py`)
- Implementeret `EconomicCalibrator` til kalibrering af økonomiske parametre baseret på historiske data (`backend/engine.py`)
- Udvidet feedback-systemet med detaljerede økonomiske narrativer og forklaringer via `EnhancedFeedbackSystem` (`backend/engine.py`)
- Omfattende implementering af `CountryAnalysisPanel` med avancerede visuelle komponenter til sammenligning af økonomiske metrics, historiske benchmarks og partner/konkurrent analyse (`frontend/src/components/CountryAnalysisPanel.jsx`, `frontend/src/styles/CountryAnalysisPanel.css`)
- Implementeret `BudgetManager` klasse til avanceret budget- og subsidiestyring med detaljeret økonomisk effektberegning (`backend/engine.py`)
- Udbygget `EnhancedFeedbackSystem` med dynamiske, kontekstuelle narrativer til at forklare økonomiske indikatorer og trends (`backend/engine.py`)
- Udbygget AI forklaringsevne med `AIExplanationSystem` til at generere detaljerede og forståelige forklaringer af AI-beslutninger (`backend/diplomacy_ai.py`)
- Implementeret automatisk generering af turnerings-sammendrag med `_generate_turn_summary` metode i GameEngine (`backend/engine.py`)
- Tilføjet avancerede benchmark funktioner til sammenligning af landets økonomiske performance med regionale og globale gennemsnit (`backend/engine.py`)
- Udvidet `CountryProfile` klassen med flere personlighedstræk for mere realistisk og nuanceret AI-beslutningstagning (`backend/diplomacy_ai.py`)
- Tilføjet detaljeret budget-allokerings-effekt-system med sektor-specifik påvirkning og narrativ forklaring (`backend/engine.py`)

### Næste trin
- Færdiggøre CountryAnalysisPanel med fuld integration af historiske data fra backend (Delvist implementeret: Panel struktur og mock data implementeret, men mangler komplet integration med backend data)
- Færdiggøre budget- og subsidiestyring med komplet integration i frontend (Delvist implementeret: Backend struktur er udviklet i BudgetManager klassen, men mangler fuld frontend integration)
- Udvide koalitionsstrategier med mere avanceret beslutningslogik og diplomatiske konsekvenser (Delvist implementeret: Grundlæggende koalitionslogik findes, men mangler avanceret beslutningslogik)
- Kalibrere økonomiske parametre baseret på historiske data ved hjælp af EconomicCalibrator (Implementeret: EconomicCalibrator klasse og metoder er udviklet i engine.py)
- Tilføje flere interaktive elementer i frontend, herunder yderligere avancerede filtreringsmuligheder (Delvist implementeret: Basis interaktive elementer findes, men avanceret filtrering mangler)
- Udvide tutorial-systemet med flere praktiske eksempler og interaktive øvelser (Status ukendt: Basisstruktur er formentlig implementeret i TutorialPanel)
- Udbygge feedback-systemet med mere detaljerede økonomiske forklaringer og konsekvensanalyser (Implementeret: EnhancedFeedbackSystem er udviklet med omfattende forklaringsfunktionalitet)
- Tilføje flere sektorspecifikke detaljer og visualiseringer i brugergrænsefladen (Delvist implementeret: Basis sektorvisualisering findes, men mangler dybere detaljer)
- Optimere simulationsydelse ved komplekse økonomiske scenarier (Status ukendt: Kræver yderligere undersøgelse af algoritmeoptimering)
- Implementere flere avancerede scenarier med unikke starttilstande og begivenheder (Status ukendt: Event management system findes, men omfang af implementerede scenarier er uklart)
- Tilføje dybere forklaringer til AI-beslutningsprocesser for at øge gennemsigtighed for spilleren (Delvist implementeret: AIExplanationSystem klassen er udviklet til at generere forklaringer af AI-beslutninger, men kan udbygges yderligere)
- Udvide benchmarking-funktionaliteten til at inkludere flere historiske sammenligninger og dynamiske visualiseringer (Delvist implementeret: Grundlæggende benchmarking findes i HistoricalDataset og EnhancedFeedbackSystem)
- Udbygge budget-visualiseringer i frontend til at vise detaljerede effekter af forskellige budget-allokeringer (Ikke implementeret: Backend logik er klar, men frontend visualisering mangler)

---

## Status for Diplomati, Alliancer, Events/Scenarier og Avanceret AI-strategi (opdateret 23. april 2025)

**Fremskridt siden sidste opdatering:**
- Implementeret omfattende diplomatisystem med relationsparametre, handelsdependensanalyse og sanktionssimulation (`backend/diplomacy_ai.py`)
- Udviklet udbyggede UI-komponenter i DiplomacyPanel.jsx med risiko- og sanktionsanalyseværktøjer (`frontend/src/components/DiplomacyPanel.jsx`)
- AI-system udvidet med meget detaljerede `CountryProfile` klasser, der dækker mange adfærds- og præferencetræk langt ud over simple arketyper (`backend/diplomacy_ai.py`)
- Implementeret robust og struktureret event-system med flere komplekse events, der har specifikke triggere, valgmuligheder, effekter og narrative følger (`backend/event_types.py`)
- Forbedret AI-beslutningslogik med bedre reaktioner på spillerens handlinger (`backend/diplomacy_ai.py`)
- Grundlæggende koalitionslogik implementeret og testet (`backend/test_coalition.py`)
- Udviklet `AIExplanationSystem` til at generere forståelige forklaringer af AI-beslutninger for spilleren
- Implementeret avanceret `BudgetManager` til håndtering af budget-allokering og subsidier med realistiske effekter
- Udvidet `CountryProfile` klassen med flere personlighedsparametre for mere nuanceret AI-beslutningstagning

**Mangler for fuldt udbygget funktionalitet:**

1. **Diplomati og alliancer:**
   - Implementering af *dynamiske forhandlingsmekanismer*, hvor lande kan indgå, forhandle og bryde alliancer (nuværende system er mere statisk)
   - Udvidelse af flere diplomatiske handlingsmuligheder (frihandelsaftaler, investeringsaftaler)
   - Videreudvikling af AI-logik for at vurdere og prioritere alliancer og diplomatiske handlinger mere dynamisk og strategisk
   - Udvikling af en mere avanceret relationsmodel der inkorporerer historiske begivenheder og kulturelle faktorer

2. **Events og scenarier:**
   - Tilføje flere event-typer (naturkatastrofer, politiske kriser, teknologiske gennembrud) til det eksisterende robuste system (`backend/event_types.py`)
   - Integrere events dybere med diplomatisystemet for at skabe komplekse scenarier
   - Udvikle scenario-vælger ved spilstart med historiske og fiktive situationer
   - Skabe bedre sammenhæng mellem events gennem spillets forløb med narrative sekvenser

3. **Avanceret AI-strategi:**
   - Implementere flere AI-handlingstyper: færdiggøre frontend integration af subsidier og budgetstyring (backend allerede udviklet i BudgetManager)
   - Udbygge AIExplanationSystem med mere detaljeret forklarende feedback til spilleren om AI'ens valg og motiver
   - Udbygge AI's evne til at danne og *anvende* koalitioner strategisk mod dominerende spillere (nuværende logik er basal)
   - Forbedre AI's langtidsplanlægning og strategiske tænkning på tværs af flere spillerrunder

**Næste skridt:**
- Færdiggøre diplomati-systemet med *dynamiske* alliance-mekanismer og flere interaktionsmuligheder
- Udvide event-systemet med mindst 20 nye event-typer fordelt på økonomiske, politiske og miljømæssige kategorier
- Integrere alle systemer bedre med frontend visualiseringer og brugerinteraktioner
- Implementere *strategisk* koalitionsdannelse og -anvendelse mellem AI-lande
- Færdiggøre frontend integration af BudgetManager for komplet budget- og subsidiestyring i UI
- Udbygge AIExplanationSystem med flere detaljerede og kontekstspecifikke forklaringer af AI-beslutninger

---

## AI-arkitektur og status (opdateret 23. april 2025)

### Valgt AI-strategi
- Hybrid-tilgang: Utility AI til beslutningsvalg (vægtning af økonomiske/politiske/diplomatiske faktorer) kombineret med Finite State Machines (FSM) eller Behavior Trees (BT) til overordnet strategistyring og sekventering af handlinger.
- AI-profiler/personligheder: Hver nation får en detaljeret `CountryProfile` med mange træk (økonomisk, diplomatisk, lederskab, tech etc.), genereret baseret på landets data og styreform, som påvirker AI'ens vægtning og adfærd (`backend/diplomacy_ai.py`).
- Forklarbarhed: AI'ens motiver og valg skal kunne forklares for spilleren (ingen sort boks).
- Ingen tung ML i realtid – evt. kun offline til tuning af parametre.

### Implementeret
- Grundlæggende FSM-struktur for AI-landes strategitilstand (fx neutral, aggressiv, samarbejdende) (`backend/diplomacy_ai.py`).
- Utility-baseret beslutningslogik for toldsatser og sektorbeskyttelse (vægtning af BNP, arbejdsløshed, sektoroutput, politisk stabilitet mv.) (`backend/diplomacy_ai.py`).
- AI-profiler: Detaljerede `CountryProfile` klasser implementeret, som dynamisk påvirker AI'ens valg (`backend/diplomacy_ai.py`).
- Simpel feedback-loop: AI's handlinger påvirker økonomimodellen, og modeloutput bruges i næste AI-evaluering (`backend/engine.py`, `backend/diplomacy_ai.py`).
- Grundlæggende koalitionslogik (`backend/test_coalition.py`).
- Backend integration for AI budget/subsidy handlinger i `engine.py` via BudgetManager klassen.
- Implementeret AIExplanationSystem til at generere detaljerede og forståelige forklaringer af AI-beslutninger.
- Ingen ML eller evolverende strategier i runtime.

### Næste trin
- Udbygge utility-funktioner med flere handlinger (færdiggøre diplomati, subsidier, budget).
- Videreudvikle AIExplanationSystem med mere omfattende forklarende feedback til spilleren om AI'ens valg og motiver.
- Udvide FSM/BT med flere tilstande og transitions.
- Udbygge koalitionslogik til strategisk dannelse og anvendelse.
- Mulighed for at vælge AI-sværhedsgrad og personlighed i UI.
- Integrere BudgetManager komplet med frontend for at give spilleren indblik i AI'ens budget- og subsidiestrategier.

### Kommentar
AI'en følger nu best practise for strategispil: Utility AI + FSM/BT, detaljerede personlighedsparametre, forklarbarhed og ingen black-box. Udviklingen følger anbefalingerne fra AI-analysen og rapporten. Klar til at udbygge med flere handlinger, feedback, forbedret koalitionslogik og sværhedsgrader. Backend integration af budget- og subsidiestyring er nu implementeret via BudgetManager klassen, men mangler fuld frontend integration.

---

## Status (opdateret 23. april 2025)

### Implementerede trin
- [x] Udvidet data- og modelstruktur til at understøtte sektorer i både Python-klasser og countries.json (`backend/models.py`, `data/countries.json`).
- [x] Grundlæggende sektorspecifik simulation: Sektorer opdateres for output, pris, import/eksport, nettoeksport og ledighed pr. tur (`backend/engine.py`).
- [x] Aggregering af BNP og arbejdsløshed fra sektorer til land (`backend/engine.py`).
- [x] Implementeret pris- og handelsdynamik pr. sektor inkl. tariffer og priselasticitet (`backend/engine.py`).
- [x] Makroøkonomiske feedbacks: valutakurs, investering, kapacitetsudbygning og finanspolitik opdateres pr. tur (`backend/engine.py`).
- [x] AI-logik: tit-for-tat-tariffer, sektorbeskyttelse og justering af skat/rente ved høj gæld (`backend/diplomacy_ai.py`).
- [x] Frontend: Dynamisk visning af lande- og sektordata, KPI'er, sektorgrafer og pædagogisk feedback til spilleren efter hver tur (`frontend/src/`).
- [x] countries.json er nu gyldig JSON uden kommentarer (`data/countries.json`).
- [x] Diplomati system med relationer, sanktioner og detaljerede AI-profiler (`backend/diplomacy_ai.py`, `frontend/src/components/DiplomacyPanel.jsx`).
- [x] Robust event system implementeret med flere komplekse events og visualiseret (`backend/event_types.py`, `frontend/src/components/EventFeedPanel.jsx`).
- [x] BNP historik panel implementeret (`frontend/src/components/BNPHistoryPanel.jsx`).
- [x] Udviklet avanceret HistoricalDataset klasse til benchmarking af økonomiske data (`backend/engine.py`).
- [x] Implementeret EconomicCalibrator til kalibrering af økonomiske parametre (`backend/engine.py`).
- [x] Udvidet feedback-systemet med EnhancedFeedbackSystem for detaljerede økonomiske forklaringer (`backend/engine.py`).
- [x] Implementeret BudgetManager for detaljeret budget- og subsidiehåndtering (`backend/engine.py`).
- [x] Udviklet AIExplanationSystem til at generere forklaringer af AI-beslutninger (`backend/diplomacy_ai.py`).

### Næste trin
- Udbygge AI-strategier (færdiggøre frontend integration af budget/subsidier, strategiske koalitioner) og politiske beslutninger.
- Tilføje flere event-typer og scenario-vælger.
- Flere interaktive frontend-elementer (avanceret filtrering).
- Udfylde tutorial (`frontend/src/components/TutorialPanel.jsx`) og færdiggøre lande-analyse (`frontend/src/components/CountryAnalysisPanel.jsx`).
- Udvide test og dokumentation.
- Kalibrere økonomiske parametre ved hjælp af den implementerede EconomicCalibrator.
- Integrere BudgetManager fuldt ud med frontend for komplet budget- og subsidiestyring i UI.
- Udvide benchmarking-funktionaliteten med flere visualiseringer og sammenligninger.

### Kommentar
Projektet har nu en fuldt funktionel turbaseret kerne, AI-modstandere med detaljerede profiler, makroøkonomiske feedbacks, et robust diplomati- og event-system, samt pædagogisk feedback til spilleren. Avanceret budget- og subsidiestyring er implementeret i backend via BudgetManager, og historiske dataevalueringer via HistoricalDataset og EconomicCalibrator. AI-beslutninger kan nu forklares ved hjælp af AIExplanationSystem. Klar til videreudvikling, indholdsudfyldning og finpudsning, med særligt fokus på at færdiggøre frontend-integrationen af budget- og subsidiesystemet.

---

## Implementeringsplan og tjekpoints (Opdateret 23. april 2025)

1.  **Basisstruktur og data**
    - [x] Udvid countries.json med flere lande og sektordata (`data/countries.json`)
    - [x] Definér sektorer og deres parametre (output, beskæftigelse, importandel, mv.) (`backend/models.py`)
    - [x] Opret grundlæggende Python-klasser for land, sektor og økonomisk model (`backend/models.py`)

2.  **Handels- og prisdynamik**
    - [x] Implementér tarif- og prisformler (P_import, P_domestic) (`backend/engine.py`)
    - [x] Implementér dynamisk kobling mellem økonomier (P_f som vægtet gennemsnit) (`backend/engine.py`)
    - [x] Implementér sektoropdelt import/eksport og elasticiteter (`backend/engine.py`)

3.  **Valutakurs og kapitalbevægelser**
    - [x] Implementér valutakursmekanisme (delta_fx) (`backend/engine.py`)
    - [ ] Kalibrér k1 og k2 (Næste trin)

4.  **Makroøkonomiske feedbacks**
    - [x] Implementér Okuns lov (arbejdsløshed) (`backend/engine.py`)
    - [x] Implementér Phillips-kurve med importpriser (inflation) (`backend/engine.py`)
    - [ ] Implementér forventningsdannelse (π^e) (Fremtidig udvidelse)

5.  **Sektorspecifik logik**
    - [x] Implementér sektorspecifikke tariffer og prisdannelse (`backend/engine.py`)
    - [x] Implementér sektoropdelt output, beskæftigelse og investering (`backend/engine.py`)
    - [x] Implementér aggregering til BNP og samlet arbejdsløshed (`backend/engine.py`)

6.  **Investering og kapacitetsudbygning**
    - [x] Implementér investeringsfunktion og fordeling på sektorer (`backend/engine.py`)
    - [x] Opdater sektorspecifik kapitalstock og kapacitet (`backend/engine.py`)

7.  **Finanspolitik og offentlig gæld**
    - [x] Implementér skatteprovenu, offentlige udgifter og gældsopbygning (`backend/engine.py`)
    - [x] Implementér detaljeret budget- og subsidiestyring med BudgetManager (`backend/engine.py`)
    - [ ] Implementér forbrugsfunktion (MPC, wealth, confidence) (Fremtidig udvidelse)

8.  **Politisk tillid og feedback**
    - [x] Implementér trust-mekanisme og kobling til økonomiske nøgletal (`backend/models.py`, `backend/engine.py`)
    - [x] Implementér effekter af politiske beslutninger på trust (`backend/engine.py`)
    - [x] Udvikle EnhancedFeedbackSystem til detaljerede økonomiske forklaringer (`backend/engine.py`)

9.  **AI og international respons**
    - [x] Implementér AI-logik for tit-for-tat, sektorbeskyttelse (`backend/diplomacy_ai.py`)
    - [x] Implementér AI's interne trust og politiske mål (`backend/diplomacy_ai.py`)
    - [x] Implementér grundlæggende AI-alliancelogik/koalitioner (`backend/test_coalition.py`, `backend/diplomacy_ai.py`)
    - [x] Udvikle AIExplanationSystem til at generere forklaringer af AI-beslutninger (`backend/diplomacy_ai.py`)
    - [ ] Udbyg AI-strategier (frontend integration af budget/subsidier, avanceret koalition) (Næste trin)

10. **Test, validering og dokumentation**
    - [x] Skriv enhedstests for centrale funktioner (`backend/test_*.py`)
    - [ ] Dokumentér alle økonomiske antagelser og formler i kode og docs (Løbende)
    - [ ] Løbende validering mod kendte økonomiske cases (Næste trin/Løbende)
    - [x] Implementér historisk data benchmarking med HistoricalDataset (`backend/engine.py`)
    - [x] Udvikle EconomicCalibrator til kalibrering af økonomiske parametre (`backend/engine.py`)

---

**Bemærk:**
- Hvert tjekpunkt bør markeres som færdigt i referencedokumentet, så fremdrift kan følges.
- Se detaljeret beskrivelse og eksempler i denne sektion for formelgrundlag og kodeeksempler.

---

## UI Design Forslag

### Overordnede UI/UX-principper (opdateret 21. april 2025)

#### Dashboard Layout & Struktur
- Brug et modulært, grid-baseret dashboard med venstre navigation, topbar og et indholdsområde med widgets (kort, KPI'er, tabeller).
- Hver widget vises i et card-lignende panel og kan flyttes, skjules eller omarrangeres af brugeren.
- Layoutet skal være responsivt til forskellige desktop-opløsninger (1080p til 4K) og kunne tilpasse sig vinduesstørrelse.
- Navigationen til venstre giver hurtig adgang til sektioner som Økonomi, Handelspolitik, Analyse og Indstillinger.

#### Visuel Stil & Tema
- Moderne, let gamificeret stil inspireret af Football Manager og Game Dev Tycoon: rene linjer, flade ikoner, subtile animationer og en sammenhængende farvepalet.
- Brug tematiske elementer (fx svage verdenskort i baggrunden) for at understøtte simulation-stemningen uden at forstyrre data.
- Indfør små gamification-elementer (progress bars, badges, avatar) for engagement, men hold fokus på data.

#### Typografi, Ikoner & Farver
- Sans-serif font med tydelig typografi-hierarki (store overskrifter, mellemstore widget-titler, små detaljer).
- Brug monospaced/tabular font til tal og tabeller for nem sammenligning.
- Ikoner skal være enkle, flade og matche temaet (fx fabrik, skib, flag, op/ned-pile).
- Farvepalet: Neutral baggrund, accentfarver til vigtige data (grøn for positivt, rød for negativt), altid kombineret med tekst/ikon.

#### Web-Only Interaktion & Responsivitet
- Optimer til mus og tastatur, desktop-opløsninger og drag-and-drop for widgets.
- Brug hover for tooltips og detaljer, højreklik til avancerede muligheder, og sørg for tastaturtilgængelighed.
- Layout og tekst skal skalere ved browser-zoom og forskellige vinduesstørrelser.

#### Datavisualisering & Interaktive Widgets
- Brug klare, interaktive diagrammer (linje, søjle, cirkel) med labels, enkle animationer og mulighed for at filtrere eller dykke ned i data.
- Anvend Chart.js, Recharts eller D3.js afhængigt af behov for tilpasning.
- Alle grafer skal have tydelige akser, enheder og titler.

#### Informationsdensitet: Tooltips, Overlays & Lag
- Brug progressiv afsløring: vis kun det vigtigste først, og lad brugeren udforske detaljer via tooltips, slide-out paneler eller overlays.
- Undgå for mange modale vinduer – brug flyouts og overlays til detaljer.

#### Notifikationssystem
- Implementer tre niveauer: inline-feed (lav), toast-popups (mellem), modal (kritisk).
- Notifikationscenter med log, farvekoder og evt. lyd (kan slås fra).

#### Tilgængelighed
- Sørg for kontrast, tekstskala, tastaturnavigation, ARIA-roller og reduceret bevægelse.
- Alle interaktive elementer skal være tilgængelige for skærmlæsere og tastatur.

#### Skalerbare & Genanvendelige UI-komponenter
- Byg UI som selvstændige, genanvendelige komponenter (React anbefales).
- Dokumentér komponenter i et design system og planlæg for tilpasning og performance.

#### Onboarding & Brugerhjælp
- Interaktiv tutorial med guided walkthrough, kontekstuelle hints og missionsbaseret læring.
- In-game manual/glossar og mulighed for at springe/skifte tutorial.

### UI Mockup Koncepter

#### **Koncept 1: Analystens Hub (Data-Drevet)**
- **Kerneidé**: Minimalistisk og professionelt design inspireret af moderne finansielle dashboards.
- **Visuel Beskrivelse**: Rene linjer, sans-serif typografi, og farver brugt funktionelt til at fremhæve data.
- **Elementer**:
  - Hovedområde: Konfigurerbare widgets til grafer og KPI'er.
  - Topbar: Viser essentielle ressourcer som budget og politisk kapital.
  - Sidepanel: Navigationsmenu til dybere sektioner som "Handel" og "Indenrigspolitik".
  - Notifikationer: Subtile ikoner med dedikeret log.
- **Styrker**: Effektiv dataadgang og analysefokus.
- **Udfordringer**: Kan føles steril og mindre immersiv.

#### **Koncept 2: Globalt Kommandocenter (Kort-Centreret)**
- **Kerneidé**: Klassisk strategi-layout med interaktivt verdenskort som centrum.
- **Visuel Beskrivelse**: Kort med forskellige tilstande (økonomisk, politisk, handelsruter) omgivet af paneler.
- **Elementer**:
  - Kort: Interaktivt med klikbare lande og dataoverlays.
  - Topbar: Viser nationale indikatorer som BNP, inflation og politisk stabilitet.
  - Sidepaneler: Kontekstafhængige paneler til detaljerede data og handlinger.
  - Notifikationer: Pop-ups og konsolideret log.
- **Styrker**: Velkendt layout og stærk rumlig kontekst.
- **Udfordringer**: Risiko for informationsoverbelastning.

#### **Koncept 3: Skyggernes Krigsrum (Stiliseret, Tematisk)**
- **Kerneidé**: Atmosfærisk og immersivt design med fokus på tema og stemning.
- **Visuel Beskrivelse**: Mørk farvepalet med høj kontrast og stiliserede elementer som holografiske kort.
- **Elementer**:
  - Center: Stiliseret global visning med strategiske elementer.
  - Paneler: Designet som kontrolkonsoller med ikoner og målere.
  - Notifikationer: Tematiske alarmer og beskeder.
- **Styrker**: Unik atmosfære og stærk tematisk fordybelse.
- **Udfordringer**: Risiko for at ofre klarhed for stil.

### Næste Skridt
1. Prototyping: Lav interaktive prototyper for de valgte koncepter.
2. Brugertest: Test med målgruppen for at identificere styrker og svagheder.
3. Iteration: Forbedr designet baseret på feedback.

### Anbefalinger
- Følg ovenstående UI/UX-principper for at sikre en brugervenlig, engagerende og skalerbar brugergrænseflade.
- Brug værktøjer som tooltips, lagdeling og progressive afsløringer for at håndtere informationsdensitet.
- Implementer et effektivt notifikationssystem, der balancerer relevans og ikke-forstyrrende præsentation.
- Prioriter klarhed og konsistens i typografi, ikoner og farvebrug.
- Sørg for, at UI'en understøtter både nybegyndere og erfarne spillere gennem onboarding og tilpasningsmuligheder.

## Opgaver
- [ ] Oprette en økonomisk model for handelssimulator.
- [ ] Implementere backend-funktionalitet.
- [ ] Tilføje data fra `countries.json`.
- [ ] Teste og validere modellen.
- [ ] Dokumentere projektet.

## Instruktioner til AI-assistenten
- Følg altid bedste praksis for kodning.
- Brug eksisterende data og filer i projektet, hvor det er muligt.
- Sørg for, at ændringer ikke bryder eksisterende funktionalitet.
- Valider altid ændringer for fejl.

## Noter
- Husk at opdatere denne fil løbende med nye opgaver og status.
- Eventuelle spørgsmål eller uklarheder kan tilføjes her.