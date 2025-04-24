"""
Country Profiles Module for Trade War Simulator

This module provides detailed profiles for major countries in the global trading system,
including economic characteristics, diplomatic tendencies, and trade policy preferences.
These profiles are used to drive realistic AI behavior in the simulation.
"""

from typing import Dict, Any, List
from diplomacy_ai import CountryProfile

# Dictionary of country profiles with realistic data
COUNTRY_PROFILES = {
    # Major Economic Powers
    "USA": {
        "name": "United States of America",
        "government_type": "democratic_republic",
        "economic_system": "market",
        "region": "North America",
        "exports_percent_gdp": 11.7,
        "imports_percent_gdp": 14.5,
        "research_percent_gdp": 3.1,
        "debt_to_gdp": 134.0,
        "key_industries": ["technology", "aerospace", "pharmaceuticals", "agriculture", "financial_services"],
        "key_exports": ["machinery", "electronics", "aircraft", "vehicles", "petroleum_products"],
        "key_imports": ["consumer_goods", "vehicles", "machinery", "oil", "pharmaceuticals"],
        "key_trade_partners": ["CAN", "MEX", "CHN", "JPN", "DEU"],
        "trade_agreements": ["USMCA", "various bilateral agreements"],
        "diplomatic_incidents": [
            {"year": 2018, "type": "aggressive", "description": "Initiating trade war with China"},
            {"year": 2020, "type": "cooperative", "description": "USMCA trade agreement"},
            {"year": 2023, "type": "aggressive", "description": "Semiconductor export controls"}
        ],
        "trade_policy_description": "Historically supportive of free trade but with increasing protectionist tendencies in recent years. Strong emphasis on intellectual property protection and market access for services. Uses trade policy as diplomatic tool.",
        "historical_context": "Post-WWII advocate of liberal international economic order, but with growing focus on reciprocity and addressing 'unfair' trade practices.",
        "resource_dependency": "Energy independent but reliant on rare earth minerals imports",
        "decision_making_structure": "Complex interagency process with congressional oversight",
        "cultural_trade_factors": "Strong emphasis on intellectual property protection in entertainment and technology",
        "crisis_response_pattern": "Tends to use economic leverage during international crises"
    },
    
    "CHN": {
        "name": "China",
        "government_type": "authoritarian_single_party",
        "economic_system": "mixed_state_capitalist",
        "region": "East Asia",
        "exports_percent_gdp": 18.5,
        "imports_percent_gdp": 17.3,
        "research_percent_gdp": 2.4,
        "debt_to_gdp": 77.5,
        "key_industries": ["manufacturing", "technology", "construction", "telecommunications", "mining"],
        "key_exports": ["electronics", "machinery", "textiles", "integrated_circuits", "steel"],
        "key_imports": ["oil", "iron_ore", "semiconductors", "agricultural_products", "machinery"],
        "key_trade_partners": ["USA", "JPN", "KOR", "DEU", "AUS"],
        "trade_agreements": ["RCEP", "various BRI agreements"],
        "diplomatic_incidents": [
            {"year": 2018, "type": "aggressive", "description": "Retaliatory tariffs against US"},
            {"year": 2020, "type": "cooperative", "description": "RCEP trade agreement"},
            {"year": 2022, "type": "aggressive", "description": "Trade restrictions against Lithuania"},
            {"year": 2024, "type": "cooperative", "description": "BRICS expansion initiative leadership"}
        ],
        "trade_policy_description": "Strategic mercantilist approach focused on export-led growth while protecting domestic markets. Increasingly using trade as geopolitical leverage while selectively opening markets. Strong focus on self-sufficiency in critical sectors.",
        "historical_context": "Transitioned from centrally planned isolation to strategic integration with global markets following 1978 reforms",
        "resource_dependency": "Heavily dependent on imported oil, iron ore, and semiconductors",
        "decision_making_structure": "Centralized with leadership by Communist Party and implementation by ministries",
        "cultural_trade_factors": "State capitalism with strong emphasis on technology transfer and long-term planning",
        "crisis_response_pattern": "Tends to use targeted economic countermeasures and strategic resource control",
        "technology_policy": "Strong emphasis on technological self-sufficiency and leadership",
        "monetary_policy_stance": "State-controlled with strategic international expansion of currency",
        "environmental_policy": "Growing focus on renewables while maintaining development priority",
        "labor_market_flexibility": 0.4,
        "corruption_index": 0.6,
        "geopolitical_alignment": 0.8,
        "sanctions_resilience": 0.8,
        "state_enterprise_dominance": 0.9,
        "regional_leadership_role": 0.9,
        "resource_nationalism": 0.8
    },
    
    "DEU": {
        "name": "Germany",
        "government_type": "parliamentary_democracy",
        "economic_system": "social_market",
        "region": "Europe",
        "exports_percent_gdp": 47.4,
        "imports_percent_gdp": 41.1,
        "research_percent_gdp": 3.1,
        "debt_to_gdp": 69.3,
        "key_industries": ["automotive", "machinery", "chemicals", "electronics", "pharmaceuticals"],
        "key_exports": ["vehicles", "machinery", "pharmaceuticals", "electronics", "chemical_products"],
        "key_imports": ["machinery", "vehicles", "oil", "electronics", "metals"],
        "key_trade_partners": ["FRA", "USA", "CHN", "NLD", "ITA"],
        "trade_agreements": ["EU", "various EU agreements"],
        "diplomatic_incidents": [
            {"year": 2020, "type": "cooperative", "description": "EU-China investment agreement negotiation"},
            {"year": 2022, "type": "cooperative", "description": "Diversification of trade away from Russian dependency"}
        ],
        "trade_policy_description": "Strong advocate for rules-based free trade through EU framework. Export-oriented economy with focus on high-value manufacturing. Balances economic interests with EU solidarity.",
        "historical_context": "Post-war economic miracle (Wirtschaftswunder) through export-led growth and European integration",
        "resource_dependency": "Highly dependent on energy imports, particularly from Russia (historically)",
        "decision_making_structure": "Federal system with strong industry associations input and EU coordination",
        "cultural_trade_factors": "Strong industrial policy tradition and 'Mittelstand' business culture",
        "crisis_response_pattern": "Prefers multilateral EU approaches and gradual adjustment to economic shocks"
    },
    
    "JPN": {
        "name": "Japan",
        "government_type": "parliamentary_democracy",
        "economic_system": "market",
        "region": "East Asia",
        "exports_percent_gdp": 17.6,
        "imports_percent_gdp": 16.8,
        "research_percent_gdp": 3.3,
        "debt_to_gdp": 263.1,
        "key_industries": ["automotive", "electronics", "machinery", "robotics", "steel"],
        "key_exports": ["vehicles", "electronics", "machinery", "chemicals", "metals"],
        "key_imports": ["oil", "natural_gas", "coal", "electronics", "food"],
        "key_trade_partners": ["CHN", "USA", "KOR", "TWN", "HKG"],
        "trade_agreements": ["CPTPP", "Japan-EU EPA", "RCEP"],
        "diplomatic_incidents": [
            {"year": 2019, "type": "aggressive", "description": "Export controls against South Korea"},
            {"year": 2020, "type": "cooperative", "description": "RCEP signing"}
        ],
        "trade_policy_description": "Export-oriented economy with gradual market opening. Strong emphasis on high-tech manufacturing and intellectual property protection. Increasingly using economic statecraft for regional influence.",
        "historical_context": "Post-war economic miracle through export-led industrialization and state-guided development",
        "resource_dependency": "Almost entirely dependent on imported energy and many raw materials",
        "decision_making_structure": "Consensus-based with strong coordination between government ministries and keiretsu business groups",
        "cultural_trade_factors": "Quality-focused manufacturing and long-term business relationships",
        "crisis_response_pattern": "Cautious, pragmatic responses with emphasis on maintaining stability"
    },
    
    # BRICS Nations - Complete set
    "IND": {
        "name": "India",
        "government_type": "federal_parliamentary_democracy",
        "economic_system": "mixed",
        "region": "South Asia",
        "exports_percent_gdp": 18.7,
        "imports_percent_gdp": 21.1,
        "research_percent_gdp": 0.7,
        "debt_to_gdp": 83.4,
        "key_industries": ["services", "agriculture", "pharmaceuticals", "textiles", "manufacturing"],
        "key_exports": ["services", "pharmaceuticals", "jewelry", "textiles", "machinery"],
        "key_imports": ["oil", "electronics", "gold", "machinery", "chemicals"],
        "key_trade_partners": ["USA", "CHN", "UAE", "SAU", "HKG"],
        "trade_agreements": ["South Asian Free Trade Area", "various bilateral agreements"],
        "diplomatic_incidents": [
            {"year": 2019, "type": "aggressive", "description": "Withdrawal from RCEP negotiations"},
            {"year": 2020, "type": "aggressive", "description": "Border tensions with China affecting trade"},
            {"year": 2023, "type": "cooperative", "description": "Expansion of trade relations with Russia"}
        ],
        "trade_policy_description": "Gradually liberalizing but with significant protectionist tendencies. Strong focus on self-reliance ('Atmanirbhar Bharat'). Agricultural protectionism alongside service sector export promotion.",
        "historical_context": "Shifted from post-independence import substitution to gradual liberalization since 1991 reforms",
        "resource_dependency": "Heavily dependent on oil imports and growing electronics dependency",
        "decision_making_structure": "Federal system with significant bureaucracy and state-level implementation",
        "cultural_trade_factors": "Strong emphasis on services exports and software development",
        "crisis_response_pattern": "Pragmatic but protective of domestic producers and food security",
        "technology_policy": "Growing digital services with focus on homegrown solutions",
        "monetary_policy_stance": "Independent central bank with inflation targeting framework",
        "environmental_policy": "Balancing development needs with growing climate commitments",
        "labor_market_flexibility": 0.5,
        "corruption_index": 0.6,
        "geopolitical_alignment": 0.5,
        "sanctions_resilience": 0.6,
        "state_enterprise_dominance": 0.6,
        "regional_leadership_role": 0.8,
        "resource_nationalism": 0.6
    },
    
    "BRA": {
        "name": "Brazil",
        "government_type": "federal_presidential_republic",
        "economic_system": "mixed",
        "region": "South America",
        "exports_percent_gdp": 16.9,
        "imports_percent_gdp": 13.8,
        "research_percent_gdp": 1.3,
        "debt_to_gdp": 78.3,
        "key_industries": ["agriculture", "mining", "manufacturing", "services", "oil"],
        "key_exports": ["soybeans", "iron_ore", "oil", "meat", "wood_pulp"],
        "key_imports": ["machinery", "chemicals", "oil_products", "electronics", "vehicles"],
        "key_trade_partners": ["CHN", "USA", "ARG", "NLD", "JPN"],
        "trade_agreements": ["Mercosur", "Mercosur-EU pending"],
        "diplomatic_incidents": [
            {"year": 2019, "type": "aggressive", "description": "Environmental disputes affecting trade negotiations"},
            {"year": 2021, "type": "cooperative", "description": "BRICS cooperation initiatives"},
            {"year": 2023, "type": "cooperative", "description": "Expansion of trade with other BRICS nations"}
        ],
        "trade_policy_description": "Traditionally protective of domestic industry through Mercosur framework, with agricultural export focus. Policy fluctuates between liberalization pushes and industrial protection based on political climate.",
        "historical_context": "Cycles of import substitution and liberalization with strong agricultural export orientation",
        "resource_dependency": "Resource-rich country with commodity export dependency",
        "decision_making_structure": "Complex federal system with powerful agricultural and industrial lobbies",
        "cultural_trade_factors": "Regional leadership ambitions within South America",
        "crisis_response_pattern": "Tends to implement temporary protectionist measures during economic downturns",
        "technology_policy": "Growing emphasis on agricultural technology and biofuels",
        "monetary_policy_stance": "Autonomous central bank with inflation targeting framework",
        "environmental_policy": "Tension between agricultural interests and environmental protection",
        "labor_market_flexibility": 0.4,
        "corruption_index": 0.7,
        "geopolitical_alignment": 0.6,
        "sanctions_resilience": 0.5,
        "state_enterprise_dominance": 0.6,
        "regional_leadership_role": 0.8,
        "resource_nationalism": 0.7
    },
    
    "RUS": {
        "name": "Russia",
        "government_type": "authoritarian_presidential",
        "economic_system": "state_capitalism",
        "region": "Eurasia",
        "exports_percent_gdp": 28.5,
        "imports_percent_gdp": 20.7,
        "research_percent_gdp": 1.0,
        "debt_to_gdp": 17.8,
        "key_industries": ["oil_gas", "mining", "defense", "agriculture", "forestry"],
        "key_exports": ["oil", "natural_gas", "metals", "weapons", "agricultural_products"],
        "key_imports": ["machinery", "pharmaceuticals", "vehicles", "electronics", "food"],
        "key_trade_partners": ["CHN", "DEU", "NLD", "BLR", "TUR"],
        "trade_agreements": ["Eurasian Economic Union", "CIS Free Trade Area"],
        "diplomatic_incidents": [
            {"year": 2014, "type": "aggressive", "description": "Western sanctions over Ukraine and counter-sanctions"},
            {"year": 2020, "type": "aggressive", "description": "Oil price war with Saudi Arabia"},
            {"year": 2022, "type": "aggressive", "description": "Military action in Ukraine leading to extensive sanctions"},
            {"year": 2023, "type": "cooperative", "description": "Expansion of trade with BRICS partners"}
        ],
        "trade_policy_description": "Resource export-focused with strategic state control of key sectors. Uses energy exports as geopolitical leverage. Increasingly pivoting trade relationships eastward under Western sanctions.",
        "historical_context": "Transitioned from Soviet planned economy to state capitalism with strategic resource control",
        "resource_dependency": "Heavily dependent on hydrocarbon exports for state revenue",
        "decision_making_structure": "Centralized with strong presidential direction and oligarch influence",
        "cultural_trade_factors": "Strategic use of energy resources and defense exports for geopolitical influence",
        "crisis_response_pattern": "Uses resource leverage during crises and adapts to sanctions through import substitution",
        "technology_policy": 0.7,
        "monetary_policy_stance": "Conservative with large foreign reserves as economic buffer",
        "environmental_policy": 0.3,
        "labor_market_flexibility": 0.4,
        "corruption_index": 0.7,
        "geopolitical_alignment": 0.9,
        "sanctions_resilience": 0.8,
        "state_enterprise_dominance": 0.8,
        "regional_leadership_role": 0.9,
        "resource_nationalism": 0.9
    },
    
    "ZAF": {
        "name": "South Africa",
        "government_type": "parliamentary_republic",
        "economic_system": "mixed",
        "region": "Africa",
        "exports_percent_gdp": 29.8,
        "imports_percent_gdp": 28.4,
        "research_percent_gdp": 0.8,
        "debt_to_gdp": 69.4,
        "key_industries": ["mining", "automobile_assembly", "metalworking", "machinery", "textiles"],
        "key_exports": ["gold", "diamonds", "platinum", "vehicles", "iron_ore"],
        "key_imports": ["machinery", "petroleum_products", "chemicals", "food", "scientific_instruments"],
        "key_trade_partners": ["CHN", "USA", "DEU", "GBR", "IND"],
        "trade_agreements": ["Southern African Development Community", "African Continental Free Trade Area"],
        "diplomatic_incidents": [
            {"year": 2018, "type": "cooperative", "description": "BRICS summit hosting"},
            {"year": 2022, "type": "cooperative", "description": "African Continental Free Trade implementation"},
            {"year": 2023, "type": "cooperative", "description": "BRICS expansion support"}
        ],
        "trade_policy_description": "Balance between export-oriented resource sectors and protection for manufacturing. Regional trade hub for Southern Africa with growing integration into African continental markets. Strategic BRICS participation.",
        "historical_context": "Post-apartheid economic integration with emphasis on inclusive development",
        "resource_dependency": "Major mineral exporter but dependent on oil imports",
        "decision_making_structure": "Democratic system with significant labor union influence",
        "cultural_trade_factors": "Regional gateway role for sub-Saharan Africa",
        "crisis_response_pattern": "Tends to seek consensus-based solutions through regional bodies",
        "technology_policy": 0.6,
        "monetary_policy_stance": "Independent central bank with inflation targeting framework",
        "environmental_policy": 0.5,
        "labor_market_flexibility": 0.3,
        "corruption_index": 0.6,
        "geopolitical_alignment": 0.6,
        "sanctions_resilience": 0.5,
        "state_enterprise_dominance": 0.6,
        "regional_leadership_role": 0.7,
        "resource_nationalism": 0.6,
        "inequality_index": 0.9
    },
    
    # Additional Central Asian Countries
    "KAZ": {
        "name": "Kazakhstan",
        "government_type": "presidential_republic",
        "economic_system": "mixed",
        "region": "Central Asia",
        "exports_percent_gdp": 37.5,
        "imports_percent_gdp": 30.2,
        "research_percent_gdp": 0.1,
        "debt_to_gdp": 26.3,
        "key_industries": ["oil_gas", "mining", "agriculture", "metallurgy", "construction"],
        "key_exports": ["oil", "natural_gas", "metals", "minerals", "grain"],
        "key_imports": ["machinery", "equipment", "chemicals", "food", "consumer_goods"],
        "key_trade_partners": ["CHN", "RUS", "ITA", "NLD", "FRA"],
        "trade_agreements": ["Eurasian Economic Union", "CIS Free Trade Area"],
        "diplomatic_incidents": [
            {"year": 2021, "type": "cooperative", "description": "Expanded economic cooperation with China"},
            {"year": 2022, "type": "cooperative", "description": "Strengthened ties within Eurasian Economic Union"},
            {"year": 2023, "type": "cooperative", "description": "Multi-vector diplomacy initiatives"}
        ],
        "trade_policy_description": "Resource export-focused with strategic diversification efforts. Balances economic ties between Russia, China, and Western partners. Pursuing modernization through foreign investment while protecting strategic sectors.",
        "historical_context": "Post-Soviet transition to market economy with significant state role in strategic resources",
        "resource_dependency": "Heavily dependent on hydrocarbon and mineral exports",
        "decision_making_structure": "Centralized with significant presidential power",
        "cultural_trade_factors": "Strategic location for Eurasian land trade routes",
        "crisis_response_pattern": "Pragmatic management of resource revenues during economic volatility",
        "technology_policy": "Increasing focus on diversification and modernization",
        "monetary_policy_stance": "Managed float with periodic interventions to maintain stability",
        "environmental_policy": "Growing renewable energy focus despite fossil fuel dominance",
        "labor_market_flexibility": 0.5,
        "corruption_index": 0.7,
        "geopolitical_alignment": 0.6,
        "sanctions_resilience": 0.6,
        "state_enterprise_dominance": 0.7,
        "regional_leadership_role": 0.7,
        "resource_nationalism": 0.7
    },
    
    "UZB": {
        "name": "Uzbekistan",
        "government_type": "presidential_republic",
        "economic_system": "mixed",
        "region": "Central Asia",
        "exports_percent_gdp": 30.1,
        "imports_percent_gdp": 38.6,
        "research_percent_gdp": 0.2,
        "debt_to_gdp": 40.4,
        "key_industries": ["cotton", "mining", "agriculture", "textiles", "automotive"],
        "key_exports": ["cotton", "gold", "natural_gas", "textiles", "food"],
        "key_imports": ["machinery", "equipment", "foodstuffs", "chemicals", "metals"],
        "key_trade_partners": ["RUS", "CHN", "KAZ", "TUR", "KOR"],
        "trade_agreements": ["CIS Free Trade Area"],
        "diplomatic_incidents": [
            {"year": 2019, "type": "cooperative", "description": "Economic liberalization reforms"},
            {"year": 2022, "type": "cooperative", "description": "Infrastructure and energy cooperation with Russia"},
            {"year": 2023, "type": "cooperative", "description": "Expanded trade cooperation with China"}
        ],
        "trade_policy_description": "Gradual liberalization of previously closed economy. Moving away from import substitution and currency controls toward more open trade. Balancing regional integration with new global partnerships.",
        "historical_context": "Transition from Soviet-era cotton monoculture to diversified economic development",
        "resource_dependency": "Agricultural exports and growing natural gas export focus",
        "decision_making_structure": "Centralized with economic reform agenda",
        "cultural_trade_factors": "Historical Silk Road trade hub with renewed emphasis on connectivity",
        "crisis_response_pattern": "Increasing economic resilience through diversification",
        "technology_policy": "Modernization of industrial base and digital infrastructure",
        "monetary_policy_stance": "Market-oriented reforms to previously restrictive policies",
        "environmental_policy": "Addressing Aral Sea crisis while balancing development needs",
        "labor_market_flexibility": 0.4,
        "corruption_index": 0.7,
        "geopolitical_alignment": 0.6,
        "sanctions_resilience": 0.5,
        "state_enterprise_dominance": 0.7,
        "regional_leadership_role": 0.5,
        "resource_nationalism": 0.6
    },
    
    # Additional Latin American Countries
    "CHL": {
        "name": "Chile",
        "government_type": "presidential_republic",
        "economic_system": "market",
        "region": "South America",
        "exports_percent_gdp": 28.2,
        "imports_percent_gdp": 26.7,
        "research_percent_gdp": 0.4,
        "debt_to_gdp": 36.3,
        "key_industries": ["mining", "forestry", "agriculture", "fisheries", "manufacturing"],
        "key_exports": ["copper", "lithium", "fruits", "wine", "fish_products"],
        "key_imports": ["machinery", "vehicles", "electronics", "petroleum", "natural_gas"],
        "key_trade_partners": ["CHN", "USA", "BRA", "JPN", "ARG"],
        "trade_agreements": ["CPTPP", "Pacific Alliance", "numerous bilateral FTAs"],
        "diplomatic_incidents": [
            {"year": 2019, "type": "cooperative", "description": "CPTPP implementation"},
            {"year": 2021, "type": "cooperative", "description": "Expansion of renewable energy partnerships"},
            {"year": 2023, "type": "cooperative", "description": "Pacific Alliance strengthening"}
        ],
        "trade_policy_description": "Highly open free-market oriented economy with extensive network of trade agreements. Strong commodity export focus (particularly copper and lithium) with value-added diversification efforts. Pioneer of liberal trade policies in Latin America.",
        "historical_context": "Shifted from import substitution to open export economy under reforms since 1970s",
        "resource_dependency": "Heavy reliance on copper and mineral exports but with growing diversification",
        "decision_making_structure": "Stable democratic system with strong institutions",
        "cultural_trade_factors": "Market-oriented development model within Latin America",
        "crisis_response_pattern": "Countercyclical fiscal policy through sovereign wealth mechanisms",
        "technology_policy": "Growing focus on renewable energy and clean mining technologies",
        "monetary_policy_stance": "Independent central bank with inflation targeting framework",
        "environmental_policy": "Increasing renewable energy focus with climate commitments",
        "labor_market_flexibility": 0.7,
        "corruption_index": 0.3,
        "geopolitical_alignment": 0.4,
        "sanctions_resilience": 0.6,
        "state_enterprise_dominance": 0.3,
        "regional_leadership_role": 0.6,
        "resource_nationalism": 0.5
    },
    
    "COL": {
        "name": "Colombia",
        "government_type": "presidential_republic",
        "economic_system": "mixed",
        "region": "South America",
        "exports_percent_gdp": 14.8,
        "imports_percent_gdp": 18.6,
        "research_percent_gdp": 0.3,
        "debt_to_gdp": 61.4,
        "key_industries": ["oil", "mining", "agriculture", "food_processing", "textiles"],
        "key_exports": ["oil", "coal", "coffee", "flowers", "gold"],
        "key_imports": ["machinery", "equipment", "chemicals", "transport_equipment", "consumer_goods"],
        "key_trade_partners": ["USA", "CHN", "MEX", "BRA", "PAN"],
        "trade_agreements": ["Pacific Alliance", "Andean Community", "US-Colombia FTA"],
        "diplomatic_incidents": [
            {"year": 2020, "type": "cooperative", "description": "Pacific Alliance integration initiatives"},
            {"year": 2022, "type": "aggressive", "description": "Border tensions affecting Venezuela trade"},
            {"year": 2023, "type": "cooperative", "description": "Agricultural export diversification"}
        ],
        "trade_policy_description": "Export-oriented with focus on commodities but pursuing diversification. Balance between free trade orientation and protection for sensitive agricultural sectors. Strategic US trade relationship alongside growing Asia-Pacific integration.",
        "historical_context": "Gradual economic liberalization since 1990s with persistent internal conflict impacts",
        "resource_dependency": "Significant reliance on oil and minerals for export revenue",
        "decision_making_structure": "Democratic system with regional inequalities",
        "cultural_trade_factors": "Growing service exports and creative industries",
        "crisis_response_pattern": "Resilient management of commodity price volatility",
        "technology_policy": "Digital economy growth focus with tech entrepreneurship hubs",
        "monetary_policy_stance": "Independent central bank with inflation targeting",
        "environmental_policy": "Balancing extractive industries with biodiversity protection",
        "labor_market_flexibility": 0.5,
        "corruption_index": 0.6,
        "geopolitical_alignment": 0.3,
        "sanctions_resilience": 0.5,
        "state_enterprise_dominance": 0.4,
        "regional_leadership_role": 0.5,
        "resource_nationalism": 0.5
    },
    
    # Additional African Countries
    "GHA": {
        "name": "Ghana",
        "government_type": "presidential_republic",
        "economic_system": "mixed",
        "region": "Africa",
        "exports_percent_gdp": 35.0,
        "imports_percent_gdp": 33.8,
        "research_percent_gdp": 0.4,
        "debt_to_gdp": 83.5,
        "key_industries": ["gold_mining", "oil", "agriculture", "services", "manufacturing"],
        "key_exports": ["gold", "oil", "cocoa", "timber", "tuna"],
        "key_imports": ["capital_equipment", "petroleum", "foodstuffs", "consumer_goods"],
        "key_trade_partners": ["CHN", "USA", "IND", "ZAF", "GBR"],
        "trade_agreements": ["African Continental Free Trade Area", "ECOWAS"],
        "diplomatic_incidents": [
            {"year": 2020, "type": "cooperative", "description": "AfCFTA headquarters establishment"},
            {"year": 2022, "type": "cooperative", "description": "Digital trade initiatives"},
            {"year": 2023, "type": "cooperative", "description": "Financial service exports expansion"}
        ],
        "trade_policy_description": "Relatively open trade regime with focus on commodity exports and growing services. African Continental Free Trade Area hub with emphasis on regional integration. Balancing export promotion with industrial development goals.",
        "historical_context": "Political stability supporting steady economic reforms since 1990s",
        "resource_dependency": "Significant gold and cocoa exports with growing oil sector",
        "decision_making_structure": "Democratic system with traditional authorities' influence",
        "cultural_trade_factors": "English-speaking advantage in services trade",
        "crisis_response_pattern": "Increasing fiscal resilience despite commodity dependence",
        "technology_policy": "Digital infrastructure development focus",
        "monetary_policy_stance": "Independent central bank managing cedi volatility",
        "environmental_policy": "Addressing mining impacts while pursuing sustainable growth",
        "labor_market_flexibility": 0.5,
        "corruption_index": 0.5,
        "geopolitical_alignment": 0.5,
        "sanctions_resilience": 0.5,
        "state_enterprise_dominance": 0.5,
        "regional_leadership_role": 0.7,
        "resource_nationalism": 0.5
    },
    
    "ETH": {
        "name": "Ethiopia",
        "government_type": "federal_parliamentary_republic",
        "economic_system": "mixed",
        "region": "Africa",
        "exports_percent_gdp": 7.9,
        "imports_percent_gdp": 18.2,
        "research_percent_gdp": 0.3,
        "debt_to_gdp": 57.4,
        "key_industries": ["agriculture", "textiles", "food_processing", "construction", "mining"],
        "key_exports": ["coffee", "oilseeds", "vegetables", "gold", "flowers"],
        "key_imports": ["machinery", "petroleum_products", "motor_vehicles", "cereals", "textiles"],
        "key_trade_partners": ["CHN", "USA", "SAU", "IND", "KOR"],
        "trade_agreements": ["African Continental Free Trade Area", "COMESA"],
        "diplomatic_incidents": [
            {"year": 2019, "type": "cooperative", "description": "Industrial parks development with Chinese investment"},
            {"year": 2021, "type": "aggressive", "description": "Regional tensions affecting trade corridors"},
            {"year": 2023, "type": "cooperative", "description": "Economic reform initiatives"}
        ],
        "trade_policy_description": "Historically state-directed economy with gradual market opening and industrialization focus. Investment-led growth model with strategic sectors development. Balancing agricultural exports with manufacturing development plans.",
        "historical_context": "Developmental state model pursuing rapid industrialization from agricultural base",
        "resource_dependency": "Agricultural export focus with growing manufacturing ambitions",
        "decision_making_structure": "Centralized development planning with regional federal system",
        "cultural_trade_factors": "Regional economic hub with ancient trade connections",
        "crisis_response_pattern": "Resilient despite external shocks and internal challenges",
        "technology_policy": "Growing tech sector with digitalization initiatives",
        "monetary_policy_stance": "State-directed with gradual liberalization",
        "environmental_policy": "Green economy strategy with climate resilience focus",
        "labor_market_flexibility": 0.4,
        "corruption_index": 0.6,
        "geopolitical_alignment": 0.5,
        "sanctions_resilience": 0.6,
        "state_enterprise_dominance": 0.7,
        "regional_leadership_role": 0.8,
        "resource_nationalism": 0.6
    }
}

