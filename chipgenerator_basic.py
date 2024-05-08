
import rasterio
import geopandas as gpd
import os
from rasterio.mask import mask

# Define the folder paths and naming pattern
base_folder = "../data"
image_folder = "tif_yan_utm1"
shp_folder = "shp_yan_utm1"
chip_folder = "yan_image_chips"

image_filename = "reprojected_10_0626_Shapefile_Anth(newDS).tif"
shp_filename = "reprojected_10_0626_Shapefile_Anth(newDS).shp"

# Generate full paths for image and shapefile
image_loc = os.path.join(base_folder,image_folder, image_filename)
shp_loc = os.path.join(base_folder, shp_folder, shp_filename)
chip_loc = os.path.join(base_folder, chip_folder)
os.makedirs(chip_loc, exist_ok=True)
    
# GENERATE IMAGE CHIPS FROM ORTHOPHOTOS
def generate_image_chips(image_path, shp_path, chip_path):
    # Open the orthophoto using rasterio
    with rasterio.open(image_path) as src:
        # Read the shapefile using GeoPandas
        shapefile = gpd.read_file(shp_path)
        
        # Loop through each polygon in the shapefile
        for index, row in shapefile.iterrows():
            #for ind in index1:
                # Get the polygon geometry
                geometry = row['geometry']
                #print(geometry)
                index1= index+1
                # Mask the orthophoto using the polygon geometry
                masked_data, masked_transform = rasterio.mask.mask(src, [geometry], crop=True,filled=False)
                
                # Exclude the alpha channel (band 6) from the masked image
                masked_data = masked_data[:10, :, :]  # Exclude the last band (band 6)
                
                # Specify a nodata value other than 0 (e.g., 65535)
                nodata_value = 65535


                # Save the image chip with stacked bands
                output_filename = os.path.join(chip_path, f"Chip_{index1}.tif")
                print('Saving chip'f'_{index1}')

                # Create the output file
                with rasterio.open(
                    output_filename,
                    "w",
                    driver="GTiff",
                    height=masked_data.shape[1],
                    width=masked_data.shape[2],
                    count=masked_data.shape[0],
                    dtype=masked_data.dtype,
                    
                    nodata=nodata_value,
                    crs=src.crs,
                    transform=masked_transform,
                ) as dst:
                    # Write the masked data to the output file
                    dst.write(masked_data)
generate_image_chips(image_loc, shp_loc, chip_loc)

# import rasterio
# import geopandas as gpd
# import numpy as np
# import math
# from scipy.ndimage import rotate as ndimage_rotate
# import os

# base_folder = "../data"
# image_folder = "tif_yan_utm1"
# shp_folder = "shp_yan_utm1"
# chip_folder = "yan_image_chips"

# image_filename = "reprojected_10_0626_Shapefile_Anth(newDS).tif"
# shp_filename = "reprojected_10_0626_Shapefile_Anth(newDS).shp"

# # Generate full paths for image and shapefile
# image_loc = os.path.join(base_folder, image_folder, image_filename)
# shp_loc = os.path.join(base_folder, shp_folder, shp_filename)
# chip_loc = os.path.join(base_folder, chip_folder)
# os.makedirs(chip_loc, exist_ok=True)

# def generate_image_chips(image_path, shp_path, chip_path):
#     # Open the orthophoto using rasterio
#     with rasterio.open(image_path) as src:
#         # Calculate the rotation angle from the affine transformation matrix
#         transform = src.transform
#         rotation_rad = math.atan2(transform.b, transform.a)
#         rotation_deg = math.degrees(rotation_rad)

#         # Read the shapefile using GeoPandas
#         shapefile = gpd.read_file(shp_path)

#         # Rotate the shapefile
#         rotated_shapefile = shapefile.copy()
#         rotated_shapefile['geometry'] = rotated_shapefile['geometry'].rotate(rotation_deg)

#         # Rotate the image
#         rotated_image = np.zeros(src.shape, dtype=src.read().dtype)
#         for i in range(src.count):
#             # Rotate each band of the image
#             rotated_image[i] = ndimage_rotate(src.read(i + 1), rotation_deg, reshape=False)

#         # Exclude the alpha channel (band 6) from the rotated image
#         rotated_image = rotated_image[:10, :, :]  # Exclude the last band (band 6)

#         # Specify a nodata value other than 0 (e.g., 65535)
#         nodata_value = 65535

#         # Loop through each polygon in the rotated shapefile
#         for index, row in rotated_shapefile.iterrows():
#             # Get the polygon geometry
#             geometry = row['geometry']
            
#             # Mask the rotated orthophoto using the polygon geometry
#             masked_data, masked_transform = rasterio.mask.mask(rotated_image, [geometry], crop=True, filled=False)
            
#             # Exclude the alpha channel (band 6) from the masked image
#             masked_data = masked_data[:10, :, :]  # Exclude the last band (band 6)
            
#             # Save the image chip with stacked bands
#             output_filename = os.path.join(chip_path, f"Chip_{index}.tif")
#             print(f"Saving chip_{index}")

#             # Create the output file
#             with rasterio.open(
#                 output_filename,
#                 "w",
#                 driver="GTiff",
#                 height=masked_data.shape[1],
#                 width=masked_data.shape[2],
#                 count=masked_data.shape[0],
#                 dtype=masked_data.dtype,
#                 nodata=nodata_value,
#                 crs=src.crs,
#                 transform=masked_transform,
#             ) as dst:
#                 # Write the masked data to the output file
#                 dst.write(masked_data)

# # Call the function
# generate_image_chips(image_loc, shp_loc, chip_loc)
