from flask import Blueprint, jsonify, request
from models import Game, Country
from engine import get_game
import uuid

diplomacy_bp = Blueprint('diplomacy', __name__)

@diplomacy_bp.route('/relations/<iso_code>', methods=['GET'])
def get_relations(iso_code):
    """Hent diplomatiske relationer for et specifikt land"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    country = game.get_country(iso_code)
    if not country:
        return jsonify({"error": f"Land med ISO kode {iso_code} ikke fundet"}), 404
    
    # Hent alle relationer, hvor det angivne land er involveret
    relations = []
    for relation in game.diplomacy.relations:
        if relation.country_a == iso_code or relation.country_b == iso_code:
            # Hvis det er landets egen relation, så kan vi returnere den direkte
            other_iso = relation.country_b if relation.country_a == iso_code else relation.country_a
            other_country = game.get_country(other_iso)
            
            if other_country:
                relations.append({
                    "iso_code": other_iso,
                    "country_name": other_country.name,
                    "relation_level": relation.relation_level,
                    "trade_agreement": relation.trade_agreement,
                    "alliance": relation.alliance,
                    "state_of_war": relation.state_of_war
                })
    
    return jsonify({
        "country": iso_code,
        "relations": relations
    })

@diplomacy_bp.route('/relations', methods=['GET'])
def get_all_relations():
    """Hent alle diplomatiske relationer"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    # Formatér relations data for frontend
    relations_data = []
    for relation in game.diplomacy.relations:
        country_a = game.get_country(relation.country_a)
        country_b = game.get_country(relation.country_b)
        
        if country_a and country_b:
            relations_data.append({
                "country_a": relation.country_a,
                "country_a_name": country_a.name,
                "country_b": relation.country_b,
                "country_b_name": country_b.name,
                "relation_level": relation.relation_level,
                "trade_agreement": relation.trade_agreement,
                "alliance": relation.alliance,
                "state_of_war": relation.state_of_war
            })
    
    return jsonify({
        "relations": relations_data
    })

@diplomacy_bp.route('/actions/propose_trade', methods=['POST'])
def propose_trade_action():
    """Foreslå en handelsaftale med et andet land"""
    game = get_game()
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    data = request.json
    player_iso = data.get('player_iso')
    target_iso = data.get('target_iso')
    offer_terms = data.get('offer_terms', {})
    
    if not player_iso or not target_iso:
        return jsonify({"error": "Manglende lande-ISO koder"}), 400
    
    # Tjek om landene eksisterer
    player_country = game.get_country(player_iso)
    target_country = game.get_country(target_iso)
    
    if not player_country or not target_country:
        return jsonify({"error": "Et eller begge lande findes ikke"}), 404
    
    # Simulér AI beslutning om at acceptere baseret på relationer og fordele
    response = game.diplomacy.propose_trade_agreement(player_iso, target_iso, offer_terms)
    
    if response.get('accepted'):
        return jsonify({
            "success": True,
            "message": f"{target_country.name} har accepteret dit handelstilbud!",
            "relation_change": response.get('relation_change', 0)
        })
    else:
        return jsonify({
            "success": False,
            "message": f"{target_country.name} afslog dit handelstilbud.",
            "reason": response.get('reason', 'Ukendt årsag'),
            "relation_change": response.get('relation_change', 0)
        })

@diplomacy_bp.route('/actions/propose_alliance', methods=['POST'])
def propose_alliance_action():
    """Foreslå en alliance med et andet land"""
    game = get_game()
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    data = request.json
    player_iso = data.get('player_iso')
    target_iso = data.get('target_iso')
    
    if not player_iso or not target_iso:
        return jsonify({"error": "Manglende lande-ISO koder"}), 400
    
    # Tjek om landene eksisterer
    player_country = game.get_country(player_iso)
    target_country = game.get_country(target_iso)
    
    if not player_country or not target_country:
        return jsonify({"error": "Et eller begge lande findes ikke"}), 404
    
    # Simulér AI beslutning om at acceptere alliancen
    response = game.diplomacy.propose_alliance(player_iso, target_iso)
    
    if response.get('accepted'):
        return jsonify({
            "success": True,
            "message": f"{target_country.name} har accepteret din alliance!",
            "relation_change": response.get('relation_change', 0)
        })
    else:
        return jsonify({
            "success": False,
            "message": f"{target_country.name} afslog din alliance.",
            "reason": response.get('reason', 'Ukendt årsag'),
            "relation_change": response.get('relation_change', 0)
        })

