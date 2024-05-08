import os
import rasterio

def find_most_negative_value(folder_path, target_files):
    most_negative_value = float('inf')

    for file_name in target_files:
        # Construct the full file path
        file_path = os.path.join(folder_path, file_name)

        # Open the GeoTIFF file using rasterio
        with rasterio.open(file_path, 'r') as src:
            # Read the pixel values
            image = src.read()

            # Get nodata value from the dataset
            nodata_value = src.nodata if src.nodata is not None else float('inf')

            # Exclude nodata values and values lower than -32000 when finding the most negative value
            valid_values = image[(image != nodata_value) & (image > -32000)]
            if valid_values.size > 0:
                min_value = valid_values.min()
                most_negative_value = min(most_negative_value, min_value)

    return most_negative_value

def process_and_save_tif_files(folder_path, most_negative_value):
    # List all files in the specified folder
    file_list = os.listdir(folder_path)

    # Filter files with the naming pattern "_dsm.tif"
    target_files = [file for file in file_list if file.endswith("_dtm.tif")]

    # Process each target file
    for file_name in target_files:
        # Construct the full file path
        file_path = os.path.join(folder_path, file_name)

        # Open the GeoTIFF file using rasterio
        with rasterio.open(file_path, 'r') as src:
            # Read the pixel values
            image = src.read()

            # Get nodata value from the dataset
            nodata_value = src.nodata if src.nodata is not None else float('inf')

            # Exclude nodata values and values lower than -32000 when processing
            valid_values = (image != nodata_value) & (image > -32000)
            image[valid_values] += abs(most_negative_value)

            # Get the metadata from the source file
            meta = src.meta

        # Construct the modified file path
        modified_file_path = os.path.join(folder_path, f"{file_name}")

        # Update metadata to reflect the modification
        meta['count'] = image.shape[0]

        # Write the modified image back to the same local folder
        with rasterio.open(modified_file_path, 'w', **meta) as dst:
            dst.write(image)

if __name__ == "__main__":
    # Replace 'your_folder_path' with the actual path to your folder containing GeoTIFF files
    #folder_path = 'your_folder_path'
    folder_path = '../G_E_PROJECT/Mosaic_LA/input_images_utm'

    # List all files in the specified folder
    file_list = os.listdir(folder_path)

    # Filter files with the naming pattern "_dsm.tif"
    target_files = [file for file in file_list if file.endswith("_dtm.tif")]

    # Find the most negative value among all DSM TIFFs
    most_negative_value = find_most_negative_value(folder_path, target_files)

    # Apply the most negative value to all DSM TIFFs
    process_and_save_tif_files(folder_path, most_negative_value)

    # Replace 'your_folder_path' with the actual path to your folder containing GeoTIFF files
    


