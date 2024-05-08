import Metashape
import os, sys, time

# Specify the root directory where your Metashape projects are located
root_directory = "C:/Users/sebav/Downloads/PROJECTS"
# Create an 'OUTPUT' folder inside the root directory if it doesn't exist
output_root_directory = os.path.join(root_directory, "OUTPUT")
os.makedirs(output_root_directory, exist_ok=True)

# Create a function to process a single project
def process_steps(project_folder):
    # Create a subfolder for the specific project in the 'OUTPUT' folder
    output_project_directory = os.path.join(output_root_directory, project_folder)
    os.makedirs(output_project_directory, exist_ok=True)
    
    print(f'Initiazing {project_folder} project')

    # Create a new document
    doc = Metashape.Document()
    doc.save(os.path.join(output_project_directory, f"{project_folder}_project.psx"))
    
    # Create a new chunk
    chunk = doc.addChunk()

    # Set the geographic coordinate system to WGS 1984
    #chunk.crs = Metashape.CoordinateSystem("EPSG::4326")  # WGS 1984
    
    # Add photos to the chunk with XMP calibration data
    def find_files(folder, types):
        return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]
    
    full_project_folder = os.path.join(raw_directory, project_folder)  # Construct the full path
    
    photos = find_files(full_project_folder, [".tif"])

    print(f'Adding photos in {project_folder} project')
    
    chunk.addPhotos(photos, load_xmp_calibration=True,load_xmp_accuracy=True, load_xmp_orientation=True, load_xmp_antenna=True)
    doc.save()
    
    print(str(len(chunk.cameras)) + " images loaded")
    chunk.matchPhotos(keypoint_limit = 40000, tiepoint_limit = 10000, reference_preselection = True)
    doc.save()
    
    print(f'Aligning photos in {project_folder} project')
    chunk.alignCameras()
    doc.save()

    print(f'Optimize alignment of photos in {project_folder} project')
    chunk.optimizeCameras(fit_corrections=True)
    doc.save()

    print(f'Calibrating reflectance in {project_folder} project')
    chunk.calibrateReflectance(use_sun_sensor=True)
    doc.save()

    print(f'Building depth Maps in {project_folder} project')
    chunk.buildDepthMaps(downscale = 2, filter_mode = Metashape.MildFiltering)
    doc.save()

    print(f'Building model in {project_folder} project')
    chunk.buildModel(source_data = Metashape.DepthMapsData)
    doc.save()
    
    #chunk.buildTexture(texture_size = 4096, ghosting_filter = True)
    #doc.save()

    has_transform = chunk.transform.scale and chunk.transform.rotation and chunk.transform.translation

    if has_transform:
        print(f'Building Point Cloud in {project_folder} project')
        chunk.buildPointCloud()
        doc.save()
        
        print(f'Building DEM in {project_folder} project')
        chunk.buildDem(source_data=Metashape.PointCloudData)
        doc.save()
        
        print(f'Building ORTHO in {project_folder} project')
        chunk.buildOrthomosaic(surface_data=Metashape.ElevationData)
        doc.save()

    # export results
    output_report = os.path.join(output_project_directory, f"{project_folder}_report.pdf")
    chunk.exportReport(output_report)

    #if chunk.model:
    #    output_model = os.path.join(output_project_directory, f"{project_folder}_model.obj")
    #    chunk.exportModel(output_model)

    #if chunk.point_cloud:
    # chunk.exportPointCloud(output_folder + '/point_cloud.las', source_data = Metashape.PointCloudData)

    if chunk.elevation:
        
        print(f'Exporting DEM in {project_folder} project')
        output_dtm = os.path.join(output_project_directory, f"{project_folder}_dtm.tif")
        chunk.exportRaster(output_dtm, source_data = Metashape.ElevationData)

    if chunk.orthomosaic:
        
        print(f'Exporting ORTHO in {project_folder} project')
        output_orthomosaic = os.path.join(output_project_directory, f"{project_folder}_orthomosaic.tif")
        chunk.exportRaster(output_orthomosaic, source_data = Metashape.OrthomosaicData, save_alpha=False)
        doc.save()
    

# Iterate over each project folder in the 'RAW' subfolder and process it as an individual project
raw_directory = os.path.join(root_directory, "RAW")
project_folders = [folder for folder in os.listdir(raw_directory) if os.path.isdir(os.path.join(raw_directory, folder))]

print(project_folders)

# Iterate over each project folder in the 'RAW' subfolder and process it as an individual project
for project_folder in project_folders:
    process_steps(project_folder)

print("Processing completed for all projects.")
