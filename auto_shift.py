import rasterio
import numpy as np
import argparse
import scipy.signal

def find_shift(reference_file, target_file):
    # Open the reference and target TIF files using rasterio
    with rasterio.open(reference_file) as ref_ds, rasterio.open(target_file) as target_ds:
        # Read the reference and target bands
        ref_band = ref_ds.read(1)
        target_band = target_ds.read(1)
        
        width = ref_ds.width  # Width of the image
        height = ref_ds.height  # Height of the image
        # Calculate the center coordinates
        center_x = width // 2
        center_y = height // 2

        # Define the ROI boundaries around the center
        roi_width = 600  # Adjust the width as needed
        roi_height = 600  # Adjust the height as needed

        # Calculate the top-left and bottom-right coordinates of the ROI
        x1 = center_x - roi_width // 2
        y1 = center_y - roi_height // 2
        x2 = x1 + roi_width
        y2 = y1 + roi_height
        
        ref_roi = ref_band[y1:y2, x1:x2]
        target_roi = target_band[y1:y2, x1:x2]

        cross_corr = scipy.signal.correlate2d(target_roi, ref_roi, mode='same', boundary='wrap')

        max_corr_offset = np.unravel_index(np.argmax(cross_corr), cross_corr.shape)

        shift_x = max_corr_offset[1] - target_roi.shape[1] // 2
        shift_y = max_corr_offset[0] - target_roi.shape[0] // 2


    return shift_x, shift_y

def shift_and_align(reference_file, target_file, output_file):
    # Find the shift using cross-correlation
    shift_x, shift_y = find_shift(reference_file, target_file)

    # Open the reference and target TIF files using rasterio
    with rasterio.open(reference_file) as ref_ds, rasterio.open(target_file) as target_ds:
        # Calculate the new affine transform for the output dataset with the calculated shifts
        output_transform = target_ds.transform * rasterio.Affine.translation(shift_x, shift_y)

        # Define the profile for the output dataset based on the target dataset
        profile = target_ds.profile

        # Update the transformation in the profile
        profile["transform"] = output_transform

        # Copy the CRS information from the reference dataset
        profile["crs"] = ref_ds.crs

        # Create the output TIF file for the shifted target image
        with rasterio.open(output_file, 'w', **profile) as output_ds:
            # Loop through each band in the target dataset
            for band_idx in range(1, target_ds.count + 1):
                # Read the data from the target band
                target_band = target_ds.read(band_idx)
                
                # Write the data to the corresponding band in the output dataset
                output_ds.write(target_band, band_idx)

def main():
    parser = argparse.ArgumentParser(description="Shift and align two geospatial raster images.")
    parser.add_argument("reference_file", help="Path to the reference TIF file")
    parser.add_argument("target_file", help="Path to the target TIF file")
    parser.add_argument("output_file", help="Path for the output shifted target TIF file")

    args = parser.parse_args()

    shift_and_align(args.reference_file, args.target_file, args.output_file)
    print("Target image has been shifted and saved to", args.output_file)

if __name__ == "__main__":
    main()
