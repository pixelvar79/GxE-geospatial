import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject
from pathlib import Path
import geopandas as gpd

def mask_images(input_dir, output_dir, files, reference_file, selected_corners):
    input_dir = Path(input_dir)  # Convert input_dir to a Path object
    output_dir = Path(output_dir)  # Convert output_dir to a Path object

    if not output_dir.is_dir():
        output_dir.mkdir(parents=True, exist_ok=True)

    # List all the TIFF files in the input folder
    #input_files = list(input_dir.glob("*.tif"))

    with rasterio.open(reference_file) as reference:
        resample_transform = reference.transform
        reference_width = reference.width
        reference_height = reference.height

    for ortho_file in files:
    #for ortho_file in tif_files:
        ortho_path = Path(ortho_file)
            # Inherit the output filename from the input image's stem
        output_file = output_dir / f"{ortho_path.stem}_masked.tif"
        # Check if the output file already exists
        if output_file.exists():
            print(f"Output file {output_file} already exists. Skipping...")
            continue

        with rasterio.open(ortho_file) as src:
            # Handle both 1-band and multi-band images
            if src.count > 1:
                with rasterio.open(reference_file) as reference:
                    transform = reference.transform
                    # print(selected_corners)
                    # transformed_corners = [rasterio.transform.xy(transform, x, y) for x, y in selected_corners]
                    # print(transformed_corners)

                    # masked = gpd.GeoDataFrame({'geometry': gpd.GeoSeries(gpd.points_from_xy(*zip(*transformed_corners)))}, crs='EPSG:32616')
                    
                    # Use the inverse transform to convert pixel coordinates to geographic coordinates
                    lon, lat = transform * np.array(selected_corners).T

                    # Create GeoDataFrame with the selected points in the reference CRS
                    masked = gpd.GeoDataFrame({'geometry': gpd.points_from_xy(lon, lat)}, crs=reference.crs)
                    mask_bounds = masked.total_bounds
    
    
                    #mask_bounds = masked.total_bounds
                    mask_window = src.window(*mask_bounds)
                    input_data = src.read(window=mask_window)

                    resampled_data = np.zeros(
                        (src.count, reference_height, reference_width),
                        dtype=np.float32
                    )
                    for band in range(src.count):
                        reproject(
                            input_data[band].astype(np.float32),
                            resampled_data[band],
                            src_transform=src.window_transform(mask_window),
                            src_crs=src.crs,
                            dst_transform=resample_transform,
                            dst_crs=src.crs,
                            resampling=Resampling.bilinear
                        )
            else:
                # Apply mask for 1-band images
                with rasterio.open(reference_file) as reference:
                    transform = reference.transform
                    # transformed_corners = [rasterio.transform.xy(transform, x, y) for x, y in selected_corners]

                    # masked = gpd.GeoDataFrame({'geometry': gpd.GeoSeries(gpd.points_from_xy(*zip(*transformed_corners)))}, crs='EPSG:32616')
                    
                    # Use the inverse transform to convert pixel coordinates to geographic coordinates
                    lon, lat = transform * np.array(selected_corners).T

                    # Create GeoDataFrame with the selected points in the reference CRS
                    masked = gpd.GeoDataFrame({'geometry': gpd.points_from_xy(lon, lat)}, crs=reference.crs)
                    mask_bounds = masked.total_bounds
                    #mask_bounds = masked.total_bounds
                    
                    
                    mask_window = src.window(*mask_bounds)
                    input_data = src.read(1, window=mask_window)

                    resampled_data = np.zeros(
                        (1, reference_height, reference_width),
                        dtype=np.float32
                    )
                    reproject(
                        input_data.astype(np.float32),
                        resampled_data[0],
                        src_transform=src.window_transform(mask_window),
                        src_crs=src.crs,
                        dst_transform=resample_transform,
                        dst_crs=src.crs,
                        resampling=Resampling.bilinear
                    )

        num_output_bands = src.count
        with rasterio.open(output_file, 'w', driver='GTiff',
                           width=reference_width,
                           height=reference_height,
                           count=num_output_bands,  # Inheriting the number of bands
                           dtype=resampled_data.dtype,
                           crs=src.crs, transform=resample_transform) as dst:
            if src.count == 1:
                dst.write(resampled_data[0], 1)
            else:
                for band in range(num_output_bands):
                    dst.write(resampled_data[band], band + 1)

        print(f"Processed and saved: {output_file}")

# Example usage:
# process_images("input_images", "output_images", "reference_image.tif", [(x1, y1), (x2, y2), (x3, y3), (x4, y4)])