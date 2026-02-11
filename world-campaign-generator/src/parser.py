from objects.region import Region
from PIL import Image
import os
import sys

from objects.script_enums import FactionEnum
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from objects.faction import FactionCharacterNames


def parse_regions(region_data):
    
    lines = region_data.split("\n")
    regions = []
    i = 0
    
    while i < len(lines):
        
        if lines[i].strip() == "":
            i += 1
            continue
        
        block = lines[i:i+9]
        
        province_name = block[0].strip()
        settlement_name = block[1].strip()
        culture = block[2].strip()
        rebels_type = block[3].strip()
        rgb_value = tuple(int(x) for x in block[4].split(" "))
        features = block[5].strip()
        famine_level = int(block[6])
        agriculture_level = int(block[7])
        religions_strings = block[8].strip().strip("religions {").strip("}").strip().split(" ")
        
        religions_dictionary = {}
        for j in range (0, len(religions_strings), 2):
            key = religions_strings[j]
            value = int(religions_strings[j+1])
            
            religions_dictionary[key] = value

        region = Region(province_name, settlement_name, culture, rebels_type, rgb_value, features, famine_level, agriculture_level, religions_dictionary, None, None, None)
        regions.append(region)
        
        i+=9
        
    return regions

#def parse_names(names_data):

def parse_settlement_coordinates(image, settlement_regions):
    
    sea_color = (41,140,233)
    settlement_color = (0,0,0)
    H = image.height
    
    for x in range(image.width):
        for y in range(image.height):
            if image.getpixel((x, y)) == settlement_color:
                coordinates_box = []
                coordinates_box.append(image.getpixel((x-1, y-1)))
                coordinates_box.append(image.getpixel((x-1, y)))
                coordinates_box.append(image.getpixel((x-1, y+1)))
                coordinates_box.append(image.getpixel((x, y-1)))
                coordinates_box.append(image.getpixel((x, y+1)))
                coordinates_box.append(image.getpixel((x+1, y-1)))
                coordinates_box.append(image.getpixel((x+1, y)))
                coordinates_box.append(image.getpixel((x+1, y+1)))
                
                coordinates_box = [coord for coord in coordinates_box if coord != sea_color]
                province_color = max(set(coordinates_box), key=coordinates_box.count)

                for region in settlement_regions:
                    if region.rgb_value == province_color:
                        region.settlement_positionX = x
                        region.settlement_positionY = H - y - 1
                        
def parse_names(text: str) -> list[FactionCharacterNames]:
    factions: list[FactionCharacterNames] = []

    current_faction: FactionCharacterNames | None = None
    current_section: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # Ignore empty lines and comments
        if not line:
            continue

        # New faction block
        if line.startswith("faction:"):
            if current_faction is not None:
                factions.append(current_faction)

            faction_name = line.split(":", 1)[1].strip()
            current_faction = FactionCharacterNames(
                faction=FactionEnum(faction_name)
            )
            current_section = None
            continue

        # Section headers
        if line in {"characters", "surnames", "women"}:
            current_section = line
            continue

        if line.startswith(";;bynames"):
            current_section = "bynames"
            continue

        # Name line
        if current_faction is None or current_section is None:
            continue  # malformed or stray data

        match current_section:
            case "characters":
                current_faction.male_names.append(line)
            case "surnames":
                current_faction.surnames.append(line)
            case "bynames":
                current_faction.bynames.append(line)
            case "women":
                current_faction.female_names.append(line)

    # Final faction
    if current_faction is not None:
        factions.append(current_faction)

    return factions

                  