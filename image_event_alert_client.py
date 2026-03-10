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

def add_image_event_alert(image_event_id):
    """
    Stores new image event alert in the image event alert database table. 
    Returns the image_event_alert id number (primary key) automatically
    generated when doing this.
    """

    global cursor

    # this will contain the primary key's unique integer value automatically generated
    # when adding the image event alert to the image event alert database table
    image_event_alert_id = -1

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

            # Add new image event alert to the image event alert database table

            print(f"Adding new image event alert (for image event #{image_event_id}) to the image event alert database table")
            add_image_event_alert_query = "INSERT INTO image_event_alert (image_event_id) VALUES (%s)"
            query_data                    = (image_event_id,)
            print(add_image_event_alert_query)
            print(f"data = {query_data}")
            cursor.execute(add_image_event_alert_query, query_data)
            break

        # for this error that is out of the programmer's control, 
        # will retry mulitple times with increasing delay to insert data into database table
        except mysql.connector.OperationalError as err:
            print(f"Operational Error when adding image event alert to image event alert table")
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
            print(f"Error when adding image event alert to image event alert table")
            logging.error(err)
            # will exit the program and print a traceback
            raise RuntimeError("A fatal run-time error occurred. Exiting with traceback.")

    try:
        rdb_connection.commit()

        # retrieve the integer just automatically generated for the new row's
        # primary key image_id column in the image event alert table
        image_event_alert_id = cursor.lastrowid
        print (f"Added new image event alert to the image event alert table. New image event alert ID# is {image_event_alert_id}")

    except Error as e:
        print("Error committing image event alert to the image event alert table")
        logging.error(e)

        rdb_connection.rollback() # Roll back the INSERT transaction

        if cursor:
            cursor.close()
        if rdb_connection and rdb_connection.is_connected():
            rdb_connection.close()
            print("Database connection closed.")

        # will exit the program and print a traceback
        raise RuntimeError("A fatal run-time error occurred. Exiting with traceback.")

    return image_event_alert_id

# ---------------------------------------------------------------------------------------------------

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
        add_image_event_alert(image_event_id)

        # HERE, EMAIL ALERTS WOULD BE SENT TO THOSE WHO HAVE SUBSCRIBED TO BE
        # ALERTED ABOUT THIS TYPE OF IMAGE EVENT

    # --------------------------------------------------------------------

    if rdb_connection is not None and rdb_connection.is_connected():
        cursor.close()
        rdb_connection.close()
        print("MySQL connection is closed.")

