#!/usr/bin/env bash

echo
echo "Trying to run the Apache Kafka container."
echo

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

