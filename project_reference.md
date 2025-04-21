# Projekt Reference Dokument

## STATUSOPDATERING (21. april 2025)

### Seneste fremskridt
- Backend og frontend er nu fuldt integreret: Politisk panel i UI sender POST til /api/policy, og økonomiske nøgletal opdateres straks i brugerfladen.
- Den neoklassiske model er implementeret i backend med sektorspecifik simulation, makroøkonomiske feedbacks, AI-modstandere og pædagogisk feedback til spilleren.
- AI-strategi, agentstruktur og feedback-loop er beskrevet og implementeret.
- Flask-backend har nu endpoint for policy-ændringer, og frontend script.js håndterer brugerens valg og opdaterer UI.
- Dokumentation, referencedokument og kodevejledning er løbende opdateret.

### Næste trin
- Udbyg AI-strategier og politiske beslutninger (alliancer, diplomati, events).
- Flere interaktive frontend-elementer og avanceret visualisering.
- Udvid test og dokumentation, især for økonomiske invarianter og edge cases.
- Løbende kalibrering og validering af modelparametre.

### Kommentar
Projektet har nu en robust, iterativ kerne med turnbaseret simulation, AI-modstandere, makroøkonomiske feedbacks og direkte policy-feedback-loop mellem UI og backend. Klar til videreudvikling og finpudsning.

---

## Projektmål
En kort beskrivelse af projektet og dets overordnede mål.

## Udvidet Projektbeskrivelse

Jeg ønsker at bygge en "Trade War Simulator". Formålet er både at have det sjovt og at bruge det til at forudsige verdensøkonomiske scenarier. Spillet skal give spilleren mulighed for at spille som et af de 20 største lande i verden samt Danmark. Det skal være realistisk og baseret på rigtige økonomiske data.

### Centrale Elementer:
- **Realistisk økonomisk model**: Brug en ægte økonomisk model til at simulere økonomien.
- **EU's fælles handelspolitik**: EU-landene skal have en fælles handelspolitik.
- **Turn-based gameplay**: Spilleren og AI-landene skiftes til at tage handlinger.
- **Økonomiske parametre**: Rente, industrier, vækst, arbejdsløshed, borgernes tillid, m.m.
- **Handlinger og konsekvenser**: Spilleren kan påvirke økonomien gennem toldsatser, subsidier, investeringer, m.m.
- **AI-intelligens**: Andre lande handler strategisk og påvirker spilleren.
- **Politiske mekanismer**: Demokratier kan have valg, diktaturer kan vælte spilleren.
- **Sjove mekanismer**: Handelskrige, naturkatastrofer, teknologiske gennembrud, m.m.

### Mål:
- At skabe en simulator, hvor spilleren kan optimere deres lands økonomi og konkurrere mod andre lande.
- At gøre spillet sjovt og udfordrende med realistiske og uforudsigelige hændelser.

### Grafisk Interface:
- Et simpelt verdenskort til at visualisere lande og deres økonomiske status.
- Et kontrolpanel til at justere parametre og se resultater.

### Næste Skridt:
1. Indsamle data for de 20 største økonomier + Danmark.
2. Implementere en prototype af den økonomiske model.
3. Udvikle AI-intelligens og turn-based mekanismer.
4. Designe et simpelt grafisk interface.

## Økonomisk Model: Neoklassisk Model for International Økonomi i Simulationsspil (opdateret 21. april 2025)

### Centrale mekanismer og formler (uddybet)

#### 1. Handelsdynamikker og tariffer
- Tariffer øger importpriser: P_import = P_f * valutakurs * (1 + t)
- Indenlandsk prisniveau: P_domestic = (1 - μ) * P_hjemmelavet + μ * P_import
- Højere importpriser reducerer importvolumen og forbedrer nettoeksport (NX = X - M), men kan føre til gengældelse og valutakursændringer
- Udenlandske priser (P_f) beregnes som vægtet gennemsnit af andre landes prisniveauer, så inflation i store økonomier smitter af via importpriser
- Pass-through af tariffer til importpriser bør sættes til ca. 1 (100%) på grænsen, men lavere til detailpriser (fx 0,3-0,5)

#### 2. Valutakursmekanisme
- Valutakursen påvirkes af renteforskel og handelsbalance:
  - delta_fx = k1 * (policyRate - policyRate_foreign) - k2 * (NX_current - NX_last)
  - exchange_rate += delta_fx
- Højere rente eller bedre handelsbalance styrker valutaen (appreciering)
- K1 og k2 skal kalibreres (fx k1=0,5, k2=0,1)