def get_country_profile(country_iso: str) -> CountryProfile:
    """
    Get a CountryProfile object for the specified country ISO code.
    
    Args:
        country_iso: ISO code for the country (3-letter code)
        
    Returns:
        CountryProfile object with realistic traits for the specified country
    """
    if country_iso not in COUNTRY_PROFILES:
        # Return a random profile for countries not in our database
        return CountryProfile.generate_random()
    
    # Generate a profile based on the country data
    return CountryProfile.generate_from_country_data(COUNTRY_PROFILES[country_iso])

def get_all_countries() -> List[str]:
    """
    Get a list of all available country ISO codes.
    
    Returns:
        List of country ISO codes
    """
    return list(COUNTRY_PROFILES.keys())

def get_country_data(country_iso: str) -> Dict[str, Any]:
    """
    Get raw data for a country by ISO code.
    
    Args:
        country_iso: ISO code for the country
        
    Returns:
        Dictionary containing country data or empty dict if not found
    """
    return COUNTRY_PROFILES.get(country_iso, {})

def get_country_description(country_iso: str) -> str:
    """
    Get a human-readable description of a country's economic and trade characteristics.
    
    Args:
        country_iso: ISO code for the country
        
    Returns:
        String with description of the country
    """
    if country_iso not in COUNTRY_PROFILES:
        return f"No detailed information available for {country_iso}."
    
    country = COUNTRY_PROFILES[country_iso]
    
    description = f"{country['name']} ({country_iso})\n"
    description += f"Government: {country['government_type'].replace('_', ' ').title()}\n"
    description += f"Economic System: {country['economic_system'].replace('_', ' ').title()}\n"
    description += f"Region: {country['region']}\n\n"
    
    description += f"Economic Profile:\n"
    description += f"- Exports: {country['exports_percent_gdp']}% of GDP\n"
    description += f"- Imports: {country['imports_percent_gdp']}% of GDP\n"
    description += f"- R&D Spending: {country['research_percent_gdp']}% of GDP\n"
    description += f"- Debt to GDP: {country['debt_to_gdp']}%\n\n"
    
    description += f"Key Industries: {', '.join(industry.replace('_', ' ').title() for industry in country['key_industries'])}\n"
    description += f"Key Exports: {', '.join(export.replace('_', ' ').title() for export in country['key_exports'])}\n"
    description += f"Key Imports: {', '.join(import_item.replace('_', ' ').title() for import_item in country['key_imports'])}\n"
    description += f"Main Trading Partners: {', '.join(country['key_trade_partners'])}\n\n"
    
    # Add historical context from the enhanced profile
    if 'historical_context' in country:
        description += f"Historical Context: {country['historical_context']}\n"
    
    # Add resource dependency from the enhanced profile
    if 'resource_dependency' in country:
        description += f"Resource Dependency: {country['resource_dependency']}\n\n"
    
    description += f"Trade Policy: {country['trade_policy_description']}"
    
    return description

