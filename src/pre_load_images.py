import os
import random
import json
from collections import Counter
import matplotlib.image as mpimg
from matplotlib import colors
import matplotlib.pyplot as plt
import pandas as pd
from scipy.cluster.vq import whiten
from sklearn.cluster import KMeans
import numpy as np
import cv2
from PIL import Image
from glob import glob
import PIL



def rgb_to_hex(rgb_color):
    hex_color = "#"
    for i in rgb_color:
        i = int(i)
        hex_color += ("{:02x}".format(i))
    return hex_color

def prep_image(raw_img):
    modified_img = cv2.resize(raw_img, (900, 600), interpolation = cv2.INTER_AREA)
    modified_img = modified_img.reshape(modified_img.shape[0]*modified_img.shape[1], 3)
    return modified_img

def color_analysis(img):
    clf = KMeans(n_clusters = 5)
    color_labels = clf.fit_predict(img)
    center_colors = clf.cluster_centers_
    counts = Counter(color_labels)
    ordered_colors = [center_colors[i] for i in counts.keys()]
    hex_colors = [rgb_to_hex(ordered_colors[i]) for i in counts.keys()]
    plt.figure(figsize = (12, 8))
    plt.pie(counts.values(), color_labels = hex_colors, colors = hex_colors)
    plt.savefig("color_analysis_report.png")
    print(hex_colors)




photos_path = '..\\photos'
photos = os.listdir(photos_path)

for i in photos:
    thumbnail_path = os.path.join(os.path.abspath("..\\thumbnails"), (i[:-4] + ".png"))

    # if os.path.exists(thumbnail_path):
    #     print("Thumbnail already exists")
    #     continue

    img = Image.open(os.path.join(os.path.abspath(photos_path), i))
    newImage = img.convert('RGBA')
    bg = Image.new('RGBA', newImage.size)
    image = Image.composite(newImage, bg, newImage)
    image.save("..\\thumbnails\\converted" + i[:-4] + ".png")
    img.close()


photos = os.listdir(os.path.abspath("..\\thumbnails"))
# # Load image
for i in photos:
    thumbnail_path = os.path.join(os.path.abspath("..\\thumbnails"), (i[:-4] + ".png"))

    image = cv2.imread(thumbnail_path)
    print(image.shape)
    image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    modified_image = prep_image(image)
    primary_colors = color_analysis(modified_image)
    image.close()










# # Function that calculates the primary colors of a picture
# def get_primary_colors(img):
    
#     # Saving the RGB values of all the pixels in separate lists
#     r = []
#     g = []
#     b = []
#     for row in img:
#         for temp_r, temp_g, temp_b, temp in row:
#             r.append(temp_r)
#             g.append(temp_g)
#             b.append(temp_b)

#     print(len(r))
#     print(len(g))
#     print(len(b))

#     img_df = pd.DataFrame({'red':r, 'green':g, 'blue':b})

#     #Scale the values
#     img_df['scaled_red'] = whiten(img_df['red'])
#     img_df['scaled_green'] = whiten(img_df['green'])
#     img_df['scaled_blue'] = whiten(img_df['blue'])


#     distortions = []
#     num_clusters = range(1,7)

#     for i in num_clusters:
#         cluster_centers, distortion = kmeans(img[['scaled_color_red', 
#                                                     'scaled_color_blue', 
#                                                     'scaled_color_green']], i)
#         distortions.append(distortion)





# # Choose random picture from folder
# photos_path = '..\\photos'
# photos = os.listdir(photos_path)
# random_bg = random.choice(photos)
 
# image_for_analysis = mpimg.imread(photos_path + '\\' + random_bg)

# primary_colors = []
# primary_colors = get_primary_colors(image_for_analysis)


