"""
Shows an Amzaon S3 bucket's contents
"""

import boto3
import logging
from botocore.exceptions import ClientError

BUCKET_NAME = 'ngr-image-pipeline-bucket'

# -------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)

# Boto3 automatically uses the IAM role attached to the EC2 instance
s3_client = boto3.client('s3')

try:

    # List objects in the bucket to verify (requires ListBucket permission)
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
    if 'Contents' in response:
        for obj in response.get('Contents', []):
            print(f"Object: {obj['Key']}")

except ClientError as e:
    logging.error(f"Failed to access S3: {e}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
