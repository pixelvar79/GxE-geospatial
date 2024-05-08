


import os
import random
import matplotlib.pyplot as plt
import rasterio
from skimage import exposure
import numpy as np

def generate_individual_figures(input_folder, output_folder, max_images_per_folder=25):
    # Iterate over subfolders
    for root, dirs, files in os.walk(input_folder):
        for subdir in dirs:
            subfolder_path = os.path.join(root, subdir)
            
            # Create output subfolder structure
            output_subfolder = os.path.join(output_folder, os.path.relpath(subfolder_path, input_folder))
            os.makedirs(output_subfolder, exist_ok=True)

            # List of tif files in the subfolder
            tif_files = [file for file in os.listdir(subfolder_path) if file.endswith(".tif")]

            # Shuffle the list of tif files
            random.shuffle(tif_files)

            # Limit the number of images to process per folder
            num_images_to_process = min(len(tif_files), max_images_per_folder)
            tif_files = tif_files[:num_images_to_process]

            for i, file in enumerate(tif_files):
                tif_path = os.path.join(subfolder_path, file)
                
                # Open tif file with rasterio
                with rasterio.open(tif_path) as src:
                    # Extract the second string of the name of the chip as subtitle
                    subtitle = file.split('_')[1]

                    # Read bands 4, 3, 2 as float for composite image
                    rgb_image = src.read([4, 3, 2]).astype(float)

                    # Apply histogram equalization to each band for composite image
                    for band in range(3):
                        rgb_image[band] = exposure.equalize_hist(rgb_image[band])

                    # Get chip dimensions
                    chip_width = src.width
                    chip_height = src.height

                    # Calculate aspect ratio
                    aspect_ratio = chip_width / chip_height

                    # Create a new figure for the composite image
                    fig_composite = plt.figure(figsize=(5 * aspect_ratio, 5))

                    # Show the composite image
                    plt.imshow(rgb_image.transpose((1, 2, 0)), extent=src.bounds, aspect='auto')

                    # Turn off ticks
                    plt.axis('off')

                    # Add subtitle
                    plt.title(subtitle, fontsize=8)

                    # Save the composite figure
                    output_composite_path = os.path.join(output_subfolder, f"individual_composite_{subdir}_{i + 1}.png")
                    plt.savefig(output_composite_path)
                    plt.close(fig_composite)

                    # Read band 1 as float for greyscale image
                    band_1_image = src.read(1).astype(float)

                    # Create a new figure for the greyscale image
                    fig_greyscale = plt.figure(figsize=(5 * aspect_ratio, 5))
                    
                    # Initialize an empty array to store all band_1_image values for histogram calculation
                    all_band_1_values = []
                    
                    # Store all band_1_image values for histogram calculation
                    all_band_1_values.extend(band_1_image.flatten())
                    
                    # Calculate the 5th and 95th percentiles for intensity range
                    lower_percentile, upper_percentile = np.percentile(all_band_1_values, [20, 80])
                    
                    # Adjust intensity range based on the 5th and 95th percentiles
                    band_1_image = exposure.rescale_intensity(band_1_image, in_range=(lower_percentile, upper_percentile))


                    # Show the greyscale image
                    plt.imshow(band_1_image, cmap='gray', extent=src.bounds, aspect='auto')

                    # Turn off ticks
                    plt.axis('off')

                    # Add subtitle
                    plt.title(subtitle, fontsize=8)

                    # Save the greyscale figure
                    output_greyscale_path = os.path.join(output_subfolder, f"individual_greyscale_{subdir}_{i + 1}.png")
                    plt.savefig(output_greyscale_path)
                    plt.close(fig_greyscale)

# Example usage
input_folder = "../data/images/image_chips"
output_folder = "../data/individual_figures_chips"
generate_individual_figures(input_folder, output_folder, max_images_per_folder=25)
