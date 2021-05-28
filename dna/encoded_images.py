import base64
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
image_file_logo = os.path.join(BASE_DIR, 'dna/resources/DNA2.png')
image_file_question = os.path.join(BASE_DIR, 'dna/resources/QuestionMark3.png')

# Create base64 encoded images for the System Tray and for a help button
with open(image_file_logo, "rb") as im_file:
    encoded_logo = base64.b64encode(im_file.read())
with open(image_file_question, "rb") as im_file:
    encoded_question = base64.b64encode(im_file.read())
