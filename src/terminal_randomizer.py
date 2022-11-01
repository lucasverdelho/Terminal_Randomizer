import os
import random
import json
import re



# Set the default color scheme
def first_run(json_settings_path):


    if not (os.path.isfile("..\\thumbnails")):
        os.mkdir("..\\thumbnails")

    import pre_load_images
    pre_load_images.main()

    # Make a backup of the settings.json file
    with open(json_settings_path, 'r') as settings_file:
        settings = json.load(settings_file)
    
    with open('..\\input_files\\json_settings_backup.json', 'w') as backup_settings_file:
        json.dump(settings, backup_settings_file, indent=4)

    
    photos_path = os.path.abspath('..\\photos')
    input_path = os.path.abspath('..\\input_files')

    photo = os.path.join(photos_path, "giphy.gif")
    shader = os.path.join(input_path, "Retro.hlsl")

    
    with open("..\\input_files\\last_run_info.txt", 'w') as last_run_info:
        last_run_info.write(str(len(os.listdir(photos_path))))



    with open(json_settings_path, 'r') as f:
        data = json.load(f)
     
    data['profiles']['defaults'].update({"backgroundImage": photo})
    data['profiles']['defaults'].update({"backgroundImageOpacity": 0.3})
    data['profiles']['defaults'].update({"cursorColor": "#71BAC6"})
    data['profiles']['defaults'].update({"experimental.pixelShaderPath": shader})
    data['profiles']['defaults'].update({"foreground":"#5bd9d0"})
    data['profiles']['defaults'].update({"selectionBackground":"#634570"})
    data['profiles']['defaults'].update({"padding":"15"})
    data['profiles']['defaults'].update({"tabColor":"#df93e1"})


    with open(json_settings_path, 'w') as f:
        json.dump(data, f, indent=4)


def main():

    # Json Settings Path
    json_settings_path = os.path.expandvars(r'%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json')
    

    # If there isn't a cache file means it is the first time executing the program
    if not (os.path.isfile("..\\input_files\\last_run_info.txt")):

        first_run(json_settings_path)
     
    # Get the number of photos in the last execution
    with open("..\\input_files\\last_run_info.txt", 'r') as last_run_info:
        last_run = int(last_run_info.readline())

    # if the number of photos in the last execution is different from the current number of photos reload images
    if (last_run != len(os.listdir('..\\photos'))):
        import pre_load_images
        pre_load_images.main()

        with open("..\\input_files\\last_run_info.txt", 'w') as last_run_info:
            last_run_info.write(str(len(os.listdir('..\\photos'))))


    # Load settings.json file
    with open(json_settings_path, 'r') as settings_file:
        settings = json.load(settings_file)

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


    # Write all parameters to be changed to the settings.json file
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