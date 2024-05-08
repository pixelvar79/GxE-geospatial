

import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import pandas as pd
from shapely.geometry import shape
from shapely.geometry import Polygon


def find_matching_shapefile(input_data_dir, subfolder_name, orthophoto_name):
    # Extract the first string of the orthophoto name
    first_string = orthophoto_name.split('_')[0]

    # Search for a shapefile with the same first string in the shp folder
    shp_subfolder_path = os.path.join(input_data_dir, 'shps/final_shps_postshifted', subfolder_name)
   
    for root, _, files in os.walk(shp_subfolder_path):
        for shapefile_name in files:
            if shapefile_name.lower().endswith('.shp') and first_string in shapefile_name:
                return os.path.join(root, shapefile_name)

    return None

def generate_image_chips(input_data_dir, output_base_dir):
    # Check if 'shifted_images' and 'shps/final_shps_postshifted' subfolders are present
    img_subfolder_path = os.path.join(input_data_dir, 'images/shifted_images')
    shp_subfolder_path = os.path.join(input_data_dir, 'shps/final_shps_postshifted')


    if not os.path.exists(img_subfolder_path) or not os.path.exists(shp_subfolder_path):
        print("Error: 'shifted_images' or 'shps/final_shps_postshifted' subfolder not found.")
        return

    # Get the list of first level subfolders in both 'shifted_images' and 'shps/final_shps_postshifted'
    img_subfolders = [folder for folder in os.listdir(img_subfolder_path) if os.path.isdir(os.path.join(img_subfolder_path, folder))]
    shp_subfolders = [folder for folder in os.listdir(shp_subfolder_path) if os.path.isdir(os.path.join(shp_subfolder_path, folder))]

    # Find common subfolder names
    common_subfolders = set(img_subfolders) & set(shp_subfolders)
    print(f"Common folders found for: {common_subfolders}.")

    for subfolder in common_subfolders:
        img_subfolder_path = os.path.join(input_data_dir, 'images/shifted_images', subfolder)

        for orthophoto_file in os.listdir(img_subfolder_path):
            if orthophoto_file.lower().endswith('.tif'):
                orthophoto_path = os.path.join(img_subfolder_path, orthophoto_file)
                orthophoto_name = os.path.splitext(orthophoto_file)[0]

                # Find the matching shapefile based on subfolder name and common first string
                shapefile_path = find_matching_shapefile(input_data_dir, subfolder, orthophoto_name)

                if shapefile_path:
                    print(f"Matching shp {os.path.basename(shapefile_path)} found for TIF {orthophoto_name} in {subfolder}.")
                    # Get the corresponding output directory based on the orthophoto filename
                    image_chip_dir = os.path.join(output_base_dir, subfolder, orthophoto_name)

                    # Check if the output directory already exists
                    if os.path.exists(image_chip_dir):
                        overwrite_choice = input(f"The output subfolder '{orthophoto_name}' already exists. Do you want to overwrite it? (yes/no): ").lower()

                        # If the user chooses not to overwrite, skip processing for this orthophoto
                        if overwrite_choice != 'yes':
                            print(f"Skipping processing for orthophoto '{orthophoto_name}'.")
                            continue

                    os.makedirs(image_chip_dir, exist_ok=True)

                    # Create a summary DataFrame for each pair
                    summary_data = {'Name of Trial': [], 'Order': [], 'Identifier': []}

                    print(f'Generating image chips for {orthophoto_name}')

                    # Open the orthophoto using rasterio
                    with rasterio.open(orthophoto_path) as src:
                        # Read the shapefile using GeoPandas
                        shapefile = gpd.read_file(shapefile_path)

                        # Get the bounding box coordinates from src.bounds
                        left, bottom, right, top = src.bounds

                        # Loop through each polygon in the shapefile
                        for index, row in shapefile.iterrows():
                            # Get the polygon geometry
                            geometry = row['geometry']
                            order = row['order']
                            identifier = row['identifier']

                            # Check if the polygon is entirely contained within the image bounds
                            if shape(geometry).within(Polygon([(left, bottom), (right, bottom), (right, top), (left, top)])):
                                # Mask the orthophoto using the polygon geometry
                                masked_image, masked_transform = mask(src, [geometry], crop=True, filled=False)

                                # Exclude the alpha channel (band 6) from the masked image
                                masked_image = masked_image[:5, :, :]  # Exclude the last band (band 6)

                                # Save the image chip with the stacked bands (excluding band 6)
                                chip_filename = f"Chip_{order}_{identifier}.tif"

                                # Specify the output path including the subfolder
                                output_chip_path = os.path.join(image_chip_dir, chip_filename)

                                # Specify a nodata value other than 0 (e.g., 65535)
                                nodata_value = 65535

                                # Create the output file with nodata specified
                                with rasterio.open(
                                    output_chip_path,
                                    "w",
                                    driver="GTiff",
                                    height=masked_image.shape[1],
                                    width=masked_image.shape[2],
                                    count=masked_image.shape[0],
                                    dtype=masked_image.dtype,
                                    nodata=nodata_value,
                                    crs=src.crs,
                                    transform=masked_transform,
                                ) as dst:
                                    # Write the masked data to the output file
                                    dst.write(masked_image)

                                # Append the details to the summary data
                                summary_data['Name of Trial'].append(orthophoto_name)
                                summary_data['Order'].append(order)
                                summary_data['Identifier'].append(identifier)

                    # Create a DataFrame from the summary data
                    summary_df = pd.DataFrame(summary_data)

                    # Save the summary DataFrame to a CSV file
                    summary_csv_filename = f'{orthophoto_name}.csv'
                    summary_csv_path = os.path.join(output_base_dir, subfolder,summary_csv_filename)
                    summary_df.to_csv(summary_csv_path, index=False)

if __name__ == "__main__":
    input_data_dir = '../data'  # Assuming the script is in the same directory as the data
    output_base_dir = '../data/image_chips_yan/image_chips'
    os.makedirs(output_base_dir, exist_ok=True)

    # Generate image chips
    generate_image_chips(input_data_dir, output_base_dir)
