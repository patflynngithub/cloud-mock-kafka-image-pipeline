# Mock Image Pipeline Using Apache Kafka

## <u>Description</u>

This is a mock image processing pipeline using Apache Kafka

It uses python Kafka clients to do the image processing work.

## <u>Commands</u>

### Build Apache Kafka image and create a container that automatically runs Apache Kafka
docker build -t pipeline_image .  
docker run -v \<path where this applications code files are stored>:/pipeline --name pipeline_container -u="root" -p 9092:9092 pipeline_image

### <u>Open a command-line window, enter the container and run the image analysis Kafka client</u>
Open a command-line window and enter the following commands:  
docker exec -it pipeline_container /bin/bash  
     (will automatically be put in /pipeline directory of container)  
python image_analysis.py

### <u>Open a command-line window, enter the container and run the image receiving Kafka client</u>
Open a command-line window and enter the following commands:  
docker exec -it pipeline_container /bin/bash  
     (will automatically be put in /pipeline directory of container)  
python image_receiving.py

