# IMAGE PRODUCER: "receives" the image from outside Apache Kafka, "stores" it,
# (client)        and sends a Kafka message about it to the image analyzer client

from constants.CONSTANTS import *

from kafka import KafkaProducer
import json

print(CODE_DIR)

# Create a Kafka Producer instance
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],  # Replace with your Kafka broker address
    value_serializer=lambda v: json.dumps(v).encode('utf-8') # Serialize messages to JSON bytes
)

print("CODE_DIR = " + CODE_DIR)
print("Starting image receiving client ...")

# Send a message to a topic
topic_name = 'image_analysis'
message_data = {'id': 1, 'name': 'example_message'}
producer.send(topic_name, message_data)

# Flush messages to ensure delivery
producer.flush()
print(f"Message sent to topic '{topic_name}': {message_data}")
