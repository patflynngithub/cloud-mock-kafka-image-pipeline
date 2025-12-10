# IMAGE ANALYZER: receives the Kafka message from the image receiving client, analyzes the images,
# (client)        and sends an alert Kafka message if the analysis uncovers possible
#                 interesting phenomena

from constants.CONSTANTS import *

from kafka import KafkaConsumer
import json

# Create a Kafka Consumer instance
consumer = KafkaConsumer(
    'image_analysis',  # Topic to consume from
    group_id='image_analysis_group', # Consumer group for offset management
    bootstrap_servers=['localhost:9092'], # Replace with your Kafka broker address
    auto_offset_reset='earliest', # Start consuming from the beginning if no offset is found
    enable_auto_commit=True, # Automatically commit offsets
    value_deserializer=lambda v: json.loads(v.decode('utf-8')) # Deserialize messages from JSON bytes
)

print("CODE_DIR = " + CODE_DIR)
print("Starting image analyzer client")

for message in consumer:
    print(f"Received message: Topic={message.topic}, Partition={message.partition}, Offset={message.offset}, Key={message.key}, Value={message.value}")

