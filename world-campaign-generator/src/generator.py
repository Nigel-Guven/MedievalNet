from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
import random
import math
from objects.script_enums import AztecCityBuilding, CastleBuilding, CityBuilding, FactionEnum, AIModel, Gender, Role
from objects.faction import Faction
from objects.character.character import FemaleCharacter, MaleCharacter
from objects.settlementconfiguration import SettlementConfiguration
import matplotlib.pyplot as plt
import consts


seed_value = None
random.seed(seed_value)

def create_factions_configuration(regions, names, region_amount):
    
    
    factions_list = create_factions(names)
    assign_settlements(factions_list, regions, region_amount)
    #visualize_map(factions_list, regions)
    #Create Characters for faction based on amount of regions
    assign_characters(factions_list)
    #Create family records for Faction characters
    
    #Create Faction standings, Alliances, Wars
    assign_faction_diplomacy_scores(factions_list)
    assign_allies_and_enemies(factions_list)
    
    update_region_settlement_configurations(factions_list)
    
    others = [f for f in factions_list if f.faction_name != "slave"]
    slaves = [f for f in factions_list if f.faction_name == "slave"]
    factions_list = others + slaves
        
    return factions_list

def create_factions(names_list):
    
    factions_list = list()
    
    for factionEnum in FactionEnum:
        faction = Faction(
            faction_name=factionEnum.value,
            ai_model=AIModel.BALANCED_SMITH,
            ai_label=getAILabel(factionEnum.value),
            denari=15000,
            kings_purse=6000,
            settlements=None,
            characters=None,
            character_records=None,
            factionCharacterNames=assign_names_for_faction(factionEnum, names_list)
        )
        
        
        
        factions_list.append(faction)
    
    return factions_list

def getAILabel(factionName):
    match factionName:
            case "turks", "egypt", "moors":
                return "islam"
            case "russia", "novgorod", "byzantium":
                return "orthodox"
            case "lithuania":
                return "pagan"
            case "mongols", "timurids":
                return "mongol"
            case "aztecs":
                return "aztecs"
            case "jerusalem", "teutonic_order", "antioch":
                return "teutonic"
            case "papal_states":
                return "papal_faction"
            case "slave":
                return "slave_faction"
            case _:
                return "catholic"
  
# TODO: Aztec need changes here 
# TODO: CONST CAPITALS BASED ON REGION AMOUNT   
def assign_settlements(factions, regions, region_amount):

    excluded_regions = consts.SPECIAL_SLAVE_REGIONS | consts.SPECIAL_AZTEC_REGIONS | consts.SPECIAL_PAPAL_REGIONS  
    potential_seeds = [r for r in regions if r.province_name in consts.CAPITAL_CANDIDATES]
    random.shuffle(potential_seeds)   
    unclaimed = [r for r in regions if r.province_name not in excluded_regions]   
    
    playable_factions = [f for f in factions if f.faction_name not in 
                         { FactionEnum.AZTECS.value, FactionEnum.PAPAL_STATES.value, FactionEnum.SLAVE.value }]
    
    random.shuffle(playable_factions)
    random.shuffle(factions)
    
    SEARCH_RADIUS = 50
    for r in unclaimed:
        r.density_score = sum(1 for other in unclaimed if simple_distance(r, other) < SEARCH_RADIUS)
    
    unclaimed.sort(key=lambda r: r.density_score, reverse=True)

    assigned_seeds = []
    for faction in playable_factions:
        if not potential_seeds:
            break 
        
        seed = max(potential_seeds, key=lambda p: min(
            [simple_distance(p, s) for s in assigned_seeds] + [999]
        ))
        
        faction.settlements = [seed]
        assigned_seeds.append(seed)
        potential_seeds.remove(seed)

        if seed in unclaimed:
            unclaimed.remove(seed)

    for _ in range(region_amount - 1):
        for faction in playable_factions:
            if not unclaimed: break

            capital = faction.settlements[0]
            next_region = min(unclaimed, key=lambda r: (
                min(simple_distance(r, c) for c in faction.settlements) * 0.7 + 
                simple_distance(r, capital) * 0.3
            ))
            
            faction.settlements.append(next_region)
            unclaimed.remove(next_region)

    aztec_faction = next(f for f in factions if f.faction_name == FactionEnum.AZTECS.value)
    aztec_faction.settlements = [
        r for r in regions
        if r.province_name in consts.SPECIAL_AZTEC_REGIONS
    ]
    
    papal_faction = next(f for f in factions if f.faction_name == FactionEnum.PAPAL_STATES.value)
    papal_faction.settlements = [
        r for r in regions
        if r.province_name in consts.SPECIAL_PAPAL_REGIONS
    ]
        
    slave_faction = next(f for f in factions if f.faction_name == FactionEnum.SLAVE.value)
    slave_faction.settlements = [
        r for r in regions
        if r.province_name in consts.SPECIAL_SLAVE_REGIONS
    ]
    slave_faction.settlements.extend(unclaimed)
    
