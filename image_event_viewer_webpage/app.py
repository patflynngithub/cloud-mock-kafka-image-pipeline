"""
This is an image event viewer for the image pipeline, 
displaying a webpage to allow viewing an image event's
involved images.

It uses the python Flask framework, which allows having
dynamic webpages via server-side python scripting.

None of Flask's nice organizational and management tools are used here.
For now, I want to stay close to the low-level for generating
dynamic webpages so that I can renew and extend my basic front-end
skills.
"""

import os
from io import BytesIO
import logging

from flask import Flask, request, send_file

# Amazon RDS MySQL database
import mysql.connector
from mysql.connector import Error

# Amazon S3 object storage
import boto3
from botocore.exceptions import ClientError

# =====================================================================

# Web address for container that contains the Flask web server
# WEB_SERVER_ADDRESS = "http://127.0.0.1:8000"
WEB_SERVER_ADDRESS = "http://35.94.18.229:80"

# Amazon RDS endpoint and database credentials

DB_CONFIG = {
    'host':     'image-pipeline.cja6aao2uw8s.us-west-2.rds.amazonaws.com',
    'user':     'admin',
    'password': 'nancygraceroman',
    'database': 'image_pipeline'
}

# Amazon S3 bucket name
BUCKET_NAME = 'ngr-image-pipeline-bucket'

# =====================================================================

app = Flask(__name__)

# ----------------------------------------------------------------------------------

def get_stored_image(image_key):
    
    """
    Retrieves the stored image into memory
    """

    s3_resource = boto3.resource('s3')    
    image_file_stream = BytesIO()
    s3_resource.Bucket(BUCKET_NAME).download_fileobj(image_key, image_file_stream)
    # seek back to the beginning of the stream to make it readable
    image_file_stream.seek(0)
    
    return image_file_stream

# ----------------------------------------------------------------------------------------

@app.route('/image/<obj_key_suffix>')
@app.route('/prev_image/<obj_key_suffix>')
@app.route('/difference_image/<obj_key_suffix>')
def serve_image(obj_key_suffix):

    """
    Get webpage requested image from the object database ant send it to the web browser
    """

    route_hardcoded_part = request.url_rule.rule.split('<')[0] # e.g., Returns "/user/" part of "/user/<username>/profile"
    route_hardcoded_part = route_hardcoded_part.replace("'", "")


    # print(f"Request URL: {request.url_rule.rule}")
    # print(f"Route hardcoded part: {route_hardcoded_part}")
    # print(f"Route hardcoded part: {repr(route_hardcoded_part)}")
    # print(f"Route variable part: {obj_key_suffix}")

    if route_hardcoded_part == "/image/":

        object_key = "image/" + obj_key_suffix
        download_name = "image.jpg"

    elif route_hardcoded_part == "/prev_image/":

        object_key = "image/" + obj_key_suffix 
        download_name = "previous_image.jpg"

    elif route_hardcoded_part == "/difference_image/":

        object_key = "difference_image/" + obj_key_suffix 
        download_name = "difference_image.jpg"

    else:

        print("Improper html <img> request URL from the webpage")
        return None

    image_in_memory = get_stored_image(object_key)

    return send_file(image_in_memory,
                     mimetype='image/jpeg',
                     download_name=download_name)
    
# ----------------------------------------------------------------------------------------

def get_image_event_image_keys(alert_num):

    """
    Retrieves from the relational database the object storage keys for the stored images
    associated with the image event indicated by the image event alert number.
    """

    alert_num = int(alert_num)

    image_id       = -1
    image_key      = ""
    image_event_id = -1
    diff_image_key = ""

    try:

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        image_keys_query = f"""
        SELECT
            i.image_id AS image_id,
            i.image_key AS image_key,
            e.image_event_id AS image_event_id,
            e.difference_image_key AS difference_image_key
        FROM
            image_event_alert a
        INNER JOIN
            image_event e ON a.image_event_id = e.image_event_id
        INNER JOIN
            image i ON e.image_id = i.image_id
        WHERE a.image_event_alert_id = '{alert_num}'
        """

        cursor.execute(image_keys_query)
        results = cursor.fetchall()

        # print(f"Image keys associated with image event alert # {alert_num}")
        for row in results:
            # print(row)
            # print(f"Image ID: {row[0]}, Image key: {row[1]}, Image event ID: {row[2]}, Difference image key: {row[3]}")
            image_id = row[0]
            image_key = row[1]
            image_event_id = row[2]
            diff_image_key = row[3]

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("Database connection closed.")    

    prev_image_id  = image_id -1 
    prev_image_key = f"image/image_{prev_image_id:05d}.jpg"

    return image_key, diff_image_key, prev_image_key

# ----------------------------------------------------------------------------------------

@app.route('/')
def display_page():

    """
    Dislays the image event alert number entry dynamic webpage. 
    It handles two states of the webpage. First is the initial
    accepting of input of an image event alert number. Second is
    the display of the image event images associated with the
    input alert number.
    """

    # note extra empty line to end the header
    webpage = "<!DOCTYPE html>\n\n"

    # Collect the HTML content

    webpage += "<html>\n"
    webpage += "<head><title>Image Event Viewer</title></head>\n"
    webpage += "<body>\n"

    webpage +=  '<h2 style="text-align:center;">Enter an image event alert number</h2>\n'
    webpage +=  '<h5 style="text-align:center;">(positive integer)</h5>\n'
    webpage += f'<form style="text-align:center;" action="{WEB_SERVER_ADDRESS}">\n'
    webpage +=  '   <label for="alert_num">Alert number:</label><br>\n'
    webpage +=  '   <input type="text" id="alert_num" name="alert_num"><br>\n'
    webpage +=  '   <input type="submit" value="Submit">\n'
    webpage +=  '</form>\n\n'

    alert_num = request.args.get('alert_num','')
    if alert_num:
        if not alert_num.isdecimal():
            webpage += f'<p style="text-align:center;">Alert number needs to be a positive integer: \"{alert_num}\" entered</p>\n'

        # a positive integer number was input
        else:
            # Display the images of the image event

            webpage += f'<p style="text-align:center;">Alert number: {alert_num}</p>\n'

            image_key, diff_image_key, prev_image_key = get_image_event_image_keys(alert_num)

            webpage  +=  '<div style="display: flex; justify-content: center; gap: 20px;" class="image_and_prev_image">\n'
            webpage  +=  "<figure>\n"
            webpage  += f'  <img src="/{image_key}" style="width: auto; height: auto; max-width: 100%;">\n'
            webpage  +=  "  <figcaption>Previous Image</figcaption>\n"
            webpage  +=  "</figure>\n"
            webpage  +=  "<figure>\n"
            webpage  += f'  <img src="/{prev_image_key}" style="width: auto; height: auto; max-width: 100%;">\n'
            webpage  +=  "  <figcaption>Image</figcaption>\n"
            webpage  +=  "</figure>\n"
            webpage  +=  '</div>\n'

            webpage  +=  '<div style="display: flex; justify-content: center; gap: 20px;" class="diff_image">\n'
            webpage  +=  "<figure>\n"
            webpage  += f'  <img src="/{diff_image_key}" style="width: auto; height: auto; max-width: 100%;">\n'
            webpage  +=  "  <figcaption>Difference Image</figcaption>\n"
            webpage  +=  "</figure>\n"
            webpage  +=  '</div>\n'

    webpage += "</body>\n"
    webpage += "</html>\n"

    return webpage

# ==================================================================

if __name__ == '__main__':

    app.run(host="0.0.0.0", port=8000, debug=True)

