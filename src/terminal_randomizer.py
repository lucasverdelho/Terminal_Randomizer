import os
import random
import json
import re



# Find path to settings.json from input file
with open('..\\input_files\\input.txt', 'r') as f:
    json_settings_path = f.readline().replace('\n', '')
    
# Load settings.json file
with open(json_settings_path, 'r') as settings_file:
    settings = json.load(settings_file)
    settings_file.close()

# Choose random picture from folder
photos_path = '..\\photos'
photos = os.listdir(photos_path)
random_bg = random.choice(photos)

# Choose color file from folder
colors_path = '..\\thumbnails'
colors_path = os.path.join(colors_path, (random_bg[:-4] + ".txt"))

# Load colors from file
with open(colors_path, 'r') as f:
    colors = f.readlines()
    f.close()

# Select Random Color From Given Set

with open('..\\input_files\\font_colors.txt', 'r') as f:
    colors = f.readlines()

font_colors = str(colors).split(", ")
random_color = re.search("#[A-Za-z0-9]*",random.choice(font_colors)).group(0)





# Write all parameters to be change to the settings.json file
with open(json_settings_path, 'w') as settings_file:

    settings['profiles']['list'][1]['cursorColor'] = colors[3].replace('\n', '')
    settings['profiles']['list'][1]['selectionBackground'] = colors[1].replace('\n', '')
    settings['profiles']['list'][1]['backgroundImage'] = os.path.join(os.path.abspath(photos_path), random_bg)
    #settings['profiles']['list'][1]['foreground'] = colors[1].replace('\n', '')
    settings['profiles']['list'][1]['foreground'] = random_color.replace('\n', '')
    settings['profiles']['list'][1]['backgroundImageOpacity'] = random.uniform(0.3, 0.4)

    json.dump(settings, settings_file, indent=4)


# TODO
# 1. Correr o script pre load caso nao existam ficheiros na pasta thumbnails
