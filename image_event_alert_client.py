"""
IMAGE EVENT ALERT: This Kafka python client sends image event alerts to subscribers.

                   It receives an image event alert message from the Kafka image analysis
                   client, saves a new image event alert in the image event alert relational
                   database table, and (not implemented yet) sends an image event alert to those 
                   who have subscribed to the type of image event that has occurred.
"""

import os
import sys
import json

# Apache Kafka for image stream message handling
from kafka import KafkaConsumer

# Amazon RDS MySQL database for storing image metadata and events
import mysql.connector
from mysql.connector import Error

from CONSTANTS.CONSTANTS import *

# relational database and object storage access info
from CLOUD_INFO.CLOUD_INFO import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

# ===================================================================================================

if __name__ == "__main__":

    print()
    print("Starting image event alert Kafka python client ...")
    print("CODE_DIR = " + CODE_DIR)
    print()

    # -----------------------------------------------------------------------

    # Create a Kafka consumer instance for receiving image event alert
    # messages from the image analysis client
    consumer = KafkaConsumer(
        IMAGE_EVENT_ALERT_TOPIC,
        client_id          = 'image event alert client',
        group_id           = 'image_event_alert_group',
        bootstrap_servers  = ['localhost:9092'],
        auto_offset_reset  = 'earliest',
        enable_auto_commit = True,
        value_deserializer = lambda v: json.loads(v.decode('utf-8'))
    )

    # -----------------------------------------------------------------------

    # Set up a relational database (rdb) connection that will be used to store
    # image event alerts

    rdb_connection = mysql.connector.connect(
        host     = DB_HOST,
        database = DB_NAME,
        user     = DB_USER,
        password = DB_PASSWORD
    )
    
    cursor = None
    if rdb_connection.is_connected():

        rdb_info = rdb_connection.server_info
        print(f"Connected to MySQL Server version {rdb_info}")
        cursor = rdb_connection.cursor()

    # -----------------------------------------------------------------------

    # Receive and act on Kafka image event alert messages from the Kafka image analysis client
    for message in consumer:

        print(f"Received message: Topic={message.topic}, Value={message.value}")
        image_event_id = message.value["image_event_id"]
        print(f"Image event ID = {image_event_id}")

        # Add new image event alert to the image event alert relational database table

        print(f"Adding new image event alert to the image event alert database table")
        add_image_event_alert_query = f"INSERT INTO image_event_alert (image_event_id) VALUES ('{image_event_id}')"
        print(add_image_event_alert_query)
        cursor.execute(add_image_event_alert_query)
        rdb_connection.commit()

        # get the image event alert ID integer just now automatically
        # generated when adding the new image event alert to the image event
        # alert database table.
        image_event_alert_id = cursor.lastrowid
        print(f"New image event alert ID = {image_event_alert_id}")
        print()

        # HERE, EMAIL ALERTS WOULD BE SENT TO THOSE WHO HAVE SUBSCRIBED TO BE
        # ALERTED ABOUT THIS TYPE OF IMAGE EVENT

    # --------------------------------------------------------------------

    if rdb_connection is not None and rdb_connection.is_connected():
        cursor.close()
        rdb_connection.close()
        print("MySQL connection is closed.")

