from PIL import Image


def main():
    
    with Image.open("../input/points_map.tga") as img:
        points_map = img.convert("RGB")
        
    parse_points_map(points_map)
        
def parse_points_map(image):
    
    field_color = (255,255,255)
    point_color = (0,0,0)
    H = image.height
    
    is_valid_map = False
    
    for x in range(image.width):
        for y in range(image.height):
            if image.getpixel((x, y)) not in (point_color, field_color):
                
                print(x, y)
      
if __name__ == "__main__":
        main()