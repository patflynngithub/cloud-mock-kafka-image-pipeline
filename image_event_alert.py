"""
IMAGE EVENT ALERTER: receives an image event alert Kafka message from the image analysis
(Kafka client)       client, "sends" an image event alert to those who have subscribed to
                     the image event, and creates an image event alert info file in the
                     image event alert directory.
"""

from constants.CONSTANTS import *

import os
import numpy as np
from PIL import Image

from kafka import KafkaConsumer
import json

# ===================================================================================================

if __name__ == "__main__":

    # Create a Kafka Consumer instance for receiving messages from the 
    # image analysis client
    consumer = KafkaConsumer(
        IMAGE_EVENT_ALERT_TOPIC,
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

        image_event_num     = message.value["image_event_num"]
        image_event_db_path = message.value["image_event_db_path"]

        # HERE, EMAIL ALERTS WOULD BE SENT TO THOSE WHO HAVE SUBSCRIBED TO BE
        # ALERTED ABOUT THIS TYPE OF IMAGE EVENT

        # Create image event alert info text file for this alert
        image_event_alert_path = IMAGE_EVENT_ALERTS_DIR + "/" + f"image_event_alert_{image_event_num:03d}.txt"
        image_event_alert_lines = [f"Image event #: {image_event_num}",
                                   f"Image event database path: {image_event_db_path}",
                                   f"Image event alertees: would be listed here ..."]
        with open(image_event_alert_path, "w") as file:
            for line in image_event_alert_lines:
                file.write(f"{line}\n")

        print(f"Image event alert stored in: {image_event_alert_path}")
        print()

