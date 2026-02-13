"""
Provides info about Amazon Cloud resources that the image pipeline uses
"""

import sys

# =====================================================================

if __name__ == "__main__":
    print("Error: This file cannot be run directly. Please import it as a module.")
    sys.exit(1)

# =====================================================================

# Amazon RDS endpoint and database credentials
DB_HOST     = "image-pipeline.cja6aao2uw8s.us-west-2.rds.amazonaws.com"
DB_NAME     = "image_pipeline"
DB_USER     = "admin"
DB_PASSWORD = "nancygraceroman"

# Amazon S3 bucket name
BUCKET_NAME = 'ngr-image-pipeline-bucket'

