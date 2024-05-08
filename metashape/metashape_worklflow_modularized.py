import Metashape
import os
import argparse

def process_project(input_folder, output_folder):
    # Create an 'OUTPUT' folder inside the output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Create a new document
    doc = Metashape.Document()

    # Create a new chunk
    chunk = doc.addChunk()

    # Add photos to the chunk with XMP calibration data
    photos = [os.path.join(input_folder, filename) for filename in os.listdir(input_folder) if filename.endswith('.tif')]

    if not photos:
        print(f"No .tif images found in {input_folder}")
        return

    chunk.addPhotos(photos, load_xmp_calibration=True)

    chunk.matchPhotos(keypoint_limit=40000, tiepoint_limit=10000, reference_preselection=True)
    chunk.alignCameras()
    chunk.optimizeCameras(fit_corrections=True)
    chunk.calibrateReflectance(use_sun_sensor=True)
    chunk.buildDepthMaps(downscale=2, filter_mode=Metashape.MildFiltering)
    chunk.buildModel(source_data=Metashape.DepthMapsData)

    has_transform = chunk.transform.scale and chunk.transform.rotation and chunk.transform.translation

    if has_transform:
        chunk.buildPointCloud()
        chunk.buildDem(source_data=Metashape.PointCloudData)
        chunk.buildOrthomosaic(surface_data=Metashape.ElevationData)

    # Export results
    project_name = os.path.basename(input_folder)
    output_report = os.path.join(output_folder, f"{project_name}_report.pdf")
    chunk.exportReport(output_report)

    if chunk.elevation:
        output_dtm = os.path.join(output_folder, f"{project_name}_dtm.tif")
        chunk.exportRaster(output_dtm, source_data=Metashape.ElevationData)

    if chunk.orthomosaic:
        output_orthomosaic = os.path.join(output_folder, f"{project_name}_orthomosaic.tif")
        chunk.exportRaster(output_orthomosaic, source_data=Metashape.OrthomosaicData, save_alpha=False)

def main():
    parser = argparse.ArgumentParser(description="Process orthomosaic projects using Metashape")
    parser.add_argument("input_folder", help="Input folder containing orthomosaic projects")
    parser.add_argument("output_folder", help="Output folder for processed results")
    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder

    project_folders = [folder for folder in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, folder))]

    for project_folder in project_folders:
        project_input = os.path.join(input_folder, project_folder)
        project_output = os.path.join(output_folder, project_folder)
        process_project(project_input, project_output)

    print("Processing completed for all projects.")

if __name__ == "__main__":
    main()