@diplomacy_bp.route('/trade_partners/<iso_code>', methods=['GET'])
def get_trade_partners(iso_code):
    """Hent handelspartnere for et specifikt land"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    country = game.get_country(iso_code)
    if not country:
        return jsonify({"error": f"Land med ISO kode {iso_code} ikke fundet"}), 404
    
    # Beregn handelspartnere baseret på relationsniveau og landestørrelse
    partners = []
    for other_country in game.countries.values():
        if other_country.iso_code == iso_code:
            continue
            
        # Find relation mellem landene
        relation = game.diplomacy.get_relation(iso_code, other_country.iso_code)
        relation_level = relation.relation_level if relation else 0
        
        # Beregn handelsvolumen baseret på relationer, BNP og andre faktorer
        trading_factor = (relation_level + 5) / 10  # Skala 0.5 til 1.0
        size_factor = (other_country.gdp / (country.gdp or 1)) ** 0.5
        
        import_volume = other_country.gdp * 0.03 * trading_factor * size_factor
        export_volume = country.gdp * 0.025 * trading_factor * size_factor
        
        # Hvis der er en handelsaftale, boost handelsvolumen
        has_trade_agreement = relation.trade_agreement if relation else False
        if has_trade_agreement:
            import_volume *= 1.5
            export_volume *= 1.5
        
        # Tilfældigt udsving for at gøre det mere realistisk
        import_variance = 0.7 + (hash(f"{country.iso_code}_{other_country.iso_code}_import") % 100) / 100.0
        export_variance = 0.7 + (hash(f"{country.iso_code}_{other_country.iso_code}_export") % 100) / 100.0
        
        import_volume *= import_variance
        export_volume *= export_variance
        
        # Beregn trade_volume, trade_balance og dependency_score
        trade_volume = import_volume + export_volume
        trade_balance = export_volume - import_volume
        dependency_score = trade_volume / (country.gdp or 1)
        
        partners.append({
            "country": {
                "iso_code": other_country.iso_code,
                "name": other_country.name,
                "gdp": other_country.gdp
            },
            "importVolume": import_volume,
            "exportVolume": export_volume,
            "tradeVolume": trade_volume,
            "tradeBalance": trade_balance,
            "dependencyScore": dependency_score,
            "isCritical": dependency_score > 0.05,
            "hasTradeDeal": has_trade_agreement
        })
    
    # Sortér efter handelsvolumen
    partners.sort(key=lambda x: x['tradeVolume'], reverse=True)
    
    return jsonify({
        "country": iso_code,
        "partners": partners[:10]  # Top 10 handelspartnere
    })

@diplomacy_bp.route('/competitors/<iso_code>', methods=['GET'])
def get_competitors(iso_code):
    """Hent konkurrenter for et specifikt land"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    country = game.get_country(iso_code)
    if not country:
        return jsonify({"error": f"Land med ISO kode {iso_code} ikke fundet"}), 404
    
    # Find konkurrenter baseret på industrisammensætning
    competitors = []
    for other_country in game.countries.values():
        if other_country.iso_code == iso_code:
            continue
            
        # Beregn industrioverlap
        industry_overlap = 0
        
        # Hvis begge lande har industridata
        if hasattr(country, 'industries') and hasattr(other_country, 'industries'):
            common_industries = set(country.industries.keys()) & set(other_country.industries.keys())
            
            for industry in common_industries:
                # Jo tættere industriværdierne er på hinanden, jo større overlap
                overlap_value = min(country.industries[industry], other_country.industries[industry])
                industry_overlap += overlap_value
        else:
            # Hvis ingen industridata, brug BNP-forskel som proxy
            gdp_ratio = min(other_country.gdp or 10, country.gdp or 10) / max(other_country.gdp or 10, country.gdp or 10)
            industry_overlap = gdp_ratio * 0.5
        
        # Konkurrenceintensitet baseret på overlap og BNP
        competition_intensity = industry_overlap * min(1, (other_country.gdp or 10) / (country.gdp or 10))
        
        # Tilføj konkurrent, hvis der er et betydeligt overlap
        if industry_overlap > 0.05:
            competitors.append({
                "country": {
                    "iso_code": other_country.iso_code,
                    "name": other_country.name,
                    "gdp": other_country.gdp
                },
                "overlapScore": industry_overlap,
                "competitionIntensity": competition_intensity,
                "mainIndustries": other_country.industries if hasattr(other_country, 'industries') else {
                    "Landbrug": 0.2,
                    "Industri": 0.3,
                    "Service": 0.5
                }
            })
    
    # Sortér efter konkurrenceintensitet
    competitors.sort(key=lambda x: x['competitionIntensity'], reverse=True)
    
    return jsonify({
        "country": iso_code,
        "competitors": competitors[:5]  # Top 5 konkurrenter
    })

@diplomacy_bp.route('/alliances', methods=['GET'])
def get_alliances():
    """Hent alle eksisterende alliancer i verden"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    # Formatér alliances data for frontend
    alliances_data = []
    
    if hasattr(game.diplomacy, 'alliances'):
        for alliance in game.diplomacy.alliances:
            # Konverter ISO koder til landenavne
            member_names = []
            for iso in alliance.members:
                country = game.get_country(iso)
                member_names.append({
                    "iso": iso,
                    "name": country.name if country else iso
                })
            
            alliances_data.append({
                "id": alliance.id,
                "name": alliance.name,
                "type": alliance.type,
                "members": alliance.members,
                "member_names": member_names,
                "date_formed": alliance.date_formed,
                "benefits": alliance.benefits,
                "terms": alliance.terms
            })
    else:
        # Eksempel alliancer (hvis spillet endnu ikke har alliances implementeret)
        alliances_data = [
            {
                "id": "nato",
                "name": "NATO",
                "type": "Militær",
                "members": ["USA", "GBR", "DEU", "FRA", "ITA", "CAN"],
                "member_names": [
                    {"iso": "USA", "name": "USA"},
                    {"iso": "GBR", "name": "Storbritannien"},
                    {"iso": "DEU", "name": "Tyskland"},
                    {"iso": "FRA", "name": "Frankrig"},
                    {"iso": "ITA", "name": "Italien"},
                    {"iso": "CAN", "name": "Canada"}
                ],
                "date_formed": "1949-04-04",
                "benefits": "Mutual defense, military cooperation",
                "terms": "An attack on one member is considered an attack on all members"
            },
            {
                "id": "eu",
                "name": "European Union",
                "type": "Økonomisk",
                "members": ["DEU", "FRA", "ITA", "ESP", "BEL", "NLD"],
                "member_names": [
                    {"iso": "DEU", "name": "Tyskland"},
                    {"iso": "FRA", "name": "Frankrig"},
                    {"iso": "ITA", "name": "Italien"},
                    {"iso": "ESP", "name": "Spanien"},
                    {"iso": "BEL", "name": "Belgien"},
                    {"iso": "NLD", "name": "Holland"}
                ],
                "date_formed": "1993-11-01",
                "benefits": "Common market, free movement, trade agreements",
                "terms": "Economic and political cooperation"
            },
            {
                "id": "ausfta",
                "name": "Australia-USA Free Trade Agreement",
                "type": "Handelsaftale",
                "members": ["USA", "AUS"],
                "member_names": [
                    {"iso": "USA", "name": "USA"},
                    {"iso": "AUS", "name": "Australien"}
                ],
                "date_formed": "2005-01-01",
                "benefits": "Reduced tariffs, increased trade",
                "terms": "Elimination of most tariffs on goods"
            }
        ]
    
    return jsonify({
        "alliances": alliances_data
    })

@diplomacy_bp.route('/trade/<iso_code>', methods=['GET'])
def get_trade_dependencies(iso_code):
    """Hent handelsafhængighed for et specifikt land"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    country = game.get_country(iso_code)
    if not country:
        return jsonify({"error": f"Land med ISO kode {iso_code} ikke fundet"}), 404
    
    # Beregn handelsafhængighed baseret på relationer, BNP og andre faktorer
    dependencies = []
    total_import = 0
    total_export = 0
    
    for other_country in game.countries.values():
        if other_country.iso_code == iso_code:
            continue
            
        # Find relation mellem landene
        relation = game.diplomacy.get_relation(iso_code, other_country.iso_code)
        relation_level = relation.relation_level if relation else 0
        
        # Beregn handelsvolumen baseret på relationer, BNP og andre faktorer
        trade_level = (relation_level + 1) / 2  # Skala 0 til 1
        
        # Brug BNP til at beregne handel
        country_gdp = country.gdp or 1000  # Undgå division med nul
        other_gdp = other_country.gdp or 1000
        
        # Beregn import og eksport baseret på BNP og relationer
        import_volume = other_gdp * 0.02 * trade_level * (hash(f"{iso_code}_{other_country.iso_code}_import") % 100 + 50) / 100
        export_volume = country_gdp * 0.025 * trade_level * (hash(f"{iso_code}_{other_country.iso_code}_export") % 100 + 50) / 100
        
        # Hvis der er en handelsaftale, boost handelsvolumen
        has_trade_agreement = relation.trade_agreement if relation else False
        if has_trade_agreement:
            import_volume *= 1.5
            export_volume *= 1.7
        
        # Beregn trade_volume og dependency_level
        trade_volume = import_volume + export_volume
        dependency_level = trade_volume / country_gdp
        
        total_import += import_volume
        total_export += export_volume
        
        dependencies.append({
            "iso": other_country.iso_code,
            "name": other_country.name,
            "import": import_volume,
            "export": export_volume,
            "volume": trade_volume,
            "level": dependency_level,
            "isCritical": dependency_level > 0.05,
            "hasTradeDeal": has_trade_agreement
        })
    
    # Sortér efter handelsvolumen
    dependencies.sort(key=lambda x: x['volume'], reverse=True)
    
    return jsonify({
        "country": iso_code,
        "totalImport": total_import,
        "totalExport": total_export,
        "balance": total_export - total_import,
        "dependencies": dependencies[:15]  # Top 15 handelspartnere
    })

