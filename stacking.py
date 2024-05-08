import os
from pathlib import Path
import rasterio
import numpy as np

#def stack_subst_bands(input_dir, output_dir):
def stack_subst_bands(input_dir):
    # Add the code from stack_idw.py here
    import os
    from pathlib import Path
    # ...

    # Suppress specific warnings (overflow and invalid value)
    np.seterr(over='ignore', invalid='ignore')

    # Get the current directory where the script is located
    current_dir = Path(__file__).parent

    # Define the input and output directories
    # input_images_dir = current_dir / 'masked_resampled_images'
    # output_images_dir = current_dir / 'output_images'
    # substr_files_dir = input_images_dir / 'substr_files'  # New subfolder
    
    input_images_dir = Path(input_dir)
    #output_images_dir = Path(output_dir) / Path("stacked_images")
    output_images_dir = Path(input_dir)
    substr_files_dir = Path(input_images_dir) / Path('substr_files')  # New subfolder
    
    # Create the 'output_images' directory if it doesn't exist
    output_images_dir.mkdir(parents=True, exist_ok=True)

    # Create the 'substr_files' directory if it doesn't exist
    substr_files_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Find 'non-ortho,' 'non-ortho baresoil,' and 'ortho' TIF files
    tif_files = [file for file in input_images_dir.glob('*.tif')]

    ortho_files = [file for file in tif_files if "ortho" in file.stem]
    non_ortho_non_baresoil_files = [file for file in tif_files if "ortho" not in file.stem and "baresoil" not in file.stem]
    non_ortho_baresoil_files = [file for file in tif_files if "ortho" not in file.stem and "baresoil" in file.stem]

    # Create a mapping to associate "ortho" with "non-ortho" files and "non-ortho baresoil"
    mapping = {}

    for non_ortho_baresoil_file in non_ortho_baresoil_files:
        # Find the corresponding "non-ortho non-baresoil" file
        non_ortho_non_baresoil_prefix = non_ortho_baresoil_file.stem.replace("_baresoil_masked", "")
        print(f' this is the pattern: {non_ortho_non_baresoil_prefix}')
        matching_non_baresoil_file = next(
            (file for file in non_ortho_non_baresoil_files if file.stem.startswith(non_ortho_non_baresoil_prefix)),
            None
        )

        if matching_non_baresoil_file:
            # Get the prefix for the "ortho" file
            ortho_prefix = non_ortho_baresoil_file.stem.rsplit("_", 1)[0]
            
            if ortho_prefix in mapping:
                mapping[ortho_prefix].append((matching_non_baresoil_file, non_ortho_baresoil_file))
            else:
                mapping[ortho_prefix] = [(matching_non_baresoil_file, non_ortho_baresoil_file)]

    # Step 2: Process and save the results as GeoTIFF
    for ortho_prefix, file_pairs in mapping.items():
        for non_ortho_file, ortho_baresoil_file in file_pairs:
            with rasterio.open(non_ortho_file) as src1, rasterio.open(ortho_baresoil_file) as src2:
                # Subtract the bands
                result = src1.read(1) - src2.read(1)

                # Create a new GeoTIFF file for the result
                output_tif = substr_files_dir / (ortho_prefix + '_subst.tif')  # Save to 'substr_files' subfolder
                
                if output_tif.exists():
                    print(f"Output file {output_tif} already exists. Skipping...")
                    continue
                
                with rasterio.open(output_tif, 'w', driver='GTiff', height=src1.height, width=src1.width, count=1,
                                   dtype=result.dtype, crs=src1.crs, transform=src1.transform) as dst:
                    dst.write(result, 1)
                    
    print(f'Substraction using IDW interpolated layer has been carried out')

    # # Step 3: Stack "ortho" TIF files with their corresponding "subst.tif" files
    # for ortho_file in ortho_files:
    #     ortho_prefix = ortho_file.stem.rsplit("_ortho_", 1)[0]
    #     #print(f'this is the ortho prefix {ortho_prefix}')
    #     matching_substr_tif = substr_files_dir / (ortho_prefix + '_baresoil_subst' '.tif')
        

    #     if matching_substr_tif.is_file():
    #         with rasterio.open(matching_substr_tif) as src1:
    #             #print(f'this is matching file {matching_substr_tif}')
    #             #print(f'this is matching file {ortho_file}')
    #             print(f'Located matching.... {ortho_file}')
    #             profile = src1.profile.copy()  # Get the profile of the "subst.tif"
                
    #             band_count = 6  # Set the desired band count (7 bands in total)

    #             # Create a new output file with the desired band count
    #             profile.update(count=band_count)

    #             # Create the output file
    #             stacked_output = output_images_dir / (ortho_file.stem + '_stacked.tif')
                
    #             if stacked_output.exists():
    #                 print(f"Output file {stacked_output} already exists. Skipping...")
    #                 continue
                
    #             with rasterio.open(stacked_output, 'w', **profile) as dst:
    #                 print(f'Stacking.... {stacked_output}')
    #                 # Write the "subst.tif" to the output file (first band)
    #                 dst.write(src1.read(1), 1)

    #                 # Open the "ortho" TIF
    #                 with rasterio.open(ortho_file) as src2:
    #                     # Write the 6 bands of the "ortho" TIF to the output file (bands 2 to 7)
    #                     for i in range(2, 7):
    #                         dst.write(src2.read(i - 1), i)
    #     else: 
    #         print("there are no matching files")
    # Step 3: Stack "ortho" TIF files with their corresponding "subst.tif" files
    for ortho_file in ortho_files:
        ortho_prefix = ortho_file.stem.rsplit("_ortho_", 1)[0]
        
        matching_substr_tif = substr_files_dir / (ortho_prefix + '_baresoil_subst.tif')
        
        if matching_substr_tif.is_file():
            # Check if the corresponding stacked file already exists
            stacked_output = output_images_dir / (ortho_prefix + '_ortho_masked_stacked.tif')
            if stacked_output.exists():
                print(f"Output file {stacked_output} already exists. Skipping...")
                continue
            
            with rasterio.open(matching_substr_tif) as src1:
                profile = src1.profile.copy()  # Get the profile of the "subst.tif"
                
                band_count = 6  # Set the desired band count (7 bands in total)

                # Create a new output file with the desired band count
                profile.update(count=band_count)

                # Create the output file
                stacked_output = output_images_dir / (ortho_prefix + '_ortho_masked_stacked.tif')
                
                with rasterio.open(stacked_output, 'w', **profile) as dst:
                    print(f'Stacking.... {stacked_output}')
                    # Write the "subst.tif" to the output file (first band)
                    dst.write(src1.read(1), 1)

                    # Open the "ortho" TIF
                    with rasterio.open(ortho_file) as src2:
                        # Write the 6 bands of the "ortho" TIF to the output file (bands 2 to 7)
                        for i in range(2, 7):
                            dst.write(src2.read(i - 1), i)
        else: 
            print(f"No matching _baresoil_subst.tif found for {ortho_file.stem}. Skipping...")
    
if __name__ == "__main__":
    run()