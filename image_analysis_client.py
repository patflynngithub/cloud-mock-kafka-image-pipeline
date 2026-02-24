"""
IMAGE ANALYSIS:  This Kafka image analysis python client receives Apache Kafka messages about
                 received images from the Kafka image receiving client and analyzes these images,
                 looking for an image event of interest. If an image event is detected, it
                 stores the associated difference image in object storage and the image event's
                 metadata to the relational database; it thens sends a Kafka message to the 
                 Kafka image event alert client so that subscribers to the image event will
                 be alerted.
"""

import os
from io import BytesIO
import json

# Numpy for doing math operations on the images
import numpy as np

# Pillow for handling images
from PIL import Image

# Apache Kafka for image stream message handling
from kafka import KafkaConsumer, KafkaProducer

# Amazon RDS MySQL database for storing image metadata
import mysql.connector
from mysql.connector import Error

# Amazon S3 object storage for storing the images themselves
import boto3
from botocore.exceptions import ClientError

from CONSTANTS.CONSTANTS import *

# relational database and object storage access info
from CLOUD_INFO.CLOUD_INFO import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, BUCKET_NAME

# =====================================================================

def analyze_image(image_num, image_id, image_filename, image_analysis_path):
    """
    Compares the current and previous images to see if the two are different, which
    is an image event. If so, the image event difference image will be stored in
    object storage and the image event metadata will be saved in the image event 
    metadata relational database table.
    """

    # if no previous image to compare with, then can't have an image event
    if image_num == 1:
        print("First received image. No image to compare it with. No image event")
        return [False]

    prev_image_num           = image_num - 1
    prev_image_analysis_path = IMAGE_ANALYSIS_DIR + "/" + f"image_{prev_image_num:05d}.jpg"

    # Open current and previous images and convert them to NumPy arrays (ensure the same dimensions and type)
    # note: these arrays will be float RGB (m x n x 3)
    print(f"image_analysis_path = {image_analysis_path}")
    print("Contents of the directory:")
    contents = os.listdir("./image_analysis")
    for item in contents:
       print(item)
    image      = np.array(Image.open(image_analysis_path)).astype(float)
    prev_image = np.array(Image.open(prev_image_analysis_path)).astype(float)

    # Analysis to see if the two images are different
    difference = image - prev_image
    l2_norm = np.linalg.norm(difference)
    print(f"l2 norm = {l2_norm}")

    # After comparing the two most recent images, the previous image is not needed
    # in the image analysis directory anymore. The current image will become the
    # previous image for the next analyzed image
    os.remove(prev_image_analysis_path)

    # If we are dealing with the last received image, it doesn't need to be kept around
    # in the image analysis directory 
    if image_num == TOTAL_NUM_IMAGES:
        os.remove(image_analysis_path)

    # if the two images are the same
    if l2_norm == 0:
        return [False]

    # else if the two images are different; an image event has occurred
    else:

        print(f"Image numbers {image_num} and {prev_image_num} are different")

        # Convert difference array to RGB format (uint8: 0...255)
        diff_min   = difference.min()
        diff_max   = difference.max()
        diff_range = diff_max - diff_min
        diff_01 = (difference - diff_min) / diff_range  # float between 0..1
        diff_uint8 = (diff_01 * 255.0).astype(np.uint8)
        diff_image = Image.fromarray(diff_uint8, 'RGB')

        # Add the new image event's' metadata to the image event database table,
        # except for the difference image object key, which we don't have
        # yet because we don't yet know the table's automatically generated
        # image_event_id, which is used to create the before mentioned key.

        image_event_id = -1

        print(f"Adding new image event to the image event database table")
        add_image_event_query = f"INSERT INTO image_event (image_id) VALUES ('{image_id}')"
        print(add_image_event_query)
        cursor.execute(add_image_event_query)
        rdb_connection.commit()

        # this is the unique integer automatically generated for the new data row's
        # image event id column in the image event table
        image_event_id = cursor.lastrowid
        print(f"Image event created with ID # {image_event_id}")

        # Now that we know the new image event's ID, we can save the difference image to
        # Amazon S3 object storage;
        # the image will be stored directly from memory (rather than from a file in the filesystem)

        difference_image_object_key = f"difference_image/image_event_{image_event_id:05d}.jpg"
        buffer = BytesIO()
        diff_image.save(buffer, format="JPEG")
        image_data = buffer.getvalue()

        # upload the bytes directly to Amazon S3
        object_storage_client.put_object(
            Bucket=BUCKET_NAME,
            Key=difference_image_object_key,
            Body=image_data,
            ContentType='image/jpeg')
        diff_image.close()

        # Update the new image event's metadata to include the difference
        # image object key, which we didn't know before because we didn't
        # yet know the image event's' automatically generated image_event_id,
        # which is used to create the before mentioned key.

        print(f"Updating new image event's difference image object key value")
        update_image_event_query = f"UPDATE image_event SET difference_image_object_key = '{difference_image_object_key}' WHERE image_event_id = {image_event_id}"
        print(update_image_event_query)
        cursor.execute(update_image_event_query)
        rdb_connection.commit()

        return [True, image_event_id]

