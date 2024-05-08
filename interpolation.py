import numpy as np
import rasterio
import pathlib
from sklearn.neighbors import KNeighborsRegressor
import matplotlib.pyplot as plt

from matplotlib.backend_bases import MouseButton


def interpolate_images(input_dir, click_limit=36):
    # List of TIFF files that meet the condition
    tif_files = [file for file in input_dir.glob('*.tif') if "ortho" not in file.stem]
    
    def onclick(event, points, limit):
        if event.button == MouseButton.RIGHT:  # Check for right-click
            x, y = int(event.xdata), int(event.ydata)  # Convert coordinates to integers
            plt.plot(x, y, 'ro')
            pixel_value = image_data[y, x]  # Access the pixel value at (x, y)
            lon, lat = src.xy(y, x)  # Convert pixel coordinates to geographic coordinates (UTM 32616)
            points.append((lon, lat, pixel_value))
            print(x, y, lon, lat, pixel_value)
            plt.draw()

            # Check if the limit is reached
            if len(points) >= limit:
                plt.title(f'Right-click limit reached (Limit: {limit}). Auto-closing...')
                #plt.pause(1)  # Pause for a moment to display the title
                plt.close()  # Close the figure


    for tif_file in tif_files:
        
        # Check if the output file already exists
        parts = tif_file.stem.split('_')[:-1]
        new_stem = "_".join(parts) + "_baresoil"
        new_tif_path = input_dir / (new_stem + ".tif")

        if new_tif_path.exists():
            print(f"Output file {new_tif_path} already exists. Skipping...")
            continue
        # Open the TIFF image
        with rasterio.open(tif_file) as src:
            print("Plotting:", tif_file)
            # Read the image data
            image_data = src.read(1)
            
            # Extract spatial information
            src_transform = src.transform
            src_crs = src.crs
            src_height, src_width = src.shape

            # Calculate vmin and vmax
            cmap = plt.cm.gray  # Use a grayscale colormap
            cmap.set_bad('black')  # Set the color for no-data values to black

            masked_data = np.ma.masked_where(image_data == -32767, image_data)

            # Display the image with a grayscale colormap
            plt.imshow(masked_data, cmap=cmap)
            plt.colorbar()

            # Collect points with x, y, and pixel intensity
            points = []
            # Flag to indicate whether the limit is reached
            #limit_reached = [False]

            # Connect the click event to the onclick function
            cid = plt.gcf().canvas.mpl_connect('button_press_event', lambda event: onclick(event, points, click_limit))
            #plt.gcf().canvas.mpl_connect('button_press_event', lambda event: onclick(event, points, click_limit, limit_reached))    

            plt.title('Right-click to select points')

            # Show the plot
            plt.show()
            
            # Continue with the rest of your code if the limit is reached
            # if limit_reached[0]:
            #     print(f"Right-click limit reached for {tif_file}. Continuing with the next steps...")


        # Close the figure to free up resources
        plt.close()
        
        plt.gcf().canvas.mpl_disconnect(cid)

        x, y, values = zip(*points)  # Extract coordinates and values

        # Define a coarser spatial resolution (e.g., 1 meter)
        resolution = 0.2  # in meters

        # Calculate the number of rows and columns based on the coarser resolution
        rows = int(src_height * src.res[0] / resolution)
        cols = int(src_width * src.res[1] / resolution)

        # Create a grid with the coarser spatial resolution
        xi, yi = np.meshgrid(np.linspace(src.bounds.left, src.bounds.right, cols),
                            np.linspace(src.bounds.bottom, src.bounds.top, rows))
        print("kNN interpolation being carried out")
        # Fit a k-NN regressor
        knn = KNeighborsRegressor(n_neighbors=12)  # Adjust n_neighbors as needed
        knn.fit(list(zip(x, y)), values)

        # Predict values at grid locations
        zi = knn.predict(np.c_[xi.ravel(), yi.ravel()])
        zi = zi.reshape(xi.shape)

        # Save the interpolated raster to the output directory with '_baresoil.tif' appended
        #new_tif_path = input_dir / f"{tif_file.stem}_baresoil.tif"
        
        # Extract parts of the stem name separated by "_"
        parts = tif_file.stem.split('_')[:-1]

        # Create the new stem by joining the parts and appending '_baresoil'
        new_stem = "_".join(parts) + "_baresoil"

        # Create the new_tif_path by combining the input_dir and the new stem with '_baresoil.tif' appended
        new_tif_path = input_dir / (new_stem + ".tif")

        
        print(f"{new_tif_path} being saved to {input_dir}")
        
        with rasterio.open(new_tif_path, 'w', driver='GTiff', width=src_width, height=src_height,
                            count=1, dtype=np.float32, crs=src_crs,
                            transform=src_transform) as dst:
            dst.write(zi, 1)
            
        print("All interpolations done")