def weighted_distance(regionA, regionB):
    
    #x_weight = (regionA.settlement_positionX + regionB.settlement_positionX) / 510
    #y_weight = (regionA.settlement_positionY + regionB.settlement_positionY) / 337
    
    #dx = (regionA.settlement_positionX - regionB.settlement_positionX) * x_weight
    #dy = (regionA.settlement_positionY - regionB.settlement_positionY) * y_weight
    
    dx = regionA.settlement_positionX - regionB.settlement_positionX
    dy = regionA.settlement_positionY - regionB.settlement_positionY
    
    return math.hypot(dx, dy)

def simple_distance(regionA, regionB):
    
    dx = regionA.settlement_positionX - regionB.settlement_positionX
    dy = regionA.settlement_positionY - regionB.settlement_positionY
    
    return math.hypot(dx, dy)

def assign_characters(factions):

    for faction in factions:
        
        royal_family = []
        capital_region = faction.settlements[0]
        
        if faction is None:
            continue  
        
        elif faction.faction_name in {FactionEnum.SLAVE.value}:          
            
            
            for i in faction.settlements[::4]:
                faction_choice= random.choice(factions)
                
                general = create_slave_character(i.settlement_positionX, i.settlement_positionY, faction_choice)
                royal_family.append(general)
            
            faction.characters = royal_family    
                
        elif faction.faction_name in {FactionEnum.PAPAL_STATES.value}:
            pope = create_pope_character(capital_region, faction)
            royal_family.append(pope)
            
            for i in faction.settlements:
                general = create_general_character(i.settlement_positionX, i.settlement_positionY, faction)
                royal_family.append(general)
            
            faction.characters = royal_family
                
        else:
            king = create_king_character(capital_region, faction)
            queen = create_queen_character()
            prince = create_prince_character(capital_region, faction)
            
            royal_family = [king,queen,prince]
            faction.characters = royal_family
            
            for i in faction.settlements:
                general = create_general_character(i.settlement_positionX, i.settlement_positionY, faction)
                faction.characters.append(general)
        if faction.faction_name not in {FactionEnum.SLAVE.value}:    
            assign_character_names(faction)
                  
def create_king_character(capital_region, faction):
    
    return MaleCharacter(
        character_name="",
        role=Role.LEADER,
        age=33,
        positionX=capital_region.settlement_positionX,
        positionY=capital_region.settlement_positionY,
        traits="Factionleader 1 , GoodCommander 4 , Energetic 1 , StrategyChivalry 4, Intelligent 1",
        ancillaries=create_ancillaries(Role.LEADER, faction.faction_name),
        army_units=create_army(faction)
    )
    
def create_queen_character():
    
    return FemaleCharacter(
        character_name="",
        role=Role.NEVERLEADER,
        age=32
    )
    
def create_prince_character(capital_region, faction):
    
    return MaleCharacter(
        character_name="",
        role=Role.HEIR,
        age=17,
        positionX=capital_region.settlement_positionX,
        positionY=capital_region.settlement_positionY,
        traits="Factionheir 1 , BattleDread 2 , StrategyDread 1 , Intelligent 2 , PublicFaith 1 , LoyaltyStarter 1, Fertile 1",
        ancillaries=create_ancillaries(Role.HEIR, ""),
        army_units=create_army(faction)
    )
    
