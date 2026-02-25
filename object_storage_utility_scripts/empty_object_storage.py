"""
This object storage utility empties the object storage 

Execution:
    $ python3 object_storage_utility_scripts/empty_object_storage.py
    or
    $ cd object_storage_utility_scripts
    $ python3 empty_object_storage.py
"""

import sys

import boto3

# Allows this utility to access the main application's CLOUD_INFO
# module when the utility is executed from one of two places: 
# 1) the main application directory, or
# 2) the subdirectory that the utility is in
sys.path.append("./CLOUD_INFO")   # add to module search path
sys.path.append("../CLOUD_INFO")  # add to module search path

# Object storage bucket name
from CLOUD_INFO import BUCKET_NAME

# =====================================================================

# Empty all objects from a non-versioned S3 bucket.

s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)

bucket.objects.all().delete()
print(f"Bucket '{BUCKET_NAME}' has been emptied.")

