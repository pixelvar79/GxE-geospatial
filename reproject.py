import os
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
import geopandas as gpd
from fiona.crs import from_epsg
import shutil

def create_or_recreate_folder(folder):
    if os.path.exists(folder):
        print(f"Removing existing folder: {folder}")
        shutil.rmtree(folder)
    print(f"Creating folder: {folder}")
    os.makedirs(folder)
    return folder

#def reproject_tiff(input_path, output_folder_reprojected, target_crs="EPSG:32616"):
def reproject_tiff(input_path, output_folder_reprojected, target_crs="EPSG:32614"):
    # Create the output directory if it doesn't exist
    #os.makedirs(output_folder_reprojected, exist_ok=True)

    # Extract the base name of the TIFF file
    tif_base_name = os.path.splitext(os.path.basename(input_path))[0]

    # Construct the output path for the reprojected TIFF using the original name
    output_path = os.path.join(output_folder_reprojected, f'{tif_base_name}.tif')

    # Open the input TIFF file
    with rasterio.open(input_path) as src:
        # Check if the TIFF is already in the target CRS
        if src.crs.to_string() == target_crs:
            print(f"TIFF file '{input_path}' is already in the target CRS '{target_crs}'. No reprojection needed.")
            return

        # Read the metadata
        meta = src.meta.copy()

        # Reproject the TIFF
        transform, width, height = calculate_default_transform(
            src.crs, target_crs, src.width, src.height, *src.bounds
        )

        meta.update({
            'crs': target_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
        print(f"TIFF file '{input_path}' is being reprojected to '{target_crs}'.")
        # Create the output raster file
        with rasterio.open(output_path, 'w', **meta) as dest:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dest, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=Resampling.nearest
                )

#def reproject_shp(input_path, output_folder, target_crs="EPSG:32616"):
def reproject_shp(input_path, output_folder, target_crs="EPSG:32614"):
    # Extract the base name of the shapefile
    shp_base_name = os.path.splitext(os.path.basename(input_path))[0]

    # Construct the output path for the reprojected shapefile using the original name
    output_path = os.path.join(output_folder, f'reprojected_{shp_base_name}.shp')

    # Read the input shapefile
    gdf = gpd.read_file(input_path)

    # Check if the shapefile is already in the target CRS
    if gdf.crs == target_crs:
        print(f"Shapefile '{input_path}' is already in the target CRS '{target_crs}'. No reprojection needed.")
        return

    # Reproject the shapefile
    gdf = gdf.to_crs(target_crs)
    
    print(f"Shapefile '{input_path}' is being reprojected to '{target_crs}'.")
    # Save the reprojected shapefile to the output path
    gdf.to_file(output_path)

def reproject_all_shps(input_folder, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through each file in the input folder and its subfolders
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith(".shp"):
                input_path = os.path.join(root, filename)
                reproject_shp(input_path, output_folder)

if __name__ == "__main__":
    # Define base folders
    # base_folder_images = '../data/images/input_images'
    # base_folder_shps = '../data/shps/final_shps_postshifted'

    # # Define output folders
    # output_folder_images_utm = '../data/images/input_images_utm1'
    # output_folder_shps_utm = '../data/shps/final_shps_postshifted_utm1'
    
    # Define base folders
    base_folder_images = '../data/tif_yan'
    base_folder_shps = '../data/shp_yan'

    # Define output folders
    output_folder_images_utm = '../data/tif_yan_utm1'
    output_folder_shps_utm = '../data/shp_yan_utm1'

    # Create or recreate the output folders
    output_folder_images_utm = create_or_recreate_folder(output_folder_images_utm)
    output_folder_shps_utm = create_or_recreate_folder(output_folder_shps_utm)

    # Iterate through each subdirectory in the image base folder and reproject images
    for root, dirs, files in os.walk(base_folder_images):
        rel_path = os.path.relpath(root, base_folder_images)
        output_subfolder_utm = os.path.join(output_folder_images_utm, rel_path)

        # Create the corresponding output subfolder in output_folder_images_utm
        os.makedirs(output_subfolder_utm, exist_ok=True)

        for filename in files:
            if filename.endswith(".tif"):
                input_path = os.path.join(root, filename)
                reproject_tiff(input_path, output_subfolder_utm)

    # Reproject all shapefiles in base_folder_shps and its subfolders
    reproject_all_shps(base_folder_shps, output_folder_shps_utm)

    # Move the reprojected files to the new destination
    download_choice = input("Do you want to delete the original image and shapefile folders? (y/n): ")

    if download_choice.lower() == 'y':
        print(f"Deleting original image folder: {base_folder_images}")
        shutil.rmtree(base_folder_images)
