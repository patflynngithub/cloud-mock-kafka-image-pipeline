# For development phase of project (source code outside of container)

FROM apache/kafka:4.1.1
WORKDIR /pipeline

# Install the application dependencies
USER root
RUN apk add python3 && \
    apk add py3-pip && \
    pip install numpy                  --break-system-packages && \
    pip install kafka-python           --break-system-packages && \
    pip install Pillow                 --break-system-packages && \
    pip install mysql-connector-python --break-system-packages && \
    pip install boto3                  --break-system-packages

# Copy the source code into the container
COPY *.py ./
COPY constants/*.py ./constants/
COPY image_original/* ./image_original/


EXPOSE 9092

