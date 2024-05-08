

# import os
# import glob
# import geopandas as gpd
# import pandas as pd
# import numpy as np
# import rasterio
# from rasterio.mask import mask
# from datetime import datetime

# def find_matching_shapefile(input_shps_dir, subfolder_name, orthophoto_name):
#     # Extract the first string of the orthophoto name
#     first_string = orthophoto_name.split('_')[0]

#     # Search for a shapefile with the same first string in the specific subfolder
#     subfolder_path = os.path.join(input_shps_dir, subfolder_name)
#     for root, _, files in os.walk(subfolder_path):
#         for shapefile_name in files:
#             if shapefile_name.lower().endswith('.shp') and first_string in shapefile_name:
#                 return os.path.join(root, shapefile_name)

#     return None

# def extract_statistics(tif_file, shp_file):
#     # Load the shapefile using GeoPandas
#     gdf = gpd.read_file(shp_file)

#     # Open the TIF file using Rasterio
#     with rasterio.open(tif_file) as src:
#         # Read the first 5 bands (excluding any additional bands)
#         bands = src.read([1, 2, 3, 4, 5, 6])

#         # Define the column names based on the number of bands and statistics descriptors
#         #stats_descriptors = ['mean', 'median', 'std', 'max', 'min']
#         stats_descriptors = ['mean', 'std', 'max', 'min']
#         band_columns = [f'Band_{i}_{stat}' for i in range(1, 6) for stat in stats_descriptors]

#         # Include NDVI and NDRE columns in the column names
#         #column_names = ['TIF_Name', 'Date', 'Date_julian', 'order', 'identifier'] + band_columns + ['NDVI_mean', 'NDVI_median', 'NDVI_std', 'NDVI_max', 'NDVI_min'] + ['NDRE_mean', 'NDRE_median', 'NDRE_std', 'NDRE_max', 'NDRE_min'] + ['fcover']
#         column_names = ['TIF_Name', 'Date', 'Date_julian', 'order', 'identifier'] + band_columns + ['NDVI_mean', 'NDVI_std', 'NDVI_max', 'NDVI_min'] + ['NDRE_mean', 'NDRE_std', 'NDRE_max', 'NDRE_min'] + ['fcover']

#         # Create an empty DataFrame to store the results
#         result_df = pd.DataFrame(columns=column_names)

#         # Extract the second string from the TIF name as the 'Date'
#         date_string = os.path.splitext(os.path.basename(tif_file))[0].split('_')[1]
        
#         # Format the date as MM-DD-YYYY
#         formatted_date = datetime.strptime(date_string, '%m%d%Y').strftime('%m-%d-%Y')

#         # Convert the formatted date to Julian date
#         julian_date = datetime.strptime(formatted_date, '%m-%d-%Y').timetuple().tm_yday

#         # Iterate over each polygon in the shapefile
#         print(f'Generating tabular stats for {tif_name}')
#         for index, row in gdf.iterrows():
#             # Get the geometry of the polygon
#             geom = row['geometry']

#             # Get the attributes from the shapefile
#             attributes = [row[field] for field in gdf.columns if field != 'geometry']

#             # Extract the 'Identifier' field from the shapefile
#             identifier = row['identifier']

#             # Initialize lists to store band statistics for each band
#             band_stats_list = [[] for _ in range(6)]
#             nodata_value = 65535

#             # Iterate over each band within the polygon
#             for band_index in range(5):
#                 #masked_data, _ = mask(src, [geom], nodata=nodata_value, crop=True, all_touched=True)
#                 masked_data, _ = mask(src, [geom], nodata=nodata_value, crop=True, filled=False)

#                 # Calculate statistics for the masked data
#                 band_stats = [getattr(np, stat)(masked_data[band_index][masked_data[band_index] != nodata_value]) for stat in stats_descriptors]
#                 band_stats_list.append(band_stats)

#             # Calculate NDVI and NDRE from masked_data
#             ndvi_values = (masked_data[5] - masked_data[3]) / (masked_data[5] + masked_data[3])
#             ndre_values = (masked_data[5] - masked_data[4]) / (masked_data[5] + masked_data[4])

