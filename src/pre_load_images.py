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


# Function that returns the complimentary of a given color
# TODO - Still not working great, need to brighten the output color as it is unreadable
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
# TODO - Improve the color selection
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

    try:
        with open(filename, "w") as f:
            f.write(get_complementary(rgb_to_hex(palette[3])) + "\n")
            for i in palette:
                f.write(rgb_to_hex(i) + "\n")
    except Exception as e:
        print(e)





