
import os
import matplotlib.pyplot as plt
import rasterio
from skimage import exposure
import numpy as np

def generate_subplot(input_folder, output_folder, max_images_per_subplot=25, max_subplot_figures=5):
    # Iterate over subfolders
    for root, dirs, files in os.walk(input_folder):
        for subdir in dirs:
            subfolder_path = os.path.join(root, subdir)
            
            # Create output subfolder structure
            output_subfolder = os.path.join(output_folder, os.path.relpath(subfolder_path, input_folder))
            os.makedirs(output_subfolder, exist_ok=True)

            # List of tif files in the subfolder
            tif_files = [file for file in os.listdir(subfolder_path) if file.endswith(".tif")]

            # Calculate the number of subplots needed
            num_subplots = -(-len(tif_files) // max_images_per_subplot)  # Equivalent to ceil(len(tif_files) / max_images_per_subplot)
            num_subplot_figures = min(num_subplots, max_subplot_figures)

            for subplot_figure_index in range(num_subplot_figures):
                # Initialize composite subplot
                fig_composite, axs_composite = plt.subplots(5, 5, figsize=(15, 15))

                # Initialize greyscale subplot
                fig_greyscale, axs_greyscale = plt.subplots(5, 5, figsize=(15, 15))

                # Pick a batch of up to max_images_per_subplot tif files
                start_idx = subplot_figure_index * max_images_per_subplot
                end_idx = (subplot_figure_index + 1) * max_images_per_subplot
                selected_tif_files = tif_files[start_idx:end_idx]

                # Initialize an empty array to store all band_1_image values for histogram calculation
                all_band_1_values = []

                # Iterate over selected tif files
                for i, file in enumerate(selected_tif_files):
                    tif_path = os.path.join(subfolder_path, file)

                    # Extract the second string of the name of the chip as subtitle
                    subtitle = file.split('_')[1]

                    # Open tif file with rasterio
                    with rasterio.open(tif_path) as src:
                        # Get chip dimensions
                        chip_width = src.width
                        chip_height = src.height

                        # Calculate aspect ratio
                        aspect_ratio = chip_width / chip_height

                        # Read bands 4, 3, 2 as float for composite subplot
                        rgb_image = src.read([4, 3, 2]).astype(float)

                        # Apply histogram equalization to each band for composite subplot
                        for band in range(3):
                            rgb_image[band] = exposure.equalize_hist(rgb_image[band])

                        # Show the composite image in the composite subplot with adjusted aspect ratio
                        axs_composite[i // 5, i % 5].imshow(rgb_image.transpose((1, 2, 0)), extent=src.bounds, aspect='auto')

                        # Turn off ticks
                        axs_composite[i // 5, i % 5].axis('off')

                        # Add subtitle
                        axs_composite[i // 5, i % 5].set_title(subtitle, fontsize=8)

                        # Read band 1 as float for greyscale subplot
                        band_1_image = src.read(1).astype(float)

                        # Store all band_1_image values for histogram calculation
                        all_band_1_values.extend(band_1_image.flatten())

                        # Show the greyscale image in the greyscale subplot with adjusted aspect ratio
                        axs_greyscale[i // 5, i % 5].imshow(band_1_image, cmap='gray', extent=src.bounds, aspect=1/aspect_ratio)

                        # Turn off ticks
                        axs_greyscale[i // 5, i % 5].axis('off')

                        # Add subtitle
                        axs_greyscale[i // 5, i % 5].set_title(subtitle, fontsize=8)

                # Calculate the 5th and 95th percentiles for intensity range
                lower_percentile, upper_percentile = np.percentile(all_band_1_values, [20, 80])

                for i, file in enumerate(selected_tif_files):
                    tif_path = os.path.join(subfolder_path, file)

                    # Extract the second string of the name of the chip as subtitle
                    subtitle = file.split('_')[1]

                    # Open tif file with rasterio
                    with rasterio.open(tif_path) as src:
                        # Read bands 4, 3, 2 as float for composite subplot
                        rgb_image = src.read([4, 3, 2]).astype(float)

                        # Apply histogram equalization to each band for composite subplot
                        for band in range(3):
                            rgb_image[band] = exposure.equalize_hist(rgb_image[band])

                        # Show the composite image in the composite subplot with adjusted aspect ratio
                        axs_composite[i // 5, i % 5].imshow(rgb_image.transpose((1, 2, 0)), extent=src.bounds, aspect=1/aspect_ratio)

                        # Turn off ticks
                        axs_composite[i // 5, i % 5].axis('off')

                        # Add subtitle
                        axs_composite[i // 5, i % 5].set_title(subtitle, fontsize=8)

                        # Read band 1 as float for greyscale subplot
                        band_1_image = src.read(1).astype(float)

                        # Adjust intensity range based on the 5th and 95th percentiles
                        band_1_image = exposure.rescale_intensity(band_1_image, in_range=(lower_percentile, upper_percentile))

                        # Show the greyscale image in the greyscale subplot with adjusted aspect ratio
                        axs_greyscale[i // 5, i % 5].imshow(band_1_image, cmap='gray', extent=src.bounds, aspect=1/aspect_ratio)

                        # Turn off ticks
                        axs_greyscale[i // 5, i % 5].axis('off')

                        # Add subtitle
                        axs_greyscale[i // 5, i % 5].set_title(subtitle, fontsize=8)

                # Adjust subplot layouts
                plt.tight_layout()

                # Save the composite figure
                output_composite_path = os.path.join(output_subfolder, f"subplot_composite_{subdir}_{subplot_figure_index + 1}.png")
                fig_composite.savefig(output_composite_path)
                plt.close(fig_composite)

                # Adjust subplot layouts
                plt.tight_layout()
                plt.axis('off')

                # Save the greyscale figure
                output_greyscale_path = os.path.join(output_subfolder, f"subplot_greyscale_{subdir}_{subplot_figure_index + 1}.png")
                fig_greyscale.savefig(output_greyscale_path)
                plt.close(fig_greyscale)

# Example usage with a limit of 25 images per subplot, 5 figures per subplot type, and axis numbers turned off
input_folder = "../data/images/image_chips"
output_folder = "../data/figures_chips"
generate_subplot(input_folder, output_folder, max_images_per_subplot=25, max_subplot_figures=5)

