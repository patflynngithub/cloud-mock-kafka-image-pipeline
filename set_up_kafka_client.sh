#!/usr/bin/env bash

python_client_filename=$1

echo
echo "Trying to run the \"$python_client_filename\" Kafka python client."
echo

# check if Apache Kafka broker is running
echo "Checking if Apache Kafka broker is running ..."
nc -vz localhost 9092
if [ "$?" -ne 0 ]; then
    echo "Apache Kafka doesn't appear to be running. Exiting ${BASH_SOURCE[0]} bash script." >&2
    exit 1
fi

# Enter running Apache Kafka container and run a Kafka python client
docker exec -it pipeline_container bash -c "python3 $python_client_filename"
if [ "$?" -ne 0 ]; then
    echo
    echo "Can't enter Apache Kafka container or can't run \"$python_client_filename\" in the container or just Ctrl-C'd out of the executing Kafka python client in the container. Exiting ${BASH_SOURCE[0]} bash script." >&2
    exit 1
fi

