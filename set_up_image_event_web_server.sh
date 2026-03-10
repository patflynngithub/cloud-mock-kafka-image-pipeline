#!/usr/bin/env bash

# Sets and runs the Image Event Viewer Web Server on the Amazon Cloud
#
# the EC2_IP environment variable must be set to the Amazon EC2 instance's public IP address

# make sure gnome-terminal terminal program is installed on the local PC
command -v "gnome-terminal" >/dev/null 2>&1
if [ "$?" -ne 0 ]; then
    echo "gnome-terminal program is not available. Either install this program or modify this file to work with another terminal program." >&2
    exit 1
fi

# make sure EC2 instance IPv4 variable has been set
if [ -n "${EC2_IP+x}" ]; then
    echo "EC2 instance public IPV4 address: $EC2_IP"
else
    echo "EC2_IP bash variable is not set to the public IPv4 address of the EC2 instance"
    exit 1
fi

echo "Setting up and starting the Image Event Viewer Web Server"

# Set up and run the Image Event Viewer Web Server container on Amazon Cloud
gnome-terminal -- bash -c 'ssh -i /home/patrick/Desktop/holding/caltech/MockImagePipeline.pem ubuntu@$EC2_IP -t "cd ~/cloud-mock-image-pipeline/image_event_viewer_webpage; ./set_up_flask_container.sh"'

echo "Done setting up and starting the Image Event Viewer Web Server"