#             # Calculate NDVI and NDRE statistics for the polygon
#             ndvi_stats = [getattr(np, stat)(ndvi_values) for stat in stats_descriptors]
#             ndre_stats = [getattr(np, stat)(ndre_values) for stat in stats_descriptors]

#             # Calculate fcover for the polygon
#             green_pixels = np.count_nonzero(ndvi_values > 0.65)
#             total_pixels = np.count_nonzero(ndvi_values)
#             fcover = (green_pixels / total_pixels) * 100

#             # Create a row for the DataFrame
#             row_data = [tif_name, formatted_date, julian_date, row['order'], identifier] + [stat for band_stats in band_stats_list for stat in band_stats] + ndvi_stats + ndre_stats + [fcover]

#             # Append the row to the result DataFrame
#             result_df.loc[len(result_df)] = row_data

#         return result_df
    


# # Define the input and output directories
# input_data_dir = '../data'
# output_base_dir = '../data/tabular_outputs'

# # Create the output directory if it doesn't exist
# os.makedirs(output_base_dir, exist_ok=True)

# # Define the paths for both shps/final_shps_test and images/shifted_images_test
# shps_path = os.path.join(input_data_dir, 'shps/final_shps_test')
# images_path = os.path.join(input_data_dir, 'images/shifted_images_test')

# # Get subfolder names dynamically from both shps and images paths
# shps_subfolders = [subfolder for subfolder in os.listdir(shps_path) if os.path.isdir(os.path.join(shps_path, subfolder))]
# images_subfolders = [subfolder for subfolder in os.listdir(images_path) if os.path.isdir(os.path.join(images_path, subfolder))]

# # Find the common subfolder names between shps and images
# common_subfolders = set(shps_subfolders) & set(images_subfolders)

# # Iterate over each common subfolder name
# for subfolder_name in common_subfolders:
#     # Find all TIF files in the images/shifted_images_test/{subfolder_name} subfolder
#     tif_files = glob.glob(os.path.join(images_path, subfolder_name, '*.tif'))

#     # Iterate over each TIF file
#     for tif_file in tif_files:
#         # Extract the TIF file name without extension
#         tif_name = os.path.splitext(os.path.basename(tif_file))[0]

#         # Find a corresponding shapefile in shps/final_shps_test/{subfolder_name} with a common name pattern
#         shp_file = find_matching_shapefile(shps_path, subfolder_name, tif_name)

#         if shp_file:
#             print(f"Matching shp found for TIF '{tif_name}' in subfolder '{subfolder_name}'.")
#             # Get the corresponding output directory based on the TIF name and subfolder name
#             output_subdir = os.path.join(output_base_dir, subfolder_name, tif_name)

#             # Check if the output directory already exists
#             if os.path.exists(output_subdir):
#                 overwrite_choice = input(f"The output subfolder '{tif_name}' already exists. Do you want to overwrite it? (yes/no): ").lower()

#                 # If the user chooses not to overwrite, skip processing for this TIF
#                 if overwrite_choice != 'yes':
#                     print(f"Skipping processing for TIF '{tif_name}'.")
#                     continue

#             os.makedirs(output_subdir, exist_ok=True)

#             # Create a CSV file path based on the TIF name
#             output_csv_path = os.path.join(output_subdir, f'{tif_name}_stats.csv')

#             # Extract statistics and save to CSV
#             result_df = extract_statistics(tif_file, shp_file)
#             result_df.to_csv(output_csv_path, index=False)

#         else:
#             print(f"Matching not found for TIF '{tif_name}' in subfolder '{subfolder_name}'. Skipping processing.")

import os
import glob
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from rasterio.mask import mask
from datetime import datetime