@diplomacy_bp.route('/agreements', methods=['GET'])
def get_trade_agreements():
    """Hent alle handelsaftaler i verden"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    # Formatér agreements data for frontend
    agreements_data = []
    
    if hasattr(game.diplomacy, 'trade_agreements'):
        for agreement in game.diplomacy.trade_agreements:
            # Konverter ISO koder til landenavne
            parties_names = []
            for iso in agreement.parties:
                country = game.get_country(iso)
                parties_names.append({
                    "iso": iso,
                    "name": country.name if country else iso
                })
            
            agreements_data.append({
                "id": agreement.id,
                "name": agreement.name,
                "type": agreement.type,
                "parties": agreement.parties,
                "party_names": parties_names,
                "terms": agreement.terms,
                "benefit": agreement.benefit,
                "date_formed": agreement.date_formed,
                "duration": agreement.duration,
                "isProposed": agreement.is_proposed if hasattr(agreement, 'is_proposed') else False
            })
    else:
        # Eksempel handelsaftaler
        agreements_data = [
            {
                "id": "usa-mex-trade-1",
                "name": "USA-Mexico Handelsaftale",
                "type": "FTA",
                "parties": ["USA", "MEX"],
                "party_names": [
                    {"iso": "USA", "name": "USA"},
                    {"iso": "MEX", "name": "Mexico"}
                ],
                "terms": "Reducerede toldsatser på industrivarer",
                "benefit": "+15% handelsvolumen",
                "date_formed": "2020-07-01",
                "duration": "10 år",
                "isProposed": False
            },
            {
                "id": "eu-jpn-trade-1",
                "name": "EU-Japan Økonomisk Partnerskab",
                "type": "EPA",
                "parties": ["EU", "JPN"],
                "party_names": [
                    {"iso": "EU", "name": "European Union"},
                    {"iso": "JPN", "name": "Japan"}
                ],
                "terms": "Fjernelse af told på 97% af varer",
                "benefit": "+20% handelsvolumen, øget BNP",
                "date_formed": "2019-02-01",
                "duration": "Ubegrænset",
                "isProposed": False
            }
        ]
    
    return jsonify({
        "agreements": agreements_data
    })

@diplomacy_bp.route('/agreements/<iso_code>', methods=['GET'])
def get_country_agreements(iso_code):
    """Hent handelsaftaler for et specifikt land"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    country = game.get_country(iso_code)
    if not country:
        return jsonify({"error": f"Land med ISO kode {iso_code} ikke fundet"}), 404
    
    # Hent alle handelsaftaler og filtrer efter det angivne land
    all_agreements_response = get_trade_agreements()
    all_agreements = all_agreements_response.json['agreements']
    
    # Filtrer efter aftaler, der involverer det angivne land
    country_agreements = [
        agreement for agreement in all_agreements
        if iso_code in agreement['parties']
    ]
    
    # Opdel i aktive og foreslåede aftaler
    active_agreements = [agreement for agreement in country_agreements if not agreement['isProposed']]
    proposed_agreements = [agreement for agreement in country_agreements if agreement['isProposed']]
    
    return jsonify({
        "country": iso_code,
        "activeAgreements": active_agreements,
        "proposedAgreements": proposed_agreements
    })

