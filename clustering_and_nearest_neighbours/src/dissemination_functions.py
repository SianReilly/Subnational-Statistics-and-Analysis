from typing import Dict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import pairwise_distances
from sklearn.decomposition import PCA
from src.data_functions import get_table_from_path

########################################################################################################################################################################
########################################################################################################################################################################
########################################################################################################################################################################
#### Variable comparison

def get_correlation_matrix(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Creates a correlation matrix between all included metrics.

    Parameters
    ----------
    df : pd.DataFrame
        dataframe of metrics to calculate correlations.

    Returns
    -------
    df_corr : pd.DataFrame
        A correlation matrix for all selected metrics

    """
    df = df.set_index("AREACD")
    df_corr = df.corr()
    return df_corr

def pca_analysis(
        loaded_config: Dict,
        df:pd.DataFrame,
        Area_code: str="AREACD",
        threshold: float=0.25,
        ):
    """
    Perform PCA analysis on the given DataFrame and generate plots and 
    dataframes for explained variance and feature loadings.

    Parameters
    ----------
    loaded_config : Dict
        Saved loaded config.
    df : pd.DataFrame
        DataFrame containing metrics to conduct PCA on.
    Area_code : str, optional
        Column in dataframe containing area codes. The default is "AREACD".
    threshold : float, optional
       Threshold for selecting important features based on their loadings.
       The default is 0.25.

    Returns
    -------
    pcs : pd.DataFrame
        DataFrame containing the principal components and their explained variance ratios.
    loading_df : pd.DataFrame
        DataFrame containing the loadings of each feature for each principal component.
    important_features : pd.DataFrame
        DataFrame containing the features with loadings above the specified threshold.

    """
    path=loaded_config["outputs_file_path"]
    df = df.set_index(Area_code)
    df.fillna(0, inplace=True)
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df)
        
    pca = PCA()
    pca.fit(df_scaled)
    
    explained_variance = pca.explained_variance_ratio_
    
    plt.figure(figsize=(15, 6))
    plt.plot(range(1, len(explained_variance) + 1), explained_variance, marker='o')
    plt.title('Explained Variance by Principal Components')
    plt.xlabel('Principal Component')
    plt.ylabel('Explained Variance Ratio')
    plt.xticks(range(1, len(explained_variance) + 1))
    plt.grid()
    plt.savefig(f"{path}/Explained Variance by Principal Components.jpeg")
    pcs = pd.DataFrame(range(1, len(explained_variance) + 1), explained_variance)
        
    loadings = pca.components_.T
    loading_df = pd.DataFrame(loadings, index=df.columns, columns=[f'PC{i+1}' for i in range(loadings.shape[1])])
        
    important_features = loading_df[loading_df.abs() > threshold]
        
    return pcs, loading_df, important_features
    
    
def variance_analysis(
        loaded_config: Dict,
        df:pd.DataFrame,
        Area_code: str="AREACD",
                      ):
    """
    Perform variance analysis on the given DataFrame and generate a plot for 
    the variance of Min-Max scaled features.

    Parameters
    ----------
    loaded_config : Dict
        Saved loaded config.
    df : pd.DataFrame
        DataFrame containing the data to be analyzed.
    Area_code : str, optional
        Column in dataframe containing area codes. The default is "AREACD".

    Returns
    -------
    variance : pd.Series
       Series containing the variance of each feature after Min-Max scaling.

    """
    path=loaded_config["outputs_file_path"]
    df = df.drop(Area_code, axis=1)
    scaler = MinMaxScaler()
    df_minmax_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
    variance = df_minmax_scaled.var()
    plt.figure(figsize=(10, 8))
    variance.plot(kind='barh', color='skyblue')
    plt.title('Variance of Min_max Scaled Features')
    plt.xlabel('Variance')
    plt.ylabel('Features')
    plt.savefig(f"{path}/Variance of Min_max Scaled Features.jpeg")
    return variance

def visualize_pairwise_distances(
        loaded_config: Dict,
        df:pd.DataFrame,
        Area_code: str="AREACD",
                      ):
    """
    Calculate and visualize pairwise distances between rows in the given DataFrame.

    Parameters
    ----------
    loaded_config : Dict
        Saved loaded config.
    df : pd.DataFrame
        DataFrame containing the data to be analyzed.
    Area_code : str, optional
        Column in dataframe containing area codes.. The default is "AREACD".

    Returns
    -------
    distances : np.ndarray
       Array containing the pairwise distances between rows of the scaled DataFrame.

    """
    path=loaded_config["outputs_file_path"]
    df = df.set_index(Area_code)
    df.fillna(0, inplace=True)
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df)
    distances = pairwise_distances(df_scaled, metric='euclidean')
    plt.figure(figsize=(10, 6))
    plt.hist(distances.flatten(), bins=50, color='blue', alpha=0.7)
    plt.title('Histogram of Pairwise Distances')
    plt.xlabel('Distance')
    plt.ylabel('Frequency')
    plt.savefig(f"{path}/Histogram of Pairwise Distances.jpeg")
    return distances

########################################################################################################################################################################
########################################################################################################################################################################
########################################################################################################################################################################
#### Cluster summary tables

def clusters_summary_stats(
        table_metrics: pd.DataFrame, 
        clusters_table: pd.DataFrame, 
        stats: str
) -> pd.DataFrame:
    """
    Creates summary stats for each cluster.

    Parameters
    ----------
    table_metrics
        DataFrame containing metrics.
    clusters_table
        DataFrame containing clusters.
    stats
        String or list of strings with names of methods. Options are:
        'mean' - calculates the mean of each cluster
        'median' - calculates the median of each cluster

    Returns
    -------
    clusters_head_avg: pd.dataframe
    DataFrame containing groups aggregated according to specified stats.
    """
    table_metrics_rescale = table_metrics.rename_axis(None).reset_index(level=0)
    
    #subset clusters table and merge to metrics
    clusters_table = clusters_table[["AREACD", "Cluster"]]
    clusters_head_figures = table_metrics_rescale.merge(clusters_table, on="AREACD", how="left")
    clusters_head_figures = clusters_head_figures.drop("index", axis=1)
    clusters_head_figures = clusters_head_figures.drop("AREACD", axis=1)
    
    #Calculate overall average
    clusters_overall_avg = clusters_head_figures.agg(stats)
    clusters_overall_avg = pd.DataFrame(clusters_overall_avg)
    clusters_overall_avg = clusters_overall_avg.transpose()
    clusters_overall_avg["Average of all areas"] = "Average of all areas"
    clusters_overall_avg = clusters_overall_avg.set_index("Average of all areas")
    
    #Calculate cluster averages
    clusters_avg = clusters_head_figures.groupby(["Cluster"]).agg(stats)
    clusters_avg = pd.DataFrame(clusters_avg)
    
    #Create final table
    frames = [clusters_avg, clusters_overall_avg]
    clusters_head_avg = pd.concat(frames)
    clusters_head_avg = clusters_head_avg.drop("Cluster", axis=1)
    return clusters_head_avg


def ITL1_summary(
        loaded_config: Dict, 
        clusters_table: pd.DataFrame
) -> pd.DataFrame:
    """
    Creates summary table showing the ITL1 regional distribution of each cluster

    Parameters
    ----------
    loaded_config : Dict
        Saved loaded config file.
    clusters_table : pd.DataFrame
        Table including the cluster allocation of each area.

    Returns
    -------
    ITL1_table : pd.DataFrame
        Summary table showing the ITL1 regional distribution of each cluster.

    """
    #Load in ITL1 lookup
    ITL1_lookup = get_table_from_path(table_name=(loaded_config["Geog_repo"]),
      path=(loaded_config["inputs_file_path"]),
      create_geodataframe=False,
      cols_to_select=[loaded_config["ITL1_col"], loaded_config["desired_geog"]])
    
    #Merge ITL1 lookup to cluster table and create ITL1 table
    ITL1_cluster_table = clusters_table.merge(ITL1_lookup, right_on=(loaded_config["desired_geog"]), left_on="AREACD", how="left")
    ITL1_table = pd.crosstab(index=(ITL1_cluster_table["Cluster"]), columns=(ITL1_cluster_table[loaded_config["ITL1_col"]]))
    return ITL1_table

########################################################################################################################################################################
########################################################################################################################################################################
########################################################################################################################################################################
#### Cluster visualisations

def cluster_map(
        loaded_config: Dict,
        clusters: pd.DataFrame,
        cmap: str='tab10'
):
    """
    Creates a map showing the cluster allocation of each area.
    
    Parameters
    ----------
    clusters : pd.DataFrame
        A geodataframe including the cluster allocation of each area.
    cmap : str, optional
        Map colour scheme. The default is 'tab10'.

    Returns
    -------
    map of clusters, which is saved into outputs folder

    """
    path=loaded_config["outputs_file_path"]
    clusters["Cluster"].apply(lambda x: int(x))
    n = len(pd.unique(clusters["Cluster"]))
    plot = clusters.plot(marker="-", column="Cluster", vmin=0,
      vmax=n,
      categorical=True,
      cmap=cmap,
      markersize=100,
      legend=True,
      figsize=(15, 15))
    plt.axis("off")
    plt.title("Cluster map", size=20, y=1.05)
    plt.savefig(f"{path}/Cluster_map.jpeg")
    return "map saved"


def radar_plot(
        loaded_config: Dict,
        metrics: pd.DataFrame, 
        clusters: pd.DataFrame, 
        centres: np.array, 
        cmap: str='tab10'
):
    """
    Creates radar plot using the standardised median of each metric for each cluster

    Parameters
    ----------
    loaded_config : Dict
        Saved config file including parameters.
    metrics : pd.DataFrame
        Table of metrics used for clustering.
    clusters : pd.DataFrame
        Table including the cluster allocation of each area.
    centres : np.array
        Cluster centres, output of the clustering function.
    cmap : str, optional
        Radar plot colour scheme. The default is 'tab10'.

    Returns
    -------
    Map saved into output folder.

    """
    analysis = clusters.merge(metrics, on="AREACD")
    performance = list(pd.DataFrame(centres)[0])
    indices = list(range(len(performance)))
    indices.sort(key=(lambda x: performance[x]))
    ranking = [0] * len(indices)
    for i, x in enumerate(indices):
        ranking[x] = i
    else:
        metrics = metrics.set_index("AREACD")
        categories = metrics.columns
        categories = [*categories, categories[0]]
        cluster_centres = []
        for i in range(len(centres)):
            cluster_i = centres[i].tolist()
            cluster_i = [*cluster_i, cluster_i[0]]
            cluster_centres.append(cluster_i)
        else:
            ranks = indices
            cluster_centres = [cluster_centres[rank] for rank in ranks]
            label_loc = np.linspace(start=0, stop=(2 * np.pi), num=(len(categories)))
            plt.figure(figsize=(14, 14))
            plt.subplot(polar=True)
            for i in range(len(centres)):
                plt.plot(label_loc, (cluster_centres[i]), label=("Cluster" + str(i)))
            else:
                plt.title("Radar plot", size=20, y=1.05)
                lines, labels = plt.thetagrids((np.degrees(label_loc)), labels=categories)
                plt.legend()
                n = len(centres)
                path=loaded_config["outputs_file_path"]
                plt.savefig(f"{path}/radar_plot.jpeg")
    return "radar plot saved"