import os
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
import config
import image_handler
import geometry_calculator
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
from skimage import exposure
from config import ImageDisplay
from rasterio.transform import xy
from rasterio.io import MemoryFile
import pyproj

def get_reverse_row_order():
    root = tk.Tk()
    root.withdraw()
    response = simpledialog.askstring("Reverse Row Order", "Do you want to reverse the row order? (yes/no)")
    return response.lower() == "yes"

def ask_plot_direction():
    root = tk.Tk()
    root.withdraw()
    response = simpledialog.askstring("Plot Direction", "Choose plot direction (v/h)")
    return response.lower()
    
def main():
    output_folder = '../data/shps1'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #input_folder = os.path.join(script_dir, '../mosaicIL')
    input_folder = '../data/images/shifted_images1/AL'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    root = tk.Tk()
    root.withdraw()

    for filename in os.listdir(input_folder):
        if filename.endswith('.tif'):
            file_path = os.path.join(input_folder, filename)
            print(file_path)
            reverse_row_order = get_reverse_row_order()
            
            # Ask the user for the plot direction
            plot_direction = ask_plot_direction()

            dialog = config.CustomDialog(root)
            user_input = dialog.result
            if user_input:
                width, length, horizontal_gap, vertical_gap, num_polygons, num_horizontal_polygons, \
                multiblock_option_selected, num_blocks, alley_width = user_input
            else:
                return

            print(file_path)

            image, stretched_image, tiff_crs, transform, extent = image_handler.open_image(file_path)
            #print(image)

            red_band = image[3 - 1]
            green_band = image[3 - 1]
            blue_band = image[2 - 1]
            print(red_band)

            # red_eq = exposure.equalize_hist(red_band)
            # green_eq = exposure.equalize_hist(green_band)
            # blue_eq = exposure.equalize_hist(blue_band)
            
            # Ensure pixel values are within the expected range [0, 1]
            # Check if the array contains only NaN values
            if np.isnan(red_band).all() or np.isnan(green_band).all() or np.isnan(blue_band).all():
                print(f"Skipping {filename} due to all NaN values in the image.")
                continue

            # Replace NaN values with zeros before normalization
            red_band[np.isnan(red_band)] = 0
            green_band[np.isnan(green_band)] = 0
            blue_band[np.isnan(blue_band)] = 0
            
            # Clip values to handle potential overflow issues during normalization
            red_band = np.clip(red_band, 0, 4000)
            green_band = np.clip(green_band, 0, 4000)
            blue_band = np.clip(blue_band, 0, 4000)
        
            # print(np.min(green_band))
            # print(np.max(green_band))
            
            red_band = (red_band - np.min(red_band)) / (np.max(red_band) - np.min(red_band))
            green_band = (green_band - np.min(green_band)) / (np.max(green_band) - np.min(green_band))
            blue_band = (blue_band - np.min(blue_band)) / (np.max(blue_band) - np.min(blue_band))

            red_eq = exposure.equalize_hist(red_band)
            green_eq = exposure.equalize_hist(green_band)
            blue_eq = exposure.equalize_hist(blue_band)

            #rgb_image = np.dstack((red_eq, green_eq, blue_eq))
            rgb_image = np.dstack((red_eq, green_eq, blue_eq))

            image_display = config.ImageDisplay(rgb_image, extent, transform)

            def close_window_and_proceed():
                image_display.fig.canvas.mpl_disconnect(image_display.cid)
                plt.close(image_display.fig)

                initial_corner = image_display.clicked_points[0]
                orientation_corner = image_display.clicked_points[1]
                
                if multiblock_option_selected:
                    if plot_direction == 'h':
                        gdf = geometry_calculator.calculate_horizontal_geometry(width, length, horizontal_gap, vertical_gap, num_polygons,
                        #gdf = geometry_calculator.calculate_horizontal_geometry(width, length, horizontal_gap, num_polygons, vertical_gap,
                                                                               num_horizontal_polygons, initial_corner[0],
                                                                               initial_corner[1], orientation_corner[0],
                                                                               orientation_corner[1], tiff_crs,
                                                                               reverse_row_order, num_blocks, alley_width)
                    else:
                        gdf = geometry_calculator.calculate_multiblock_geometry(width, length, horizontal_gap, num_polygons, vertical_gap,
                                                                               num_horizontal_polygons, initial_corner[0],
                                                                               initial_corner[1], orientation_corner[0],
                                                                               orientation_corner[1], tiff_crs,
                                                                               reverse_row_order, num_blocks, alley_width)
                    print("multiblock being constructed")
                else:
                    if plot_direction == 'h':
                        gdf = geometry_calculator.calculate_horizontal_geometry(width, length, horizontal_gap, vertical_gap, num_polygons,
                        #gdf = geometry_calculator.calculate_horizontal_geometry(width, length, horizontal_gap, num_polygons, vertical_gap,
                                                                               num_horizontal_polygons, initial_corner[0],
                                                                               initial_corner[1], orientation_corner[0],
                                                                               orientation_corner[1], tiff_crs,
                                                                               reverse_row_order)
                    else:
                        gdf = geometry_calculator.calculate_geometry(width, length, horizontal_gap, vertical_gap,
                                                                     num_polygons, num_horizontal_polygons,
                                                                     initial_corner[0], initial_corner[1],
                                                                     orientation_corner[0], orientation_corner[1],
                                                                     tiff_crs, reverse_row_order)




                geometry_calculator.save_to_shapefile(gdf, file_path, output_folder)
                overlay_tif_with_gdf(rgb_image, extent, gdf)
                
                # Ask the user if they are happy with the GeoDataFrame
                happy_with_gdf = ask_user_satisfaction()

                # If not happy, delete the created GeoDataFrame and rerun the process for the last TIFF
                if not happy_with_gdf:
                    os.remove(os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.shp"))
                    return main()

            

            image_display.set_next_step_callback(close_window_and_proceed)
            image_display.show()

def overlay_tif_with_gdf(rgb_image, extent, gdf):
    fig_overlay, ax_overlay = plt.subplots(figsize=(12, 12))
    transformer = pyproj.Transformer.from_crs("EPSG:32616", gdf.crs, always_xy=True)
    xmin, ymin = transformer.transform(extent[0], extent[2])
    xmax, ymax = transformer.transform(extent[1], extent[3])
    extent_epsg32616 = [xmin, xmax, ymin, ymax]
    ax_overlay.imshow(rgb_image, extent=extent_epsg32616, origin='lower')
    
    # Plot GeoDataFrame with 'order' labels
    gdf_epsg32616 = gdf.to_crs("EPSG:32616")
    gdf_epsg32616.plot(ax=ax_overlay, edgecolor='red', facecolor='none')
    
    # Add 'order' labels to the plot
    for idx, row in gdf_epsg32616.iterrows():
        ax_overlay.text(row['geometry'].centroid.x, row['geometry'].centroid.y, str(row['order']),
                        color='white', fontsize=5,fontweight='bold', ha='center', va='center',rotation= 90)

    ax_overlay.set_xlabel('X (meters)')
    ax_overlay.set_ylabel('Y (meters)')
    ax_overlay.set_title('Orthomosaic TIFF with GeoDataFrame Overlay (EPSG:32616)')
    ax_overlay.invert_yaxis()
    plt.show()
    
def ask_user_satisfaction():
   root = tk.Tk()
   root.withdraw()
   response = simpledialog.askstring("Satisfaction", "Are you happy with the GeoDataFrame? (yes/no)")
   return response.lower() == "yes"

if __name__ == "__main__":
    main()
