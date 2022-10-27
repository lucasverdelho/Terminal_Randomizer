import os
from PIL import Image
from colorthief import ColorThief


# Function that convers a tuple of RGB values to a hex string
def rgb_to_hex(rgb_color):
    hex_color = "#"
    for i in rgb_color:
        i = int(i)
        hex_color += ("{:02x}".format(i))
    return hex_color


# Brighten a color
def color_variant(hex_color, brightness_offset=1):

    if len(hex_color) != 7:
        raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)

    rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int] # make sure new values are between 0 and 255
    # hex() produces "0x88", we want just "88"
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])


# Function that returns the complimentary of a given color
def get_complementary(color):
    color = color[1:]
    color = int(color, 16)
    comp_color = int("0xFFFFFF", base=16) - color
    comp_color = hex(comp_color)
    return str(comp_color).replace("0x", "#")


# Define the path of the photos folder
photos_path = '..\\photos'
photos = os.listdir(photos_path)

# Check if a thumbnail already exists for the gif, else create one, converting the GIF to a PNG
for i in photos:
    thumbnail_path = os.path.join(os.path.abspath("..\\thumbnails"), (i[:-4] + ".png"))

    if (os.path.exists(os.path.join(thumbnail_path, i[:-4] + ".png"))):
        continue

    # Convert Gif to PNG
    img = Image.open(os.path.join(os.path.abspath(photos_path), i))
    newImage = img.convert('RGBA')
    bg = Image.new('RGBA', newImage.size)
    image = Image.composite(newImage, bg, newImage)
    image.save("..\\thumbnails\\zconverted" + i[:-4] + ".png")
    img.close()


# Define the path of the thumbnails folder
thumbnails = os.listdir(os.path.abspath("..\\thumbnails"))
thumbnails_path = "..\\thumbnails\\"


# To get the colors from the thumbnails
for i in thumbnails:
    if (i[-4:] == ".txt"):
        os.remove(os.path.join(thumbnails_path, i))
        continue
    
    # Get the colors from the image into a pallette and write them 
    # to a txt file with the same name as the original gif
    temp_path = os.path.join(thumbnails_path, i)
    img = ColorThief(temp_path)
    palette = img.get_palette(color_count = 3)
    filename = thumbnails_path + i[1:-4] + ".txt"
    filename = filename.replace("converted", "")

    def is_dark_color(color):
        return sum(color) < 382

    try:
        with open(filename, "w") as f:
            
            temporary_complimentary = color_variant(get_complementary(rgb_to_hex(palette[0])),80)
            if (is_dark_color(palette[0])):
                temporary_complimentary = color_variant(rgb_to_hex(palette[0]), 120)
            
            f.write(temporary_complimentary + "\n")
            for i in palette:
                # if(i == palette[0]):
                #     f.write(color_variant(rgb_to_hex(i), 50))
                f.write(rgb_to_hex(i) + "\n")
    except Exception as e:
        print(e)





