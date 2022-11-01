import os
import random
import json
import re


# Import the settings from the preset_settings.json file and change the paths to generic
def first_run():
    
    import pre_load_images
    pre_load_images.main()

    # Find path to settings.json from input file and copy the preset settings into it
    with open('..\\input_files\\input.txt', 'r') as f:
        json_settings_path = f.readline().replace('\n', '')
        
    with open('..\\input_files\\preset_settings.json', 'r') as f:
        preset_settings = json.load(f)

    photos_path = os.path.abspath('..\\photos')
    input_path = os.path.abspath('..\\input_files')

    preset_settings['profiles']['defaults']['backgroundImage'] = os.path.join(photos_path, "giphy.gif")
    preset_settings['profiles']['defaults']['experimental.pixelShaderPath'] = os.path.join(input_path, "Retro.hlsl")
    preset_settings['profiles']['defaults']['icon'] = os.path.join(input_path, "terminal.ico")

    with open(json_settings_path, 'w') as f:
        json.dump(preset_settings, f, indent=4)


def main():

    # Check if the thumbnails folder is empty
    thumbnails_path = '..\\thumbnails'
    thumbnails = os.listdir(thumbnails_path)
 
    if (len(thumbnails) == 0):
        first_run()


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

    # Choose the color file of the randomly selected picture
    colors_path = '..\\thumbnails'
    colors_path = os.path.join(colors_path, (random_bg[:-4] + ".txt"))

    # Load colors from file
    with open(colors_path, 'r') as f:
        colors = f.readlines()
        f.close()


    # This is an old piece of code to run in case you just want
    # a bright color as default, and it will select
    # a random color from a handpicked set

    # with open('..\\input_files\\font_colors.txt', 'r') as f:
    #     new_colors = f.readlines()

    # font_colors = str(new_colors).split(", ")
    # colors[0] = re.search("#[A-Za-z0-9]*",random.choice(font_colors)).group(0)



    # Write all parameters to be change to the settings.json file
    with open(json_settings_path, 'w') as settings_file:

        settings['profiles']['list'][1]['cursorColor'] = colors[3].replace('\n', '')
        settings['profiles']['list'][1]['selectionBackground'] = colors[1].replace('\n', '')
        settings['profiles']['list'][1]['tabColor'] = colors[1].replace('\n', '')
        settings['profiles']['list'][1]['backgroundImage'] = os.path.join(os.path.abspath(photos_path), random_bg)
        settings['profiles']['list'][1]['foreground'] = colors[0].replace('\n', '')
        settings['profiles']['list'][1]['backgroundImageOpacity'] = random.uniform(0.15, 0.3)
        
        json.dump(settings, settings_file, indent=4)



if __name__ == '__main__':
    main()