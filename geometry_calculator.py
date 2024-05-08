import geopandas as gpd
from shapely.geometry import Polygon
import math
import os
from shapely.affinity import translate, rotate
from shapely.geometry import Point
import pandas as pd


def calculate_horizontal_geometry(width, length, horizontal_gap, vertical_gap, num_polygons, num_horizontal_polygons, x1, y1, x2, y2, tiff_crs, reverse_row_order, num_blocks=None, alley_width=None, multiblock=False):
    # Calculate the number of rows and columns based on user input
        num_vertical_polygons = math.ceil(num_polygons / num_horizontal_polygons)

        # Calculate the angle between the original line (x1, y1) - (x2, y2) and the horizontal axis
        angle_radians = math.atan2(y2 - y1, x2 - x1)

        # Calculate the new initial corner coordinates to align the left edge with the line
        new_x1 = x1 + (width/2)
        new_y1 = y1 #+ (width / 2)
        
        # Calculate the angle for tilting the MultiPolygon to align with the line
        tilt_angle = math.degrees(math.atan2(y2 - new_y1, x2 - new_x1))

        # Create an empty list to store polygons
        polygons = []

        for row in range(num_vertical_polygons):
            for col in range(num_horizontal_polygons):
                x_offset = col * (width + horizontal_gap)
                y_offset = row * (length + vertical_gap)

                # Calculate the coordinates based on the orientation angle, offsets, and gaps
                #lon1 = new_x1 + x_offset
                #lat1 = new_y1 + y_offset
                #lon2 = lon1 + length * math.cos(angle_radians)
                #lat2 = lat1 + length * math.sin(angle_radians)
                #lon3 = lon2 + width * math.cos(angle_radians + math.pi / 2)
                #lat3 = lat2 + width * math.sin(angle_radians + math.pi / 2)
                #lon4 = lon1 + width * math.cos(angle_radians + math.pi / 2)
                #lat4 = lat1 + width * math.sin(angle_radians + math.pi / 2)
                # Calculate the coordinates skipping orientation angle spec, but offsets, and gaps
                lon1 = new_x1 + x_offset
                lat1 = new_y1 + y_offset
                lon2 = lon1 + width
                lat2 = lat1 
                lon3 = lon2 
                lat3 = lat2 + length
                lon4 = lon1  
                lat4 = lat3 
                

                # Create a rectangle based on the coordinates
                rectangle = Polygon([(lon1, lat1), (lon2, lat2), (lon3, lat3), (lon4, lat4)])

                polygons.append(rectangle)

        # Create a GeoDataFrame from the list of individual polygons
        gdf = gpd.GeoDataFrame(geometry=polygons, crs=tiff_crs)
    
        # Calculate the rotation angle needed to align with the line between points 1 and 2
        #rotation_angle = math.degrees(angle_radians)
        # Calculate the tilt angle based on the difference between the original line angle and the horizontal axis
        tilt_angle = math.degrees(angle_radians) - 90.0

        # Rotate the entire GeoDataFrame to align with the line between points 1 and 2
        gdf['geometry'] = gdf['geometry'].rotate(tilt_angle, origin=(x1, y1))

        # Add 'order' and 'identifier' columns
        gdf['order'] = range(1, num_polygons + 1)
        #gdf['order'] = range(1351, 1351 + num_polygons )
        gdf['identifier'] = range(101, 101 + num_polygons)
        #gdf['identifier'] = range(1451, 1451 + num_polygons)

        return gdf

def calculate_geometry(width, length, horizontal_gap, vertical_gap, num_polygons, num_horizontal_polygons, x1, y1, x2, y2, tiff_crs, reverse_row_order, num_blocks=None, alley_width=None, multiblock=False):
    # Calculate the number of rows and columns based on user input
    num_vertical_polygons = math.ceil(num_polygons / num_horizontal_polygons)

    # Calculate the angle between the original line (x1, y1) - (x2, y2) and the horizontal axis
    angle_radians = math.atan2(y2 - y1, x2 - x1)

    # Create an empty list to store polygons
    polygons = []
    #order = 1  # Initial order value

    for col in range(num_horizontal_polygons):
        for row in range(num_vertical_polygons):
            if col % 2 == 0:  # Even columns (0-based index)
                # Even columns go from south to north
                x_offset = col * (width + horizontal_gap)
            else:  # Odd columns
                # Odd columns go from north to south
                x_offset = col * (width + horizontal_gap)
                if reverse_row_order:
                    row = num_vertical_polygons - row - 1  # Reverse the row order for odd columns

            y_offset = row * (length + vertical_gap)

            # Calculate the coordinates based on the orientation angle, offsets, and gaps
            lon1 = x1 + x_offset
            lat1 = y1 + y_offset
            lon2 = lon1 + width
            lat2 = lat1
            lon3 = lon2
            lat3 = lat2 + length
            lon4 = lon1
            lat4 = lat3

            # Create a rectangle based on the coordinates
            rectangle = Polygon([(lon1, lat1), (lon2, lat2), (lon3, lat3), (lon4, lat4)])

            polygons.append(rectangle)
            #order += 1  # Increment the order value

    # Create a GeoDataFrame from the list of individual polygons
    gdf = gpd.GeoDataFrame(geometry=polygons, crs=tiff_crs)

    # Calculate the rotation angle needed to align with the line between points 1 and 2
    tilt_angle = math.degrees(angle_radians) - 90.0

    # Rotate the entire GeoDataFrame to align with the line between points 1 and 2
    gdf['geometry'] = gdf['geometry'].rotate(tilt_angle, origin=(x1, y1))

    # Add 'order' and 'identifier' columns
    gdf['order'] = range(1, 1 + num_polygons)
    gdf['identifier'] = range(101, 101 + num_polygons)
    
    # Add 'order' and 'identifier' columns with adjusted values
    #gdf['order'] = range(order + 1, order + 1 + len(num_polygons))
    #gdf['identifier'] = range(order+ 101, order + 101 + len(num_polygons))
    
    # Update the 'order' value for the next block
    #order += len(num_polygons)
    
    return gdf


