"""
IMAGE ANALYSIS:  receives Apache Kafka messages from the image receiving client, analyzes images
(Kafka client)   for an image event of interest, and, if an image event is detected, it adds the 
                 event to the image event "database" and it sends a Kafka message to the image 
                 event alerting client
"""

from CONSTANTS import *
from CLOUD_INFO import *

import os
from io import BytesIO
from datetime import datetime
import logging
import json

# Numpy for doing math operations on the images
import numpy as np

# Pillow for handling images
from PIL import Image

# Apache Kafka for image stream message handling
from kafka import KafkaProducer
from kafka import KafkaConsumer

# Amazon RDS MySQL database for storing image metadata
import mysql.connector
from mysql.connector import Error

# Amazon S3 object storage for storing the images themselves
import boto3
from botocore.exceptions import ClientError

# =====================================================================

def analyze_images(image_num, image_id, image_filename, image_analysis_path):

    """
    Analyzes the current image and the previous image to see if the two are different,
    which is an image event. If so, this image event info will be saved in the image
    event database table and the generated difference image stored in object storage.
    """

    # if no previous image to compare with
    if image_num == 1:
        print("First received image. No image to compare it with")
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
    # previous image for the next received and analyzed image.
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

        # Save image event data (except for difference image) in database

        image_event_id = -1

        try:
            connection = mysql.connector.connect(
                host     = DB_HOST,
                database = DB_NAME,
                user     = DB_USER,
                password = DB_PASSWORD
            )

            if connection.is_connected():

                db_info = connection.server_info
                print(f"Connected to MySQL Server version {db_info}")

                cursor = connection.cursor()

                # Add the new image event's' metadata to the image database table,
                # except for the difference image object key, which we don't know
                # because we don't yet know the table's automatically generated
                # image_event_id, which is used to create the before mentioned key.

                print(f"Adding new image event to the image event database table")
                add_image_event_query = f"INSERT INTO image_event (image_id) VALUES ('{image_id}')"
                print(add_image_event_query)
                cursor.execute(add_image_event_query)
                connection.commit()

                # this is the integer just automatically generated for the new row's image event id
                # column in the image event table
                image_event_id = cursor.lastrowid

        except Error as e:
            print(f"Error connecting to MySQL database: {e}")

        finally:
            if connection is not None and connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed.")

        print(f"Image event created with ID # {image_event_id}")

        # Save the difference image to Amazon S3 storage;
        # the image will be saved to storage directly from memory (rather from a file in the filesystem)

        diff_image_key = f"difference_image/image_event_{image_event_id:03d}.jpg"
        buffer = BytesIO()
        diff_image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()

        # Boto3 automatically uses the IAM role attached to the EC2 instance
        s3_client  = boto3.client('s3')

        # upload the bytes directly to Amazon S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=diff_image_key,
            Body=image_bytes,
            ContentType='image/jpeg')
        s3_client.close()
        diff_image.close()

        try:
            connection = mysql.connector.connect(
                host     = DB_HOST,
                database = DB_NAME,
                user     = DB_USER,
                password = DB_PASSWORD
            )

            if connection.is_connected():

                db_info = connection.server_info
                print(f"Connected to MySQL Server version {db_info}")

                cursor = connection.cursor()

                # Update the new image event's metadata to include the difference
                # image object key, which we didn't know before because we didn't
                # yet know the image event's' automatically generated image_event_id,
                # which is used to create the before mentioned key.

                print(f"Updating new image event's difference image key value")
                update_image_event_query = f"UPDATE image_event SET difference_image_key = '{diff_image_key}' WHERE image_event_id = {image_event_id}"
                print(update_image_event_query)
                cursor.execute(update_image_event_query)
                connection.commit()

        except Error as e:
            print(f"Error connecting to MySQL database: {e}")

        finally:
            if connection is not None and connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed.")

        return [True, image_event_id]

# ===================================================================================================

if __name__ == "__main__":

    # Create a Kafka Consumer instance for receiving messages from the 
    # Kafka image receiving client
    consumer_topic = IMAGE_ANALYSIS_TOPIC
    consumer = KafkaConsumer(
        consumer_topic,
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

    print()
    print("Starting image analyzer client")
    print("CODE_DIR = " + CODE_DIR)
    print()

    # Receive and handle Kafka messages from the Kafka image receiving client
    for message in consumer:

        print(f"Received message: Topic={message.topic}, Value={message.value}")

        image_num           = message.value["image_num"]
        image_id            = message.value["image_id"]
        image_filename      = message.value["image_filename"]
        image_analysis_path = message.value["image_analysis_path"]

        # Analyze the current image and the previous image to see if the two are different,
        # which is an image event. If so, this function will also save this image event info
        # in the image event database table and store the generated difference image in 
        # object storage
        retvals = analyze_images(image_num, image_id, image_filename, image_analysis_path)

        # No image event
        if retvals[0] == False:
            print()
            continue

        # An image event has occurred
        else:
            image_event_id = retvals[1]

            # Send an image event message to the Kafka image event alert client
            message_data = {'image_event_id': image_event_id}
            producer.send(IMAGE_EVENT_ALERT_TOPIC, message_data)
            # Flush message to ensure delivery
            producer.flush()

            print(f"Sent image event ID # {image_event_id} message to the Kafka image event alert client")
            print()

