#import matplotlib.pyplot as plt
from pyproj import CRS  # Import CRS from pyproj
import matplotlib
from matplotlib.colors import Normalize
import rasterio
from rasterio.transform import xy
from config import ImageDisplay

matplotlib.use('TkAgg')

# Define the CRS for UTM 16N (EPSG:32616)
utm_crs = CRS.from_epsg(32616)

    
def open_image(file_path):
    with rasterio.open(file_path) as src:
        image = src.read()
        stretched_image = src.read(window=rasterio.windows.Window(0, 0, src.width // 2, src.height // 2))
        width = src.width
        height = src.height
        transform = src.transform
        xmin, ymin = transform * (0,0)
        xmax, ymax = transform * (width, height)

        # Define the extent as [xmin, xmax, ymin, ymax]
        extent = [xmin, xmax, ymin, ymax]
   
        tiff_crs = CRS(src.crs.to_string())
        #print(tiff_crs)
        
    return image, stretched_image, tiff_crs, transform, extent

def display_image(image_band, extent, transform):
    image_display = ImageDisplay(image_band, extent, transform)
    return image_display