@diplomacy_bp.route('/propose_agreement', methods=['POST'])
def propose_agreement():
    """Foreslå en ny handelsaftale"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    data = request.json
    proposer_iso = data.get('proposer_iso')
    target_iso = data.get('target_iso')
    agreement_type = data.get('type', 'FTA')
    terms = data.get('terms', 'Reducerede toldsatser')
    
    if not proposer_iso or not target_iso:
        return jsonify({"error": "Manglende lande-ISO koder"}), 400
    
    # Tjek om landene eksisterer
    proposer_country = game.get_country(proposer_iso)
    target_country = game.get_country(target_iso)
    
    if not proposer_country or not target_country:
        return jsonify({"error": "Et eller begge lande findes ikke"}), 404
    
    # Opret nyt forslag og simulér AI svar
    # (I en rigtig implementering ville det her gå gennem spillogikken)
    proposed_agreement = {
        "id": f"{proposer_iso}-{target_iso}-{hash(str(data)) % 1000}",
        "name": f"Handelsaftale mellem {proposer_country.name} og {target_country.name}",
        "type": agreement_type,
        "parties": [proposer_iso, target_iso],
        "terms": terms,
        "benefit": "Forventede økonomiske fordele for begge parter",
        "isProposed": True
    }
    
    # Simulér AI beslutning baseret på relation
    relation = game.diplomacy.get_relation(proposer_iso, target_iso)
    relation_level = relation.relation_level if relation else 0
    
    acceptance_chance = (relation_level + 1) / 2  # Konverter fra -1,1 til 0,1
    import random
    accepted = random.random() < acceptance_chance
    
    if accepted:
        return jsonify({
            "success": True,
            "message": f"{target_country.name} har accepteret dit forslag!",
            "agreement": proposed_agreement
        })
    else:
        reason = "Utilstrækkelige diplomatiske relationer"
        if relation_level < -0.3:
            reason = "Nuværende diplomatiske spændinger"
        elif random.random() < 0.3:
            reason = "Ikke fordelagtigt for vores økonomi lige nu"
        
        return jsonify({
            "success": False,
            "message": f"{target_country.name} afslog dit forslag.",
            "reason": reason,
            "agreement": proposed_agreement
        })

@diplomacy_bp.route('/actions/apply_sanctions', methods=['POST'])
def apply_sanctions():
    """Anvend økonomiske sanktioner mod et andet land"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    data = request.json
    player_iso = data.get('player_iso')
    target_iso = data.get('target_iso')
    sanction_type = data.get('sanction_type', 'moderate')  # light, moderate, severe
    
    if not player_iso or not target_iso:
        return jsonify({"error": "Manglende lande-ISO koder"}), 400
    
    # Tjek om landene eksisterer
    player_country = game.get_country(player_iso)
    target_country = game.get_country(target_iso)
    
    if not player_country or not target_country:
        return jsonify({"error": "Et eller begge lande findes ikke"}), 404
    
    # Beregn effekter på diplomati og økonomi
    relation_impact = 0
    if sanction_type == 'light':
        relation_impact = -0.1
        economic_impact = 0.02
    elif sanction_type == 'moderate':
        relation_impact = -0.25
        economic_impact = 0.05
    else:  # severe
        relation_impact = -0.4
        economic_impact = 0.1
    
    # Beregn også gensidige økonomiske konsekvenser
    # Hvor meget det skader dig selv afhænger af handelsafhængighed
    
    # Hent handelsafhængighed
    trade_response = get_trade_dependencies(player_iso)
    trade_data = trade_response.json
    
    # Find target i dependencies
    target_dependency = next(
        (dep for dep in trade_data.get('dependencies', []) if dep['iso'] == target_iso),
        None
    )
    
    self_impact = 0
    if target_dependency:
        self_impact = target_dependency['level'] * economic_impact * 0.8
    
    # Opdater relation i spillet
    relation = game.diplomacy.get_relation(player_iso, target_iso)
    if relation:
        old_level = relation.relation_level
        relation.relation_level = max(-1.0, relation.relation_level + relation_impact)
        
        # Opdater også handelsvolumen (hvis implementeret i spilmotoren)
        if hasattr(relation, 'trade_volume'):
            relation.trade_volume *= (1 - economic_impact)
    
    return jsonify({
        "success": True,
        "message": f"Sanktioner pålagt {target_country.name}",
        "effects": {
            "diplomaticImpact": relation_impact,
            "economicImpactTarget": economic_impact,
            "economicImpactSelf": self_impact,
            "relationAfter": relation.relation_level if relation else None
        },
        "warning": self_impact > 0.05,
        "warningMessage": "Disse sanktioner vil have betydelig negativ effekt på din egen økonomi" if self_impact > 0.05 else None
    })

@diplomacy_bp.route('/missions', methods=['GET'])
def get_diplomatic_missions():
    """Hent alle aktive diplomatiske missioner"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    # Formatér diplomatiske missioner data for frontend
    missions_data = []
    
    if hasattr(game.diplomacy, 'missions'):
        for mission in game.diplomacy.missions:
            source_country = game.get_country(mission.source_country)
            target_country = game.get_country(mission.target_country)
            
            if source_country and target_country:
                missions_data.append({
                    "id": mission.id,
                    "source_country": mission.source_country,
                    "source_country_name": source_country.name,
                    "target_country": mission.target_country,
                    "target_country_name": target_country.name,
                    "mission_type": mission.mission_type,
                    "start_turn": mission.start_turn,
                    "duration": mission.duration,
                    "current_progress": mission.current_progress,
                    "success_chance": mission.success_chance,
                    "status": mission.status,
                    "objectives": mission.objectives,
                    "expected_outcome": mission.expected_outcome
                })
    
    return jsonify({
        "missions": missions_data
    })

@diplomacy_bp.route('/missions/<iso_code>', methods=['GET'])
def get_country_missions(iso_code):
    """Hent alle diplomatiske missioner for et specifikt land"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    country = game.get_country(iso_code)
    if not country:
        return jsonify({"error": f"Land med ISO kode {iso_code} ikke fundet"}), 404
    
    # Hent aktive og afsluttede missioner relateret til landet
    missions_data = []
    
    if hasattr(game.diplomacy, 'missions'):
        for mission in game.diplomacy.missions:
            if mission.source_country == iso_code or mission.target_country == iso_code:
                source_country = game.get_country(mission.source_country)
                target_country = game.get_country(mission.target_country)
                
                if source_country and target_country:
                    missions_data.append({
                        "id": mission.id,
                        "source_country": mission.source_country,
                        "source_country_name": source_country.name,
                        "target_country": mission.target_country,
                        "target_country_name": target_country.name,
                        "mission_type": mission.mission_type,
                        "start_turn": mission.start_turn,
                        "duration": mission.duration,
                        "current_progress": mission.current_progress,
                        "success_chance": mission.success_chance,
                        "status": mission.status,
                        "objectives": mission.objectives,
                        "expected_outcome": mission.expected_outcome,
                        "is_source": mission.source_country == iso_code
                    })
    
    return jsonify({
        "country": iso_code,
        "missions": missions_data
    })

@diplomacy_bp.route('/missions/create', methods=['POST'])
def create_diplomatic_mission():
    """Opret en ny diplomatisk mission"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    data = request.json
    source_iso = data.get('source_iso')
    target_iso = data.get('target_iso')
    mission_type = data.get('mission_type')
    objectives = data.get('objectives', {})
    duration = data.get('duration', 3)  # Standard varighed på 3 ture
    
    if not source_iso or not target_iso or not mission_type:
        return jsonify({"error": "Manglende påkrævede parametre"}), 400
    
    # Tjek om landene eksisterer
    source_country = game.get_country(source_iso)
    target_country = game.get_country(target_iso)
    
    if not source_country or not target_country:
        return jsonify({"error": "Et eller begge lande findes ikke"}), 404
    
    # Opret missionen via diplomacy subsystemet
    mission_result = game.diplomacy.create_diplomatic_mission(
        source_iso, 
        target_iso, 
        mission_type, 
        objectives, 
        duration
    )
    
    if mission_result.get('success'):
        return jsonify({
            "success": True,
            "message": f"Diplomatisk mission til {target_country.name} er blevet igangsat.",
            "mission": mission_result.get('mission')
        })
    else:
        return jsonify({
            "success": False,
            "message": f"Kunne ikke oprette diplomatisk mission til {target_country.name}.",
            "reason": mission_result.get('reason', 'Ukendt årsag')
        })

@diplomacy_bp.route('/missions/<mission_id>/cancel', methods=['POST'])
def cancel_diplomatic_mission(mission_id):
    """Annuller en igangværende diplomatisk mission"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    # Annuller missionen via diplomacy subsystemet
    result = game.diplomacy.cancel_diplomatic_mission(mission_id)
    
    if result.get('success'):
        return jsonify({
            "success": True,
            "message": "Diplomatisk mission er blevet annulleret."
        })
    else:
        return jsonify({
            "success": False,
            "message": "Kunne ikke annullere diplomatisk mission.",
            "reason": result.get('reason', 'Ukendt årsag')
        })

