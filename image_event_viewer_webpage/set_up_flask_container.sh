#!/usr/bin/env bash

# Clean up any previous image event viewer webpage docker images and containers
docker rm python-flask-server_container
docker rmi python-flask-server_image:latest

# Set up image event viewer Flask webpage docker image/container

cp -f ../CONSTANTS/CONSTANTS.py .
cp -f ../CLOUD_INFO/CLOUD_INFO.py .

docker build --progress=plain -t python-flask-server_image .
docker run --rm -p 80:8000 --name python-flask-server_container python-flask-server_image

