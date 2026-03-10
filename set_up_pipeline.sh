#!/usr/bin/env bash

# Sets and runs the mock image pipeline on the Amazon Cloud
#
# the EC2_IP environment variable must be set to the Amazon EC2 instance's public IP address

# make sure gnome-terminal terminal program is installed
command -v "gnome-terminal" >/dev/null 2>&1
if [ "$?" -ne 0 ]; then
    echo "gnome-terminal program is not available. Either install this program or modify this file to work with another terminal program." >&2
    exit 1
fi

# make sure EC2 instance IPv4 variable has beens et
if [ -n "${EC2_IP+x}" ]; then
    echo "EC2 instance public IPV4 address: $EC2_IP"
else
    echo "EC2_IP bash variable is not set to the public IPv4 address of the EC2 instance"
    exit 1
fi

echo "Setting up and starting the Mock Image Pipeline"

# Set up and run Apache Kafka container on Amazon Cloud
gnome-terminal -- bash -c 'ssh -i /home/patrick/Desktop/holding/caltech/MockImagePipeline.pem ubuntu@$EC2_IP -t "cd ~/cloud-mock-image-pipeline; ./set_up_kafka_broker.sh"'

WAIT_SECONDS=15
echo "Waiting $WAIT_SECONDS seconds for Kafka broker to finish setting up"
sleep $WAIT_SECONDS

# Run the image event alert Kafka python client on Amazon Cloud
gnome-terminal -- bash -c 'ssh -i /home/patrick/Desktop/holding/caltech/MockImagePipeline.pem ubuntu@$EC2_IP -t "cd ~/cloud-mock-image-pipeline; ./set_up_kafka_client.sh image_event_alert_client.py; exec bash -l"'

# Run the image analysis Kafka python client on Amazon Cloud
gnome-terminal -- bash -c 'ssh -i /home/patrick/Desktop/holding/caltech/MockImagePipeline.pem ubuntu@$EC2_IP -t "cd ~/cloud-mock-image-pipeline; ./set_up_kafka_client.sh image_analysis_client.py; exec bash -l"'

# Run the image receiving Kafka python client on Amazon Cloud
gnome-terminal -- bash -c 'ssh -i /home/patrick/Desktop/holding/caltech/MockImagePipeline.pem ubuntu@$EC2_IP -t "cd ~/cloud-mock-image-pipeline; ./set_up_kafka_client.sh image_receiving_client.py; exec bash -l"'

echo "Done setting up and starting the Mock Image Pipeline"

