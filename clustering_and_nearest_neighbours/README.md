# Clustering and Statistical Nearest Neighbours

This is the public version of the code used to create the ONS clustering and statistical nearest neighbours analysis, which groups UK local authorities with similar characteristics and outcomes. 
See the below for a guide to the different files within the clustering refactor repository. 
If you run the code as specified with suitable data, all outputs and model information will automatically be generated.

## Contact
This repository was developed by the ONS Subnational Methods for Dissemination team.

> To contact us raise an issue on Github or via email at [subnational@ons.gov.uk](mailto:subnational@ons.gov.uk).
> See our most recent publication here: [Clustering similar local authorities and statistical nearest neighbours in the UK](https://www.ons.gov.uk/peoplepopulationandcommunity/wellbeing/methodologies/clusteringsimilarlocalauthoritiesandstatisticalnearestneighboursintheuk)
> See our dataset here: [Clustering similar local authorities and statistical nearest neighbours in the UK, 2026](https://www.ons.gov.uk/peoplepopulationandcommunity/wellbeing/datasets/clusteringsimilarlocalauthoritiesandstatisticalnearestneighboursintheuk).

## Setup

* This project was developed using Python 3.10.5
* Required Python libraries are listed in `requirements.txt`

## Getting started

### Config.yaml
This file defines the file paths, the names of columns in the lookup files and the metrics you want to include in the model. There are notes within the script to guide you through this and the file must be saved before the model is run. Aside from the two analysis notebooks, this is the only file you need to alter to run the model.

### Notebooks/nn_analysis.ipynb
This notebook calls in the functions and information from the other files and runs the nearest neighbours analysis. 
As it is currently set up it will run the analysis, creating files for main results and variable selection alongside all relevant visualisations, which are saved in the specified output folder.
There are notes in each cell which detail what the code is doing and provides information on where you can customise the parameters of models.

### Notebooks/clustering_analysis.ipynb
This notebook calls in the functions and information from the other files and runs the clustering analysis. 
As it is currently set up it will run the analysis, creating files for main results and variable selection alongside all relevant visualisations, which are saved in the specified output folder. 
There are notes in each cell which detail what the code is doing and provides information on where you can customise the parameters of models.

### clustering_refactor/src

- `[data_functions.py]` - All functions required to set up the data that are called and qpplied in the analysis scripts. The sections in the script cover data import and export, data cleaning and data transformation (eg winsorization).
- `[neighbour_functions.py]` - The functions involved in implementing the euclidean distance calculation for the nearest neighbours as well as to find the optimum number of neighbours.
- `[clustering_functions.py]` - The functions involved in running the clustering model. These are called in the clustering_analysis notebook and have docstrings detailing inputs and outputs. Some functions have multiple outputs which must be allocated, these are detailed in the notes within the clustering_analysis notebook.
- `[dissemination_functions.py]` - The functions to compare variables and to create supplementary tables and plots that output from the analysis scripts. This includes PCA, correlations, variance analysis, cluster average, ITL distribution and charts such as cluster maps and radar plot.

### Data
To be compatible with the code, your data must include all variables stacked into one csv file. This data must include the following columns:
-	AREACD and AREANM: The code and name of each area.
-	Indicator: The name of the variable.
-	Period: Reference period of the source data.
-	Value: The data value for an area for a given variable.


### Lookups
The code requires several lookup files, which should be saved in a lookups folder. You can specify the file location, names and desired columns of the lookups within the config file.
The files required include:
-	Shapefiles: UK Local Authority District (LAD) boundary file - in shapefile format - used in our mapping function. These are available through the [ONS open geography portal](https://geoportal.statistics.gov.uk/datasets/79a4e87783be4b6bbb96ddad6dda52a3_0/explore)
-	Geography repository: A csv repository including sets of separate columns with geography names and codes. Any geography you have in your data and want to output can be added here, the base version needs lower-tier local authority names, codes and corresponding ITL1 regions. It also has the upper-tier local authority names and codes. This dataset is used in the functions to create summary tables of the clusters. [Available through the ONS open geoportal]( https://geoportal.statistics.gov.uk)

If you are struggling to source these lookups, we can provide them if you get in touch using the below email, however this is a busy shared inbox so there may be a slight delay in our reply.

## Project structure

```text
| config.yaml             			  	 <- contains all the configuration/settigs needed to run.
| requirements.txt          		 	 <- python libraries required.
|
+---src                    			 	 <- This is a placeholder which the pipeline populates with data
|   |  	data_functions.py            	 <- cleaning, importing and transforming the data
|   |   neighbour_functions.py    	     <- statistical nearest neighbours calculations 
|   |   clustering_functions.py          <- KMeans algorithm
|   |   dissemination_functions.py       <- variable summaries, summary tables and cluster visualisations
+--- notebooks                         
|   |   nn_analysis.ipynb         	     <- runs the nearest neighbours analysis using the modules above
|   |   clustering_analysis.ipynb        <- runs the clustering analysis using the modules above

```