@diplomacy_bp.route('/missions/types', methods=['GET'])
def get_mission_types():
    """Hent alle tilgængelige typer af diplomatiske missioner"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    # Hent missionstyperne fra diplomacy subsystemet
    mission_types = []
    
    if hasattr(game.diplomacy, 'mission_types'):
        mission_types = game.diplomacy.mission_types
    else:
        # Standard missionstyper hvis ikke implementeret endnu
        mission_types = [
            {
                "id": "trade_delegation",
                "name": "Handelsdelegation",
                "description": "Send en delegation for at forbedre handelsrelationer og åbne for nye muligheder.",
                "duration_range": [2, 4],
                "success_factors": ["relation_level", "economic_compatibility"],
                "potential_outcomes": [
                    "Forbedrede handelsrelationer", 
                    "Øget eksport/import", 
                    "Reduktion af toldsatser"
                ]
            },
            {
                "id": "cultural_exchange",
                "name": "Kulturel Udveksling",
                "description": "Promovér kulturel forståelse og diplomatiske bånd gennem kulturelle arrangementer.",
                "duration_range": [1, 3],
                "success_factors": ["relation_level", "cultural_similarity"],
                "potential_outcomes": [
                    "Forbedrede relationer", 
                    "Øget kulturel påvirkning", 
                    "Bedre offentlig opinion"
                ]
            },
            {
                "id": "intelligence_operation",
                "name": "Efterretningsoperation",
                "description": "Indsaml strategisk information og analysér mållandets intentioner og svagheder.",
                "duration_range": [3, 6],
                "success_factors": ["intelligence_capacity", "target_security_level"],
                "potential_outcomes": [
                    "Strategisk information", 
                    "Økonomiske indsigter", 
                    "Forhandlingsfordele"
                ]
            },
            {
                "id": "diplomatic_pressure",
                "name": "Diplomatisk Pres",
                "description": "Anvend diplomatisk pres for at påvirke mållandets politik eller beslutninger.",
                "duration_range": [2, 4],
                "success_factors": ["economic_power", "international_support"],
                "potential_outcomes": [
                    "Ændret politik hos målet", 
                    "Indrømmelser", 
                    "Internationalt omdømmetab"
                ]
            },
            {
                "id": "technology_transfer",
                "name": "Teknologioverførsel",
                "description": "Del teknologi eller ekspertise for at styrke bånd og skabe gensidig afhængighed.",
                "duration_range": [3, 5],
                "success_factors": ["technology_level", "relation_level"],
                "potential_outcomes": [
                    "Teknologisk samarbejde", 
                    "Industriel vækst", 
                    "Langsigtet alliance"
                ]
            }
        ]
    
    return jsonify({
        "mission_types": mission_types
    })

@diplomacy_bp.route('/missions/cancel', methods=['POST'])
def cancel_diplomatic_mission():
    """Annuller en eksisterende diplomatisk mission"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    data = request.json
    mission_id = data.get('mission_id')
    country_iso = data.get('country_iso')
    
    if not mission_id or not country_iso:
        return jsonify({"error": "Manglende mission ID eller lande-ISO"}), 400
    
    # Tjek om landet eksisterer
    country = game.get_country(country_iso)
    if not country:
        return jsonify({"error": f"Land med ISO kode {country_iso} ikke fundet"}), 404
    
    # Annuller missionen via diplomacy subsystemet
    cancel_result = game.diplomacy.cancel_diplomatic_mission(mission_id, country_iso)
    
    if cancel_result.get('success'):
        return jsonify({
            "success": True,
            "message": "Diplomatisk mission er blevet annulleret.",
            "diplomatic_impact": cancel_result.get('diplomatic_impact', 0)
        })
    else:
        return jsonify({
            "success": False,
            "message": "Kunne ikke annullere den diplomatiske mission.",
            "reason": cancel_result.get('reason', 'Ukendt årsag')
        })

@diplomacy_bp.route('/actions/secret_negotiation', methods=['POST'])
def secret_negotiation():
    """Start hemmelige forhandlinger med et andet land"""
    game = get_game()
    
    if not game:
        return jsonify({"error": "Intet aktivt spil"}), 404
    
    data = request.json
    player_iso = data.get('player_iso')
    target_iso = data.get('target_iso')
    negotiation_topic = data.get('topic', 'trade')  # trade, alliance, military
    proposal = data.get('proposal', {})
    
    if not player_iso or not target_iso:
        return jsonify({"error": "Manglende lande-ISO koder"}), 400
    
    # Tjek om landene eksisterer
    player_country = game.get_country(player_iso)
    target_country = game.get_country(target_iso)
    
    if not player_country or not target_country:
        return jsonify({"error": "Et eller begge lande findes ikke"}), 404
    
    # Simulér resultatet af hemmelige forhandlinger
    # Dette er selvfølgelig en simplificeret version af hvad der faktisk ville ske i spilmotoren
    relation = game.diplomacy.get_relation(player_iso, target_iso)
    relation_level = relation.relation_level if relation else 0
    
    import random
    success_chance = (relation_level + 1) / 2.5 + 0.2  # 0.2-0.8 baseret på relation
    
    # Bonus baseret på emne og diplomatiske egenskaber
    if negotiation_topic == 'trade' and hasattr(player_country, 'trade_bonus'):
        success_chance += player_country.trade_bonus * 0.1
    
    # Simulér forhandlingsresultat
    success = random.random() < success_chance
    
    # Generer respons
    if success:
        # Positiv respons
        messages = [
            f"{target_country.name} er interesseret i dit forslag.",
            f"Der er opnået foreløbig enighed med {target_country.name}.",
            f"Hemmelige forhandlinger med {target_country.name} er lovende."
        ]
        message = random.choice(messages)
        
        # Forbedre relation
        if relation:
            relation.relation_level = min(1.0, relation.relation_level + 0.05)
        
        return jsonify({
            "success": True,
            "message": message,
            "next_steps": [
                "Send en officiel diplomat for at fortsætte forhandlingerne",
                "Forbered en formel aftale til underskrivning",
                "Overvej pressestrategi omkring offentliggørelse"
            ],
            "relation_change": "+0.05"
        })
    else:
        # Negativ respons
        messages = [
            f"{target_country.name} afviser diskret dit forslag.",
            f"Hemmelige forhandlinger med {target_country.name} er ikke kommet videre.",
            f"{target_country.name} viser ikke interesse for emnet på nuværende tidspunkt."
        ]
        message = random.choice(messages)
        
        return jsonify({
            "success": False,
            "message": message,
            "suggestions": [
                "Prøv igen på et senere tidspunkt",
                "Overvej at forbedre diplomatiske relationer først",
                "Tilbyd mere attraktive vilkår i fremtidige forhandlinger"
            ],
            "relation_change": "0"
        })

