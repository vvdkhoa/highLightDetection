# https://cloud.google.com/vision/docs/drag-and-drop?hl=ja
import csv
import glob
import os
import tkinter
import tkinter.messagebox
from datetime import datetime
from time import sleep

import cv2
import numpy as np
from PIL import Image


def resize(img, max_height=800):
    size = img.shape
    new_size = (max_height, int(max_height / size[1] * size[0]))
    return cv2.resize(img, new_size)


# Detect and return image within hsv
def detectColor(img, hsv):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([hsv[0], hsv[2], hsv[4]])
    upper = np.array([hsv[1], hsv[3], hsv[5]])
    mask = cv2.inRange(imgHSV, lower, upper)
    imgResult = cv2.bitwise_and(img, img, mask=mask)
    # cv2.imshow("Mask", resize(mask))
    # cv2.imshow("HSV",resize(imgHSV))
    # cv2.imshow("imgResult", resize(imgResult))
    # cv2.waitKey(0)
    return imgResult


# Get relative image path from relative folder path, folder_path example: "Resources/Photos/"
def getListImages(folder_path):
    onlyfiles = [folder_path + f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return onlyfiles


def save_image(img, folder):
    file_name = folder + datetime.now().strftime("%Y%m%d_%H%M%S%f.jpg")
    cv2.imwrite(file_name, img)


# Detect highlight word from photo, crop and save word img
def detect_highlight(path, setting):
    # Read
    img = cv2.imread(path)

    # Color detect
    imgColorDetected = detectColor(img, setting['hsv'])

    # Dialate
    kerner = np.ones((setting['offset_height'], setting['offset_width']),
                     np.uint8)  # Offset setting (add height, add width)
    imgCanny = cv2.Canny(imgColorDetected, 150, 200)  # edges image for detecting, Threshold values
    imgDialation = cv2.dilate(imgCanny, kerner, iterations=4)  # iterations: them pixel vào bien

    # Get contours
    imgContour = img.copy()
    contours, hierarchy = cv2.findContours(imgDialation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    i = 1
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # print("Countour Area: {}".format(area))
        if setting['min_area'] < area < setting['max_area']:
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 0), 3)  # Draw countours, Blue
            # print("Get Area: {}".format(area))

            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # objCor = len(approx)
            x, y, w, h = cv2.boundingRect(approx)

            # Crop top and bottom
            top_crop = 12  # Crop Setting
            bottom_crop = 8  # Crop Setting

            # Draw area rectangle
            cv2.rectangle(imgContour, (x, y + top_crop), (x + w, y + h - bottom_crop), (0, 255, 0), 2)

            # Crop and save
            img_cropped = img[y + top_crop: y + h - bottom_crop, x: x + w]
            save_image(img_cropped, 'Resources/Trimmed_Images/')
            sleep(0.1)
        i += 1

    cv2.imshow('Original', resize(img))
    cv2.imshow('imgCanny', resize(imgCanny))
    cv2.imshow('imgDialation', resize(imgDialation))
    cv2.imshow('Color Detected', resize(imgColorDetected))

    save_image(imgContour, 'Resources/imgContour/')
    cv2.imshow('imgContour', resize(imgContour, 1000))

    cv2.waitKey(setting['delay'])


# Copy and paste all words to white background image with default background size
# NO USING Delete after confirm
def concatenate_words_img_old(setting):
    img_path_list = getListImages('Resources/Trimmed_Images/')
    background_img = Image.new('RGB', setting['background_size'], color='white')
    paste_position = background_img.width
    for img_path in img_path_list:
        word_img = Image.open(img_path)
        paste_position = paste_position - word_img.width - 70  # Relative margin setting

        # Save concatenated Image
        if paste_position < 0:
            background_img.save('Resources/Concatenate_Images/' + datetime.now().strftime("%Y%m%d_%H%M%S%f.jpg"))
            background_img = Image.new('RGB', setting['background_size'], color='white')
            paste_position = background_img.width
        elif img_path == img_path_list[-1]:
            background_img.paste(word_img, (paste_position, 5))  # Top margin setting
            background_img.save('Resources/Concatenate_Images/' + datetime.now().strftime("%Y%m%d_%H%M%S%f.jpg"))

        # Insert image into background
        background_img.paste(word_img, (paste_position, 5))  # Top margin setting


# Copy and paste all words to white background image with default background size
def concatenate_words_img(setting, word_img_list):
    # Get background image size and create
    bg_width = 100
    bg_height = 100

    # max_words_number = 100
    # chunks_list = [word_img_list[x:x + max_words_number] for x in range(0, len(word_img_list), max_words_number)]

    for img_path in word_img_list:
        word_img = Image.open(img_path)
        if word_img.height > bg_height:
            bg_height = word_img.height + setting['top_margin'] * 2
        bg_width = bg_width + word_img.width + setting['left_margin']
    background_img = Image.new('RGB', (bg_width, bg_height), color='white')

    # Paste word into background
    paste_position = background_img.width
    for img_path in word_img_list:
        word_img = Image.open(img_path)
        paste_position = paste_position - word_img.width - setting['left_margin']
        background_img.paste(word_img, (paste_position, setting['top_margin']))

        # Save concatenated Image
        if img_path == word_img_list[-1]:
            background_img.save('Resources/Concatenate_Images/' + datetime.now().strftime("%Y%m%d_%H%M%S%f.jpg"))

    print("Concatenate Background Image size: {} x {}".format(bg_width, bg_height))
    return background_img


def clean_folder(folder_list):
    for path in folder_list:
        files = glob.glob(path + '*')
        for f in files:
            os.remove(f)


# Message box without main window, return True or False
def messagebox(title, text):
    root = tkinter.Tk()
    root.withdraw()
    res = tkinter.messagebox.askokcancel(title, text)
    root.destroy()
    print(res)
    return res

# Row 1 of csv to list, only using for string
def get_list_from_csv(path):
    with open("hsv_saved.csv", "r") as f:
        f_reader = csv.reader(f, delimiter=',')
        for row in f_reader:
            data = row
            break
    for i in range(len(data)):
        data[i] = int(data[i])
    return data

#################################################################
if __name__ == '__main__':

    # Setting
    setting = {
        'offset_height': 8,  # highlight object add height
        'offset_width': 13,  # highlight object add width
        'hsv': get_list_from_csv('hsv_saved.csv'),
        'left_margin': 100,  # Left right margin when concatenate
        'top_margin': 50,  # Top bottom margin when concatenate
        'min_area': 3000,  # Contour min Area
        'max_area': 100000,  # Contour max Area
        'credential_json_path': 'key/CloudVisionAPIDemo-2108ddfbcbfc.json',
        'delay': 1,  # Delay (ms) when show image
    }

    # Clean folder
    clean_folder(['Resources/Trimmed_Images/', 'Resources/Concatenate_Images/', 'Resources/imgContour/'])

    # Step 1: Detect highlight word from photo, crop and save word img
    images_list_path = getListImages("Resources/Photos/")
    for image_path in images_list_path:
        detect_highlight(image_path, setting)

    # Step 2: Copy and paste all words to white background image
    if messagebox('不要写真の削除', '不要写真を削除してください。\nResources/Trimmed_Images/'):
        word_img_list = getListImages('Resources/Trimmed_Images/')
        chunks = [word_img_list[100 * i:100 * (i + 1)] for i in range(int(len(word_img_list)/100 + 1))] # Chia nho list
        for word_img_list in chunks:
            concatenate_words_img(setting, word_img_list)
