"""
IMAGE RECEIVING:  This Kafka python client receives images from outside Apache Kafka,
                  stores these images in object storage, saves their metadata in a
                  relational database, and copies the images one by one to the image 
                  analysis directory for future analysis by the Kafka image analysis
                  client, sending an individual Kafka message for each image to 
                  that client.

                  NOTE: with this application being a MOCK image pipeline, the image stream
                  is based on a first original image. Most of the time, the next image in
                  the stream is an exact copy of the previous image. Occasionally, though,
                  the next image is a modified copy of the previous image, which results
                  in an image event when the new image is analyzed by the Kafka
                  image analysis client.
"""

# =====================================================================

import os
import sys
import shutil
import json
import logging
import time

# Pillow for image handling
from PIL import Image

# Apache Kafka for image stream message handling
from kafka import KafkaProducer

# Amazon RDS MySQL relational database for storing image metadata
import mysql.connector
from mysql.connector import errorcode

# Amazon S3 object storage for storing the images themselves
import boto3
from botocore.exceptions import ClientError

from CONSTANTS.CONSTANTS import *
# relational database and object storage access info
from CLOUD_INFO.CLOUD_INFO import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, BUCKET_NAME
from pipeline_utils.pipeline_utils import remove_ebs_file, copy_ebs_file

# =====================================================================

def generate_image(image_num, image_filename):
    """
    For the MOCK image pipeline, the image to be received is generated here from
    an original image (image # = 1) or from a previously generated image (image # > 1).
    Occasionally, the previous image is modified to create a new changed image.
    """

    image_recv_path = IMAGE_RECV_DIR + "/" + image_filename

    prev_image_num = image_num - 1

    # Use the original image for the first received image
    if image_num == 1:
        prev_image_recv_path = ""
        copy_ebs_file(ORIGINAL_IMAGE_PATH, image_recv_path)

    # Generate an image from the previously received image
    else:
        prev_image_recv_path = IMAGE_RECV_DIR + "/" + f"image_{prev_image_num:05d}.jpg"

        # Occasionally, modify the previous image to generate a new changed image
        if image_num % 4 == 3:
            print("... CHANGING IMAGE: Rotating 90°")
            prev_image = Image.open(prev_image_recv_path)
            rotated_image = prev_image.rotate(90)
            rotated_image.save(image_recv_path)
            rotated_image.close()
            prev_image.close()

        # Copy the previous image w/o modification to generate the new image
        else:
            copy_ebs_file(prev_image_recv_path, image_recv_path)

    return image_recv_path, prev_image_recv_path

# ------------------------------------------------------------------------

def store_image_metadata(image_filename, image_object_key):
    """
    Stores image metadata in relational database table. Returns the image_id number
    (primary key) automatically generated when doing this.
    """

    global cursor

    # this will contain the primary key's integer value automatically generated
    # when adding the image's metadata to the image metadata database table
    image_id = -1

    attempt  = 1
    attempts = 3
    delay    = 2
    # loop is for retrying when "retryable" cursor.execute() error happens
    while attempt <= attempts:
    
        try:
            # if the connection is lost, attempt to reconnect
            if not rdb_connection.is_connected():
                rdb_connection.reconnect()
                cursor = rdb_connection.cursor()

            # Add image's metadata to the image metadata database table

            print(f"Adding image filename {image_filename} and its image object key {image_object_key} to the image metadata database table")
            add_image_metadata_query = "INSERT INTO image_metadata (image_filename, image_object_key) VALUES (%s, %s)"
            query_data               = (image_filename, image_object_key)
            print(add_image_metadata_query)
            print(f"data = {query_data}")
            cursor.execute(add_image_metadata_query, query_data)
            break

        # for this error that is out of the programmer's control, 
        # will retry mulitple times with increasing delay to insert data into database table
        except mysql.connector.OperationalError as err:
            print(f"Operational Error when adding image metadata to image metadata table")
            logging.error(err)
            if attempt == attempts:
                print(f"Failed after {attempts} attempts")
                # will exit the program and print a traceback
                raise RuntimeError("A fatal run-time error occurred. Exiting with traceback.")
            print(f"Retrying ({attempt}/{attempts})...")
            time.sleep(delay ** (attempt-1)) # Exponential backoff
            attempt += 1
            continue

        # non-retryable error
        except mysql.connector.Error as err:
            print(f"Error when adding image metadata to image metadata table")
            logging.error(err)
            # will exit the program and print a traceback
            raise RuntimeError("A fatal run-time error occurred. Exiting with traceback.")

    try:
        rdb_connection.commit()

        # retrieve the integer just automatically generated for the new row's
        # primary key image_id column in the image metadata table
        image_id = cursor.lastrowid
        print (f"Added image metadata. Image ID# is {image_id}")

    except Error as e:
        print("Error committing image metadata to the image metadata table")
        logging.error(e)

        rdb_connection.rollback() # Roll back the INSERT transaction

        if cursor:
            cursor.close()
        if rdb_connection and rdb_connection.is_connected():
            rdb_connection.close()
            print("Database connection closed.")

        # will exit the program and print a traceback
        raise RuntimeError("A fatal run-time error occurred. Exiting with traceback.")

    return image_id

