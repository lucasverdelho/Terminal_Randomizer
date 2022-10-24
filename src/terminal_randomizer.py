import os
import random
import json

with open('input.txt', 'r') as f:
    json_settings_path = f.readline().replace('\n', '')
    

with open(json_settings_path, 'r') as settings_file:
    settings = json.load(settings_file)
    settings_file.close()

photos_path = '..\\photos'

photos = os.listdir(photos_path)
random_bg = random.choice(photos)


with open(json_settings_path, 'w') as settings_file:

    settings['profiles']['list'][1]['backgroundImage'] = os.path.join(os.path.abspath(photos_path), random_bg)
    json.dump(settings, settings_file, indent=4)
    