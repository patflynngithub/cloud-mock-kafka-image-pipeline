import boto3
import sys

BUCKET_NAME = 'ngr-image-pipeline-bucket'

# ====================================================================================

def empty_s3_bucket():
    """
    Empties THE S3 bucket by deleting all objects and object versions
    (if versioning is enabled).
    """

    s3     = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET_NAME)

    print(f"Attempting to empty S3 bucket: {BUCKET_NAME}")

    try:
        # Check if versioning is enabled
        bucket_versioning = s3.BucketVersioning(BUCKET_NAME)
        if bucket_versioning.status == 'Enabled':
            print("Bucket versioning is ENABLED. Deleting all object versions...")
            # Deletes all object versions (including delete markers)
            bucket.object_versions.delete()
        else:
            print("Bucket versioning is DISABLED. Deleting all objects...")
            # Deletes all objects
            bucket.objects.all().delete()

        print(f"Bucket '{BUCKET_NAME}' has been emptied.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure your IAM user/role has the necessary permissions (s3:ListBucket, s3:DeleteObject, s3:DeleteObjectVersion).")

# -------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    empty_s3_bucket()

