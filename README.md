# GxE-Geospatial 

This is part of a research project for implementing a regional network for monitoring bioenergy field trials utilizing UAS. I have developed automated processing tools to reduce data latency and extract biological insights for decision-making in breeding programs. The tools enable the semi-automatic processing and extraction of spectral and photogrammetric features from aerial images captured from hundreds of flights at four locations in Central and South-East US (figure below). This collaborative effort involves research groups from the University of Illinois Urbana-Champaign, Mississippi State University, Alabama A&M University, and USDA-Louisiana. The project progresses through key stages to ensure automation: 1) selection of a suitable UAS platform, 2) easy data upload to a central server at the Institute for Genomic Biology at the University of Illinois Urbana-Champaign, 3) semi-automated processing and co-registration of images from successive flights, and 4) automated generation of image chips and extraction of temporal trajectories at the genotype and plot levels. Initial results indicate distinctive temporal trajectories for the same genetic materials across locations, suggesting the potential use of aerial imagery to anticipate decisions, reduce costs, and understand genotype-by-environment interactions in breeding programs. 

This is a sequence of Python scripts that allow to semi-automatically process large volumne of UAS imagery from a P4 UAS platforms distributed in four locations across US.

This is an evolving process and the plan is to make it flexible enough to process any kind of aerial imagery regardless of the aerial platform or sensor dealing with.


1) check if anaconda is installed locally
```
conda --version

```
  https://docs.conda.io/projects/miniconda/en/latest/
  
  miniconda will be enough for creating venv and dependencies
  
  During the installation, you might be prompted to add Anaconda to the system PATH. If not, and if you encounter issues, you can add it manually:
  
  On Windows, you can check "Add Anaconda to my PATH environment variable" during installation.
  On Linux you may need to add the following line to your shell profile file (e.g., .bashrc or .zshrc):

Build local Conda virtual environment and dependencies
```
  conda create --name gxe python=3.9  

  conda activate gxe
  
  pip install -r requirements.txt
```
  rasterio==1.3.8
  pyproj==3.6.1
  fiona==1.9.4
  geopandas==0.14.0
  matplotlib==3.8.0
  numpy==1.26.0
  pandas==2.1.1
  scikit-image==0.22.0
  scipy==1.11.3
  tk==8.6.13
  seaborn

2) Execute lodging detection evaluation
```
  python lodging_detection.py --fit-type time-point 
```
  (for traditional time-point CNN analysis)

  or
  
  ```
  python lodging_detection.py --fit-type temporal 
```
  (for temporal integrated CNN analysis)

3) Execute lodging severity evaluation
```
  python lodging_severity.py --fit-type time-point
```
  (for traditional time-point CNN analysis)

  or
  ```
  python lodging_severity.py --fit-type temporal 
  ```
  (for temporal integrated CNN analysis)















<h1 style="text-align: center;">'pyAerialExtractor' A GEOSPATIAL TOOLBOX FOR PROCESSING VERY-HIGH-SPATIAL RESOLUTION AERIAL IMAGERY OVER AGRONOMIC AND BREEDING TRIALS</h1> 

-------
-------


The story of this started as part of a collaboratory regional nextwork among bioenergy breeders and agronomists willing to better understand the seasonal dynamics of these crops under different environment conditions in US.

The following diagram describes a summary of the steps involved in the processing of the datasets:

-------
-------

<p align="center">
  <img src="Screenshot1.png">
</p>


The process starts with the implementation of Metashape API Professional Edition in a BioCluster located at the Institie for Genomic Biology (IGB) at the University of Illinois Urbana-Champaign. This py script enables to automate 
the Metashape processing steps of the original imagery collected with the UAV flights at different locations preventing to use the interactive traditional GUI interface of the software which can be a limitation for processing large number 
of flights over the growing season of the crops.

------
------

*Reproject Tool* 

The tool was desinged as early step for checking and reprojecting if needed tif files generated in Metashape API and vector shapefiles under EPSG:3246 (spherical coordindates system) into planar coordindate systems e.g., EPSG:32616 (Illinois) 
given that planar features calculation is going to be produced in the following steps.

The following parameters should be provided in the tool as function arguments in the command line: (relative input folder path for shps, relative output folder path for shps, relative input folder path for tifs, relative output folder path for tifs, 
output target coordindate system).