#### 3. Arbejdsløshed via Okuns lov
- Okuns lov: Δu = -β * (gdpGrowth - potentialGrowth), typisk β ≈ 0,3–0,5
- Høj vækst reducerer arbejdsløshed, lav vækst øger den
- β kan gøres landespecifik eller cyklisk

#### 4. Inflationsmekanisme med importeffekter
- Inflation opdateres som: inflation_new = inflation_old + φ * (outputGap) + γ * (Δ P_import)
- φ styrer følsomhed for output gap, γ for importpriser (fx γ=0,05–0,15)
- Importeret inflation og valutakursændringer slår direkte igennem på prisniveauet
- Forventningsdannelse kan inkluderes: inflation_new = π^e + φ*outputGap + γ*ΔP_import

#### 5. Sektorspecifik dynamik
- Tariffer og prisdannelse pr. sektor: P_import[s] = P_f[s] * valutakurs * (1 + t_s)
- Sektorens pris: P_d[s] = (1 - μ_s) * P_hjem[s] + μ_s * P_import[s]
- Nettoeksport og beskæftigelse beregnes pr. sektor, og Okuns lov kan anvendes sektorspecifikt
- Sektorspecifikke effekter af tariffer og modforanstaltninger
- Sektorer har egne output, beskæftigelse, investering, kapacitet og profit

#### 6. BNP og arbejdsløshed som aggregerede størrelser
- BNP = sum(Output_s) på tværs af sektorer
- Samlet arbejdsløshed: u_total = sum(L_s * u_s), hvor L_s er sektorens andel af arbejdsstyrken

#### 7. Investering og kapacitetsudbygning
- Investering: I = max(0, i0 + i1 * ΔGDP - i2 * r)
- Fordeles på sektorer efter vækst, profit eller andel af output
- Investering øger sektors kapacitet og potentiale output
- Sektorspecifik kapitalstock opdateres: K_s,t+1 = (1-δ_s)*K_s,t + I_s,t

#### 8. Finanspolitik
- Skatteprovenu: T = τ * GDP, hvor τ er samlet skatteprocent
- Offentlige udgifter G indgår direkte i efterspørgslen
- Disponibel indkomst: Y_disposable = (1 - τ) * Y
- Budgetsaldo og gæld: debt = debt_last + (G - T)

#### 9. Politisk tillid / borgernes opbakning
- Trust falder ved høj arbejdsløshed og inflation: Δtrust = -a * (unemp_rate - u_target) - b * (inflation - π_target) - c * (shock_unpopular)
- Politisk upopulære beslutninger (fx skatteforhøjelser) trækker trust yderligere ned
- Lav trust kan føre til politisk ustabilitet eller tab af spillet

#### 10. AI-opførsel (andre lande)
- AI reagerer strategisk på spillerens handlinger (fx gengældelse ved told)
- Beskytter nøglesektorer og kan danne alliancer mod spilleren
- AI har egne trust-mekanismer og politiske mål
- Simpel tit-for-tat logik for handelspolitik og sektorbeskyttelse

---

## Teknisk Setup og Udviklingsvejledning (opdateret 21. april 2025)

Denne sektion samler anbefalinger fra 'Kodevejledning til Trade War Simulator_.txt' og danner grundlag for projektets tekniske setup og udviklingspraksis.

### 1. Projektstruktur
- Brug en klar adskillelse mellem frontend (brug UI-framework, fx React/Vue) og backend (Python, fx Flask/FastAPI).
- Organisér projektet som et monorepo med separate mapper for frontend og backend.
- Backend: src-layout anbefales (src/ med underpakker for models, web/routes, services).
- Frontend: src/ med komponenter, pages/views, services (API-kald), state management, assets.
- Overvej en delt mappe (shared/) for fælles typer eller valideringslogik, hvis relevant.

### 2. Kodestandarder og Stil
- Python: Følg PEP8, brug Black og Ruff til formatering/linting.
- JavaScript/TypeScript: Følg Airbnb/Google styleguide, brug Prettier og ESLint.
- Aktiver format-on-save og linter integration i VSCode.
- Brug meningsfulde navne, docstrings og kommentarer – især som Copilot-prompts.

### 3. Modularitet og Designprincipper
- Separation of Concerns: Adskil UI, forretningslogik og dataadgang.
- High Cohesion & Low Coupling: Hold moduler fokuserede og uafhængige.
- Brug MVC, Repository Pattern og Service Layer i backend.
- Brug Dependency Injection for at sikre testbarhed og fleksibilitet.

