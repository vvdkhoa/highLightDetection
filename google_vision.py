#  https://cloud.google.com/vision/docs/libraries#client-libraries-install-python
import io
import os
from google.cloud import vision

import csv
from datetime import datetime

class GoogleVision:

    def __init__(self, credential_json_path, image_path):
        self.credential_json_path = credential_json_path
        self.img_path = image_path
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_json_path
        self.client = vision.ImageAnnotatorClient()

    def request(self):
        file_name = os.path.abspath(self.img_path)
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()
        img = vision.Image(content=content)
        return self.client.text_detection(image=img)

    def get_description_list(self):
        response = self.request()
        text_list = response.text_annotations[0].description.split()
        return text_list


# Save list to csv column
def save_csv(words_list):
    file = 'Results/words_list_' + datetime.now().strftime("%Y%m%d_%H%M%S%f.csv")
    with open(file, 'w', newline='', encoding='utf8') as f:
        writer = csv.writer(f, delimiter=',')
        for val in words_list:
            writer.writerow([val])

# Get relative image path from relative folder path, folder_path example: "Resources/Photos/"
def getListImages(folder_path):
    onlyfiles = [folder_path + f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return onlyfiles


# Chua su dung, Remove char in word, ex: [')', ',']
def clean_word(words_list, remove_char):
    for i in range(len(words_list)):
        word = words_list[i]
        for char in remove_char:
            if char in word:
                word = word.replace(char, '')
        words_list[i] = word
    return words_list

if __name__ == '__main__':

    setting = {
        # 'credential_json_path': 'key/CloudVisionAPIDemo-2108ddfbcbfc.json',
        'credential_json_path': 'key/credential.json',
    }

    # Step 3: Using Vision to get text
    words_list = []
    c_images_list_path = getListImages("Resources/Concatenate_Images/")  # Concatenate Image list path
    for image_path in c_images_list_path:
        google_vision = GoogleVision(setting['credential_json_path'], image_path)
        words_list = words_list + google_vision.get_description_list()
    print("Total words: {}".format(len(words_list)))
    print(words_list)

    # Save CSV
    save_csv(words_list)
