
# Import other necessary modules as before
from pathlib import Path
import os
from corner_selector import select_reference_image, select_corners
from image_processor import mask_images
from interpolation import interpolate_images
from itertools import groupby
from stacking import stack_subst_bands

def delete_previous_masked_stacked_files(output_dir_mask_subfolder):
    files = os.listdir(output_dir_mask_subfolder)
    
    for file in files:
        if file.endswith("_masked.tif"):
            file_path = os.path.join(output_dir_mask_subfolder, file)
            os.remove(file_path)
        if file.endswith("_stacked.tif"):
            file_path = os.path.join(output_dir_mask_subfolder, file)
            os.remove(file_path)
            
def delete_masked_files(output_dir_mask_subfolder):
    files = os.listdir(output_dir_mask_subfolder)
    
    for file in files:
        if file.endswith("_masked.tif"):
            file_path = os.path.join(output_dir_mask_subfolder, file)
            os.remove(file_path)

def delete_previous_baresoil_files(input_dir):
    files = os.listdir(input_dir)
    
    for file in files:
        if file.endswith("_baresoil.tif"):
            file_path = os.path.join(input_dir, file)
            os.remove(file_path)

# def create_output_folders(input_dir, output_dir_mask_root):
#     relative_path = Path(input_dir).relative_to(os.path.join(base_dir, "input_images_utm"))
#     output_dir_mask_subfolder = os.path.join(output_dir_mask_root, str(relative_path))
#     os.makedirs(output_dir_mask_subfolder, exist_ok=True)
#     return output_dir_mask_subfolder

def create_output_folders(input_dir, output_dir_mask_root):
    relative_path = Path(input_dir).relative_to(os.path.join(base_dir, "input_images1"))
    output_dir_mask_subfolder = os.path.join(output_dir_mask_root, str(relative_path))
    
    # Ask the user whether to delete previous _masked_stacked.tif files
    delete_previous = input(f"Do you want to delete previous _masked or stacked.tif files in {output_dir_mask_subfolder}? (y/n): ").lower()
    if delete_previous == "y":
        delete_previous_masked_stacked_files(output_dir_mask_subfolder)

    os.makedirs(output_dir_mask_subfolder, exist_ok=True)
    return output_dir_mask_subfolder

def process_sequence(base_dir):
    input_dir_root = os.path.join(base_dir, "input_images1")
    output_dir_mask_root = os.path.join(base_dir, "masked_resampled_images1")

    # Iterate through subfolders under input_images_utm
    for root, dirs, _ in os.walk(input_dir_root):
        # Process each subfolder
        for subfolder in dirs:
            subfolder_path = os.path.join(root, subfolder)
            
            # Ask the user whether to delete previous baresoil files
            delete_previous = input("Do you want to delete previous baresoil files in the directory? (y/n): ").lower()
            if delete_previous == "y":
                delete_previous_baresoil_files(subfolder_path)
            print(subfolder_path)
            # Step 1: Interpolate dsm to generate baresoil dtm using the interpolation module
            interpolate_images(Path(subfolder_path))
            
            # Process ortho images for each group
            input_files = list(Path(subfolder_path).glob("*.tif"))
            
            # Convert WindowsPath objects to strings for the grouped_files
            input_files_strings = [str(file) for file in input_files]
            
            print(input_files_strings)
            
            # Group files in the current subfolder
            grouped_files = {key: list(group) for key, group in groupby(sorted(input_files, key=lambda f: f.stem.rsplit("_", 3)[0]), key=lambda f: f.stem.rsplit("_", 3)[0])}

            print(f"the groups in {subfolder_path} are: {grouped_files}")

            # Build subfolder name inside masked_resampled_images
            output_dir_mask_subfolder = create_output_folders(subfolder_path, output_dir_mask_root)

            # Steps 1, 2, 3, 4: Interpolate, select corners, mask, and stack for each subfolder
            for common_stem, files in grouped_files.items():
                # Build the reference file for the current group 
                reference_file = select_reference_image(files)
                print(f'reference file is: {reference_file}')
                if reference_file is not None:  
                    
                    # Step 2: for each group and reference file, select corners interactively for the current group
                    selected_corners = select_corners(reference_file)

                    # Step 3: Process ortho images for the current group
                    mask_images(subfolder_path, output_dir_mask_subfolder, files, reference_file, selected_corners)
                    
                    # Step 4: stack the subtracted dsm and bands 1-5 from MSI sensor
                    #stack_subst_bands(output_dir_mask_subfolder, base_dir)
                    stack_subst_bands(output_dir_mask_subfolder)
                    
    #ask to delete intermediate _mask.tif in output location at the end of the execution
    
            # Ask the user whether to delete previous _masked_stacked.tif files
            delete_previous = input(f"Do you want to delete intermediate _masked files in {output_dir_mask_subfolder}? (y/n): ").lower()
            if delete_previous == "y":
                delete_masked_files(output_dir_mask_subfolder)