@diplomacy_bp.route('/coalitions', methods=['GET'])
def get_coalitions():
    """Hent alle aktive koalitioner i verden"""
    from main import game_state
    
    if not hasattr(game_state, 'diplomacy') or not hasattr(game_state.diplomacy, 'coalitions'):
        # Hvis vi ikke har koalitionssystemet implementeret endnu, returner tomme data
        return jsonify({
            "coalitions": []
        })
    
    # Formatér koalitioner for frontend
    coalitions_data = []
    for coalition in game_state.diplomacy.coalitions:
        # Konverter medlems-ISO koder til landenavne
        member_names = []
        for iso in coalition.member_countries:
            country = game_state.countries.get(iso)
            member_names.append({
                "iso": iso,
                "name": country.name if country else iso
            })
        
        coalitions_data.append({
            "id": coalition.id,
            "name": coalition.name,
            "purpose": coalition.purpose,
            "members": coalition.member_countries,
            "member_names": member_names,
            "leader": coalition.leader_country,
            "formation_turn": coalition.formation_turn,
            "duration": coalition.duration,
            "cohesion_level": coalition.cohesion_level,
            "active_actions": coalition.active_actions if hasattr(coalition, 'active_actions') else []
        })
    
    return jsonify({
        "coalitions": coalitions_data
    })

@diplomacy_bp.route('/coalitions/<country_iso>', methods=['GET'])
def get_country_coalitions(country_iso):
    """Hent koalitioner som et bestemt land er medlem af"""
    from main import game_state
    
    if not country_iso or country_iso not in game_state.countries:
        return jsonify({"error": f"Land med ISO kode {country_iso} ikke fundet"}), 404
    
    if not hasattr(game_state, 'diplomacy') or not hasattr(game_state.diplomacy, 'coalitions'):
        # Hvis vi ikke har koalitionssystemet implementeret endnu, returner tomme data
        return jsonify({
            "country": country_iso,
            "coalitions": []
        })
    
    # Find koalitioner land er medlem af
    country_coalitions = []
    led_coalitions = []
    for coalition in game_state.diplomacy.coalitions:
        if country_iso in coalition.member_countries:
            coalition_data = {
                "id": coalition.id,
                "name": coalition.name,
                "purpose": coalition.purpose,
                "members": coalition.member_countries,
                "leader": coalition.leader_country,
                "is_leader": coalition.leader_country == country_iso,
                "formation_turn": coalition.formation_turn,
                "cohesion_level": coalition.cohesion_level
            }
            
            country_coalitions.append(coalition_data)
            
            if coalition.leader_country == country_iso:
                led_coalitions.append(coalition_data)
    
    return jsonify({
        "country": country_iso,
        "member_of": country_coalitions,
        "leading": led_coalitions
    })

@diplomacy_bp.route('/coalitions/proposals', methods=['GET'])
def get_coalition_proposals():
    """Hent aktive koalitionsforslag"""
    from main import game_state
    
    if not hasattr(game_state, 'diplomacy') or not hasattr(game_state.diplomacy, 'coalition_proposals'):
        # Hvis vi ikke har koalitionssystemet implementeret endnu, returner tomme data
        return jsonify({
            "proposals": []
        })
    
    # Formatér koalitionsforslag for frontend
    proposals_data = []
    for proposal_id, proposal in game_state.diplomacy.coalition_proposals.items():
        # Konverter lande-ISO koder til navne
        proposer = game_state.countries.get(proposal['proposer'])
        candidates_info = []
        for iso in proposal['candidates']:
            country = game_state.countries.get(iso)
            candidates_info.append({
                "iso": iso,
                "name": country.name if country else iso,
                "response": proposal.get('responses', {}).get(iso)
            })
        
        proposals_data.append({
            "id": proposal_id,
            "coalition_name": proposal['coalition_name'],
            "purpose": proposal['purpose'],
            "proposer": proposal['proposer'],
            "proposer_name": proposer.name if proposer else proposal['proposer'],
            "candidates": proposal['candidates'],
            "candidates_info": candidates_info,
            "turn_proposed": proposal['turn_proposed'],
            "expires_turn": proposal['turn_proposed'] + proposal.get('expiry', 3),
            "description": proposal.get('description', ''),
            "benefits": proposal.get('benefits', [])
        })
    
    return jsonify({
        "proposals": proposals_data
    })

