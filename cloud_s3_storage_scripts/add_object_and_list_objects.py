import boto3
from datetime import datetime
import logging
from botocore.exceptions import ClientError

"""
Adds an object to the S3 bucket and lists all the objects in the bucket
"""

logging.basicConfig(level=logging.INFO)

# Boto3 automatically uses the IAM role attached to the EC2 instance
s3_client = boto3.client('s3')
bucket_name = 'ngr-image-pipeline-bucket' # Replace with your S3 bucket name
object_key = 'first bucket object.txt'

try:
    # Generate content for adding data (or could be a file) to the S3 bucket
    content = 'The time now is ' + str(datetime.now())

    # Upload the content to S3
    s3_client.put_object(
        Body=content,
        Bucket=bucket_name,
        Key=object_key
    )
    logging.info(f"Successfully uploaded '{object_key}' to '{bucket_name}'")

    # List objects in the bucket to verify (requires ListBucket permission)
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    for obj in response.get('Contents', []):
        logging.info(f"Object: {obj['Key']}")

except ClientError as e:
    logging.error(f"Failed to access S3: {e}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
