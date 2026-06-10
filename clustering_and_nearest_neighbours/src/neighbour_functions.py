from typing import Dict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from src.data_functions import get_table_from_path
from scipy.spatial.distance import cdist
from sklearn.neighbors import NearestNeighbors
from itertools import product
import copy


def nearest_neighbours(
        loaded_config: Dict,
        df: pd.DataFrame,
        number: int,
        geography_col: str ="AREACD",
        distance_metric: str = "euclid",
):
    """
    Generates lists of statistical nearest neighbours from input metrics

    Parameters
    ----------
    loaded_config : Dict
        Contains the loaded config.
    data : pd.DataFrame
        Processed data for all nearest neighbour areas.
    number : int
        Number of neighbours required
    geography_col : str, optional
        Name of the geography column to index. The default is "AREACD".
    distance_metric : str, optional
        Type of distance used. The default is "euclid".    

    Returns
    -------
    distances: pd.DataFrame
        Dataframe including the specified number of nearest neighbours for each area.   
    distances_table: pd.DataFrame
        Dataframe including the distance between all areas in the model.
    """
    #Set index, replace NAs and standardise data
    geographies = list(df[geography_col])
    data = copy.deepcopy(df)
    data.set_index(geography_col, inplace=True)
    data.fillna(data.median(numeric_only= True), inplace= True)
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    #Generate distance matrix
    distances = cdist(data_scaled, data_scaled, distance_metric)
    distances_table = copy.deepcopy(distances)
    distances_table = pd.DataFrame(distances_table)
    distances = pd.DataFrame(distances, columns=geographies, index=geographies)
    
    #Create dataframe of closest points
    distances = distances.apply(lambda row: pd.Series([col for _, col in sorted(zip(row.values, distances.columns))], index=row.index), axis=1)
    distances = distances.rename(columns={x:y for x,y in zip(distances.columns,range(0,len(distances.columns)))})
    distances.reset_index(inplace=True)

    #Remove index variable
    distances = distances.drop(['index'],axis=1)

    #Trim dataframe to desired number
    distances = distances.iloc[:, :number+1]
    
    return distances, distances_table


    
def find_optimal_neighbors(
        loaded_config: Dict,
        df:pd.DataFrame,
        max_neighbours:float,
        Area_code: str="AREACD",
        ):
    """
    Calculates the number of neighbours that can be considered similar    
    
    Parameters
    ----------
    loaded_config : Dict
        Saved loaded config.
    df : pd.DataFrame
        Input data.
    max_neighbours : float
        Maximum number of neighbours to be considered.
    Area_code : str, optional
        Column of dataframe containing area codes. The default is "AREACD".

    Returns
    -------
    sorted_distances: pd.DataFrame
        Sorted dataframe representing optimal nearest neighbours.

    """
    
    path=loaded_config["outputs_file_path"]
    df = df.set_index(Area_code)  
    df.fillna(0, inplace=True)
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df)
    nbrs = NearestNeighbors(n_neighbors=max_neighbours).fit(df_scaled)
    distances, indices = nbrs.kneighbors(df_scaled)
        
    sorted_distances = np.sort(distances[:, -1])
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_distances, marker='o', color='blue')
    plt.title("Elbow Method for Optimal k (Nearest Neighbors)")
    plt.xlabel("Data Points")
    plt.ylabel("Distance to k-th Neighbor")
    plt.grid()
    plt.savefig(f"{path}/Elbow Method for Optimal k (Nearest Neighbors).jpeg")
    return sorted_distances
    
    