@diplomacy_bp.route('/coalitions/propose', methods=['POST'])
def propose_coalition():
    """Foreslå en ny koalition"""
    from main import game_state
    
    data = request.json
    proposer_iso = data.get('proposer_iso')
    coalition_name = data.get('coalition_name')
    purpose = data.get('purpose')
    candidates = data.get('candidates', [])
    description = data.get('description', '')
    benefits = data.get('benefits', [])
    
    if not proposer_iso or not coalition_name or not purpose or not candidates:
        return jsonify({"error": "Mangler påkrævede parametre"}), 400
    
    # Tjek om forslagsstiller findes
    if proposer_iso not in game_state.countries:
        return jsonify({"error": f"Land med ISO kode {proposer_iso} ikke fundet"}), 404
    
    # Opretter koalitionsforslag
    proposal_id = str(uuid.uuid4())
    
    if not hasattr(game_state, 'diplomacy'):
        game_state.diplomacy = type('obj', (), {})()
    
    if not hasattr(game_state.diplomacy, 'coalition_proposals'):
        game_state.diplomacy.coalition_proposals = {}
    
    proposal = {
        "id": proposal_id,
        "coalition_name": coalition_name,
        "purpose": purpose,
        "proposer": proposer_iso,
        "candidates": candidates,
        "turn_proposed": game_state.current_turn,
        "expiry": 3,  # Forslag udløber efter 3 ture
        "description": description,
        "benefits": benefits,
        "responses": {}  # Vil indeholde svar fra kandidater
    }
    
    game_state.diplomacy.coalition_proposals[proposal_id] = proposal
    
    # Simulér AI-reaktioner hvis diplomacy_ai er tilgængelig
    ai_responses = {}
    if hasattr(game_state.diplomacy, 'ai'):
        for country_iso in candidates:
            if country_iso != proposer_iso and country_iso != game_state.player_country_iso:
                # AI beslutning om at tilslutte sig koalitionen
                will_join = game_state.diplomacy.ai.ai_decide_coalition_response(country_iso, proposal_id)
                proposal['responses'][country_iso] = "accept" if will_join else "decline"
                ai_responses[country_iso] = {
                    "country_name": game_state.countries[country_iso].name,
                    "response": "accept" if will_join else "decline",
                    "reason": "Strategiske interesser stemmer overens" if will_join else "Ikke i vores interesse på nuværende tidspunkt"
                }
    
    return jsonify({
        "success": True,
        "message": "Koalitionsforslag oprettet",
        "proposal": proposal,
        "ai_responses": ai_responses
    })

@diplomacy_bp.route('/coalitions/respond', methods=['POST'])
def respond_to_coalition():
    """Reagér på et koalitionsforslag"""
    from main import game_state
    
    data = request.json
    proposal_id = data.get('proposal_id')
    country_iso = data.get('country_iso')
    response = data.get('response')  # 'accept' eller 'decline'
    
    if not proposal_id or not country_iso or not response:
        return jsonify({"error": "Mangler påkrævede parametre"}), 400
    
    # Tjek om land og forslag findes
    if country_iso not in game_state.countries:
        return jsonify({"error": f"Land med ISO kode {country_iso} ikke fundet"}), 404
    
    if not hasattr(game_state, 'diplomacy') or not hasattr(game_state.diplomacy, 'coalition_proposals') or proposal_id not in game_state.diplomacy.coalition_proposals:
        return jsonify({"error": "Koalitionsforslag ikke fundet"}), 404
    
    proposal = game_state.diplomacy.coalition_proposals[proposal_id]
    
    # Tjek om landet er en kandidat
    if country_iso not in proposal['candidates']:
        return jsonify({"error": "Dit land er ikke inviteret til denne koalition"}), 403
    
    # Registrér svaret
    if 'responses' not in proposal:
        proposal['responses'] = {}
    
    proposal['responses'][country_iso] = response
    
    # Tjek om alle har svaret, og om koalitionen kan dannes
    all_responded = all(candidate in proposal['responses'] for candidate in proposal['candidates'])
    
    if all_responded:
        accepted_members = [candidate for candidate in proposal['candidates'] 
                          if proposal['responses'].get(candidate) == 'accept']
        
        # Inkluder forslagsstiller
        if proposal['proposer'] not in accepted_members:
            accepted_members.append(proposal['proposer'])
        
        # Danner koalitionen hvis der er nok medlemmer (mindst 2)
        if len(accepted_members) >= 2:
            new_coalition = _form_coalition(proposal, accepted_members)
            
            # Fjern forslaget efter det er behandlet
            del game_state.diplomacy.coalition_proposals[proposal_id]
            
            return jsonify({
                "success": True,
                "message": "Koalitionen er dannet!",
                "coalition": new_coalition
            })
        else:
            # Ikke nok medlemmer til at danne koalitionen
            del game_state.diplomacy.coalition_proposals[proposal_id]
            return jsonify({
                "success": False,
                "message": "Koalitionen kunne ikke dannes, da der ikke var nok interesserede medlemmer."
            })
    else:
        # Nogle kandidater mangler stadig at svare
        return jsonify({
            "success": True,
            "message": f"{country_iso} har svaret {response} på koalitionsforslaget. Afventer svar fra andre kandidater.",
            "proposal": proposal
        })

def _form_coalition(proposal, members):
    """Hjælpefunktion til at danne en koalition fra et forslag"""
    from main import game_state
    
    if not hasattr(game_state.diplomacy, 'coalitions'):
        game_state.diplomacy.coalitions = []
    
    coalition = {
        "id": str(uuid.uuid4()),
        "name": proposal['coalition_name'],
        "purpose": proposal['purpose'],
        "leader_country": proposal['proposer'],
        "member_countries": members,
        "formation_turn": game_state.current_turn,
        "duration": 10, # Standard varighed
        "cohesion_level": 0.7, # Starter med god samhørighed
        "description": proposal.get('description', ''),
        "active_actions": []
    }
    
    # Tilføj koalitionen til spilstaten
    game_state.diplomacy.coalitions.append(coalition)
    
    return coalition

@diplomacy_bp.route('/coalitions/<coalition_id>/leave', methods=['POST'])
def leave_coalition(coalition_id):
    """Forlad en koalition"""
    from main import game_state
    
    data = request.json
    country_iso = data.get('country_iso')
    
    if not country_iso:
        return jsonify({"error": "Mangler lande-ISO kode"}), 400
    
    # Tjek om landet eksisterer
    if country_iso not in game_state.countries:
        return jsonify({"error": f"Land med ISO kode {country_iso} ikke fundet"}), 404
    
    if not hasattr(game_state, 'diplomacy') or not hasattr(game_state.diplomacy, 'coalitions'):
        return jsonify({"error": "Koalitionssystem ikke tilgængeligt"}), 404
    
    # Find koalitionen
    coalition = None
    for c in game_state.diplomacy.coalitions:
        if (isinstance(c, dict) and c.get('id') == coalition_id) or (hasattr(c, 'id') and c.id == coalition_id):
            coalition = c
            break
    
    if not coalition:
        return jsonify({"error": "Koalition ikke fundet"}), 404
    
    # Tjek om landet er medlem
    member_countries = coalition.member_countries if hasattr(coalition, 'member_countries') else coalition.get('member_countries', [])
    
    if country_iso not in member_countries:
        return jsonify({"error": "Dit land er ikke medlem af denne koalition"}), 403
    
    # Håndter udmeldelse
    leader_country = coalition.leader_country if hasattr(coalition, 'leader_country') else coalition.get('leader_country')
    
    if country_iso == leader_country:
        # Hvis lederen forlader koalitionen, opløses den
        game_state.diplomacy.coalitions.remove(coalition)
        
        return jsonify({
            "success": True,
            "message": "Som leder har du opløst koalitionen.",
            "coalition_dissolved": True
        })
    else:
        # Fjern landet fra koalitionen
        if isinstance(coalition, dict):
            coalition['member_countries'].remove(country_iso)
            # Reducér samhørighed da et medlem har forladt
            if 'cohesion_level' in coalition:
                coalition['cohesion_level'] = max(0.0, coalition['cohesion_level'] - 0.1)
        else:
            coalition.member_countries.remove(country_iso)
            if hasattr(coalition, 'cohesion_level'):
                coalition.cohesion_level = max(0.0, coalition.cohesion_level - 0.1)
        
        return jsonify({
            "success": True,
            "message": "Du har forladt koalitionen.",
            "coalition_dissolved": False
        })

