from PIL import Image
from consts import FACTION_COLOR
import os
import shutil

TEMPLATE_PATH = "./templates/map_regions.tga"
OUTPUT_DIR = "./output"

def render_world_map(world_id, factions):
    DEFAULT_COLOR = (255, 0, 0)

    region_color_map = {}
    for faction in factions:
        faction_color = FACTION_COLOR.get(faction["faction_name"], DEFAULT_COLOR)
        for settlement in faction["settlements"]:
            region_rgb = tuple(settlement["rgb_value"])
            region_color_map[region_rgb] = faction_color

    with Image.open(TEMPLATE_PATH) as image:
        image = image.convert("RGB")
        pixels = image.load()
        print("Rendering map...")

        for x in range(image.width):
            for y in range(image.height):
                current_color = pixels[x, y]
                if current_color in region_color_map:
                    pixels[x, y] = region_color_map[current_color]

        world_folder = os.path.join(OUTPUT_DIR, str(world_id))
        os.makedirs(world_folder, exist_ok=True)
        file_name = f"{world_id}.png"
        file_path = os.path.join(world_folder, file_name)
        image.save(file_path)
        print(f"Map saved to {file_path}")

        latest_png_path = os.path.join(OUTPUT_DIR, "latest_map.png")
        image.save(latest_png_path)
        print(f"Latest map updated at {latest_png_path}")

