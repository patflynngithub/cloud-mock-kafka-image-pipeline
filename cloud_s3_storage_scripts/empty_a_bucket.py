import boto3
import sys

def empty_s3_bucket(bucket_name):
    """
    Empties an S3 bucket by deleting all objects and object versions
    (if versioning is enabled).

    Args:
        bucket_name (str): The name of the S3 bucket to empty.
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    print(f"Attempting to empty S3 bucket: {bucket_name}")

    try:
        # Check if versioning is enabled
        bucket_versioning = s3.BucketVersioning(bucket_name)
        if bucket_versioning.status == 'Enabled':
            print("Bucket versioning is ENABLED. Deleting all object versions...")
            # Deletes all object versions (including delete markers)
            bucket.object_versions.delete()
        else:
            print("Bucket versioning is DISABLED. Deleting all objects...")
            # Deletes all objects
            bucket.objects.all().delete()

        print(f"Bucket '{bucket_name}' has been emptied.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure your IAM user/role has the necessary permissions (s3:ListBucket, s3:DeleteObject, s3:DeleteObjectVersion).")

if __name__ == "__main__":

    bucket_to_empty = 'ngr-image-pipeline-bucket'
    empty_s3_bucket(bucket_to_empty)
