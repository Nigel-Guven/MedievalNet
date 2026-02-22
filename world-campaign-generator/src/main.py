import sys
import uuid
from PIL import Image
import parser
from generator import create_factions_configuration
from objects.script_enums import Gender, Role
import kafka_producer

def main():

    
    region_amount = 5
    
    try:
        region_amount = int(sys.argv[1])
    
        if 3 <= region_amount <= 6:
            region_amount= region_amount 
        else:
            print(f"Invalid number {region_amount}, using default REGION_AMOUNT={region_amount}")
    except (IndexError, ValueError):
        print(f"No valid input provided, using default REGION_AMOUNT={region_amount}")
        print(f"Using REGION_AMOUNT={region_amount}")
    
    with open("../input_files/descr_regions.txt", "r") as f:
        regions_data = f.read()
    with open("../input_files/descr_names.txt", "r") as f:
        names_data = f.read()

    with Image.open("../input_files/map_regions.tga") as img:
        region_map = img.convert("RGB")

    regions = parser.parse_regions(regions_data)
    parser.parse_settlement_coordinates(region_map, regions)
    names = parser.parse_names(names_data)
    
    
    campaign_factions = create_factions_configuration(regions, names, region_amount)
    
    world_uuid = str(uuid.uuid4().hex)
    
    world_event = {
        "worldId": world_uuid,
        "factions": [kafka_producer.faction_to_dictionary(f) for f in campaign_factions]
    }
    
    kafka_producer.send_world_event(world_event, key=world_uuid)
    print(f"World {world_uuid} pushed to Kafka topic 'world.generated'")
    
    
    with open("../input_files/descr_strat_campaign_settings.txt", "r") as f:
        campaign_settings = f.read()
    with open("../input_files/descr_strat_resources.txt", "r") as f:
        resources = f.read()
    with open("../input_files/descr_strat_script_plugins.txt", "r") as f:
        script_plugin = f.read()  
    
    with open("../output_files/descr_strat_modified" + world_uuid + ".txt" , "w", encoding="utf-8") as dst:
        
        dst.write(";*********************\n")
        dst.write(";**    CAMPAIGN     **\n")
        dst.write(";*********************\n")
        for line in campaign_settings:
            dst.write(line)  
        
        dst.write("\n\n")
        
        dst.write(";*********************\n")
        dst.write(";**    RESOURCES    **\n")
        dst.write(";*********************\n")
        for line in resources:
            dst.write(line)
            
        dst.write("\n\n") 
            
        dst.write(";*********************\n")
        dst.write(";**    FACTIONS     **\n")
        dst.write(";*********************\n")
        
        for faction in campaign_factions:
            
            dst.write("\n") 
            dst.write(";*********************\n")
            dst.write(f";** {faction.faction_name} **\n")
            dst.write(";*********************\n")
            dst.write("\n")
            
            dst.write("faction\t" + faction.faction_name + ", " + faction.ai_model + "\n")
            dst.write("ai_label\t\t" + faction.ai_label + "\n")
            dst.write(f"denari\t{faction.denari}\n")
            dst.write(f"denari_kings_purse\t{faction.kings_purse}\n")
            
            for settlementI in faction.settlements:
                settlement_config = settlementI.settlement_configuration
                dst.write("settlement castle\n" if settlement_config.is_castle == True else "settlement\n",)
                dst.write("{\n")
                
                dst.write(f"\tlevel {settlement_config.level}\n")
                dst.write(f"\tregion {settlement_config.region}\n")
                dst.write(f"\tyear_founded {settlement_config.year_founded}\n")
                dst.write(f"\tpopulation {settlement_config.population}\n")
                dst.write(f"\tplan_set {settlement_config.plan_set}\n")
                dst.write(f"\tfaction_creator {settlement_config.faction_creator}\n")
                if settlement_config.buildings is not None:
                    for building in settlement_config.buildings:
                        if building.value != "":
                            dst.write("\tbuilding\n")
                            dst.write("\t{\n")
                            dst.write(f"\t\ttype {building.value}\n")
                            dst.write("\t}\n")
                else:
                    print(settlement_config.buildings)
                dst.write("}\n")
            dst.write("\n")
            for characterI in faction.characters:
                if characterI.gender == Gender.MALE:
                    if faction.faction_name == "slave":
                        dst.write(f"character\t{characterI.role}, {characterI.character_name}, named character, {characterI.gender.value}, age {characterI.age}, x {characterI.positionX}, y {characterI.positionY} \n")
                        dst.write(f"traits {characterI.traits} \n")
                        dst.write(f"ancillaries {characterI.ancillaries}\n")
                        dst.write("army\n")
                        for unit in characterI.army_units:
                            dst.write(f"unit\t\t{unit}\t\t\texp 0 armour 0 weapon_lvl 0\n")
                        dst.write("\n")
                    elif characterI.role == Role.HEIR or characterI.role == Role.LEADER:
                        dst.write(f"character\t{characterI.character_name}, {characterI.defined_character}, {characterI.gender.value}, {characterI.role.value}, age {characterI.age}, x {characterI.positionX}, y {characterI.positionY} \n")
                        dst.write(f"traits {characterI.traits} \n")
                        dst.write(f"ancillaries {characterI.ancillaries}\n")
                        dst.write("army\n")
                        for unit in characterI.army_units:
                            dst.write(f"unit\t\t{unit}\t\t\texp 3 armour 0 weapon_lvl 0\n")
                        dst.write("\n")
                    else:
                        dst.write(f"character\t{characterI.character_name}, {characterI.defined_character}, {characterI.gender.value}, age {characterI.age}, x {characterI.positionX}, y {characterI.positionY} \n")
                        dst.write(f"traits {characterI.traits} \n")
                        dst.write(f"ancillaries {characterI.ancillaries}\n")
                        dst.write("army\n")
                        for unit in characterI.army_units:
                            dst.write(f"unit\t\t{unit}\t\t\texp 1 armour 0 weapon_lvl 0\n")
                        dst.write("\n")
            dst.write("\n")  
            for characterI in faction.characters:
                if characterI.gender == Gender.FEMALE:
                    dst.write(f"character_record\t\t{characterI.character_name}, \t{characterI.gender.value}, age {characterI.age}, {characterI.alive}, {characterI.role.value}\n")
            dst.write("\n")       
            if faction.faction_name not in ("slave", "papal_states"):
                dst.write(
                    f"relative \t{faction.characters[0].character_name},"
                    f"\t{faction.characters[1].character_name},"
                    f"\t{faction.characters[2].character_name},\tend\n"
                )
                
            dst.write("\n") 
        
                        
            
        dst.write("\n\n")
        dst.write(";*********************\n")
        dst.write(";**   DIPLOMACY     **\n")
        dst.write(";*********************\n")
        
        for faction in campaign_factions:
            for score, otherFactions in faction.factionRelations.items():
                if not otherFactions:
                    continue
                
                dst.write(
                    f"faction_standings\t{faction.faction_name},\t\t"
                    f"{score:.2f}\t{', '.join(otherFactions)}\n")
                
            dst.write("\n")
        
        dst.write("\n\n")
        
        dst.write(";*********************\n")
        dst.write(";**      WARS       **\n")
        dst.write(";*********************\n")
        
        for faction in campaign_factions:
            
            enemies = ", ".join(faction.enemies)
            dst.write(f"faction_relationships \t{faction.faction_name}, at_war_with \t")   
            dst.write(enemies +"\n") 
        dst.write("\n\n")
        
        dst.write(";*********************\n")
        dst.write(";** SCRIPTPLUGINS  **\n")
        dst.write(";*********************\n")
        for line in script_plugin:
            dst.write(line) 
            
if __name__ == "__main__":
        main()