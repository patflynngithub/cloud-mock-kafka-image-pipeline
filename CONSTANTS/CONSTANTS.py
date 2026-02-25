""" 
CONSTANTS for mock image pipeline application using Apache Kafka.
"""

import sys
import os

# =====================================================================

# Apache Kafka topics
IMAGE_ANALYSIS_TOPIC    = "image_analysis"
IMAGE_EVENT_ALERT_TOPIC = "image_event_alert"

CODE_DIR = os.getcwd()

# Original image is the first received image and
# is used to generate the second received image,
# which is used to generate the third received image,
# and so on.
ORIGINAL_IMAGE_DIR  = CODE_DIR + "/image_original"
ORIGINAL_IMAGE_PATH = ORIGINAL_IMAGE_DIR + "/original_image.jpg"

IMAGE_RECV_DIR         = CODE_DIR + "/image_receiving"       # directory holding new images for Kafka image receiving python client
IMAGE_ANALYSIS_DIR     = CODE_DIR + "/image_analysis"        # directory to move received images into for Kafka image analysis python client

# total number of images to be (generated and) received
TOTAL_NUM_IMAGES = 10

# --------------------------------------------------------------------------------

if __name__ == "__main__":
    print("Error: This file cannot be run directly. Please import it as a module.")
    sys.exit(1)

