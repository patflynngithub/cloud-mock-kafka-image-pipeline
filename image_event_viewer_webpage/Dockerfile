# Use an official Python runtime as a parent image
FROM python:3
ENV PYTHONUNBUFFERED="True"

# Set the working directory in the container
WORKDIR /usr/src/app

# Install the application dependencies
USER root 
RUN apt update && \
    apt -y install python3-pip && \
    pip install Flask --break-system-packages

# Copy server-side python code contents into the container
COPY app.py /usr/src/app

# Expose port 8000
EXPOSE 8000

# Run the Python Flask development web server
CMD ["python3", "app.py"]