### 4. Backend Arkitektur
- Byg simuleringsmotoren som agent-baseret model (lande, sektorer, markeder som agenter).
- Overvej Event Sourcing eller TSDB til historik og analyse.
- Optimer tunge beregninger med NumPy/Pandas og multiprocessing.

### 5. Frontend Arkitektur
- Brug moderne framework (React/Vue).
- Implementér state management (Redux, Zustand, Pinia).
- Integrér datavisualisering (Plotly.js, Chart.js).
- Brug WebSockets til realtidsopdateringer fra backend.

### 6. API Design
- REST anbefales som udgangspunkt, evt. GraphQL for fleksible queries.
- Følg best practices for endpoints, statuskoder, fejlhåndtering og versionering (fx /api/v1/...).
- Implementér WebSockets for realtidsdata.
- Følg OWASP API Security Top 10.

### 7. Teststrategi
- Følg testpyramiden: mange unit tests, færre integration, få E2E.
- Python: pytest, unittest, Hypothesis (property-based testing).
- Frontend: Jest, React/Vue Testing Library, Cypress/Playwright.
- Brug mocking og fixtures til at isolere tests.
- Test også økonomiske invarianter og scenarier.

### 8. Versionskontrol og Workflow
- Brug Git (GitHub Flow anbefales).
- Små, atomare commits med Conventional Commits standard.
- Opret Pull Requests for alle ændringer, også solo.
- Gennemgå AI-genereret kode kritisk.

### 9. AI Samarbejde
- Brug kommentarer og docstrings som Copilot-prompts.
- Bryd opgaver ned i små trin og iterér.
- Gennemgå og valider altid AI-forslag.
- Brug Copilot Chat og VSCode-udvidelser aktivt.

### 10. Dokumentation
- Dokumentér økonomiske modeller, antagelser og API-kontrakter i docs/ og i kode.
- Hold README og projektbeskrivelser opdateret.

---

## AI-arkitektur og status (opdateret 21. april 2025)

### Valgt AI-strategi
- Hybrid-tilgang: Utility AI til beslutningsvalg (vægtning af økonomiske/politiske/diplomatiske faktorer) kombineret med Finite State Machines (FSM) eller Behavior Trees (BT) til overordnet strategistyring og sekventering af handlinger.
- AI-profiler/personligheder: Hver nation får personlighed baseret på styreform (demokrati, autokrati, hybrid) og økonomisk situation, som påvirker AI’ens vægtning og adfærd.
- Forklarbarhed: AI’ens motiver og valg skal kunne forklares for spilleren (ingen sort boks).
- Ingen tung ML i realtid – evt. kun offline til tuning af parametre.

### Implementeret
- Grundlæggende FSM-struktur for AI-landes strategitilstand (fx neutral, aggressiv, samarbejdende).
- Utility-baseret beslutningslogik for toldsatser og sektorbeskyttelse (vægtning af BNP, arbejdsløshed, sektoroutput, politisk stabilitet mv.).
- AI-profiler: Landenes styreform og økonomiske situation påvirker AI’ens valg (fx demokrati vægter stabilitet, autokrati vægter magt).
- Simpel feedback-loop: AI’s handlinger påvirker økonomimodellen, og modeloutput bruges i næste AI-evaluering.
- Ingen ML eller evolverende strategier i runtime.

### Næste trin
- Udbygge utility-funktioner med flere handlinger (alliancer, diplomati, subsidier, budget).
- Implementere forklarende feedback til spilleren om AI’ens valg og motiver.
- Udvide FSM/BT med flere tilstande og transitions.
- Mulighed for at vælge AI-sværhedsgrad og personlighed i UI.

### Kommentar
AI’en følger nu best practise for strategispil: Utility AI + FSM/BT, personlighedsparametre, forklarbarhed og ingen black-box. Udviklingen følger anbefalingerne fra AI-analysen og rapporten. Klar til at udbygge med flere handlinger, feedback og sværhedsgrader.

---

## Status (opdateret 21. april 2025)

