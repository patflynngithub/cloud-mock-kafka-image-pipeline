#!/usr/bin/env bash

echo
echo "Trying to run the Apache Kafka container."
echo

# Clean out image directories in case previous pipeline run failed
# and didn't empty them
sudo rm -rf image_receiving/*.jpg
sudo rm -rf image_analysis/*.jpg

# Clear data in relational database and object storage
python3 database_utility_scripts/empty_database_tables.py
python3 object_storage_utility_scripts/empty_object_storage.py

# Remove previous Apache Kafka container
echo "Removing the previous Apache Kafka docker container, if it exists ..."
docker rm pipeline_container
echo

# Remove previous Apache Kafka image
echo "Removing the previous Apache Kafka docker image, if it exists ..."
docker rmi pipeline_image:latest
echo

echo "Building the Apache Kafka docker image ..."
docker build -t pipeline_image .
if [ "$?" -ne 0 ]; then
    echo "Failure building the Apache Kafka docker image" >&2
    exit 1
fi
echo "Successful"
echo

echo "Running the Apache Kafka docker container ..."
docker run --rm -v .:/pipeline --name pipeline_container -u="root" -p 9092:9092 pipeline_image
if [ "$?" -ne 0 ]; then
    echo "Failure running the Apache Kafka docker container" >&2
    exit 1
fi
echo "Successful"
echo

