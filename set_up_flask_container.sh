#!/usr/bin/env bash

# Clean up any previous image event viewer webpage docker images and containers
docker rm python-flask-server_container
docker rmi python-flask-server_image:latest

# Set up image event viewer Flask webpage docker image/container

docker build -f Dockerfile_image_alert_webpage --progress=plain -t python-flask-server_image .

# the .. in the -v argument below references the image pipeline's main application directory;
# allows the Flask application in the container to access the data file results of the most 
# recent image pipeline run
docker run --rm -v .:/pipeline -p 80:8000 --name python-flask-server_container python-flask-server_image