### Implementerede trin
- [x] Udvidet data- og modelstruktur til at understøtte sektorer i både Python-klasser og countries.json.
- [x] Grundlæggende sektorspecifik simulation: Sektorer opdateres for output, pris, import/eksport, nettoeksport og ledighed pr. tur.
- [x] Aggregering af BNP og arbejdsløshed fra sektorer til land.
- [x] Implementeret pris- og handelsdynamik pr. sektor inkl. tariffer og priselasticitet.
- [x] Makroøkonomiske feedbacks: valutakurs, investering, kapacitetsudbygning og finanspolitik opdateres pr. tur.
- [x] AI-logik: tit-for-tat-tariffer, sektorbeskyttelse og justering af skat/rente ved høj gæld.
- [x] Frontend: Dynamisk visning af lande- og sektordata, KPI’er, sektorgrafer og pædagogisk feedback til spilleren efter hver tur.
- [x] countries.json er nu gyldig JSON uden kommentarer.

### Næste trin
- Udbygge AI-strategier og politiske beslutninger.
- Flere interaktive frontend-elementer (valg, events, avanceret visualisering).
- Udvide test og dokumentation.

### Kommentar
Projektet har nu en fuldt funktionel turbaseret kerne, AI-modstandere, makroøkonomiske feedbacks og pædagogisk feedback til spilleren. Klar til videreudvikling og finpudsning.

---

## Glossar (centrale økonomiske termer)
- **Output gap**: Forskellen mellem faktisk og potentiel BNP.
- **Pass-through**: Hvor meget en prisændring (fx told) slår igennem til forbrugerpriser.
- **Accelerator**: Mekanisme hvor høj vækst øger investeringer.
- **Stylized facts**: Empirisk observerede mønstre i økonomiske data.
- **Emergens**: Makroeffekter opstår fra mikrointeraktioner mellem agenter.

## Datakilder og Vedligeholdelse
- Data for lande og sektorer hentes primært fra Verdensbanken, IMF, Eurostat og nationale statistikkontorer. Data lagres i JSON/CSV-format.
- Data opdateres manuelt efter behov (ikke automatisk/dagligt i første version).
- Dokumentér datakilder og versionshistorik i docs/.

## Data- og afhængighedsstyring
- Alle eksterne Python-pakker og versioner angives i requirements.txt eller pyproject.toml.
- Brug venv til at oprette virtuelt miljø: `python3 -m venv .venv && source .venv/bin/activate`.
- Frontend-afhængigheder styres med package.json.

## Agent-baseret Model (ABM) og AI
- AI-agenters beslutningslogik starter med simple regler (fx tit-for-tat, heuristikker). Mulighed for senere udvidelse med machine learning.
- Interaktion mellem agenter sker globalt (alle lande kan handle med alle, men vægte kan bruges for netværkseffekter).
- Emergens: Målet er at observere makroøkonomiske fænomener, der opstår fra agenternes mikrobeslutninger.
- Informationsflow: Agenter har adgang til relevante globale og lokale økonomiske indikatorer.

## Simuleringsmotor og Tidsstyring
- Spillet er turbaseret (turn-based). Hver tur repræsenterer et kvartal.
- Simuleringsloop: 1) Spilleren vælger politikker, 2) AI-lande agerer, 3) Simulering køres, 4) Resultater vises, 5) Trust og events opdateres.
- Handlinger udføres sekventielt pr. tur.

## Modelvalidering og Kalibrering
- Modellen valideres mod historiske data og stylized facts (fx recessioner, handelschok).
- Parametre (k1, k2, β, φ, γ) kalibreres manuelt og dokumenteres i en config-fil og i docs/.

## Tekniske Detaljer
- Database: Simulationsdata og historik gemmes i fil (JSON/CSV) eller evt. SQLite. Event Sourcing/TSDB kan overvejes for avanceret analyse.
- Skalerbarhed: Systemet designes modulært, så flere lande/sektorer kan tilføjes uden større omskrivning.
- Deployment: Lokalt på macOS, evt. Docker til containerisering. Cloud kan overvejes senere.

## Dokumentationsstandard (ODD-principper integreret)
- Formål, entiteter, processer, designkoncepter, initialisering, inputdata og submodeller beskrives løbende i relevante afsnit.
- ODD-struktur bruges som guideline for modelbeskrivelser og kodekommentarer.

## CI/CD, Versionskontrol og Workflow
- Brug Git og GitHub. GitHub Actions kan bruges til automatiske tests, linting og deploy.
- Små, atomare commits med Conventional Commits.
- README indeholder Getting Started, installationsvejledning og kodeeksempler.

## Error handling, logging og overvågning
- Brug Python logging med INFO/WARNING/ERROR-niveauer.
- Fejl håndteres med undtagelser og brugervenlige fejlbeskeder. Manglende data eller beregningsfejl logges og vises i UI.

