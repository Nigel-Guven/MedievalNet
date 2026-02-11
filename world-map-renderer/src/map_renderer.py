from PIL import Image, ImageDraw
from consts import FACTION_COLOR
import os

TEMPLATE_PATH = "./templates/map_regions.tga"
OUTPUT_DIR = "./output"

def render_world_map(world_id, factions):

    DEFAULT_COLOR = (255, 0, 0)

    # Build region → faction color map
    region_color_map = {}

    for faction in factions:
        faction_color = FACTION_COLOR.get(
            faction["faction_name"], DEFAULT_COLOR
        )

        for settlement in faction["settlements"]:
            region_rgb = tuple(settlement["rgb_value"])
            region_color_map[region_rgb] = faction_color

    with Image.open(TEMPLATE_PATH) as image:
        image = image.convert("RGB")
        pixels = image.load()
        print("We Get to HEREA!!!!!")
        # Scan image ONCE
        for x in range(image.width):
            for y in range(image.height):
                current_color = pixels[x, y]

                if current_color in region_color_map:
                    pixels[x, y] = region_color_map[current_color]
        print("We Get to HEREB!!!!!")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"world_{world_id}.png")
        image.save(path)

        print(f"Rendered map saved to {path}")