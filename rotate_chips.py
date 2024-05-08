# import rasterio
# from rasterio.enums import Resampling

# from rasterio import rotate

# # Rest of your code...

# def rotate_image(data, nodata_value, rotation_angle, order=Resampling.nearest):
#   """
#   Rotates the entire image data and handles NoData values.

#   Args:
#       data: The entire image data as a NumPy array (bands, height, width).
#       nodata_value: The value representing NoData pixels.
#       rotation_angle: The rotation angle in degrees (counter-clockwise).
#       order: Resampling method for rotation (optional).

#   Returns:
#       A NumPy array containing the rotated image data with NoData handled.
#   """

#   # Rotate the entire image data
#   rotated_data = rotate(data, rotation_angle, order=order)
#   #rotated_data = rasterio.transform.rotate(data, rotation_angle, order=order)

#   # Handle NoData values
#   rotated_data[rotated_data == nodata_value] = nodata_value

#   return rotated_data

# def main():
#   # Replace with your file path
#   filepath = "../data/yan_image_chips/Chip_1.tif"

#   # Define rotation angle and NoData value
#   rotation_angle = 270  # Assuming NE orientation needs 270-degree rotation
#   nodata_value = 65535

#   with rasterio.open(filepath) as src:
#     # Get image information
#     data = src.read()  # Read all bands as a NumPy array
#     profile = src.profile.copy()

#     # Update profile with rotation
#     profile["transform"] = rasterio.Affine.rotation(rotation_angle)

#     # Rotate and handle NoData in the entire image
#     rotated_data = rotate_image(data, nodata_value, rotation_angle)

#     # Write the rotated data to a new file
#     with rasterio.open("../data/yan_image_chips/Chip_1_rotated.tif", "w", **profile) as dst:
#       dst.write(rotated_data)  # Write the entire rotated data

# if __name__ == "__main__":
#   main()




from osgeo import gdal  # For read and manipulate rasters
from affine import Affine  # For easly manipulation of affine matrix


# Some functions declaration for clarify the code


def raster_center(raster):
    """This function return the pixel coordinates of the raster center 
    """

    # We get the size (in pixels) of the raster
    # using gdal
    width, height = raster.RasterXSize, raster.RasterYSize

    # We calculate the middle of raster
    xmed = width / 2
    ymed = height / 2

    return (xmed, ymed)


def rotate_gt(affine_matrix, angle, pivot=None):
    """This function generate a rotated affine matrix
    """

    # The gdal affine matrix format is not the same
    # of the Affine format, so we use a bullit-in function
    # to change it
    # see : https://github.com/sgillies/affine/blob/master/affine/__init__.py#L178
    affine_src = Affine.from_gdal(*affine_matrix)
    # We made the rotation. For this we calculate a rotation matrix,
    # with the rotation method and we combine it with the original affine matrix
    # Be carful, the star operator (*) is surcharged by Affine package. He make
    # a matrix multiplication, not a basic multiplication
    affine_dst = affine_src * affine_src.rotation(angle, pivot)
    # We retrun the rotated matrix in gdal format
    return affine_dst.to_gdal()


# Import the raster to rotate
# Here I use a sample of GDAL, dowloaded here : https://download.osgeo.org/geotiff/samples/spot/chicago/SP27GTIF.TIF
# and transformed in nc with qgis
# NB: the transformation in nc is specific for the original question,
# this step is not neccecary if you copy/past this code
dataset_src = gdal.Open("../data/yan_image_chips/Chip_1.tif")

# For no overwriting the original raster I make a copy

# I Get the reading/writing driver (GTIFF)
driver = gdal.GetDriverByName("GTiff")
# A new raster, the destination file, is created.
# This raster is a copy of the source raster (same size, values...)
datase_dst = driver.CreateCopy("../data/yan_image_chips/Chip_1_rotated.tif", dataset_src, strict=0)

# Now we can rotate the raster

# First step, we get the affine tranformation matrix of the initial fine
# More info here : https://gdal.org/tutorials/geotransforms_tut.html#geotransforms-tut
gt_affine = dataset_src.GetGeoTransform()

# Second we get the center of the raster to set the rotation center
# Be carefull, the center is in pixel number, not in projected coordinates
# More info on the  "raster_center" comment's
center = raster_center(dataset_src)

# Third we rotate the destination raster, datase_dst, with setting a new
# affine matrix made by the "rotate_gt" function.
# gt_affine is the initial affine matrix
# -33 is an exemple angle (in degrees)
# and center the center of raster
datase_dst.SetGeoTransform(rotate_gt(gt_affine, -33, center))