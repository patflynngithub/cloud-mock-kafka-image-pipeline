"""
This object storage utility stores an object in object storage and 
lists all the objects in object storage.

Execution:
    $ python3 object_storage_utility_scripts/store_object_and_list_objects.py
    or
    $ cd object_storage_utility_scripts
    $ python3 store_object_and_list_objects.py
"""

import boto3
from datetime import datetime
from botocore.exceptions import ClientError

import sys

# Allows this utility to access the main application's CLOUD_INFO
# module when the utility is executed from one of two places: 
# 1) the main application directory, or
# 2) the subdirectory that the utility is in
sys.path.append("./CLOUD_INFO")   # add to module search path
sys.path.append("../CLOUD_INFO")  # add to module search path

# Object storage bucket name
from CLOUD_INFO import BUCKET_NAME

# =====================================================================

# Boto3 automatically uses the IAM role attached to the EC2 instance
object_storage_client = boto3.client('s3')
object_storage_key    = 'text/first_storage_object.txt'

try:
    # Generate content for storing data (or could be a file) to object storage
    content = 'The time now is ' + str(datetime.now())

    # Upload the content to object storage
    object_storage_client.put_object(
        Body=content,
        Bucket=BUCKET_NAME,
        Key=object_storage_key
    )
    print(f"Successfully uploaded '{object_storage_key}' to '{BUCKET_NAME}'")

    # List objects in object storage to verify (requires ListBucket permission)
    response = object_storage_client.list_objects_v2(Bucket=BUCKET_NAME)
    for an_object in response.get('Contents', []):
        print(f"Object: {an_object['Key']}")

except ClientError as e:
    print(f"Failed to access object strage: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

