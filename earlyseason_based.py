import os
import glob
from pathlib import Path
import rasterio
from rasterio.merge import merge

def run():
    # Add the code from stack_earlyseason.py here
    import os
    import glob

    # Get the current directory where the script is located
    current_dir = Path(__file__).parent

    #print(current_dir)

    # Define the input and output directories
    input_images_dir = current_dir / 'masked_resampled_images'
    stacked_tif_dir = current_dir / 'output_images'

    #print(input_images_dir)
    #print(stacked_tif_dir)

    # Create the 'stacked_tif' directory if it doesn't exist
    stacked_tif_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Group non-'ortho' TIF files by the common part of their filenames
    grouped_orthos = {}
    input_files = list(input_images_dir.glob('*.tif'))

    for file in input_files:
        filename = file.stem
        common_part = filename.split('_')[4]
        key = common_part
        #print(key)
        if key in grouped_orthos:
            grouped_orthos[key].append(file)
            #print(grouped_orthos)
        else:
            grouped_orthos[key] = [file]
            
        
    # Step 2: Find the reference raster
    reference_raster = None
    min_numeric_value = float('inf')
    for common_part, files in grouped_orthos.items():
        for tif_file in files:
            numeric_value = int(tif_file.stem.split('_')[4])
            if numeric_value < min_numeric_value:
                min_numeric_value = numeric_value
                reference_raster = tif_file
                
                #print(reference_raster)
            
    # Step 2: Subtract each tif file from the reference
    #tif_files = glob.glob(os.path.join(input_images_dir, '*.tif'))
    tif_files = [file for file in input_images_dir.glob('*.tif') if "_ortho_" not in file.stem]

    # Step 2: Subtract and save the results as GeoTIFF
    for tif_file in tif_files:
        with rasterio.open(tif_file) as src:
            with rasterio.open(reference_raster) as ref_src:
                # Subtract the bands
                result = src.read(1) - ref_src.read(1)

                # Create a new GeoTIFF file for the result
                output_tif = stacked_tif_dir / (tif_file.stem + '_subtracted.tif')
                with rasterio.open(output_tif, 'w', driver='GTiff', height=src.height, width=src.width, count=1,
                                   dtype=result.dtype, crs=src.crs, transform=src.transform) as dst:
                    dst.write(result, 1)


    # Step 3: Find and stack 6-band ortho TIF files with their corresponding 1-band subtracted TIF
    ortho_files = [file for file in input_images_dir.glob('*.tif') if "_ortho_" in file.stem]
    subtracted_tif_files = list(stacked_tif_dir.glob('*_subtracted.tif'))

    for ortho_file, subtracted_tif_file in zip(ortho_files, subtracted_tif_files):
        # Define the path where the stacked output will be saved
        stacked_output = stacked_tif_dir / (ortho_file.stem + '_stacked.tif')

        # Open the 1-band ortho
        with rasterio.open(subtracted_tif_file) as src1:
            profile = src1.profile.copy()  # Get the profile of the 1-band ortho
            band_count = 7  # Set the desired band count (7 bands in total)

            # Create a new output file with the desired band count
            profile.update(count=band_count)

            # Create the output file
            with rasterio.open(stacked_output, 'w', **profile) as dst:
                # Write the 1-band ortho to the output file (first band)
                dst.write(src1.read(1), 1)

                # Open the 6-band ortho
                with rasterio.open(ortho_file) as src2:
                    # Write the 6 bands of the 6-band ortho to the output file (bands 2 to 7)
                    for i in range(2, 8):
                        dst.write(src2.read(i - 1), i)

if __name__ == "__main__":
    run()
            
    