@diplomacy_bp.route('/coalitions/<coalition_id>/propose_action', methods=['POST'])
def propose_coalition_action(coalition_id):
    """Foreslå en handling for en koalition"""
    from main import game_state
    
    data = request.json
    country_iso = data.get('country_iso')
    action_type = data.get('action_type')
    action_details = data.get('action_details', {})
    
    if not country_iso or not action_type:
        return jsonify({"error": "Mangler påkrævede parametre"}), 400
    
    # Tjek om landet eksisterer
    if country_iso not in game_state.countries:
        return jsonify({"error": f"Land med ISO kode {country_iso} ikke fundet"}), 404
    
    if not hasattr(game_state, 'diplomacy') or not hasattr(game_state.diplomacy, 'coalitions'):
        return jsonify({"error": "Koalitionssystem ikke tilgængeligt"}), 404
    
    # Find koalitionen
    coalition = None
    for c in game_state.diplomacy.coalitions:
        if (isinstance(c, dict) and c.get('id') == coalition_id) or (hasattr(c, 'id') and c.id == coalition_id):
            coalition = c
            break
    
    if not coalition:
        return jsonify({"error": "Koalition ikke fundet"}), 404
    
    # Tjek om landet er medlem og har autoritet (leder)
    leader_country = coalition.leader_country if hasattr(coalition, 'leader_country') else coalition.get('leader_country')
    member_countries = coalition.member_countries if hasattr(coalition, 'member_countries') else coalition.get('member_countries', [])
    
    if country_iso not in member_countries:
        return jsonify({"error": "Dit land er ikke medlem af denne koalition"}), 403
        
    if country_iso != leader_country:
        return jsonify({"error": "Kun lederen kan foreslå handlinger for koalitionen"}), 403
    
    # Opret handling
    action_id = str(uuid.uuid4())
    action = {
        "id": action_id,
        "coalition_id": coalition_id,
        "type": action_type,
        "details": action_details,
        "proposer": country_iso,
        "turn_proposed": game_state.current_turn,
        "status": "proposed",
        "member_responses": {}
    }
    
    # Tilføj handlingen til koalitionen
    if not hasattr(coalition, 'active_actions') and isinstance(coalition, dict):
        coalition['active_actions'] = []
    elif not hasattr(coalition, 'active_actions'):
        coalition.active_actions = []
    
    if hasattr(coalition, 'active_actions'):
        coalition.active_actions.append(action)
    else:
        coalition['active_actions'].append(action)
    
    # Simulér AI-reaktioner hvis diplomacy_ai er tilgængelig
    ai_responses = {}
    if hasattr(game_state.diplomacy, 'ai'):
        for member_iso in member_countries:
            if member_iso != country_iso and member_iso != game_state.player_country_iso:
                # AI beslutning om at støtte handlingen
                will_support = game_state.diplomacy.ai.ai_decide_coalition_action_response(member_iso, action)
                action['member_responses'][member_iso] = "support" if will_support else "oppose"
                ai_responses[member_iso] = {
                    "country_name": game_state.countries[member_iso].name,
                    "response": "support" if will_support else "oppose",
                    "reason": "I overensstemmelse med vores interesser" if will_support else "Strider mod vores prioriteter"
                }
    
    return jsonify({
        "success": True,
        "message": "Koalitionshandling foreslået",
        "action": action,
        "ai_responses": ai_responses
    })

@diplomacy_bp.route('/ai/personalities', methods=['GET'])
def get_ai_personalities():
    """Hent tilgængelige AI-personligheder for analyse"""
    from main import game_state
    
    if not hasattr(game_state, 'diplomacy') or not hasattr(game_state.diplomacy, 'ai') or not hasattr(game_state.diplomacy.ai, 'country_personalities'):
        return jsonify({"error": "AI-personligheder ikke tilgængelige"}), 404
    
    # Formatér personlighed for frontend
    personalities = {}
    for country_iso, personality in game_state.diplomacy.ai.country_personalities.items():
        if country_iso in game_state.countries:
            country_name = game_state.countries[country_iso].name
            
            # Konverter personlighed til dict med de relevante attributter
            personality_data = {}
            
            if hasattr(personality, 'risk_aversion'):
                personality_data['risk_aversion'] = personality.risk_aversion
            
            if hasattr(personality, 'retaliation'):
                personality_data['retaliation'] = personality.retaliation
                
            if hasattr(personality, 'trust_weight'):
                personality_data['trust_weight'] = personality.trust_weight
                
            if hasattr(personality, 'growth_weight'):
                personality_data['growth_weight'] = personality.growth_weight
                
            if hasattr(personality, 'sector_protection'):
                personality_data['sector_protection'] = personality.sector_protection
                
            if hasattr(personality, 'ideology'):
                personality_data['ideology'] = personality.ideology
                
            if hasattr(personality, 'regime_type'):
                personality_data['regime_type'] = personality.regime_type
                
            if hasattr(personality, 'personality') and personality.personality:
                if hasattr(personality.personality, 'leadership_style'):
                    personality_data['leadership_style'] = personality.personality.leadership_style
                    
                if hasattr(personality.personality, 'communication_style'):
                    personality_data['communication_style'] = personality.personality.communication_style
                    
                if hasattr(personality.personality, 'strategic_focus'):
                    personality_data['strategic_focus'] = personality.personality.strategic_focus
                    
                if hasattr(personality.personality, 'memorable_quotes') and personality.personality.memorable_quotes:
                    personality_data['quotes'] = personality.personality.memorable_quotes[:3]  # Vis op til 3 citater
            
            personalities[country_iso] = {
                "iso": country_iso,
                "name": country_name,
                "personality": personality_data
            }
    
    return jsonify({
        "personalities": list(personalities.values())
    })