def find_matching_shapefile(input_shps_dir, subfolder_name, orthophoto_name):
    # Extract the first string of the orthophoto name
    first_string = orthophoto_name.split('_')[0]

    # Search for a shapefile with the same first string in the specific subfolder
    subfolder_path = os.path.join(input_shps_dir, subfolder_name)
    for root, _, files in os.walk(subfolder_path):
        for shapefile_name in files:
            if shapefile_name.lower().endswith('.shp') and first_string in shapefile_name:
                return os.path.join(root, shapefile_name)

    return None

def extract_statistics(tif_file, shp_file):
    # Load the shapefile using GeoPandas
    gdf = gpd.read_file(shp_file)

    # Open the TIF file using Rasterio
    with rasterio.open(tif_file) as src:
        # Read the first 5 bands (excluding any additional bands)
        bands = src.read([1, 2, 3, 4, 5, 6])

        # Define the column names based on the number of bands and statistics descriptors
        stats_descriptors = ['mean', 'std', 'max', 'min']
        band_columns = [f'Band_{i}_{stat}' for i in range(1, 7) for stat in stats_descriptors]

        # Include NDVI and NDRE columns in the column names
        column_names = ['TIF_Name', 'Date', 'Date_julian', 'order', 'identifier'] + band_columns + ['NDVI_mean', 'NDVI_std', 'NDVI_max', 'NDVI_min'] + ['NDRE_mean', 'NDRE_std', 'NDRE_max', 'NDRE_min'] + ['fcover']

        # Create an empty DataFrame to store the results
        result_df = pd.DataFrame(columns=column_names)

        # Extract the second string from the TIF name as the 'Date'
        date_string = os.path.splitext(os.path.basename(tif_file))[0].split('_')[1]
        
        # Format the date as MM-DD-YYYY
        formatted_date = datetime.strptime(date_string, '%m%d%Y').strftime('%m-%d-%Y')

        # Convert the formatted date to Julian date
        julian_date = datetime.strptime(formatted_date, '%m-%d-%Y').timetuple().tm_yday

        #Iterate over each polygon in the shapefile
        print(f'Generating tabular stats for {tif_name}')
        # Iterate over each row in the GeoDataFrame
        

        for index, row in gdf.iterrows():
            
                # Get the geometry of the polygon
                geom = row['geometry']

                # Get the attributes from the shapefile
                attributes = [row[field] for field in gdf.columns if field != 'geometry']

                # Extract the 'Identifier' field from the shapefile
                identifier = row['identifier']

                # Initialize lists to store band statistics for each band
                band_stats_list = [[] for _ in range(7)]
                nodata_value = 65535
                try:
                    # Iterate over each band within the polygon
                    for band_index in range(6):
                        masked_data, _ = mask(src, [geom], nodata=nodata_value, crop=True, filled=False)

                        # Calculate statistics for the masked data
                        band_stats = [getattr(np, stat)(masked_data[band_index][masked_data[band_index] != nodata_value]) for stat in stats_descriptors]
                        band_stats_list.append(band_stats)

                    # Calculate NDVI and NDRE from masked_data
                    #print(masked_data[1])
                    ndvi_values = (masked_data[5] - masked_data[3]) / (masked_data[5] + masked_data[3])
                    ndre_values = (masked_data[5] - masked_data[4]) / (masked_data[5] + masked_data[4])
                    
                    # ndvi_values = (masked_data[6] - masked_data[4]) / (masked_data[6] + masked_data[4])
                    # ndre_values = (masked_data[6] - masked_data[5]) / (masked_data[6] + masked_data[5])

                    # Calculate NDVI and NDRE statistics for the polygon
                    ndvi_stats = [getattr(np, stat)(ndvi_values) for stat in stats_descriptors]
                    ndre_stats = [getattr(np, stat)(ndre_values) for stat in stats_descriptors]

                    # Calculate fcover for the polygon
                    green_pixels = np.count_nonzero(ndvi_values > 0.65)
                    total_pixels = np.count_nonzero(ndvi_values)
                    fcover = (green_pixels / total_pixels) * 100

                    # Create a row for the DataFrame
                    row_data = [tif_name, formatted_date, julian_date, row['order'], identifier] + [stat for band_stats in band_stats_list for stat in band_stats] + ndvi_stats + ndre_stats + [fcover]

                except Exception as e:
                    # Handle the case when intersection is empty
                    print(f"Error processing row {index}: {e}")
                    row_data = [tif_name, formatted_date, julian_date, row['order'], identifier] + [np.nan] * (len(result_df.columns) - 5)
                    #row_data = np.nan_to_num(row_data, nan=-66666)
                    # Change only the NaN values to a specific numeric value (e.g., -66666)
                    row_data = pd.Series(row_data).fillna(-66666).tolist()
                    print(row_data)

                finally:
                    # Append the row to the result DataFrame
                    result_df.loc[len(result_df)] = row_data

        return result_df


