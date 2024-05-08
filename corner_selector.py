import matplotlib.pyplot as plt
import numpy as np
import skimage.exposure as exposure
import rasterio
from pathlib import Path
from itertools import groupby

def select_reference_image(files):
    if not files:
        print("No TIF files found in the input list.")
        return None

    # Automatically detect the reference image with 'ortho' in the filename
    reference_file = None
    for file in files:
        if "ortho" in Path(file).stem.lower():
            reference_file = Path(file)
            break

    # If no 'ortho' reference image is found, print a message
    if reference_file is None:
        print("No reference image with 'ortho' naming pattern found.")

    return reference_file

def select_corners(reference_file):
    #fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    print("Plotting:", reference_file)
    with rasterio.open(reference_file) as src:
        # Read specific bands (e.g., 3, 2, 1 for RGB) and equalize the image
        red_band = src.read(3)
        green_band = src.read(2)
        blue_band = src.read(1)

        rgb_image = np.dstack((red_band, green_band, blue_band))
        equalized_image = exposure.equalize_hist(rgb_image)

        plt.imshow(equalized_image)
        #plt.set_title("Select 4 Corners on Reference Image")
        #ax.axis('on')

        # Store the coordinates of the clicked points
        corners = []
        
        def onclick(event):
            if event.button == 3:  # Right-click
                x, y = int(event.xdata), int(event.ydata)
                corners.append((x, y))
                plt.plot(x, y, 'ro')
                plt.draw()

        cid = plt.gcf().canvas.mpl_connect('button_press_event', onclick)
        
        # Wait for the user to click four points
        while len(corners) < 4:
            plt.pause(0.1)

    plt.close()
    plt.gcf().canvas.mpl_disconnect(cid)

    return corners
