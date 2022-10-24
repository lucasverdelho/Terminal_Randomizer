import os
import random
import json
import matplotlib.image as mpimg
import pandas as pd
from scipy.cluster.vq import whiten
from PIL import Image, ImageFilter



# Function that calculates the primary colors of a picture
def get_primary_colors(img):
    
    # Saving the RGB values of all the pixels in separate lists
    r = []
    g = []
    b = []
    for row in img:
        for temp_r, temp_g, temp_b, temp in row:
            r.append(temp_r)
            g.append(temp_g)
            b.append(temp_b)

    print(len(r))
    print(len(g))
    print(len(b))

    img_df = pd.DataFrame({'red':r, 'green':g, 'blue':b})

    #Scale the values
    img_df['scaled_red'] = whiten(img_df['red'])
    img_df['scaled_green'] = whiten(img_df['green'])
    img_df['scaled_blue'] = whiten(img_df['blue'])


    distortions = []
    num_clusters = range(1,7)

    for i in num_clusters:
        cluster_centers, distortion = kmeans(img[['scaled_color_red', 
                                                    'scaled_color_blue', 
                                                    'scaled_color_green']], i)
        distortions.append(distortion)





# Choose random picture from folder
photos_path = '..\\photos'
photos = os.listdir(photos_path)
random_bg = random.choice(photos)
 
image_for_analysis = mpimg.imread(photos_path + '\\' + random_bg)

primary_colors = []
primary_colors = get_primary_colors(image_for_analysis)