# Define the input and output directories
input_data_dir = '../data'
output_base_dir = '../data/tabular_outputs'

# Create the output directory if it doesn't exist
os.makedirs(output_base_dir, exist_ok=True)

# Define the paths for both shps/final_shps_test and images/shifted_images_test
shps_path = os.path.join(input_data_dir, 'shps/final_shps_postshifted')
images_path = os.path.join(input_data_dir, 'images/shifted_images')

# Get subfolder names dynamically from both shps and images paths
shps_subfolders = [subfolder for subfolder in os.listdir(shps_path) if os.path.isdir(os.path.join(shps_path, subfolder))]
images_subfolders = [subfolder for subfolder in os.listdir(images_path) if os.path.isdir(os.path.join(images_path, subfolder))]

# Find the common subfolder names between shps and images
common_subfolders = set(shps_subfolders) & set(images_subfolders)
print(f"Common folders found for: {common_subfolders}.")


# Iterate over each common subfolder name
for subfolder_name in common_subfolders:
    # Find all TIF files in the images/shifted_images_test/{subfolder_name} subfolder
    tif_files = glob.glob(os.path.join(images_path, subfolder_name, '*.tif'))

    # Iterate over each TIF file
    for tif_file in tif_files:
        # Extract the TIF file name without extension
        tif_name = os.path.splitext(os.path.basename(tif_file))[0]

        # Find a corresponding shapefile in shps/final_shps_test/{subfolder_name} with a common name pattern
        shp_file = find_matching_shapefile(shps_path, subfolder_name, tif_name)

        if shp_file:
            #print(f"Matching shp found for TIF '{tif_name}' in subfolder '{subfolder_name}'.")
            print(f"Matching shp {os.path.basename(shp_file)} found for TIF {tif_name} in {subfolder_name}.")
            # Get the corresponding output directory based on the TIF name and subfolder name
            output_subdir = os.path.join(output_base_dir, subfolder_name, tif_name)

            # Check if the output directory already exists
            if os.path.exists(output_subdir):
                overwrite_choice = input(f"The output subfolder '{tif_name}' already exists. Do you want to overwrite it? (yes/no): ").lower()

                # If the user chooses not to overwrite, skip processing for this TIF
                if overwrite_choice != 'yes':
                    print(f"Skipping processing for TIF '{tif_name}'.")
                    continue

            os.makedirs(output_subdir, exist_ok=True)

            # Create a CSV file path based on the TIF name
            output_csv_path = os.path.join(output_subdir, f'{tif_name}_stats.csv')

            # Extract statistics and save to CSV
            result_df = extract_statistics(tif_file, shp_file)
            
            result_df.replace('--', -66666, inplace=True)
            
            # Define a function to replace values less than -500 with -66666
            def replace_values(x):
                if pd.notnull(x) and isinstance(x, (int, float)) and x < -500:
                    return -66666
                return x

            # Apply the replacement function to each element in numeric columns of the DataFrame
            numeric_columns = result_df.select_dtypes(include=[np.number]).columns
            result_df[numeric_columns] = result_df[numeric_columns].applymap(replace_values)

            
            result_df.to_csv(output_csv_path, index=False)

        else:
            print(f"Matching not found for TIF '{tif_name}' in subfolder '{subfolder_name}'. Skipping processing.")

