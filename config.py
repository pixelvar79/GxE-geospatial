import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.backend_bases import PickEvent
from rasterio.transform import xy
from pyproj import CRS, Transformer
import pyproj

def get_user_input():
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window

    dialog = CustomDialog(root)
    user_input = dialog.result

    if user_input:
        width, length, horizontal_gap, vertical_gap, num_polygons, num_horizontal_polygons, \
        multiblock_option_selected, num_blocks, alley_width = user_input
    else:
        return

    return width, length, horizontal_gap, vertical_gap, num_polygons, num_horizontal_polygons, multiblock_option_selected, num_blocks, alley_width

default_values = ["2.0", "5.0", "1.0", "1.0", "100", "10", "", ""]


class CustomDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Enter width (e.g., 2.0):").grid(row=0, sticky="w")
        tk.Label(master, text="Enter length (e.g., 5.0):").grid(row=1, sticky="w")
        tk.Label(master, text="Enter horizontal gap (e.g., 1.0):").grid(row=2, sticky="w")
        tk.Label(master, text="Enter vertical gap (e.g., 1.0):").grid(row=3, sticky="w")
        tk.Label(master, text="Enter number of polygons (e.g., 100):").grid(row=4, sticky="w")
        tk.Label(master, text="Enter number of polygons in the horizontal direction (e.g., 10):").grid(row=5, sticky="w")
        tk.Label(master, text="Enable multiblock?").grid(row=6, sticky="w")
        tk.Label(master, text="Number of blocks (e.g., 5):").grid(row=7, column=0, sticky="w")
        tk.Label(master, text="Alley width (e.g., 2.0):").grid(row=8, column=0, sticky="w")

        self.entries = []  # Define the 'entries' attribute as an empty list

        for i in range(8):
            entry = tk.Entry(master)
            entry.grid(row=i, column=1)
            entry.insert(0, default_values[i])  # Insert the default value
            self.entries.append(entry)  # Append each Entry field to 'entries'

        self.multiblock_var = tk.IntVar()
        self.multiblock_checkbox = tk.Checkbutton(master, text="Enable multiblock", variable=self.multiblock_var)
        self.multiblock_checkbox.grid(row=6, column=1, columnspan=2)

        self.num_blocks_entry = tk.Entry(master)
        self.num_blocks_entry.grid(row=7, column=1)

        self.alley_width_entry = tk.Entry(master)
        self.alley_width_entry.grid(row=8, column=1)

    def apply(self):
        self.result = (
            float(self.entries[0].get()) if self.entries[0].get() else None,
            float(self.entries[1].get()) if self.entries[1].get() else None,
            float(self.entries[2].get()) if self.entries[2].get() else None,
            float(self.entries[3].get()) if self.entries[3].get() else None,
            int(self.entries[4].get()) if self.entries[4].get() else None,
            int(self.entries[5].get()) if self.entries[5].get() else None,
            self.multiblock_var.get(),
            int(self.num_blocks_entry.get()) if self.num_blocks_entry.get() else None,
            float(self.alley_width_entry.get()) if self.alley_width_entry.get() else None
        )


class ImageDisplay:
    def __init__(self, image_band, extent, transform):
        # ... (previous code)

        # Initialize variables to capture mouse clicks
        self.clicked_points = []

        # Store the georeferencing transform for pixel to coordinate conversion
        self.transform = transform

        # Keep track of the number of clicks
        self.num_clicks = 0
        
         # Store the height of the image
        self.image_height = image_band.shape[0]
        self.image_width = image_band.shape[1]
        
        self.fig, self.ax = plt.subplots(figsize=(12, 12))
        # Rotate the display by 180 degrees
        
        self.norm = Normalize(vmin=0, vmax=8000)
        self.im = self.ax.imshow(image_band, extent=extent,origin='lower')
        #self.ax.invert_xaxis()
        self.ax.invert_yaxis()
        # Connect the mouse click event
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_click)

    def on_mouse_click(self, event):
        if event.button == 3:
            if self.num_clicks < 2:
                x_pixel, y_pixel = event.xdata, event.ydata
                x_coord, y_coord = x_pixel, y_pixel
                self.clicked_points.append((x_coord, y_coord))
                print(f"Clicked at (x, y): ({x_coord}, {y_coord})")
                self.num_clicks += 1
                if self.num_clicks == 2:
                    print("Two clicks captured.")
                    if self.next_step_callback:
                        self.next_step_callback()

    def set_next_step_callback(self, callback):
        self.next_step_callback = callback

    def show(self):
        plt.show()
