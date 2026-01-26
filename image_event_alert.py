"""
IMAGE EVENT ALERT: Receives an image event alert message from the Kafka image analysis
 (Kafka client)    client, saves the image event alert info in the relational database,
                   (not implemented yet) and sends an image event alert to those who
                   have subscribed to the image event.
"""

from constants.CONSTANTS import *

import os
import numpy as np

from PIL import Image

# Apache Kafka
from kafka import KafkaConsumer
import json

# Amazon RDS MySQL database
import mysql.connector
from mysql.connector import Error

# ===================================================================================================

# RDS endpoint and database credentials
DB_HOST     = "image-pipeline.cja6aao2uw8s.us-west-2.rds.amazonaws.com"
DB_NAME     = "image_pipeline"
DB_USER     = "admin"
DB_PASSWORD = "nancygraceroman"

# -------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    # Create a Kafka Consumer instance for receiving messages from the 
    # image analysis client
    consumer_topic = IMAGE_EVENT_ALERT_TOPIC
    consumer = KafkaConsumer(
        consumer_topic,
        group_id='image_event_alert_group',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    print()
    print("Starting image event alert Kafka client")
    print("CODE_DIR = " + CODE_DIR)
    print()

    # Receive and handle Kafka messages from the image analysis Kafka client
    for message in consumer:

        print(f"Received message: Topic={message.topic}, Value={message.value}")

        image_event_id = message.value["image_event_id"]
        print(f"Image event ID = {image_event_id}")

        # Add image event alert to relational database
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

                # Add an image event alert to image alert event database table

                print(f"Adding new image event alert to the image event alert database table")
                add_image_event_alert_query = f"INSERT INTO image_event_alert (image_event_id) VALUES ('{image_event_id}')"
                print(add_image_event_alert_query)
                cursor.execute(add_image_event_alert_query)
                connection.commit()

                # this is the integer just automatically generated for the new row's
                # image_event_alert_id column in the image event alert table
                image_event_alert_id = cursor.lastrowid
                print(f"New image event alert ID = {image_event_alert_id}")
                print()

        except Error as e:
            print(f"Error connecting to MySQL database: {e}")

        finally:
            if connection is not None and connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed.")

        # HERE, EMAIL ALERTS WOULD BE SENT TO THOSE WHO HAVE SUBSCRIBED TO BE
        # ALERTED ABOUT THIS TYPE OF IMAGE EVENT