def create_general_character(x, y, faction):
    
    return MaleCharacter(
        character_name="",
        role=None,
        age=16,
        positionX=x,
        positionY=y,
        traits="GoodCommander 2 , BattleChivalry 2 , StrategyChivalry 1 , ReligionStarter 1 , PublicFaith 1 , LoyaltyStarter 1",
        ancillaries=create_ancillaries(None, ""),
        army_units=create_army(faction)
    )
    
def create_pope_character(capital_region, faction):
    
    return MaleCharacter(
        character_name="",
        role=Role.LEADER,
        age=40,
        positionX=capital_region.settlement_positionX,
        positionY=capital_region.settlement_positionY,
        traits="IAmPope 1 , GoodCommander 2 , PoliticsSkill 3 , PublicFaith 1 , GoodAdministrator 2 , Austere 1 , Intelligent 2 , ReligionStarter 1 , Fertile 1",
        ancillaries=create_ancillaries(Role.LEADER, "papal_states"),
        army_units=create_army(faction)
    )
    
def create_slave_character(x, y, faction):
    
    name_for_slave_general = random.choice(faction.factionCharacterNames.male_names)
    
    return MaleCharacter(
        character_name=name_for_slave_general,
        role=Role.SLAVER.value + faction.faction_name,
        age=25,
        positionX=x,
        positionY=y,
        traits="GoodCommander 4 , GoodAttacker 3 , PublicFaith 3 , BattleChivalry 4 , StrategyChivalry 3 , ReligiousActivity 2 , ReligionStarter 1",
        ancillaries=create_ancillaries(None, ""),
        army_units=create_army(faction)
    )
    
def create_ancillaries(role, faction_name):

    match(role):
        case Role.LEADER:
            match(faction_name):
                case "russia":
                    return "crown_russia" + ", " + assignRandomAncillary()
                case "hre":
                    return "crown_hre" + ", " + assignRandomAncillary()
                case "venice":
                    return "crown_venice" + ", " + assignRandomAncillary()
                case "mongols":
                    return "crown_mongols" + ", " + assignRandomAncillary()
                case "denmark":
                    return "crown_denmark" + ", " + assignRandomAncillary()
                case "egypt":
                    return "crown_egypt" + ", " + assignRandomAncillary()
                case "turks":
                    return "crown_turks" + ", " + assignRandomAncillary()
                case "poland":
                    return "crown_poland" + ", " + assignRandomAncillary()
                case "novgorod":
                    return "crown_novgorod" + ", " + assignRandomAncillary()
                case "france":
                    return "crown_france" + ", " + assignRandomAncillary()
                case "moors":
                    return "crown_moors" + ", " + assignRandomAncillary()
                case "spain":
                    return "crown_spain" + ", " + assignRandomAncillary()
                case "hungary":
                    return "crown_hungary" + ", " + assignRandomAncillary()
                case "timurids":
                    return "crown_mongols" + ", " + assignRandomAncillary()
                case "antioch":
                    return "crown_antioch" + ", " + assignRandomAncillary()
                case "milan":
                    return "crown_milan" + ", " + assignRandomAncillary()
                case "ireland":
                    return "crown_ireland" + ", " + assignRandomAncillary()
                case "aztecs":
                    return "crown_aztecs" + ", " + assignRandomAncillary()
                case "byzantium":
                    return "crown_greeks" + ", " + assignRandomAncillary()
                case "papal_states":
                    return "crown_of_thorns" + ", " + assignRandomAncillary()
                case "lithuania":
                    return "crown_lithuania" + ", " + assignRandomAncillary()
                case "norway":
                    return "crown_norway" + ", " + assignRandomAncillary()
                case "wales":
                    return "crown_wales" + ", " + assignRandomAncillary()
                case "jerusalem":
                    return "crown_elo" + ", " + assignRandomAncillary()
                case "scotland":
                    return "crown_scotland" + ", " + assignRandomAncillary()
                case "portugal":
                    return "crown_portugal" + ", " + assignRandomAncillary()
                case "sicily":
                    return "crown_sicily" + ", " + assignRandomAncillary()
                case "teutonic_order":
                    return "crown_teutonic_order" + ", " + assignRandomAncillary()
                case "england":
                    return "crown_england" + ", " + assignRandomAncillary()
        case _:
            return assignRandomAncillary()
           