# ===================================================================================================

if __name__ == "__main__":

    print()
    print("Starting image analyzer client")
    print("CODE_DIR = " + CODE_DIR)
    print()

    # Create a Kafka Consumer instance for receiving messages from the 
    # Kafka image receiving client
    consumer = KafkaConsumer(
        IMAGE_ANALYSIS_TOPIC,
        group_id='image_analysis_group',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    # Create a Kafka Producer instance for sending messages to the Kafka image event alert client
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    # --------------------------------------------------

    # Set up a relational database (rdb) connection and cursor
    # for storing image metadata

    rdb_connection = mysql.connector.connect(
        host     = DB_HOST,
        database = DB_NAME,
        user     = DB_USER,
        password = DB_PASSWORD
    )

    cursor = None
    if rdb_connection.is_connected():

        rdb_info = rdb_connection.server_info
        print(f"Connected to the relational database: {rdb_info}")
        cursor = rdb_connection.cursor()

    # --------------------------------------------------

    # Set up an object storage client for storing the images themselves

    # Boto3 automatically uses the IAM role attached to the EC2 instance
    object_storage_client  = boto3.client('s3')
    print(f"Connected to object storage")
    print()

    # --------------------------------------------------

    # Receive and act upon Kafka messages from the Kafka image receiving client
    for message in consumer:

        print(f"Received message: Topic={message.topic}, Value={message.value}")
        image_num           = message.value["image_num"]
        image_id            = message.value["image_id"]
        image_filename      = message.value["image_filename"]
        image_analysis_path = message.value["image_analysis_path"]

        # Analyzes the current and previous images to see if the two are different, which
        # is an image event. If so, the image event difference image will be stored in
        # object storage and the image event metadata will be saved in the image event 
        # relational database table.
        retvals = analyze_image(image_num, image_id, image_filename, image_analysis_path)

        # First returned value signals if an image event occured
        # False = no image event occured
        if retvals[0] == False:
            print()
            continue

        # An image event has occurred and the image event ID was also returned
        else:
            image_event_id = retvals[1]

            # Send an image event message to the Kafka image event alert client
            message_data = {'image_event_id': image_event_id}
            producer.send(IMAGE_EVENT_ALERT_TOPIC, message_data)
            # Flush message to ensure delivery
            producer.flush()
            print(f"Sent image event ID # {image_event_id} message to the Kafka image event alert client")
            print()

    # --------------------------------------------------

    if object_storage_client is not None:
        object_storage_client.close()
        print("Object storage client is closed")

    if rdb_connection is not None and rdb_connection.is_connected():
        cursor.close()
        rdb_connection.close()
        print("Relational database connection is closed")

