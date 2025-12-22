import tkinter as tk
from PIL import Image, ImageTk
import os

def extract_path(a_string):

    """ Extract the "outside of the docker container" path. """

    start_wanted_path = a_string.find("pipeline/") + len("pipeline/")
    wanted_path = a_string[start_wanted_path:-1]

    return wanted_path

# -------------------------------------------------------------------------------------

def get_image_paths(image_event_alert_path):

    """ Get image paths from image event file. """

    # Get image event file path
    try:
        with open(image_event_alert_path, 'r') as f:
            lines = f.readlines()
    
        for line in lines:
            line = line.strip()  # strip() removes leading/trailing whitespace, including \n
            print(line)

        image_event_path = extract_path(lines[1])
        print("Image event path: ", image_event_path)

    except FileNotFoundError:
        print(f"Error: Image event alert file {image_event_alert_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Get image, previous image and difference image paths
    try:
        with open(image_event_path, 'r') as f:
            lines = f.readlines()
    
        for line in lines:
            line = line.strip()  # strip() removes leading/trailing whitespace, including \n
            print(line) 

        image_database_path      = extract_path(lines[2])
        prev_image_database_path = extract_path(lines[3])
        diff_image_database_path = extract_path(lines[4])

    except FileNotFoundError:
        print(f"Error: The file '{image_event_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return image_database_path, prev_image_database_path, diff_image_database_path

# -------------------------------------------------------------------------------------

def display_images():

    """ Reads the image event alert number from the entry and displays the related image event images. """

    try:
        # Get the image event alert number from the entry widget and convert to an integer
        image_event_alert_num = int(image_event_alert_str.get())
        image_event_alert_path = f"image_event_alerts/image_event_alert_{image_event_alert_num:03d}.txt"

        if image_event_alert_path and os.path.exists(image_event_alert_path):

            image_database_path, prev_image_database_path, diff_image_database_path = \
                    get_image_paths(image_event_alert_path)

            # Image
            # -----

            img = Image.open(image_database_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            image_label.config(image=photo)
            # Keep a reference to the image to prevent garbage collection
            image_label.image = photo 

            # Difference image
            # ----------------

            img = Image.open(diff_image_database_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            diff_image_label.config(image=photo)
            # Keep a reference to the image to prevent garbage collection
            diff_image_label.image = photo 

            # Previous image
            # --------------

            img = Image.open(prev_image_database_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            prev_image_label.config(image=photo)
            # Keep a reference to the image to prevent garbage collection
            prev_image_label.image = photo 

            # ----------------

            status_label.config(text=f"Displaying image, difference image and previous image", fg="green")

        else:
            status_label.config(text=f"Can't find image alert # {image_event_alert_num} information", fg="red")
            image_label.config(image='')      # Clear the image if not found
            diff_image_label.config(image='') # Clear the difference image if not found
            prev_image_label.config(image='') # Clear the previous image if not found

    except ValueError:
        status_label.config(text="Invalid input. Please enter a valid number.", fg="red")
        image_label.config(image='') # Clear the image if input is invalid
    except Exception as e:
        status_label.config(text=f"An error occurred: {e}", fg="red")

# =====================================================================

# MAIN

# Tkinter GUI Setup

root = tk.Tk()
root.title("View Image Alert")
root.geometry("400x500")

# Label to display status messages
status_label = tk.Label(root, text="Enter the image event alert number", fg="black")
status_label.grid(row=0, column=1, padx=5, pady=5)

# Entry Widget for user input of image event alert number
image_event_alert_str = tk.StringVar()
entry = tk.Entry(root, textvariable=image_event_alert_str, font=("Helvetica", 14))
entry.grid(row=1, column=1, padx=5, pady=5)

# Button to trigger the display function
button = tk.Button(root, text="Submit Image Event Alert Number", command=display_images)
button.grid(row=2, column=1, padx=5, pady=5)

# Label to display the image
image_label = tk.Label(root)
image_label.grid(row=3, column=0, padx=5, pady=5)

# Label to display the difference image
diff_image_label = tk.Label(root)
diff_image_label.grid(row=3, column=1, padx=5, pady=5)

# Label to display the previous image
prev_image_label = tk.Label(root)
prev_image_label.grid(row=3, column=2, padx=5, pady=5)

# Start the Tkinter event loop
root.mainloop()