def create_army(faction):
    
    faction_name = faction.faction_name
    
    units = list()
    
    match(faction_name):
        case "france" | "hre":
            units.append("NE Bodyguard")
            units.append("Sergeant Spearmen")
            units.append("Sergeant Spearmen")
            units.append("Sergeant Spearmen")
            units.append("Sergeant Spearmen")
            return units
        case "milan" | "venice" | "sicily":
            units.append("SE Bodyguard")
            units.append("Sergeant Spearmen")
            units.append("Sergeant Spearmen")
            units.append("Sergeant Spearmen")
            units.append("Sergeant Spearmen")
            return units
        case "byzantium":
            units.append("Greek Bodyguard")
            units.append("Byzantine Spearmen")
            units.append("Byzantine Spearmen")
            units.append("Byzantine Spearmen")
            units.append("Byzantine Spearmen")
            return units
        case "denmark" | "norway":
            units.append("NE Bodyguard")
            units.append("Viking Raiders")
            units.append("Viking Raiders")
            units.append("Viking Raiders")
            units.append("Viking Raiders")
            return units
        case "novgorod" | "hungary" | "lithuania" | "russia":
            units.append("EE Bodyguard")
            units.append("EE Spear Militia")
            units.append("EE Spear Militia")
            units.append("EE Spear Militia")
            units.append("EE Spear Militia")
            return units
        case "poland" | "hungary":
            units.append("NE Bodyguard")
            units.append("EE Spear Militia")
            units.append("EE Spear Militia")
            units.append("EE Spear Militia")
            units.append("EE Spear Militia")
            return units
        case "spain" | "portugal":
            units.append("SE Bodyguard")
            units.append("Spear Militia")
            units.append("Spear Militia")
            units.append("Spear Militia")
            units.append("Spear Militia")
            return units
        case "england" | "scotland" | "wales":
            units.append("NE Bodyguard")
            units.append("Spear Militia")
            units.append("Spear Militia")
            units.append("Spear Militia")
            units.append("Spear Militia")
            return units
        case "mongols" | "timurids":
            units.append("Mongol Bodyguard")
            units.append("Dismounted Heavy Lancers")
            units.append("Dismounted Heavy Lancers")
            units.append("Dismounted Heavy Lancers")
            units.append("Dismounted Heavy Lancers")
            return units
        case "moors" | "egypt" | "turks":
            units.append("ME Bodyguard")
            units.append("ME Spear Militia")
            units.append("ME Spear Militia")
            units.append("ME Spear Militia")
            units.append("ME Spear Militia")
            return units
        case "antioch":
            units.append("NE Bodyguard")
            units.append("Hospitaller Sergeant")
            units.append("Hospitaller Sergeant")
            units.append("Hospitaller Sergeant")
            units.append("Hospitaller Sergeant")
            return units
        case "ireland":
            units.append("NE Bodyguard")
            units.append("Cliathairi")
            units.append("Cliathairi")
            units.append("Cliathairi")
            units.append("Cliathairi")
            return units
        case "aztecs":
            units.append("Aztec Bodyguard")
            units.append("Aztec Spearmen")
            units.append("Aztec Spearmen")
            units.append("Aztec Spearmen")
            units.append("Aztec Spearmen")
            return units
        case "papal_states":
            units.append("SE Bodyguard")
            units.append("Papal Guard")
            units.append("Papal Guard")
            units.append("Papal Guard")
            units.append("Papal Guard")
            return units
        case "jerusalem":
            units.append("NE Bodyguard")
            units.append("Templar Sergeant")
            units.append("Templar Sergeant")
            units.append("Templar Sergeant")
            units.append("Templar Sergeant")
            return units
        case "teutonic_order":
            units.append("TO Bodyguard")
            units.append("Spear Militia")
            units.append("Spear Militia")
            units.append("Spear Militia")
            units.append("Spear Militia")
            return units
        case "slave":
            units.append("NE Bodyguard")
            units.append("Jinetes")
            units.append("Jinetes")
            units.append("Crossbow Militia")
            units.append("Spear Militia")
            units.append("Spear Militia")
            units.append("Croat Axemen")
            units.append("Croat Axemen")
            units.append("Kazaks")
            units.append("Tuareg Camel Spearmens")
            return units
        