## Performance og skalering
- Tunge simuleringer kan køres asynkront eller i batch (fx med multiprocessing eller asyncio).
- Caching af resultater kan implementeres senere (fx med memoization).

## Sikkerhed og adgangskontrol
- Simulatoren er singleplayer og kræver ikke login.
- Inputvalidering på alle brugerinput og API-kald.

## Parameter-kalibrering og validering
- Standardværdier for parametre dokumenteres i config-fil og docs.
- Mulighed for at justere parametre via UI eller config.

## Scenario- og event-system
- Events (fx naturkatastrofer, teknologiske gennembrud) implementeres som modulært event-system med triggers, sandsynligheder og effekter.
- Events vises i UI som notifikationer.

## Turn-sequence og game-flow
- Hver tur: 1) Spilleren vælger handlinger, 2) AI-lande agerer, 3) Simulering, 4) Resultater, 5) Trust/events opdateres.
- En tur = ét kvartal. En kamp varer typisk 20-40 ture.

## API-specifikation
- REST API med endpoints som fx GET /api/v1/countries, POST /api/v1/actions.
- Input/output i JSON. API-dokumentation i docs/.

## Onboarding og udviklervejledning
- README har Getting Started, installationsguide, testkørsel, kode-style, og almindelige kommandoer.
- Coding conventions og branch-politik beskrives i CONTRIBUTING.md.

## Licens & bidrag
- Licens (fx MIT) angives i LICENSE.txt. Eksterne bidragsherrer henvises til CONTRIBUTING.md.

## Accessibility & internationalisering
- UI designes til dansk (ingen i18n i første version).
- Grundlæggende tilgængelighed (kontrast, tastaturnavigation) overholdes.

## Implementeringsplan og tjekpoints

1. **Basisstruktur og data**
   - [ ] Udvid countries.json med flere lande og sektordata
   - [ ] Definér sektorer og deres parametre (output, beskæftigelse, importandel, mv.)
   - [ ] Opret grundlæggende Python-klasser for land, sektor og økonomisk model

2. **Handels- og prisdynamik**
   - [ ] Implementér tarif- og prisformler (P_import, P_domestic)
   - [ ] Implementér dynamisk kobling mellem økonomier (P_f som vægtet gennemsnit)
   - [ ] Implementér sektoropdelt import/eksport og elasticiteter

3. **Valutakurs og kapitalbevægelser**
   - [ ] Implementér valutakursmekanisme (delta_fx)
   - [ ] Kalibrér k1 og k2

4. **Makroøkonomiske feedbacks**
   - [ ] Implementér Okuns lov (arbejdsløshed)
   - [ ] Implementér Phillips-kurve med importpriser (inflation)
   - [ ] Implementér forventningsdannelse (π^e)

5. **Sektorspecifik logik**
   - [ ] Implementér sektorspecifikke tariffer og prisdannelse
   - [ ] Implementér sektoropdelt output, beskæftigelse og investering
   - [ ] Implementér aggregering til BNP og samlet arbejdsløshed

6. **Investering og kapacitetsudbygning**
   - [ ] Implementér investeringsfunktion og fordeling på sektorer
   - [ ] Opdater sektorspecifik kapitalstock og kapacitet

7. **Finanspolitik og offentlig gæld**
   - [ ] Implementér skatteprovenu, offentlige udgifter og gældsopbygning
   - [ ] Implementér forbrugsfunktion (MPC, wealth, confidence)

8. **Politisk tillid og feedback**
   - [ ] Implementér trust-mekanisme og kobling til økonomiske nøgletal
   - [ ] Implementér effekter af politiske beslutninger på trust

9. **AI og international respons**
   - [ ] Implementér AI-logik for tit-for-tat, sektorbeskyttelse og alliancer
   - [ ] Implementér AI’s interne trust og politiske mål

10. **Test, validering og dokumentation**
   - [ ] Skriv enhedstests for alle centrale funktioner
   - [ ] Dokumentér alle økonomiske antagelser og formler i kode og docs
   - [ ] Løbende validering mod kendte økonomiske cases

---

**Bemærk:**
- Hvert tjekpunkt bør markeres som færdigt i referencedokumentet, så fremdrift kan følges.
- Se detaljeret beskrivelse og eksempler i denne sektion for formelgrundlag og kodeeksempler.

## UI Design Forslag

### Overordnede UI/UX-principper (opdateret 21. april 2025)

#### Dashboard Layout & Struktur
- Brug et modulært, grid-baseret dashboard med venstre navigation, topbar og et indholdsområde med widgets (kort, KPI’er, tabeller).
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