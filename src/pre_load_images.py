from genericpath import exists
import os
from PIL import Image
from colorthief import ColorThief
import matplotlib.pyplot as plt



def rgb_to_hex(rgb_color):
    hex_color = "#"
    for i in rgb_color:
        i = int(i)
        hex_color += ("{:02x}".format(i))
    return hex_color


def get_complementary(color):
    color = color[1:]
    color = int(color, 16)
    comp_color = int("0xFFFFFF", base=16) - color
    comp_color = hex(comp_color)
    return str(comp_color).replace("0x", "#")


photos_path = '..\\photos'
photos = os.listdir(photos_path)

for i in photos:
    thumbnail_path = os.path.join(os.path.abspath("..\\thumbnails"), (i[:-4] + ".png"))

    img = Image.open(os.path.join(os.path.abspath(photos_path), i))
    newImage = img.convert('RGBA')
    bg = Image.new('RGBA', newImage.size)
    image = Image.composite(newImage, bg, newImage)
    image.save("..\\thumbnails\\converted" + i[:-4] + ".png")
    img.close()


photos = os.listdir(os.path.abspath("..\\thumbnails"))


for i in photos:
    temp_path = os.path.join(os.path.abspath("..\\thumbnails"), i)
    img = ColorThief(temp_path)
    palette = img.get_palette(color_count = 5)
    filename = "..\\thumbnails\\" + i[:-4] + ".txt"
    filename = filename.replace("converted", "")


    with open((filename), "a") as f:
        f.write(get_complementary(rgb_to_hex(palette[4])) + "\n")
        for j in palette:
            temp_list = list(j)
            f.write(rgb_to_hex(j) + "\n")
        f.write("\n")



# TODO
# Limpar o codigo e meter comments
# Fazer o script para apagar os ficheiros .txt cada vez que o programa é executado
# Escolher uma cor para o texto com base na imagem, talvez com o colorthief
# Fazer o batch file alternar os fundos a cada 5 ou 10 ssegundos




