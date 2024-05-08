import rasterio
import numpy as np
import argparse
import matplotlib.pyplot as plt
from skimage import exposure
import os

# Lists to store the clicked points for reference and target images
reference_points = []
target_points = []
# Variables to keep track of the number of right-clicks and reference/target mode
right_click_count = 0

def show_image(image, ax):
    #plt.figure(figsize=(8, 8))
    ax.imshow(image, origin='lower')
    ax.axis('on')
    ax.invert_yaxis()
    #plt.show()
    
# def show_image(image, ax):
#     ax.imshow(image)
#     ax.axis('on')
#     #ax.invert_yaxis()
fig = None

def click_event(event, reference_file, target_file, output_file):
    global reference_points, target_points, right_click_count
    if event.inaxes:
        x, y = event.xdata, event.ydata
        if event.button == 1:  # Left-click for zoom
            # Implement zoom-in functionality here
            # Implement zoom-in functionality here
            # for ax in fig.axes:
            #     ax.set_xlim([x - 50, x + 50])  # Adjust the zoom level as needed
            #     ax.set_ylim([y - 50, y + 50])  # Adjust the zoom level as needed

            pass
        elif event.button == 3:  # Right-click for capturing points
            if right_click_count % 2 == 0:
                reference_points.append((x, y))
                plt.scatter(x, y, c='r', s=20, label='Reference')
            else:
                target_points.append((x, y))
                plt.scatter(x, y, c='g', s=20, label='Target')

            right_click_count += 1

            if right_click_count >= 4:
                # #Prompt user if they want to proceed to the next iteration or reiterate over the same target_tif
                # choice = input("Do you want to proceed to the next iteration over the next target_tif? (y/n): ")
                # if choice.lower() == 'y':
                    # Perform alignment after capturing two reference and two target points
                    shift_and_align(reference_file, target_file, output_file)
                    # Optionally, you can clear the lists for the next alignment
                    reference_points.clear()
                    target_points.clear()
                    right_click_count = 0
                    #plt.close()  # Close the plot after processing

                # elif choice.lower() == 'n':
                #     # Clear the lists for reiteration over the same target_tif
                #     reference_points.clear()
                #     target_points.clear()
                #     right_click_count = 0
                # else:
                #     print("Invalid choice. Please enter 'y' or 'n.'")

            plt.draw()
    # Close all plots after processing
            #plt.close('all')

def shift_and_align(reference_file, target_file, output_file):
    global right_click_count  # Add this line to access the global variable
    if len(reference_points) != len(target_points) or len(reference_points) < 2:
        print("Please click at least two corresponding points on both images.")
        right_click_count = 0  # Reset right_click_count
        return

    # Calculate the shift based on the captured points
    x_shifts = [reference[0] - target[0] for reference, target in zip(reference_points, target_points)]
    y_shifts = [reference[1] - target[1] for reference, target in zip(reference_points, target_points)]

    # Calculate the average shift
    shift_x = np.mean(x_shifts)
    shift_y = np.mean(y_shifts)

    print(f"Average shift: Shift_x = {shift_x}, Shift_y = {shift_y}")

    # Open the reference and target TIF files using rasterio
    with rasterio.open(reference_file) as ref_ds, rasterio.open(target_file) as target_ds:
        # Calculate the new affine transform for the output dataset with the specified shifts
        output_transform = target_ds.transform * rasterio.Affine.translation(shift_x, shift_y)

        # Define the profile for the output dataset based on the target dataset
        profile = target_ds.profile

        # Update the transformation in the profile
        profile["transform"] = output_transform

        # Copy the CRS information from the reference dataset
        profile["crs"] = ref_ds.crs

        # Create the output TIF file for the shifted target image
        with rasterio.open(output_file, 'w', **profile) as output_ds:
            # Loop through each band in the target dataset
            for band_idx in range(1, target_ds.count + 1):
                # Read the data from the target band
                target_band = target_ds.read(band_idx)

                # Write the data to the corresponding band in the output dataset
                output_ds.write(target_band, band_idx)

def main(reference_file, target_file, output_file):
    # Create a figure with two subplots for reference and target images
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))

    # Define a custom event handler function to capture clicks
    def custom_event_handler(event):
        click_event(event, reference_file, target_file, output_file)

    # Load your reference and target images using rasterio
    with rasterio.open(reference_file) as ref_ds:
        with rasterio.open(target_file) as target_ds:
            # Read the first three bands for RGB from both datasets
            reference_image = np.dstack([ref_ds.read(band) for band in [4, 3, 2]])
            target_image = np.dstack([target_ds.read(band) for band in [4, 3, 2]])
    reference_image = (reference_image).astype(np.uint16)
    target_image = (target_image).astype(np.uint16)
    # Use histogram equalization for better color stretching
    reference_image = exposure.equalize_hist(reference_image)
    target_image = exposure.equalize_hist(target_image)
    
    #show_image(reference_image, ax[0])
    ax[0].imshow(reference_image, origin='lower')
    ax[0].set_title(f"Reference Image\n({os.path.basename(reference_file)})", fontsize=6)
    #ax[0].set_aspect('auto')  # Set aspect ratio to 'auto'
    ax[0].invert_yaxis()

    # Display target image on the second subplot
    
    #show_image(target_image, ax[1])
    ax[1].imshow(target_image, origin='lower')    
    ax[1].set_title(f"Target Image\n({os.path.basename(target_file)})", fontsize=6)
    #ax[1].set_aspect('auto') 
    ax[1].invert_yaxis()
    # Synchronize zooming between the subplots
    def on_xlims_change(axes):
        xlims = axes.get_xlim()
        ax[0].set_xlim(xlims)
        ax[0].figure.canvas.draw_idle()

    def on_ylims_change(axes):
        ylims = axes.get_ylim()
        ax[0].set_ylim(ylims)
        ax[0].figure.canvas.draw_idle()
        
    ax[1].callbacks.connect('xlim_changed', on_xlims_change)
    ax[1].callbacks.connect('ylim_changed', on_ylims_change)
        
    
    # Add click event handler for capturing points
    fig.canvas.mpl_connect('button_press_event', custom_event_handler)

    # Show the plot with both images
    plt.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Display and compare reference and target images.")
    parser.add_argument("reference_file", help="Path to the reference TIF file")
    parser.add_argument("target_file", help="Path to the target TIF file")
    parser.add_argument("output_file", help="Path for the output shifted target TIF file")
    args = parser.parse_args()

    main(args.reference_file, args.target_file, args.output_file)
