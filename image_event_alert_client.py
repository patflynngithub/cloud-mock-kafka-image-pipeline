"""
IMAGE EVENT ALERT Kafka client: Receives an image event alert message from the Kafka image analysis
                                client, saves a new image event alert into the relational database,
                                and (not implemented yet) sends an image event alert to those who
                                have subscribed to the type of image event that has occurred.
"""

from CONSTANTS import *
from CLOUD_INFO import *

import os
import sys
import logging
import traceback
import json

# Apache Kafka for image stream message handling
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable, OffsetOutOfRangeError

# Amazon RDS MySQL database for storing image metadata and events
import mysql.connector
from mysql.connector import Error

# ===================================================================================================

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("image_event_alert_client.log", mode='w')
        ]
    )

    consumer = None
    try:

        # Create a Kafka consumer instance for receiving messages from the 
        # image analysis client
        consumer_topic = IMAGE_EVENT_ALERT_TOPIC
        consumer = KafkaConsumer(
            consumer_topic,
            client_id          = 'image event alert client',
            group_id           = 'image_event_alert_group',
            bootstrap_servers  = ['localhost:9092'],
            auto_offset_reset  = 'earliest',
            enable_auto_commit = True,
            value_deserializer = lambda v: json.loads(v.decode('utf-8'))
        )

    except (OffsetOutOfRangeError, NoBrokersAvailable, Exception) as error:
        logging.exception("KafkaConsumer initializer exception")
        exit_msg = "KafkaConsumer initialization ERROR: exiting Kafka image event alert client"
        logging.error(exit_msg)
        # passing a string to sys.exit() will always result in an exit code of 1 (failure)
        sys.exit(exit_msg)

    print()
    print("Started image event alert Kafka client")
    print("CODE_DIR = " + CODE_DIR)
    print()

    # Receive and handle Kafka messages from the Kafka image analysis client
    for message in consumer:

        print(f"Received message: Topic={message.topic}, Value={message.value}")

        image_event_id = message.value["image_event_id"]
        print(f"Image event ID = {image_event_id}")

        # Add a new image event alert to the relational database
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

                # Add new image event alert to the image event alert relational database table

                print(f"Adding new image event alert to the image event alert database table")
                add_image_event_alert_query = f"INSERT INTO image_event_alert (image_event_id) VALUES ('{image_event_id}')"
                print(add_image_event_alert_query)
                cursor.execute(add_image_event_alert_query)
                connection.commit()

                # get the image event alert ID integer just now automatically
                # generated when adding the new image event alert to the image event
                # alert database table.
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