def get_regional_groups() -> Dict[str, List[str]]:
    """
    Get countries grouped by geographic region.
    
    Returns:
        Dictionary mapping regions to lists of country ISO codes
    """
    regions = {}
    
    for iso, data in COUNTRY_PROFILES.items():
        region = data.get('region', 'Other')
        if region not in regions:
            regions[region] = []
        regions[region].append(iso)
    
    return regions

def get_trading_blocs() -> Dict[str, List[str]]:
    """
    Get major trading blocs and their members.
    
    Returns:
        Dictionary mapping bloc names to lists of member country ISO codes
    """
    blocs = {
        "EU": [],
        "USMCA": [],
        "RCEP": [],
        "Mercosur": [],
        "GCC": [],
        "BRICS": [],
        "EEU": [],  # Eurasian Economic Union
        "ASEAN": [],
        "AfCFTA": [],  # African Continental Free Trade Area
    }
    
    # Populate blocs based on country data
    for iso, data in COUNTRY_PROFILES.items():
        agreements = data.get('trade_agreements', [])
        
        if "EU" in agreements or "European Union" in agreements:
            blocs["EU"].append(iso)
        
        if "USMCA" in agreements:
            blocs["USMCA"].append(iso)
            
        if "RCEP" in agreements:
            blocs["RCEP"].append(iso)
            
        if "Mercosur" in agreements:
            blocs["Mercosur"].append(iso)
            
        if "GCC" in agreements or "GCC Customs Union" in agreements:
            blocs["GCC"].append(iso)
            
        if "ASEAN" in agreements:
            blocs["ASEAN"].append(iso)
            
        if "African Continental Free Trade Area" in agreements:
            blocs["AfCFTA"].append(iso)
            
        if "Eurasian Economic Union" in agreements:
            blocs["EEU"].append(iso)
    
    # Manually add BRICS members
    blocs["BRICS"] = ["BRA", "RUS", "IND", "CHN", "ZAF"]
    
    # Remove empty blocs
    return {k: v for k, v in blocs.items() if v}

# Example usage
if __name__ == "__main__":
    # Generate a profile for the US
    us_profile = get_country_profile("USA")
    
    # Get the profile description
    print(us_profile.get_description())
    
    # Get detailed country data
    print(get_country_description("USA"))