if __name__ == "__main__":
    # Set the base directory within the code
    base_dir = "../data/images"
    process_sequence(base_dir)

    
    
    
# # Import other necessary modules as before
# from pathlib import Path
# import os
# from corner_selector import select_reference_image, select_corners
# from image_processor import mask_images
# from interpolation import interpolate_images
# from itertools import groupby
# from stacking import stack_subst_bands

# def delete_previous_baresoil_files(input_dir):
#     files = os.listdir(input_dir)
    
#     for file in files:
#         if file.endswith("_baresoil.tif"):
#             file_path = os.path.join(input_dir, file)
#             os.remove(file_path)

# def create_output_folders(input_dir, output_dir_mask_root):
#     relative_path = Path(input_dir).relative_to(os.path.join(base_dir, "input_images_utm"))
#     output_dir_mask_subfolder = os.path.join(output_dir_mask_root, str(relative_path))
#     os.makedirs(output_dir_mask_subfolder, exist_ok=True)
#     return output_dir_mask_subfolder

# def process_sequence(base_dir):
#     input_dir_root = os.path.join(base_dir, "input_images_utm")
#     output_dir_mask_root = os.path.join(base_dir, "masked_resampled_images")

#     # Iterate through subfolders under input_images_utm
#     for root, dirs, _ in os.walk(input_dir_root):
#         # Process each subfolder
#         for subfolder in dirs:
#             subfolder_path = os.path.join(root, subfolder)
            
#             # Ask the user whether to delete previous baresoil files
#             delete_previous = input("Do you want to delete previous baresoil files in the directory? (y/n): ").lower()
#             if delete_previous == "y":
#                 delete_previous_baresoil_files(subfolder_path)

#             # Step 1: Interpolate dsm to generate baresoil dtm using the interpolation module
#             interpolate_images(subfolder_path)
            
#             # Process ortho images for each group
#             input_files = list(Path(subfolder_path).glob("*.tif"))
            
#             # Convert WindowsPath objects to strings for the grouped_files
#             input_files_strings = [str(file) for file in input_files]
            
#             print(input_files_strings)
            
#             # Group files in the current subfolder
#             grouped_files = {key: list(group) for key, group in groupby(sorted(input_files, key=lambda f: f.stem.rsplit("_", 3)[0]), key=lambda f: f.stem.rsplit("_", 3)[0])}

#             print(f"the groups in {subfolder_path} are: {grouped_files}")

#             # Build subfolder name inside masked_resampled_images
#             output_dir_mask_subfolder = create_output_folders(subfolder_path, output_dir_mask_root)

#             # Steps 1, 2, 3, 4: Interpolate, select corners, mask, and stack for each subfolder
#             for common_stem, files in grouped_files.items():
#                 # Build the reference file for the current group 
#                 reference_file = select_reference_image(files)
#                 print(f'reference file is: {reference_file}')
#                 if reference_file is not None:  
                    
#                     # Step 2: for each group and reference file, select corners interactively for the current group
#                     selected_corners = select_corners(reference_file)

#                     # Step 3: Process ortho images for the current group
#                     mask_images(subfolder_path, output_dir_mask_subfolder, files, reference_file, selected_corners)
                    
#                     # Step 4: stack the subtracted dsm and bands 1-5 from MSI sensor
#                     stack_subst_bands(output_dir_mask_subfolder, base_dir)

# if __name__ == "__main__":
#     # Set the base directory within the code
#     base_dir = "../data/images"
#     process_sequence(base_dir)
