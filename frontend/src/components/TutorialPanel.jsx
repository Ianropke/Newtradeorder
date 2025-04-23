import React, { useState, useEffect } from 'react';
import '../styles/TutorialPanel.css'; // We'll create this file shortly

function TutorialPanel({ onClose }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [show, setShow] = useState(true);
  const [tutorialCategory, setTutorialCategory] = useState('basic');
  
  const tutorialContent = {
    basic: [
      {
        title: "Velkommen til Trade War Simulator!",
        content: "Dette er en handelskrigssimulator, hvor du kan spille som et land og navigere gennem internationale handelsudfordringer.",
        image: "/tutorial/welcome.png"
      },
      {
        title: "Sådan starter du",
        content: "Først skal du vælge det land, du vil spille som. Hvert land har forskellige styrker, svagheder og udgangspunkter. Når du har valgt land, kan du trykke på 'Start Spillet' for at begynde.",
        image: "/tutorial/country_selection.png"
      },
      {
        title: "Scenarievælger",
        content: "I stedet for at starte et standard spil, kan du vælge et scenario med foruddefinerede udfordringer og situationer. Dette giver forskellige spilmuligheder og læringsperspektiver.",
        image: "/tutorial/scenario_selector.png"
      },
      {
        title: "Spilfaser",
        content: "Spillet er inddelt i faser for hver tur: Forberedelse, Handelsvalg, Simulering, Resultater og Afslutning. Hver fase giver dig forskellige handlingsmuligheder, og du skal gennemføre dem i rækkefølge.",
        image: "/tutorial/game_phases.png"
      },
      {
        title: "Ture",
        content: "Spillet er turbaseret. Efter du har gennemført alle dine handlinger, trykker du på 'Næste Tur' for at simulere resultatet og gå videre. Hver tur repræsenterer 3 måneder i spilverdenen.",
        image: "/tutorial/turns.png"
      },
      {
        title: "Brugerfladen",
        content: "Brugerfladen består af forskellige paneler: Landeinformation, BNP-historie, Diplomati, Begivenheder, Kort og Politikpanel. Disse giver dig overblik og styring af din nation.",
        image: "/tutorial/ui_overview.png"
      },
      {
        title: "Flere tutorials",
        content: "Vælg en kategori nedenfor for at lære mere om specifikke aspekter af spillet. Du kan altid vende tilbage til denne tutorial senere ved at klikke på 'Vis Tutorial' knappen."
      }
    ],
    economy: [
      {
        title: "Økonomisystemet",
        content: "Din nations økonomi er baseret på forskellige sektorer såsom landbrug, industri og service. Hver sektor påvirkes forskelligt af handelspolitikker."
      },
      {
        title: "BNP og vækst",
        content: "BNP (Bruttonationalprodukt) er den primære indikator for din økonomis størrelse. Vækstraten viser, hvor hurtigt din økonomi ændrer sig. Positiv vækst er godt, negativ vækst (recession) er dårligt."
      },
      {
        title: "Import og eksport",
        content: "Handel med andre lande er afgørende for din økonomi. Balance mellem import og eksport er vigtig, men fokuser på at maksimere værdien af din handel, ikke bare balancen."
      },
      {
        title: "Toldsatser",
        content: "Toldsatser er ekstra afgifter på importvarer. Høje toldsatser beskytter din industri men gør også importvarer dyrere for dine borgere og kan føre til gengældelse fra handelspartnere."
      },
      {
        title: "Subsidier",
        content: "Subsidier er støtte til din egen industri, som gør dine eksportvarer mere konkurrencedygtige. Men de kan betragtes som uretfærdig konkurrence af andre lande."
      },
      {
        title: "Skatter",
        content: "Skattesatsen påvirker både regeringens indtægter og din økonomiske vækst. For høje skatter kan reducere produktivitet, men for lave skatter kan begrænse din handlingsfrihed."
      }
    ],
    diplomacy: [
      {
        title: "Diplomatiske relationer",
        content: "Relationerne mellem lande repræsenteres på en skala fra -100 (fjendtlig) til +100 (allieret). Disse relationer påvirker handel, alliance-muligheder og reaktion på dine politikker."
      },
      {
        title: "Alliancer",
        content: "Alliancer giver fordele som øget handel, støtte under handelskrige og fælles reaktion på globale begivenheder. Stærke alliancer er værdifulde i usikre tider."
      },
      {
        title: "Handelsaftaler",
        content: "Handelsaftaler reducerer handelsbarrierer mellem lande. De kan være bilaterale (mellem to lande) eller multilaterale (mellem flere lande)."
      },
      {
        title: "Sanktioner",
        content: "Økonomiske sanktioner kan bruges til at presse andre lande. De reducerer handel men kan skade begge parter. Brug dem strategisk og vær forberedt på modreaktioner."
      },
      {
        title: "Koalitioner",
        content: "Koalitioner er grupper af lande med fælles interesser. De kan modsætte sig dine handelspolitikker eller støtte dig, afhængigt af relationerne."
      }
    ],
    events: [
      {
        title: "Krisebegivenheder",
        content: "Under spillet vil forskellige begivenheder opstå - fra naturkatastrofer til teknologiske gennembrud. Disse kræver din reaktion og kan ændre spillets forløb."
      },
      {
        title: "Handelskrige",
        content: "Handelskrige udbryder når lande eskalerer toldsatser og handelsbegrænsninger mod hinanden. De kan skade begge parters økonomier men kan være nødvendige for at beskytte vigtige sektorer."
      },
      {
        title: "Globale kriser",
        content: "Globale kriser som finanskriser, pandemier eller ressourcemangel påvirker alle lande men i forskellig grad. Din håndtering af disse kan styrke eller svække din position."
      },
      {
        title: "Responsmuligheder",
        content: "Når begivenheder indtræffer, får du ofte flere valgmuligheder. Hver mulighed har forskellige konsekvenser for økonomi, diplomati og befolkningstilfredshed."
      }
    ],
    advanced: [
      {
        title: "Avanceret handelsstrategi",
        content: "En god handelsstrategi involverer balancering af protektionisme og frihandel. Beskyt strategisk vigtige industrier mens du fremmer handel i sektorer hvor du har konkurrencefordele."
      },
      {
        title: "Langsigtede virkninger",
        content: "Handelspolitikker har både kort- og langsigtede effekter. Toldsatser kan give umiddelbar beskyttelse men skade innovation og produktivitet på lang sigt."
      },
      {
        title: "Sektorspecifikke strategier",
        content: "Forskellige økonomiske sektorer reagerer forskelligt på handelspolitikker. Forarbejdningsindustri er f.eks. mere følsom over for toldsatser end serviceindustri."
      },
      {
        title: "Global magtbalance",
        content: "Handelskrige handler ikke kun om økonomi men også om geopolitisk indflydelse. Stærke økonomier kan udøve diplomatisk pres gennem handelspolitikker."
      },
      {
        title: "Komparative fordele",
        content: "Lande har forskellige komparative fordele baseret på ressourcer, arbejdskraft og teknologi. Udnyt dine fordele og find strategiske partnere der komplementerer din økonomi."
      }
    ]
  };

  // Get current tutorial steps based on category
  const tutorialSteps = tutorialContent[tutorialCategory] || tutorialContent.basic;
  
  const handleCloseClick = () => {
    setShow(false);
    if (onClose) onClose();
  };
  
  const nextStep = () => {
    if (currentStep < tutorialSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else if (tutorialCategory === 'basic') {
      // If we're at the end of basic tutorial, prompt for choosing a category
      // No action needed - just show the category selection which is displayed
      // when we're at the end of the basic tutorial
    } else {
      // For other categories, go back to basic at the end
      setTutorialCategory('basic');
      setCurrentStep(6); // Go to the category selection step in basic
    }
  };
  
  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    } else if (tutorialCategory !== 'basic') {
      // If we're at the first step of a non-basic category, go back to basic
      setTutorialCategory('basic');
      setCurrentStep(6); // Go to the category selection step in basic
    }
  };

  const selectCategory = (category) => {
    setTutorialCategory(category);
    setCurrentStep(0);
  };
  
  if (!show) return null;

  const showCategorySelection = tutorialCategory === 'basic' && currentStep === tutorialSteps.length - 1;
  
  return (
    <div className="tutorial-overlay">
      <div className="tutorial-content">
        <button className="close-tutorial" onClick={handleCloseClick}>✕</button>
        
        <h3>{tutorialSteps[currentStep].title}</h3>
        <div className="tutorial-body">
          {tutorialSteps[currentStep].image && (
            <div className="tutorial-image">
              <img src={tutorialSteps[currentStep].image} alt={tutorialSteps[currentStep].title} />
            </div>
          )}
          <p>{tutorialSteps[currentStep].content}</p>
        </div>

        {showCategorySelection && (
          <div className="tutorial-categories">
            <h4>Vælg en kategori for at lære mere:</h4>
            <div className="category-buttons">
              <button onClick={() => selectCategory('economy')}>Økonomi</button>
              <button onClick={() => selectCategory('diplomacy')}>Diplomati</button>
              <button onClick={() => selectCategory('events')}>Begivenheder</button>
              <button onClick={() => selectCategory('advanced')}>Avanceret</button>
            </div>
          </div>
        )}
        
        <div className="tutorial-navigation">
          <button 
            onClick={prevStep} 
            disabled={currentStep === 0 && tutorialCategory === 'basic'}
            className={currentStep === 0 && tutorialCategory === 'basic' ? "disabled" : ""}
          >
            Forrige
          </button>
          <span>{currentStep + 1} / {tutorialSteps.length}</span>
          {(currentStep < tutorialSteps.length - 1 || tutorialCategory !== 'basic') ? (
            <button onClick={nextStep}>Næste</button>
          ) : (
            <button onClick={() => handleCloseClick()}>Afslut tutorial</button>
          )}
        </div>
      </div>
    </div>
  );
}

export default TutorialPanel;
