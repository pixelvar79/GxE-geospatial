import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import contextily as ctx
from matplotlib.backend_bases import PickEvent

selected_indices = set()
dragging = False

def onpick(event):
    global dragging

    # Check if the event is a MouseEvent
    if isinstance(event, mpl.backend_bases.MouseEvent):
        # Check if any points were picked
        if not event.ind:
            return

        # Get the index of the picked polygon
        ind = event.ind[0]

        # Toggle the selection status of the polygon
        if ind in selected_indices:
            selected_indices.remove(ind)
        else:
            selected_indices.add(ind)

        # Print a message indicating which polygon was picked
        print(f'Polygon {ind + 1} was selected')

        # Redraw the map with the updated selection
        update_plot()

        # Set the dragging flag to True only for left-click
        if event.mouseevent.button == 1:
            dragging = True

    # Check if the event is a PickEvent
    elif isinstance(event, mpl.backend_bases.PickEvent):
        # Check if the right mouse button was clicked
        if event.mouseevent.button == 3 and selected_indices and dragging:
            # Get the new coordinates
            new_lon, new_lat = event.mouseevent.xdata, event.mouseevent.ydata

            # Update the selected polygons with the new location
            for ind in selected_indices:
                gdf.at[ind, 'geometry'] = Point(new_lon, new_lat)

            # Print a message indicating which polygons were dragged
            print(f'Polygons {", ".join(str(ind + 1) for ind in selected_indices)} were dropped to a new location')

            # Redraw the map with the updated positions
            update_plot()

            # Reset the dragging flag to False
            dragging = False

def update_plot():
    ax.clear()

    # Plot all polygons
    gdf.plot(ax=ax, alpha=0.7, picker=True)

    # Highlight selected polygons
    selected_gdf = gdf.iloc[list(selected_indices)]
    selected_gdf.plot(ax=ax, color='red', alpha=0.7)

    # Plot labels for all polygons
    for idx, row in gdf.iterrows():
        ax.text(row.geometry.centroid.x, row.geometry.centroid.y, str(row['order']),
                color='black', fontsize=8, ha='center', va='center')

    plt.draw()

# Load your GeoDataFrame with multipolygon geometry
file_path = r'D:\OneDrive - University of Illinois - Urbana\TF\JUPYTER_NOTEBOOKS\polygon_creator\output\WY_04042023_SX_20230807T2351_ortho_dsm.shp'
gdf = gpd.read_file(file_path)

# Create a matplotlib figure and axis
fig, ax = plt.subplots()

# Plot the GeoDataFrame with polygons and labels
gdf.plot(ax=ax, alpha=0.7, picker=True)
for idx, row in gdf.iterrows():
    ax.text(row.geometry.centroid.x, row.geometry.centroid.y, str(row['order']),
            color='yellow', fontsize=12, ha='center', va='center')

# Connect the pick event to the onpick function
fig.canvas.mpl_connect('pick_event', onpick)

# Display the plot
plt.show()