def assign_names_for_faction(faction, names_list):
    
    for name_block in names_list:
        if name_block.faction == faction:        
            return name_block
        
    return None

def assign_character_names(faction):

    pool = faction.factionCharacterNames
    
    if not pool:
        print(f"No name pool found for {faction.faction_name}")
        return

    royal_surname = ""
    if pool.surnames:
        royal_surname = random.choice(pool.surnames)
        pool.surnames.remove(royal_surname)

    
    for character in faction.characters:
        
        is_male = character.gender == Gender.MALE
        first_pool = pool.male_names if is_male else pool.female_names
        
        if not first_pool:
            continue
        
        fname = random.choice(first_pool)
        first_pool.remove(fname)

        bname = ""
        if character.role in [Role.LEADER, Role.NEVERLEADER, Role.HEIR]:
            # Royals get the pre-selected family name
            sname = royal_surname
            # Optional: Give royals a byname and remove it from pool
        else:
            # Non-royals get random surnames/bynames
            sname = ""
            if pool.surnames:
                sname = random.choice(pool.surnames)
                pool.surnames.remove(sname)
            
            if pool.bynames:
                bname = random.choice(pool.bynames)
                pool.bynames.remove(bname)

        # 5. Assign and format
        if not is_male:
            character.character_name = f"{fname}".strip()
        else: 
            character.character_name = f"{fname} {sname}".strip().replace("  ", " ")     

def assignRandomAncillary():
    
    list_of_ancillaries = (
        "armour_custom", 
        "armour_ornate", 
        "bodyguard", 
        "dancer", 
        "foodtaster", 
        "foreign_dignitary", 
        "mercenary_captain", 
        "musician", 
        "nosy_mother", 
        "obsessed_suitor", 
        "overseer", 
        "pet_monkey", 
        "physician", 
        "chancellor", 
        "privyseal", 
        "marshall", 
        "harsh_judge", 
        "exotic_gifts", 
        "explosives", 
        "evil_mother-in-law",
        "joan_of_arc", 
        "peter_the_hermit", 
        "pierre_abelard", 
        "francesco_petrarca", 
        "roger_bacon", 
        "geoffrey_chaucer", 
        "john_wycliffe", 
        "simon_de_montfort", 
        "amerigo_vespucci", 
        "niels_ebbesen", 
        "vlad_tepes", 
        "meister_eckhart", 
        "arnold_von_winkelried")
    
    return "" + random.choice(list_of_ancillaries)
  
def assign_faction_diplomacy_scores(factions):
    
    STEP = Decimal("0.05")
    SLAVE_VALUE = Decimal("-0.90") 
    
    for factionI in factions:
        factionI.factionRelations = defaultdict(list)
           
        for factionJ in factions:
                     
            if factionI == factionJ:
                continue
            
            if factionI.faction_name == "slave":
                factionI.factionRelations[SLAVE_VALUE].append(factionJ.faction_name)
                continue
   
            if factionJ.faction_name == "slave":
                factionI.factionRelations[SLAVE_VALUE].append(factionJ.faction_name)
                continue
   
            random_value = Decimal(random.randrange(-96, 96))/100         
            rounded_random = (random_value / STEP).quantize(Decimal("1"),rounding=ROUND_HALF_UP) * STEP
            
            if rounded_random == Decimal("0.00"):
                continue
            
            factionI.factionRelations[rounded_random].append(factionJ.faction_name)
        
        factionI.factionRelations = dict(factionI.factionRelations)       

def assign_allies_and_enemies(factions):
    
    for factionI in factions:
        for factionJ in factions:
            
            if factionI == factionJ:
                continue
            
            if factionI.faction_name == "slave":
                factionI.enemies.append(factionJ.faction_name)
                
            if factionJ.faction_name == "slave":
                factionI.enemies.append(factionJ.faction_name)
