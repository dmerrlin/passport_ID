
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'



import imghdr
import numpy as np
import pathlib
import pytesseract
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras import optimizers
from tensorflow.keras.layers import Convolution2D, MaxPooling2D, Dropout, Flatten, Dense, Reshape, LSTM, BatchNormalization
from tensorflow.keras.optimizers import SGD, RMSprop, Adam
from tensorflow.keras import backend as K
from keras.constraints import maxnorm
import tensorflow as tf
from scipy import io as spio
import idx2numpy  # sudo pip3 install idx2numpy
from matplotlib import pyplot as plt
from typing import *
import time
from cv2 import cv2
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

emnist_labels = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]

def emnist_predict_img(model, img):
    img_arr = np.expand_dims(img, axis=0)
    img_arr = 1 - (img_arr/255.0)


    img_arr[0] = np.rot90(img_arr[0], 3)
    img_arr[0] = np.fliplr(img_arr[0])
    img_arr = img_arr.reshape((1, 28, 28, 1))
    result = model.predict_classes([img_arr])
    res = model.predict_proba([img_arr])
    return chr(emnist_labels[result[0]])

def letters_extract(image_file: str, out_size=28):

    img = cv2.imread(image_file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)

    img_erode = cv2.erode(thresh, np.ones((2, 2), np.uint16), iterations=1)

    contours, hierarchy = cv2.findContours(img_erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    output = img.copy()


    letters = []
    y1 = 0
    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)

        if hierarchy[0][idx][3] == 0:


            if (w > 15):
                for i in range(w // 10):
                    cv2.rectangle(output, (x, y), (x + 11, y + 13), (70, 0, 0), 1)
                    letter_crop = gray[y:y + 11, x-2:x + 11]
                    y1 += 1
                    x += 10

                    letters.append((x, 18, cv2.resize(letter_crop, (out_size, out_size), interpolation=cv2.INTER_AREA)))
            else:
                y1 += 1
                cv2.rectangle(output, (x, y), (x + 14, y + 14), (70, 0, 0), 1)
                letter_crop = gray[y:y + 11, x-2:x + 11]

                letters.append((x, 18, cv2.resize(letter_crop, (out_size, out_size), interpolation=cv2.INTER_AREA)))





    cv2.waitKey(0)
    # Sort array in place by X-coordinate
    letters.sort(key=lambda x: x[0] , reverse=False)
    return letters


def img_to_str(model: Any, image_file: str):
    letters = letters_extract(image_file)
    s_out = ""
    for i in range(len(letters)):

        dn = letters[i+1][0] - letters[i][0] - letters[i][1] if i < len(letters) - 1 else 0

        s_out += emnist_predict_img(model, letters[i][2])

        if (dn > letters[i][1]/4):
            s_out += ' '
    return s_out


if __name__ == "__main__":
    img = cv2.imread("D:\\output.png")
    config = r'--oem 3 --psm 6'

    print(pytesseract.image_to_string(img, lang='mrz', config=config))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    img_erode = cv2.erode(thresh, np.ones((10, 10), np.uint16), iterations=1)
    contours, hierarchy = cv2.findContours(img_erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    model = keras.models.load_model('emnist_letters1.h5')
    output = img.copy()
    letters = []
    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        print (x, y, w, h)
        if hierarchy[0][idx][3] == 0:

            cv2.rectangle(output, (x, y), (x + w, y + h), (70, 0, 0), 1)
            letter_crop = gray[y:y + h, x:x + w]
            im = Image.fromarray(letter_crop)
            im.save("1.png")
           # s_out = img_to_str(model, "1.png")
            #print(s_out)


