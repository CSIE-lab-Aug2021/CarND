#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 15:32:35 2017

@author: priyankadwivedi
"""

## Load and check image sizes
import glob
import os
from PIL import Image
import csv
import numpy as np
import cv2
import sklearn
import random
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


## Only use udacity's data
paths = "/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/data/"
os.chdir(r"/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/data/")

new_path = os.path.join(paths, "IMG/", "*.jpg")
cwd = os.getcwd()
print(cwd)

for infile in glob.glob(new_path)[:2]:
    im = Image.open(infile)
    print(im.size, im.mode)

# All images are 320x160
# Cut size by half and overwrite existing image

df = pd.read_csv('driving_log.csv', header=0)
df.columns = ["center_image", "left_image", "right_image", "steering", "throttle", "break", "speed"]
df.drop(['throttle', 'break', 'speed'], axis = 1, inplace = True)

# Decide on crop
n = 2

file = df["center_image"][n]
img = cv2.imread(file)
#cv2.imshow('image',img)
#cv2.waitKey(0)
print(img.shape)

## Crop am image
cropped = img[60:140, :, :]
#cv2.imshow('image1',cropped)
#cv2.waitKey(0)

#df.head()

import seaborn as sns
sns.set(style="whitegrid", color_codes=True)
sns.distplot(df['steering'], kde = False)

print(len(df))

## Checking extreme values

df_sharpleft = df.loc[df['steering'] <=-0.6]
df_new = df_sharpleft.reset_index()


img = df_new["center_image"][11]
image = mpimg.imread(img)
#plt.imshow(image)

df_sharpright = df.loc[df['steering'] >= 0.6]
df_new = df_sharpright.reset_index()
print(len(df_new))

img = df_new["center_image"][7]
image = mpimg.imread(img)
#plt.imshow(image)

#8036 samples from Udacity

## Oversample left and right turns. Downsample turns close to zero.
straight =[]
left_turn = []
right_turn = []

for i in range(len(df)):

    # Very sharp right - Keep only 50% sample
    keep_prob = random.random()
    if (df["steering"][i] >0.50):
        if keep_prob<=0.50:
            right_turn.append([df["center_image"][i], df["left_image"][i], df["right_image"][i], df["steering"][i]])

    # Normal right turns - Double
    elif (df["steering"][i] >0.20 and df["steering"][i] <=0.50):
        #right_turn.append([df["center_image"][i], df["left_image"][i], df["right_image"][i], df["steering"][i]])

        for j in range(2):
            new_steering = df["steering"][i]*(1.0 + np.random.uniform(-1,1)/40.0)
            right_turn.append([df["center_image"][i], df["left_image"][i], df["right_image"][i], new_steering])

    #Very sharp Left turns - Keep only 30% of sample

    elif (df["steering"][i] < -0.50):
        if keep_prob <=0.90:
            left_turn.append([df["center_image"][i], df["left_image"][i], df["right_image"][i], df["steering"][i]])

    # Normal left turns - Double

    elif (df["steering"][i] >= -0.50 and df["steering"][i] < -0.15):

        for j in range(2):
            new_steering = df["steering"][i]*(1.0 + np.random.uniform(-1,1)/40.0)
            left_turn.append([df["center_image"][i], df["left_image"][i], df["right_image"][i], new_steering])

    ## straight driving - undersample
    elif (df["steering"][i] > -0.02 and df["steering"][i] < 0.02):
        if keep_prob <=0.90:
            straight.append([df["center_image"][i], df["left_image"][i], df["right_image"][i], df["steering"][i]])

    else:
        straight.append([df["center_image"][i], df["left_image"][i], df["right_image"][i], df["steering"][i]])

new_list = []
new_list = right_turn + left_turn + straight
print(len(new_list), len(straight), len(left_turn), len(right_turn))


df_straight = pd.DataFrame(straight, columns=["center_image", "left_image", "right_image", "steering"])
df_left = pd.DataFrame(left_turn, columns=["center_image", "left_image", "right_image", "steering"])
df_right = pd.DataFrame(right_turn, columns=["center_image", "left_image", "right_image", "steering"])

mod_df = pd.concat([df_right, df_left, df_straight], ignore_index=True)
sns.distplot(mod_df['steering'], kde = False)

#Shuffle new_list
random.shuffle(new_list)

from sklearn.model_selection import train_test_split
train_samples, validation_samples = train_test_split(new_list, test_size=0.20)

print(len(train_samples), len(validation_samples))
print(train_samples[0])

batch_size = 128

def train_generator(samples, batch_size=batch_size):
    num_samples = len(samples)
    while 1: # Loop forever so the generator never terminates
        from sklearn.utils import shuffle
        shuffle(samples)
        for offset in range(0, num_samples, batch_size):
            batch_samples = samples[offset:offset+batch_size]

            images = []
            angles = []

            for batch_sample in batch_samples:
                center_name = './IMG/'+batch_sample[0].split('/')[-1]
                center_image = cv2.imread(center_name)
                center_image = cv2.cvtColor(center_image, cv2.COLOR_BGR2RGB)
                left_name = './IMG/'+batch_sample[1].split('/')[-1]
                left_image = cv2.imread(left_name)
                left_image = cv2.cvtColor(left_image, cv2.COLOR_BGR2RGB)
                right_name = './IMG/'+batch_sample[2].split('/')[-1]
                right_image = cv2.imread(right_name)
                right_image = cv2.cvtColor(right_image, cv2.COLOR_BGR2RGB)

                center_angle = float(batch_sample[3])

                correction = 0.20
                left_angle = center_angle + correction
                right_angle = center_angle - correction

                # Randomly include either center, left or right image
                num = random.random()
                if num <= 0.33:
                    select_image = center_image
                    select_angle = center_angle
                    images.append(select_image)
                    angles.append(select_angle)
                elif num>0.33 and num<=0.66:
                    select_image = left_image
                    select_angle = left_angle
                    images.append(select_image)
                    angles.append(select_angle)
                else:
                    select_image = right_image
                    select_angle = right_angle
                    images.append(select_image)
                    angles.append(select_angle)

                # Randomly horizontally flip selected images with 80% probability
                keep_prob = random.random()
                if keep_prob >0.20:
                    flip_image = np.fliplr(select_image)
                    flip_angle = -1*select_angle
                    images.append(flip_image)
                    angles.append(flip_angle)

                # Augment with images of different brightness
                # Randomly select a percent change
                change_pct = random.uniform(0.4, 1.2)

                # Change to HSV to change the brightness V
                hsv = cv2.cvtColor(select_image, cv2.COLOR_RGB2HSV)

                hsv[:, :, 2] = hsv[:, :, 2] * change_pct
                # Convert back to RGB and append

                bright_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
                images.append(bright_img)
                angles.append(select_angle)

                ## Randomly shear image with 80% probability
                shear_prob = random.random()
                if shear_prob >=0.20:
                    shear_range = 40
                    rows, cols, ch = select_image.shape
                    dx = np.random.randint(-shear_range, shear_range + 1)
                    #    print('dx',dx)
                    random_point = [cols / 2 + dx, rows / 2]
                    pts1 = np.float32([[0, rows], [cols, rows], [cols / 2, rows / 2]])
                    pts2 = np.float32([[0, rows], [cols, rows], random_point])
                    dsteering = dx / (rows / 2) * 360 / (2 * np.pi * 25.0) / 10.0
                    M = cv2.getAffineTransform(pts1, pts2)
                    shear_image = cv2.warpAffine(center_image, M, (cols, rows), borderMode=1)
                    shear_angle = select_angle + dsteering
                    images.append(shear_image)
                    angles.append(shear_angle)

            # trim image to only see section with road
            X_train = np.array(images)
            y_train = np.array(angles)

            yield shuffle(X_train, y_train)

def valid_generator(samples, batch_size=batch_size):
        num_samples = len(samples)
        while 1:  # Loop forever so the generator never terminates
            from sklearn.utils import shuffle
            shuffle(samples)
            for offset in range(0, num_samples, batch_size):
                batch_samples = samples[offset:offset + batch_size]

                images = []
                angles = []

                for batch_sample in batch_samples:
                    center_name = './IMG/' + batch_sample[0].split('/')[-1]
                    center_image = cv2.imread(center_name)
                    center_image = cv2.cvtColor(center_image, cv2.COLOR_BGR2RGB)

                    center_angle = float(batch_sample[3])

                    images.append(center_image)
                    angles.append(center_angle)

                X_train = np.array(images)
                y_train = np.array(angles)

                yield shuffle(X_train, y_train)


# compile and train the model using the generator function
train_generator = train_generator(train_samples, batch_size=batch_size)
validation_generator = valid_generator(validation_samples, batch_size=batch_size)

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Lambda, ELU, Activation
from keras.layers.convolutional import Convolution2D, Cropping2D, ZeroPadding2D, MaxPooling2D
from keras.optimizers import SGD, Adam, RMSprop


def resize_image(image):
    import tensorflow as tf
    return tf.image.resize_images(image,[64,64])


#Params
row, col, ch = 160, 320, 3
nb_classes = 1


model = Sequential()
model.add(ZeroPadding2D((1, 1), input_shape=(row, col, ch)))
# Crop 70 pixels from top of image and 25 pixels from bottom
model.add(Cropping2D(cropping=((60, 20), (0, 0))))

# Resise data
model.add(Lambda(resize_image))
model.add(Lambda(lambda x: (x / 127.5 - 1.)))
#so the model can automatically figure out the best color space for the hypothesis
model.add(Convolution2D(3, 1, 1, border_mode='same', name='color_conv'))
# CNN model
model.add(Convolution2D(32, 3,3 ,border_mode='same', subsample=(2,2)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2),strides=(1,1)))
model.add(Convolution2D(64, 3,3 ,border_mode='same',subsample=(2,2)))
model.add(Activation('relu',name='relu2'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Convolution2D(128, 3,3,border_mode='same',subsample=(1,1)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size= (2,2)))
model.add(Flatten())
model.add(Dropout(0.5))
model.add(Dense(128))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(128))
#model.add(Activation('relu'))
#model.add(Dropout(0.5))
model.add(Dense(1))

model.compile(optimizer=Adam(lr= 0.0001), loss="mse")

# weights_path = '/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/model3.h5'
# model.load_weights(weights_path)
#
# # Make all conv layers non trainable
# for layer in model.layers[:16]:
#     layer.trainable = False
#
# model.compile(optimizer=Adam(lr= 1e-5), loss="mse")

nb_epoch = 8
samples_per_epoch = 20000
nb_val_samples = 2000


#save every model
from keras.callbacks import ModelCheckpoint
filepath="/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/checkpoint2/check-{epoch:02d}-{val_loss:.4f}.hdf5"
checkpoint = ModelCheckpoint(filepath= filepath, verbose=1, save_best_only=False)
callbacks_list = [checkpoint]

history_object = model.fit_generator(train_generator, samples_per_epoch= samples_per_epoch,
                                     validation_data=validation_generator,
                                     nb_val_samples=nb_val_samples, nb_epoch=nb_epoch, verbose=1, callbacks=callbacks_list)

import matplotlib.pyplot as plt

print(history_object.history.keys())
plt.plot(history_object.history['loss'])
plt.plot(history_object.history['val_loss'])

plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

from keras.models import model_from_json

model_json = model.to_json()
with open("/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/model5.json", "w") as json_file:
    json_file.write(model_json)

model.save("/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/model5.h5")
print("Saved model to disk")

print(model.summary())
