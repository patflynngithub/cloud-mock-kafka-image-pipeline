import os

from flask import Flask, request, send_from_directory

# Create an instance of the Flask class
app = Flask(__name__)

# Define the absolute path to your image directory
# Replace 'path/to/your/images' with the actual path
# IMAGE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'path/to/your/images')
IMAGE_FOLDER = "/pipeline"

# ----------------------------------------------------------------------------------

def extract_path(a_string):

    """ Extract the "outside of the docker container" path. """

    start_wanted_path = a_string.find("/pipeline")
    wanted_path = a_string[start_wanted_path:-1]

    return wanted_path

# -------------------------------------------------------------------------------------

def get_image_paths(image_event_alert_path):

    """ Use Image event alert file to get image paths from image event file. """

    image_path      = None
    diff_image_path = None
    prev_image_path = None

    # Get image event file path from image event alert file
    try:
        with open(image_event_alert_path, 'r') as f:
            lines = f.readlines()
    
        for line in lines:
            line = line.strip()

        image_event_path = extract_path(lines[1])

    except FileNotFoundError:
        print(f"Error: Image event alert file {image_event_alert_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Get image, previous image and difference image paths from image event file
    try:
        with open(image_event_path, 'r') as f:
            lines = f.readlines()
    
        for line in lines:
            line = line.strip()  # strip() removes leading/trailing whitespace, including \n

        image_path      = extract_path(lines[2])
        prev_image_path = extract_path(lines[3])
        diff_image_path = extract_path(lines[4])

    except FileNotFoundError:
        print(f"Error: The file '{image_event_path}' was not found.")
    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred: {e}")

    return image_path, diff_image_path, prev_image_path

# ----------------------------------------------------------------------------------------

@app.route('/pipeline/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

# ----------------------------------------------------------------------------

def get_image_event_imgs(alert_num_str):

    alert_num = int(alert_num_str)
    image_event_alert_path = f"/pipeline/image_event_alerts/image_event_alert_{alert_num:03d}.txt"

    image_path, diff_image_path, prev_image_path = get_image_paths(image_event_alert_path)

    return image_path, diff_image_path, prev_image_path

# ----------------------------------------------------------------------------------------

# Use the route() decorator to tell Flask what URL should trigger the function
@app.route('/')
def display_page():

    # note extra empty line to end the headers
    # webpage = "Content-Type: text/html\n\n"
    webpage = "<!DOCTYPE html>\n\n"

    # Now print the HTML content
    webpage += "<html>\n"
    webpage += "<head><title>Image Event Viewer</title></head>\n"
    webpage += "<body>\n"

    webpage += '<h1 style="text-align:center;">Enter an image event alert number (positive integer)</h1>\n'
    webpage += '<form style="text-align:center;" action="http://127.0.0.1:8000">\n'
    webpage += '   <label for="alert_num">Alert number:</label><br>\n'
    webpage += '   <input type="text" id="alert_num" name="alert_num"><br>\n'
    webpage += '   <input type="submit" value="Submit">\n'
    webpage += '</form>\n\n'

    alert_num = request.args.get('alert_num','')
    if alert_num:
        if not alert_num.isdecimal():
            webpage += f"<p>Alert number not a decimal': {alert_num}</p>\n"
        else:
            webpage += f"<p>Alert number: {alert_num}</p>\n"
            image_path, diff_image_path, prev_image_path = get_image_event_imgs(alert_num)

            webpage  +=  '<div style="display: flex; justify-content: center; gap: 20px;" class="image_and_prev_image">\n'
            webpage  +=  "<figure>\n"
            webpage  += f'  <img src="{prev_image_path}"" style="width: auto; height: auto; max-width: 100%;">\n'
            webpage  +=  "  <figcaption>Previous Image</figcaption>\n"
            webpage  +=  "</figure>\n"
            webpage  +=  "<figure>\n"
            webpage  += f'  <img src="{image_path}"" style="width: auto; height: auto; max-width: 100%;">\n'
            webpage  +=  "  <figcaption>Image</figcaption>\n"
            webpage  +=  "</figure>\n"
            webpage  +=  '</div>\n'

            webpage  +=  '<div style="display: flex; justify-content: center; gap: 20px;" class="diff_image">\n'
            webpage  +=  "<figure>\n"
            webpage  += f'  <img src="{diff_image_path}"" style="width: auto; height: auto; max-width: 100%;">\n'
            webpage  +=  "  <figcaption>Difference Image</figcaption>\n"
            webpage  +=  "</figure>\n"
            webpage  +=  '</div>\n'

    webpage += "</body>\n"
    webpage += "</html>\n"

    return webpage
    # return f'<p>Hello, World!</p><p>__name__={__name__}</p>'

# ==================================================================

# Run the application
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)

