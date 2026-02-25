"""
This object storage utility shows all the object storage keys.

Execution:
    $ python3 object_storage_utility_scripts/show_object_storage_keys.py
    or
    $ cd object_storage_utility_scripts
    $ python3 show_object_storage_keys.py
"""

import sys

import boto3
from botocore.exceptions import ClientError

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

try:
    # List object keys in object storage (requires ListBucket permission)
    response = object_storage_client.list_objects_v2(Bucket=BUCKET_NAME)
    if 'Contents' in response:
        for an_object in response.get('Contents', []):
            print(f"Object: {an_object['Key']}")

except ClientError as e:
    print(f"Failed to access object storage: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

