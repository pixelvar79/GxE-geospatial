# GxE-Geospatial 

This is part of a research project for implementing a regional network for monitoring bioenergy field trials utilizing UAS. I have developed automated processing tools to reduce data latency and extract biological insights for decision-making in breeding programs. The tools enable the semi-automatic processing and extraction of spectral and photogrammetric features from aerial images captured from hundreds of flights at four locations in Central and South-East US (figure below). This collaborative effort involves research groups from the University of Illinois Urbana-Champaign, Mississippi State University, Alabama A&M University, and USDA-Louisiana. The project progresses through key stages to ensure automation: 1) selection of a suitable UAS platform, 2) easy data upload to a central server at the Institute for Genomic Biology at the University of Illinois Urbana-Champaign, 3) semi-automated processing and co-registration of images from successive flights, and 4) automated generation of image chips and extraction of temporal trajectories at the genotype and plot levels. Initial results indicate distinctive temporal trajectories for the same genetic materials across locations, suggesting the potential use of aerial imagery to anticipate decisions, reduce costs, and understand genotype-by-environment interactions in breeding programs. 

This is a sequence of Python scripts that allow to semi-automatically process large volumne of UAS imagery from a P4 UAS platforms distributed in four locations across US.

This is an evolving process and the plan is to make it flexible enough to process any kind of aerial imagery regardless of the aerial platform or sensor dealing with.

All py files assumes assumes one target flight dataset per subfolder, so they iterate over them generating separated Metashape px and further processing steps.


1) check if anaconda is installed locally
```
conda --version

```
  https://docs.conda.io/projects/miniconda/en/latest/
  
  miniconda will be enough for creating venv and dependencies
  
  During the installation, you might be prompted to add Anaconda to the system PATH. If not, and if you encounter issues, you can add it         manually:
  
  On Windows, you can check "Add Anaconda to my PATH environment variable" during installation.
  On Linux you may need to add the following line to your shell profile file (e.g., .bashrc or .zshrc):

Build local Conda virtual environment and dependencies
```
  conda create --name gxe python=3.9  

  conda activate gxe
  
  pip install -r requirements.txt
```
  Metashape
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

2) Execute Metashape step, check guideline on how to install Metashape API and key license in https://agisoft.freshdesk.com/support/solutions/articles/31000148930-how-to-install-metashape-stand-alone-python-module 
```
  python metashape_workflow_modularized.py input_folder output_folder
```

3) Reproject all to common geographic system
```
  python reproject_files.py
```
4) Resample, mask, stack (5-MSI + CSM)

  ```
  python mas_stacking_processing.py
```

5) Shift X and Y correction between consecutive dates of Orthomosaics stacked and reprojected

```
python shift_corrector.py --mode manual 
```
6) Chips generator for each orthomosaic+CSM stack shift and ground normalized corrected (at field trial)

```
python chip_generator.py 
```
7) Tabular stats extractor at the plot level for each  orthomosaic+CSM stack shift and ground normalized corrected (at field trial). Included stats descriptors such as mean, min, max for each of the bands, csm, fcover, ndvi, ndre.

```
python tabular_stats_extractor.py 
```
The following diagram describes the steps involved in processing the datasets:
-------

<p align="center">
  <img src="Screenshot 2024-05-08 125520.png" width="400" height="400">
</p>



