# IMAGE ANALYZER: receives Kafka messages from the image receiving client, analyzes the images
# (client)        for a phenomenon of interest, and, if the phenomenon is detected, it sends a
#                 Kafka message to the phenomenon alerter client

from constants.CONSTANTS import *

import os
import numpy as np
from PIL import Image

from kafka import KafkaConsumer
import json

# Compares the two most recent imaages in the pipeline to see if they are different
def are_images_different(image_num, prev_image_num):

    # if no previous image
    if image_num == 0:
        print("First received image. No image to compare it with")
        return False

    image_analysis_path      = IMAGE_ANALYSIS_DIR + "/" + f"{image_num:05d}"      + ".jpg"
    prev_image_analysis_path = IMAGE_ANALYSIS_DIR + "/" + f"{prev_image_num:05d}" + ".jpg"

    # Open images and convert to NumPy arrays (ensure the same dimensions and type)
    image      = np.array(Image.open(image_analysis_path).convert('L')) # Convert to grayscale for simplicity
    prev_image = np.array(Image.open(prev_image_analysis_path).convert('L'))

    # Calculate the element-wise difference
    difference = image.astype("float") - prev_image.astype("float")

    # Calculate the l2 norm of the difference vector/matrix
    # np.linalg.norm(difference) calculates the Frobenius norm for matrices,
    # which is the l2 norm for the flattened array
    l2_norm = np.linalg.norm(difference)

    # afer comparing the most recent two images, the previous image is not needed
    # in the image analysis directory anymore. The current image will become the
    # previous image
    os.remove(prev_image_analysis_path)

    # if we are dealing with the last generated image, it doesn't need to be kept around
    # in the image analysis directory to later function as the previous image 
    if image_num == TOTAL_NUM_IMAGES:
        os.remove(image_analysis_path)

    print(f"l2 norm = {l2_norm}")

    if l2_norm == 0:   # not different
       return False

    else:  # are different
       print(f"Images {image_num} and {prev_image_num} are different")
       return True

# Main part of the program
if __name__ == "__main__":

    # Create a Kafka Consumer instance
    consumer = KafkaConsumer(
        'image_analysis',  # Topic to consume from
        group_id='image_analysis_group', # Consumer group for offset management
        bootstrap_servers=['localhost:9092'], # Replace with your Kafka broker address
        auto_offset_reset='earliest', # Start consuming from the beginning if no offset is found
        enable_auto_commit=True, # Automatically commit offsets
        value_deserializer=lambda v: json.loads(v.decode('utf-8')) # Deserialize messages from JSON bytes
    )

    print()
    print("Starting image analyzer client")
    print("CODE_DIR = " + CODE_DIR)
    print()

    for message in consumer:
        print(f"Received message: Topic={message.topic}, Value={message.value}")

        image_num      = message.value["image_num"]
        prev_image_num = image_num - 1

        are_different = are_images_different(image_num, prev_image_num)
        print()

