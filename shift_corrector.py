import argparse
import os
import re
import shutil
from pathlib import Path
from itertools import groupby

def select_reference_file(files, reference_files_folder, group_prefix):
    matching_reference_files = list(reference_files_folder.glob(f"{group_prefix}_*.tif"))

    if matching_reference_files:
        print("Matching reference files found in the subfolder:")
        for i, file in enumerate(matching_reference_files, start=1):
            print(f"{i}. (Reference File) {file.name}")

        while True:
            try:
                choice = int(input("Enter the number corresponding to the reference file: "))
                if 1 <= choice <= len(matching_reference_files):
                    return matching_reference_files[choice - 1]
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    print("No matching reference files found in the subfolder. Choosing from all files in the group:")
    return select_reference_from_all(files,reference_files_folder, group_prefix)

            
def select_reference_from_all(files, reference_files_folder, group_prefix):
    print("List of TIF files:")
    files = [Path(file) for file in files]
    for i, file in enumerate(files, start=1):
        print(f"{i}. {file.name}")

    while True:
        try:
            choice = int(input("Enter the number corresponding to the reference file: "))
            if 1 <= choice <= len(files):
                selected_reference_file = files[choice - 1]

                # Copy the selected reference file to the reference file subfolder with "_shifted" suffix
                reference_output_file_subfolder = reference_files_folder / f"{selected_reference_file.stem}_shifted.tif"
                shutil.copy(str(selected_reference_file), str(reference_output_file_subfolder))

                return selected_reference_file
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")




def delete_previous_shifted_files(output_folder):
    delete_previous = input("Do you want to delete any previous '_shifted.tif' files in the output folder? (y/n): ")
    if delete_previous.lower() == 'y':
        previous_files = list(output_folder.glob("*_shifted.tif"))
        for file in previous_files:
            file.unlink()
        print("Previous '_shifted.tif' files deleted.")
    elif delete_previous.lower() == 'n':
        print("Previous '_shifted.tif' files will not be deleted.")
    else:
        print("Invalid choice. Please enter 'y' or 'n'.")

def group_files_by_prefix(files):
    grouped_files = {}
    for file in files:
        parts = file.stem.split('_')
        stable_index = next((i for i, part in enumerate(parts[::-1]) if part.startswith('ortho')), None)

        if stable_index is not None:
            prefix = '_'.join(parts[:len(parts)-stable_index][::-1])

            if prefix not in grouped_files:
                grouped_files[prefix] = {'files': []}

            grouped_files[prefix]['files'].append(file)

    return grouped_files


def main():
    parser = argparse.ArgumentParser(description="Shift and align a reference image with a list of target images.")
    parser.add_argument("mode", help="Alignment mode: 'manual' or 'automated'")
    args = parser.parse_args()

    base_dir = "../data/images"
    input_dir = os.path.join(base_dir, "masked_resampled_images1")
    output_dir = os.path.join(base_dir, "shifted_images1")
    
    # input_dir = os.path.join(base_dir, "Raw_ORTHO20230626")
    # output_dir = os.path.join(base_dir, "Raw_ORTHO202306261")

    input_folder = Path(input_dir)
    output_folder = Path(output_dir)

    if not output_folder.is_dir():
        os.makedirs(output_folder)

    delete_previous_shifted_files(output_folder)

    # reference_files_folder = output_folder / "reference_files"
    # os.makedirs(reference_files_folder, exist_ok=True)

    # Iterate through subdirectories
    for subfolder in input_folder.iterdir():
        if subfolder.is_dir():
            subfolder_output = output_folder / subfolder.name
            os.makedirs(subfolder_output, exist_ok=True)

            input_files = list(subfolder.glob("*_stacked.tif"))
            #input_files = list(subfolder.glob("*.tif"))
            print(input_files)

            if not input_files:
                print(f"No '_stacked.tif' files found in the subfolder {subfolder.name}. Skipping...")
                continue

            #grouped_files = group_files_by_prefix(input_files)
            input_files_strings = [str(file) for file in input_files]

            date_pattern = re.compile(r'_\d{8}_ortho_masked_stacked')

            grouped_files = {key: list(group) for key, group in groupby(sorted(input_files_strings, key=lambda f: date_pattern.split(Path(f).stem)[0]), key=lambda f: date_pattern.split(Path(f).stem)[0] )}

            for prefix, files in grouped_files.items():
                existing_shifted_files = [file.stem for file in subfolder_output.glob(f"{prefix}_*_shifted.tif")]

                for file_str in files:
                    file = Path(file_str)
                    shifted_file = subfolder_output / f"{file.stem}_shifted.tif"
                    if shifted_file.stem in existing_shifted_files:
                        print(f"Shifted file {shifted_file} already exists. Skipping...")
                        continue
                    # Update the path of reference_files_folder for each subfolder
                    reference_files_folder = subfolder_output / "reference_files"
                    os.makedirs(reference_files_folder, exist_ok=True)

                    reference_file_subfolder = reference_files_folder / f"{file.stem}_shifted.tif"

                    if reference_file_subfolder.exists():
                        print(f"Matching reference file {reference_file_subfolder} found in the subfolder. Copying to the main folder.")
                        reference_output_file_mainfolder = subfolder_output / f"{file.stem}_shifted.tif"
                        shutil.copy(str(reference_file_subfolder), str(reference_output_file_mainfolder))
                        continue
                    else:
                        reference_file = select_reference_file(files, reference_files_folder, prefix)

                            
                    if args.mode == "manual":
                        import manual_shift

                        for target_file_path in files:
                            target_file = Path(target_file_path)
                            output_file = subfolder_output / f"{target_file.stem}_shifted.tif"

                            # Check if the target file has a corresponding reference file
                            reference_file_name = f"{target_file.stem}_shifted.tif"
                            reference_file_subfolder = reference_files_folder / reference_file_name

                            if reference_file_subfolder.exists():
                                print(f"Matching reference file {reference_file_subfolder} found in the subfolder. Copying to the main folder.")
                                reference_output_file_mainfolder = subfolder_output / f"{target_file.stem}_shifted.tif"
                                shutil.copy(str(reference_file_subfolder), str(reference_output_file_mainfolder))
                                continue
                            elif output_file.exists():
                                print(f"Output file '{output_file.name}' already exists. Skipping to the next target file.")
                                continue

                            # Proceed with the manual shifting
                            manual_shift.main(str(reference_file), str(target_file), str(output_file))      
                                        
                    elif args.mode == "automated":
                        import auto_shift
                        for target_file_path in files:
                            target_file = Path(target_file_path)
                            output_file = subfolder_output / f"{target_file.stem}_shifted.tif"
                            if output_file.exists():
                                print(f"Output file '{output_file.name}' already exists. Skipping to the next target file.")
                                continue
                            auto_shift.main(str(reference_file), str(target_file), str(output_file))
                    else:
                        print("Invalid alignment mode. Please use 'manual' or 'automated'.")

if __name__ == "__main__":
    main()