# ------------------------------------------------------------------------

def store_image(image_filename, image_recv_path):
    """
    Stores the image itself in object storage. Returns image object key.
    """

    image_object_key = f'image/{image_filename}'

    try:
        """
        Note: Do not need to have retry logic for upload_file() method because
              Boto3's built-in retry mechanism handles temporary, recoverable failures.
              It can be relied on for network issues, timeouts, server-side Errors (HTTP 5xx),
              and throttling Errors (HTTP 429).

              For large files, the upload_file() method automatically leverages multipart uploads,
              which breaks the file into parts and retries individual part failures without
              restarting the entire upload. 
        """

        object_storage_client.upload_file(image_recv_path, BUCKET_NAME, image_object_key)
        return image_object_key

    except ClientError as e:
        # Log and handle AWS service-side errors (e.g., NoSuchBucket, AccessDenied)
        logging.error(e)
        error_code = e.response.get('Error', {}).get('Code')
        print(f"AWS Error (while storing '{image_recv_path}'): {error_code}")
    except FileNotFoundError:
        logging.error(f"{e} The file '{image_recv_path}' was not found.")

    raise RuntimeError("A run-time error occurred, exiting with traceback.")

# -----------------------------------------------------------------------------------

def receive_image(image_num, image_filename, image_recv_path, prev_image_recv_path):
    """
    Receives the next image: storing the image itself in object storage, storing
    its metadata in a relational database, and putting a copy of it in
    the image analysis directory so that the Kafka image analysis client
    can analyze it.
    """

    # store image itself in object storage
    image_object_key = store_image(image_filename, image_recv_path)

    # store image metadata in relational database;
    # returned new image_id will be passed to the Kafka image analysis client
    image_id = store_image_metadata(image_filename, image_object_key)

    # Copy received image to the image analysis directory
    # so that the Kafka image analysis client can analyze it
    # using the previously received image that was already
    # copied there in the previous iteration
    image_analysis_path = IMAGE_ANALYSIS_DIR + "/" + image_filename
    copy_ebs_file(image_recv_path, image_analysis_path)

    # if on second or later received image in the image stream, remove the
    # previously received image from the image receiving directory
    # because don't need it anymore for generating the next image
    if image_num > 1:
        remove_ebs_file(prev_image_recv_path)

    # if just received the last image in the image stream, don't need
    # to keep it around in the image receiving directory to use as a
    # a previous image to generate the next image
    if image_num == TOTAL_NUM_IMAGES:
        remove_ebs_file(image_recv_path)

    return image_id, image_analysis_path

# ===================================================================================

if __name__ == "__main__":

    print()
    print("Starting image receiving Kafka python client ...")
    print("CODE_DIR = ",CODE_DIR)
    print()

    # Create a Kafka Producer instance for sending messages
    # to the Kafka image analysis client
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

    # Main part of the Kafka image receiving python client

    image_num  =  1
    while image_num <= TOTAL_NUM_IMAGES:

        # Since this a MOCK image pipeline, need to generate the next image to be received
        print("Generating Image # = ", image_num)
        image_filename = f"image_{image_num:05d}.jpg"
        image_recv_path, prev_image_recv_path = generate_image(image_num, image_filename)

        # Receive the image: i.e., store image itself, store image's metadata, and prepare
        # a copy of the image for the Kafka image analysis client
        print("Receiving Image # ", image_num)
        image_id, image_analysis_path = receive_image(image_num, image_filename, 
                                                      image_recv_path, prev_image_recv_path)

        # Send a Kafka message to the Kafka image analysis client, alerting the client
        # that there is an image in its image analysis directory that is ready to be analyzed
        message_data = {'image_num': image_num, 'image_id': image_id, 'image_filename': image_filename,
                        'image_analysis_path': image_analysis_path}
        producer.send(IMAGE_ANALYSIS_TOPIC, message_data)
        producer.flush()  # flush message to ensure delivery
        print(f"Message sent to topic '{IMAGE_ANALYSIS_TOPIC}': {message_data}")
        print()

        image_num += 1

    # --------------------------------------------------

    if object_storage_client is not None:
        object_storage_client.close()
        print("Object storage client is closed")

    if cursor:
        cursor.close()
    if rdb_connection is not None and rdb_connection.is_connected():
        rdb_connection.close()
        print("Relational database connection is closed")

