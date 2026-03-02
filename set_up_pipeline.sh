#!/usr/bin/env bash

# Set up and run Apache Kafka container on Amazon Cloud
gnome-terminal -- bash -c 'ssh -i /home/patrick/Desktop/holding/caltech/MockImagePipeline.pem ubuntu@54.188.16.159 -t "cd ~/cloud-mock-image-pipeline; ./set_up_kafka_broker.sh"'

echo "Waiting for Kafka broker to finish setting up"
sleep 20

# Run the image event alert Kafka python client on Amazon Cloud
gnome-terminal -- bash -c 'ssh -i /home/patrick/Desktop/holding/caltech/MockImagePipeline.pem ubuntu@54.188.16.159 -t "cd ~/cloud-mock-image-pipeline; ./set_up_kafka_client.sh image_event_alert_client.py"'

# Run the image analysis Kafka python client on Amazon Cloud
gnome-terminal -- bash -c 'ssh -i /home/patrick/Desktop/holding/caltech/MockImagePipeline.pem ubuntu@54.188.16.159 -t "cd ~/cloud-mock-image-pipeline; ./set_up_kafka_client.sh image_analysis_client.py"'

# Run the image receiving Kafka python client on Amazon Cloud
gnome-terminal -- bash -c 'ssh -i /home/patrick/Desktop/holding/caltech/MockImagePipeline.pem ubuntu@54.188.16.159 -t "cd ~/cloud-mock-image-pipeline; ./set_up_kafka_client.sh image_receiving_client.py"'