# TODO: Aztec need changes here
def update_region_settlement_configurations(factions):
    for factionI in factions:
        
        #PAPAL FACTION
        if factionI.faction_name == "papal_states":
            for i in range(len(factionI.settlements)):
                settlementI = factionI.settlements[i]
                settlement_config = SettlementConfiguration(
                    settlementI.province_name,
                    level="city",
                    population=22000,
                    faction_creator=factionI.faction_name,
                    is_castle=False,
                    buildings=create_city_buildings(),
                )
                settlementI.settlement_configuration = settlement_config               
        #AZTEC FACTION
        elif factionI.faction_name == "aztecs":
            for i in range(len(factionI.settlements)):
                settlementI = factionI.settlements[i]
                settlement_config = SettlementConfiguration(
                    settlementI.province_name,
                    level="city",
                    population=22000,
                    faction_creator=factionI.faction_name,
                    is_castle=False,
                    buildings=create_aztec_city_buildings(),
                )
                settlementI.settlement_configuration = settlement_config          
        #SLAVE FACTION
        elif factionI.faction_name == "slave":
            for i in range(len(factionI.settlements)):
                for i in range(len(factionI.settlements)):
                    settlementI = factionI.settlements[i] 
                    if i < 10:
                        settlementI.settlement_configuration = create_town_configuration(settlementI)
                    elif i >= 10 and i < 15:
                        settlementI.settlement_configuration = create_castle_configuration(settlementI)  
                    elif i >= 15 and i < 25:
                        settlementI.settlement_configuration = create_large_town_configuration(settlementI)  
                    elif i >= 25 and i < 30:
                        settlementI.settlement_configuration = create_motte_bailey_configuration(settlementI)  
                    else:
                        settlementI.settlement_configuration = create_village_configuration(settlementI)
        else:                 
        #PLAYABLE FACTIONS
            for i in range(len(factionI.settlements)):
                settlementI = factionI.settlements[i] 
                if i == 0:
                    settlementI.settlement_configuration = create_large_town_configuration(settlementI, factionI.faction_name)
                elif i == 1:
                    settlementI.settlement_configuration = create_motte_bailey_configuration(settlementI, factionI.faction_name)  
                elif i == 2:
                    settlementI.settlement_configuration = create_castle_configuration(settlementI, factionI.faction_name)  
                elif i == 3:
                    settlementI.settlement_configuration = create_town_configuration(settlementI, factionI.faction_name)  
                else:
                    settlementI.settlement_configuration = create_village_configuration(settlementI, factionI.faction_name)
                
def create_large_town_configuration(region, faction_specified = None):
    return SettlementConfiguration( 
        region.province_name, 
        level="large_town", 
        population=12000, 
        faction_creator= region.culture if faction_specified is None else faction_specified,
        is_castle=False, 
        buildings=create_large_town_buildings(),)
def create_town_configuration(region, faction_specified = None):
    return SettlementConfiguration( 
        region.province_name, 
        level="town", 
        population=6000, 
        faction_creator=region.culture if faction_specified is None else faction_specified, 
        is_castle=False, 
        buildings=create_town_buildings(),)
def create_village_configuration(region, faction_specified = None):
    return SettlementConfiguration( 
        region.province_name, 
        level="village", 
        population=2000, 
        faction_creator=region.culture if faction_specified is None else faction_specified, 
        is_castle=False, buildings=create_village_buildings(),)
def create_castle_configuration(region, faction_specified = None):
    return SettlementConfiguration( 
        region.province_name, 
        level="large_town", 
        population=8000, 
        faction_creator=region.culture if faction_specified is None else faction_specified, 
        is_castle=True, 
        buildings=create_castle_buildings(),)
def create_motte_bailey_configuration(region, faction_specified = None):
    return SettlementConfiguration( 
        region.province_name, 
        level="village", 
        population=2000, 
        faction_creator=region.culture if faction_specified is None else faction_specified,
        is_castle=True, 
        buildings=create_motte_bailey_buildings(),)
    
def create_motte_bailey_buildings():
    return [
        CastleBuilding.CORE_CASTLE_BUILDING_MOTTE, 
        CastleBuilding.CASTLE_FARM_LEVEL_1]
