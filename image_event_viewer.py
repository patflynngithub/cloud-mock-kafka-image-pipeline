"""
This is standalone (from Apache Kafka) python program that displays an image event

It accepts input of the image event alert number and displays the images making up the event
"""

from constants.CONSTANTS import *

import tkinter as tk
from PIL import ImageTk, Image
import traceback

class ImageEventAlert(tk.Tk):

    def __init__(self):

        """
        Sets up the tkinter GUI interface
        """

        super().__init__()

        self.title("View Image Event")
        self.geometry("1200x500")

        alert_num_label = tk.Label(self, text="Input Image Event Alert # and press ENTER", bg="lightgrey", fg="black", pady=10)
        self.enter_image_event_alert_num = tk.Text(self, width=10, height=1)

        alert_num_label.pack(side=tk.TOP, fill=tk.X)
        self.enter_image_event_alert_num.pack(side=tk.TOP)
        self.enter_image_event_alert_num.focus_set()

        self.bind("<Return>", self.process_image_event_alert)

        images_frame = tk.Frame(self, bg='lightblue', width=400, height=150)

        # ------------------------------------

        image_frame = tk.Frame(images_frame, bg='lightblue', width=400, height=150)

        self.image_label = tk.Label(image_frame, image=None, text="Image", compound=tk.TOP)
    
        self.image_label.pack(side=tk.TOP, pady=20)
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ------------------------------------

        diff_image_frame = tk.Frame(images_frame, bg='lightblue', width=400, height=150)

        self.diff_image_label = tk.Label(diff_image_frame, image=None, text="Difference", compound=tk.TOP)

        self.diff_image_label.pack(side=tk.TOP, pady=20)
        diff_image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ------------------------------------

        prev_image_frame = tk.Frame(images_frame, bg='lightblue', width=400, height=150)

        self.prev_image_label = tk.Label(prev_image_frame, image=None, text="Previous Image", compound=tk.TOP)
    
        self.prev_image_label.pack(side=tk.TOP, pady=20)
        prev_image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        images_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# --------------------------------------------------------------------------------------------

    def process_image_event_alert(self, event=None):

        # print("Got to display_image_event function")

        try:
            # Get the image event alert number from the entry widget and convert to an integer
            alert_num_str = self.enter_image_event_alert_num.get(1.0, tk.END).strip()
            alert_num = int(alert_num_str)
            self.enter_image_event_alert_num.delete("1.0", "end")

            image_event_alert_path = f"{IMAGE_EVENT_ALERTS_DIR}/image_event_alert_{alert_num:03d}.txt"

            if image_event_alert_path and os.path.exists(image_event_alert_path):

                image_path, diff_image_path, prev_image_path = get_image_paths(image_event_alert_path)
                print(image_path)
                print(diff_image_path)
                print(prev_image_path)

                # Image
                # -----

                img = Image.open(image_path)
                img = img.resize((300, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo)
                # Keep a reference to the image to prevent garbage collection
                self.image = photo 

                # Difference image
                # ----------------

                img = Image.open(diff_image_path)
                img = img.resize((300, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.diff_image_label.config(image=photo)
                # Keep a reference to the image to prevent garbage collection
                self.diff_image = photo 

                # Previous image
                # --------------

                img = Image.open(prev_image_path)
                img = img.resize((300, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.prev_image_label.config(image=photo)
                # Keep a reference to the image to prevent garbage collection
                self.prev_image = photo 

                # ----------------

                # status_label.config(text=f"Displaying image, difference image and previous image", fg="green")

            else:
                # status_label.config(text=f"Can't find image alert # {image_event_alert_num} information", fg="red")
                print("hit else statement")
                self.image_label.config(image='')       # Clear the image if not found
                self.diff_image_label.config(image='')  # Clear the difference image if not found
                self.prev_image_label.config(image='')  # Clear the previous image if not found

        except ValueError:
            # status_label.config(text="Invalid input. Please enter a valid number.", fg="red")
            print(f"ValueError exception")
            self.image_label.config(image='')       # Clear the image if input is invalid
            self.diff_image_label.config(image='')  # Clear the image if input is invalid
            self.prev_image_label.config(image='')  # Clear the image if input is invalid
        except Exception as e:
            # status_label.config(text=f"An error occurred: {e}", fg="red")
            traceback.print_exc()
            print(f"An error occurred: {e}")

# -------------------------------------------------------------------------------------------------------------

def extract_path(a_string):

    """ Extract the "outside of the docker container" path. """

    start_wanted_path = a_string.find("pipeline/") + len("pipeline/")
    wanted_path = a_string[start_wanted_path:-1]

    return wanted_path

# -------------------------------------------------------------------------------------

def get_image_paths(image_event_alert_path):

    """ Get image paths from image event file. """

    # Get image event file path from image event alert file
    try:
        with open(image_event_alert_path, 'r') as f:
            lines = f.readlines()
    
        for line in lines:
            line = line.strip()
            print(line)

        image_event_path = extract_path(lines[1])
        print("Image event path: ", image_event_path)

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
            print(line) 

        image_path      = extract_path(lines[2])
        prev_image_path = extract_path(lines[3])
        diff_image_path = extract_path(lines[4])

    except FileNotFoundError:
        print(f"Error: The file '{image_event_path}' was not found.")
    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred: {e}")

    return image_path, diff_image_path, prev_image_path
    # return image_database_path, prev_image_database_path, diff_image_database_path

# ========================================================================================

if __name__ == "__main__":

    image_event_alert = ImageEventAlert()
    image_event_alert.mainloop()

