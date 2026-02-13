# Dockerfile for Python Flask development webserver (server-side python scripting)

# Use an official Python runtime as a parent image
FROM python:3

# Allows python print() statements while using Flask to be displayed on the console
ENV PYTHONUNBUFFERED="True"

# Set the working directory in the container
# WORKDIR /usr/src/app
WORKDIR /pipeline

# Install the application dependencies
USER root 
RUN apt update && \
    apt -y install python3-pip && \
    pip install Flask                  --break-system-packages && \ 
    pip install requests               --break-system-packages && \
    pip install mysql-connector-python --break-system-packages && \
    pip install boto3                  --break-system-packages

# Copy server-side python code contents into the container
# COPY app.py /usr/src/app
COPY app.py ./

# Expose port 8000
EXPOSE 8000

# Run the Python Flask development web server
CMD ["python3", "app.py"]

