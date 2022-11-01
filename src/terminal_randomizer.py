import os
import random
import json
import re



def main():
    # Check if the thumbnails folder is empty
    thumbnails_path = '..\\thumbnails'
    thumbnails = os.listdir(thumbnails_path)

    if (len(thumbnails) == 0):
        import pre_load_images
        print("shit")
        pre_load_images.main()


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