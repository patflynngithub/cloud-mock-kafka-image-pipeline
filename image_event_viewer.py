"""
This standalone (standalone from Apache Kafka) python program displays an image event that occurred on the mock image pipeline.

It accepts input of the image event alert number and displays the image event's images
"""

from constants.CONSTANTS import *

import tkinter as tk
from PIL import ImageTk, Image
import traceback

# =======================================================================================

class ImageEventAlert(tk.Tk):

    def __init__(self):

        """
        Sets up the Tkinter GUI
        """

        super().__init__()

        self.title("View Image Event")
        self.geometry("1200x600")

        # Set up input area

        alert_num_entry_instruction = tk.Label(self, text="Input Image Event Alert # (positive integer) and press ENTER", bg="lightgrey", fg="black", pady=10)
        self.enter_image_event_alert_num = tk.Text(self, width=20, height=1)
        self.status_label = tk.Label(self, text = "", pady=10)

        alert_num_entry_instruction.pack(side=tk.TOP, fill=tk.X)
        self.enter_image_event_alert_num.pack(side=tk.TOP)
        self.status_label.pack(side=tk.TOP)

        self.enter_image_event_alert_num.focus_set()
        self.bind("<Return>", self.process_image_event_alert)

        # ------------------------------------

        all_images_frame = tk.Frame(self, bg='lightblue', width=400, height=150)

        # Set up Image display

        image_frame = tk.Frame(all_images_frame, bg='lightblue', width=400, height=150)

        self.image_label  = tk.Label(image_frame, image=None, text="Image", compound=tk.TOP)
        self.image_detail = tk.Label(image_frame, text="", width=20, compound=tk.TOP, bg='lightblue')

        self.image_label.pack(side=tk.TOP, pady=20)
        self.image_detail.pack(side=tk.TOP, pady=20)
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ------------------------------------

        # Set up Difference image display

        diff_image_frame = tk.Frame(all_images_frame, bg='lightblue', width=400, height=150)

        self.diff_image_label  = tk.Label(diff_image_frame, image=None, text="Difference image", compound=tk.TOP)
        self.diff_image_detail = tk.Label(diff_image_frame, text="", width=20, compound=tk.TOP, bg='lightblue')

        self.diff_image_label.pack(side=tk.TOP, pady=20)
        self.diff_image_detail.pack(side=tk.TOP, pady=20)
        diff_image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ------------------------------------

        # Set up Previous image display

        prev_image_frame = tk.Frame(all_images_frame, bg='lightblue', width=400, height=150)

        self.prev_image_label  = tk.Label(prev_image_frame, image=None, text="Previous Image", compound=tk.TOP)
        self.prev_image_detail = tk.Label(prev_image_frame, text="", width=20, compound=tk.TOP, bg='lightblue')
    
        self.prev_image_label.pack(side=tk.TOP, pady=20)
        self.prev_image_detail.pack(side=tk.TOP, pady=20)
        prev_image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        all_images_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# --------------------------------------------------------------------------------------------

    def process_image_event_alert(self, event=None):

        """
        Processes the input image event alert number, gets the image event info and displays the image event's images
        """

        # Get the image event alert number from the input
        alert_num_str = self.enter_image_event_alert_num.get(1.0, tk.END).strip()
        self.enter_image_event_alert_num.delete("1.0", "end")

        if not alert_num_str.isdecimal():
            self.status_label.config(text=f"Improper entry ({alert_num_str}). Enter a positive integer", fg="red")
            self.make_labels_blank()
            return

        alert_num = int(alert_num_str)
        image_event_alert_path = f"{IMAGE_EVENT_ALERTS_DIR}/image_event_alert_{alert_num:03d}.txt"

        if not os.path.exists(image_event_alert_path):

            self.status_label.config(text=f"Image event alert # {alert_num} doesn't exist", fg="red")
            self.make_labels_blank()

        else:

            image_path, diff_image_path, prev_image_path = get_image_paths(image_event_alert_path)

            # Image
            # -----

            img = Image.open(image_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_detail.config(text=os.path.basename(image_path))
            # Keep a reference to the image to prevent garbage collection
            self.image = photo 

            # Difference image
            # ----------------

            img = Image.open(diff_image_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.diff_image_label.config(image=photo)
            self.diff_image_detail.config(text=os.path.basename(diff_image_path))
            # Keep a reference to the image to prevent garbage collection
            self.diff_image = photo 

            # Previous image
            # --------------

            img = Image.open(prev_image_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.prev_image_label.config(image=photo)
            self.prev_image_detail.config(text=os.path.basename(prev_image_path))
            # Keep a reference to the image to prevent garbage collection
            self.prev_image = photo 

            # ----------------

            self.status_label.config(text=f"Image event alert # {alert_num}. Displaying image, difference image and previous image", fg="green")

    def make_labels_blank(self):

        """ Used to clear labels if there is a bad image event alert number entry """

        self.image_label.config(image='')
        self.diff_image_label.config(image='')
        self.prev_image_label.config(image='')
        # ---
        self.image_detail.config(text="")
        self.diff_image_detail.config(text="")
        self.prev_image_detail.config(text="")

# -------------------------------------------------------------------------------------------------------------

def extract_path(a_string):

    """ Extract the "outside of the docker container" path. """

    start_wanted_path = a_string.find("pipeline/") + len("pipeline/")
    wanted_path = a_string[start_wanted_path:-1]

    return wanted_path

# -------------------------------------------------------------------------------------

def get_image_paths(image_event_alert_path):

    """ Use Image event alert file to get image paths from image event file. """

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

# ========================================================================================

if __name__ == "__main__":

    image_event_alert = ImageEventAlert()
    image_event_alert.mainloop()