import math
import geopandas as gpd
from shapely.geometry import Polygon
import pandas as pd

def calculate_multiblock_geometry(width, length, horizontal_gap, num_polygons, vertical_gap, num_horizontal_polygons,
                                  x1, y1, x2, y2, tiff_crs, reverse_row_order, num_blocks=None, alley_width=None):
    # Calculate the number of rows and columns based on user input
    num_vertical_polygons = math.ceil(num_polygons / num_horizontal_polygons)

    # Create an empty list to store GeoDataFrames for each block
    gdf_list = []
    order_offset = 0  # Initial order offset for the entire multiblock geometry
    order = 1  # Initial order value for the entire multiblock geometry
    cumulative_block_x_offset = 0
    cumulative_block_y_offset = 0

    for block in range(num_blocks):
        # Calculate the total length of the previous blocks
        total_previous_length = block * (num_vertical_polygons * (length + vertical_gap) + alley_width)

        # Calculate the offsets for the current block
        if block == 0:
            block_x_offset = 0
            block_y_offset = 0
        else:
            block_x_offset = cumulative_block_x_offset
            block_y_offset = total_previous_length  # Use total_previous_length directly

        # Create an empty list to store polygons for the current block
        block_polygons = []

        for col in range(num_horizontal_polygons):
            for row in range(num_vertical_polygons):
                if col % 2 == 0:  # Even columns (0-based index)
                    # Even columns go from south to north
                    x_offset = col * (width + horizontal_gap)
                else:  # Odd columns
                    # Odd columns go from north to south
                    x_offset = col * (width + horizontal_gap)
                    if reverse_row_order:
                        row = num_vertical_polygons - row - 1  # Reverse the row order for odd columns

                y_offset = row * (length + vertical_gap)

                # Calculate the coordinates based on the orientation angle, offsets, and gaps
                lon1 = x1 + x_offset + block_x_offset
                lat1 = y1 + y_offset + block_y_offset
                lon2 = lon1 + width
                lat2 = lat1
                lon3 = lon2
                lat3 = lat2 + length
                lon4 = lon1
                lat4 = lat3

                # Create a rectangle based on the coordinates
                rectangle = Polygon([(lon1, lat1), (lon2, lat2), (lon3, lat3), (lon4, lat4)])

                block_polygons.append(rectangle)
                order += 1

        # Create a GeoDataFrame for the current block
        block_gdf = gpd.GeoDataFrame(geometry=block_polygons, crs=tiff_crs)

        # Calculate the rotation angle needed to align with the line between points 1 and 2
        tilt_angle = math.degrees(math.atan2(y2 - y1, x2 - x1)) - 90.0

        # Rotate the entire GeoDataFrame to align with the line between points 1 and 2
        block_gdf['geometry'] = block_gdf['geometry'].rotate(tilt_angle, origin=(x1, y1))

        # Translate the entire GeoDataFrame to adjust the position based on the block offset
        # block_gdf['geometry'] = block_gdf['geometry'].translate(0, 0)

        # Add 'order' and 'identifier' columns with adjusted values
        block_gdf['order'] = range(order_offset + 1, order_offset + 1 + len(block_polygons))
        block_gdf['identifier'] = range(order_offset + 101, order_offset + 101 + len(block_polygons))

        # Append the GeoDataFrame for the current block to the list
        gdf_list.append(block_gdf)

        # Update the cumulative block offsets for the next block
        #cumulative_block_x_offset +=  horizontal_gap #+ alley_width 
        cumulative_block_x_offset = 0 #+ alley_width

        # Update the cumulative block offset for the next block (except for the first block)
        if block > 0:
            cumulative_block_y_offset += num_vertical_polygons * (length + vertical_gap) + alley_width

        # Update the 'order' value for the next block
        order += len(block_polygons)

        # Update the 'order_offset' value for the next block
        order_offset += len(block_polygons)

    # Concatenate all GeoDataFrames for individual blocks into a single GeoDataFrame
    merged_gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True), crs=tiff_crs)

    return merged_gdf



def save_to_shapefile(gdf, tif_file_path, output_folder):
    # Extract the basename of the reference TIFF file
    tif_basename = os.path.basename(tif_file_path)
    
    # Remove the file extension (e.g., ".tif") to use as the shapefile name
    shapefile_name = os.path.splitext(tif_basename)[0]
    
    # Create the "output" folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Construct the output shapefile path using the TIFF file's basename
    output_path = os.path.join(output_folder, f"{shapefile_name}.shp")

    # Save the GeoDataFrame to the shapefile
    gdf.to_file(output_path)