def create_castle_buildings():
    return [
        CastleBuilding.CORE_CASTLE_BUILDING_STONE_WALL,
        CastleBuilding.CASTLE_BARRACKS_GARRISON_QUARTERS,
        CastleBuilding.CASTLE_MISSILES_ARCHERY_RANGE,
        CastleBuilding.CASTLE_SIEGE_CATAPULT,
        CastleBuilding.EQUESTRIAN_STABLES,
        CastleBuilding.CASTLE_SMITH_BLACKSMITH,
        CastleBuilding.CASTLE_ROADS,
        CastleBuilding.CASTLE_FARM_LEVEL_1,]
def create_village_buildings():
    return [
        CityBuilding.CORE_VILLAGE_BUILDING_NO_WALLS,
        CityBuilding.CITY_FARM_LEVEL_1,]      
def create_town_buildings():
    return [
        CityBuilding.CORE_TOWN_BUILDING_PALLISADE,
        CityBuilding.CITY_BARRACKS_TOWN_WATCH,
        CityBuilding.CITY_MARKET_CORN_EXCHANGE,
        CityBuilding.CITY_SMITH_LEATHER_TANNER,
        CityBuilding.CITY_FARM_LEVEL_1]     
def create_large_town_buildings():
    return [
        CityBuilding.CORE_LARGE_TOWN_BUILDING_WOODEN_WALL,
        CityBuilding.CITY_BARRACKS_TOWN_WATCH,
        CityBuilding.CITY_MARKET_MARKET,
        CityBuilding.CITY_SMITH_LEATHER_TANNER,
        CityBuilding.CITY_FARM_LEVEL_1]     

# Aztec Faction
def create_aztec_city_buildings():
    return [
        AztecCityBuilding.AZTEC_CORE_CITY_BUILDING_STONE_WALL,
        AztecCityBuilding.AZTEC_CITY_PALACE_COMPLEX,
        AztecCityBuilding.AZTEC_CITY_MARKET_MARKET,
        AztecCityBuilding.AZTEC_GREAT_PYRAMID,
        AztecCityBuilding.AZTEC_CITY_ROADS,
        AztecCityBuilding.AZTEC_FARM_LEVEL_2]
def create_aztec_large_town_buildings():
    return [
        AztecCityBuilding.AZTEC_CORE_CITY_BUILDING_WOODEN_WALL,
        AztecCityBuilding.AZTEC_CITY_PALACE,
        AztecCityBuilding.AZTEC_CITY_MARKET_MARKET,
        AztecCityBuilding.AZTEC_PYRAMID,
        AztecCityBuilding.AZTEC_FARM_LEVEL_2]
def create_aztec_village_buildings():
    return [
        AztecCityBuilding.AZTEC_CORE_CITY_BUILDING_NO_WALLS,
        AztecCityBuilding.AZTEC_FARM_LEVEL_1]
    
# Papal Faction
def create_city_buildings():
    return [
        CityBuilding.CORE_CITY_BUILDING_STONE_WALL,
        CityBuilding.CORE_CITY_HALL_TOWN_HALL,
        CityBuilding.CITY_BARRACKS_TOWN_GUARD,
        CityBuilding.CITY_MARKET_FAIRGROUND,
        CityBuilding.CITY_SMITH_BLACKSMITH,
        CityBuilding.CITY_FARM_LEVEL_2,
        CityBuilding.CITY_ROADS,]        

def visualize_map(factions, regions):
    plt.figure(figsize=(12, 8))

    # plot all regions in light gray
    xs = [r.settlement_positionX for r in regions]
    ys = [r.settlement_positionY for r in regions]
    plt.scatter(xs, ys, s=10, c="lightgray", label="All regions")

    for faction in factions:
        if not faction.settlements:
            continue

        fx = [r.settlement_positionX for r in faction.settlements]
        fy = [r.settlement_positionY for r in faction.settlements]

        plt.scatter(
            fx,
            fy,
            s=30,
            label=faction.faction_name
        )

        # mark the seed clearly
        seed = faction.settlements[0]
        plt.scatter(
            seed.settlement_positionX,
            seed.settlement_positionY,
            s=120,
            marker="X",
            edgecolors="black"
        )

    plt.legend(
        fontsize=8,
        bbox_to_anchor=(1.05, 1),
        loc="upper left"
    )
    plt.title("MTW2 Campaign Region Assignment")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()  
