from typing import Dict
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from src.data_functions import get_table_from_path

def relabel_clusters(
        clusters: pd.DataFrame, 
        model, 
        output: str='clusters'
) -> pd.DataFrame:
    """
    Relabels the clusters based on average metric value.

    Parameters
    ----------
    clusters : pd.DataFrame
        DataFrame containing cluster allocation of each area.
    model: 
        Instance of the clustering model.
    output : str, optional
        Specifies what to output. Options are 'clusters' and 'ranks'. The default is 'clusters'.

    Returns
    -------
    clusters: pd.DataFrame
    DataFrame containing re-labelled clusters, or ranks if specified.

    """
    centres = model.cluster_centers_
    performance = list(pd.DataFrame(centres)[0])
    indices = list(range(len(performance)))
    indices.sort(key=(lambda x: performance[x]))
    ranking = [0] * len(indices)
    for i, x in enumerate(indices):
        ranking[x] = i
    else:
        if output == "ranks":
            return indices
        clusters["Cluster"] = clusters["Cluster"].apply(lambda x: ranking[x])
        return clusters


def cluster_table(
        loaded_config: Dict, 
        clusters_table: pd.DataFrame
) -> pd.DataFrame:
    """
    Creates readable cluster table from the clustering model results.

    Parameters
    ----------
    loaded_config : Dict
        Contains the loaded config.
    clusters_table : pd.DataFrame
        DataFrame containing cluster allocation of each area.

    Returns
    -------
    cluster_table : pd.DataFrame
        Readable table containing cluster allocation for each area.

    """
    Area_names = get_table_from_path(table_name=(loaded_config["Geog_repo"]),
      path=(loaded_config["inputs_file_path"]),
      create_geodataframe=False,
      cols_to_select=[loaded_config["desired_geog"], loaded_config["desired_geog_nm"]])
    cluster_table = clusters_table.merge(Area_names, right_on=(loaded_config["desired_geog"]), left_on="AREACD", how="left")
    cluster_table = cluster_table[["AREACD", loaded_config["desired_geog_nm"], "Cluster"]]
    return cluster_table



def make_clustering_model(
    metrics: pd.DataFrame, 
    loaded_config: Dict, 
    seed: int=19042022, 
    n_init: int=10, 
    min_k: int=4, 
    max_k: int=15,
):
    """
    Takes the input metrics and creates clustering model to group similar areas.

    Parameters
    ----------
    metrics : pd.DataFrame
        Winsorized and processed DataFrame containing clustering input metrics.
    loaded_config : Dict
        Contains the loaded config.
    seed : int, optional
        Seed for clustering initialisation. The default is 19042022.
    n_init : int, optional
        number of clustering model initialisations. The default is 10.
    min_k : int, optional
        Minimum number of clusters. The default is 4.
    max_k : int, optional
        Maximum number of clusters. The default is 15.

    Returns
    -------
    best_clusters: pd.DataFrame
        geodataframe including cluster allocation and mapping infromation    
    cluster_centers: np.array
        array of cluster centres used for the radar plot
    sil_data_df: pd.DataFrame.
        dataframe including the silhouette score.
    """
    np.random.seed(seed=seed)
    best_k = 0
    best_sil = 0
    min_k = min_k
    max_k = max_k
    metrics_indexed = metrics.set_index("AREACD")
    
    #optimises the number of clusters over the specified range
    for k in range(min_k, max_k):
        np.random.seed(seed=seed)
        model = KMeans(n_clusters=k, n_init=n_init, max_iter=300)
        no_na_metrics = metrics_indexed[metrics_indexed.notna().all(axis=1)]
        scaler = StandardScaler()
        metrics_scaled = scaler.fit_transform(no_na_metrics)
        model.fit(metrics_scaled)
        clusters = pd.DataFrame(no_na_metrics.reset_index("AREACD"))
        clusters["Cluster"] = model.labels_
        labels = model.fit_predict(no_na_metrics)
        sil = silhouette_score(no_na_metrics, labels)
        if sil > best_sil:
            best_sil = sil
            best_k = k
    np.random.seed(seed=seed)
    
    #specifies the best model using optomised k
    best_model = KMeans(n_clusters=best_k, n_init=n_init, max_iter=300)
    no_na_metrics_best = metrics_indexed[metrics_indexed.notna().all(axis=1)]
    scaler = StandardScaler()
    metrics_scaled = scaler.fit_transform(no_na_metrics_best)
    best_model.fit(metrics_scaled)
    best_clusters = pd.DataFrame(no_na_metrics_best.reset_index()["AREACD"])
    best_clusters["Cluster"] = best_model.labels_
    
    #loads in the shapefile and stitches to cluster table
    la_geo = get_table_from_path(
            table_name=(loaded_config["shapefile"]),
            path=(loaded_config["inputs_file_path"]),
            cols_to_select=[loaded_config["shapefile_area_col"], "geometry", "BNG_E", "BNG_N"],
            create_geodataframe=True)

    best_clusters = la_geo.merge(best_clusters, right_on="AREACD", left_on=(loaded_config["shapefile_area_col"]), how="right")
    best_clusters = best_clusters.drop((loaded_config["shapefile_area_col"]), axis=1)
    
    #obtains the cluster centres
    best_clusters = relabel_clusters(best_clusters, best_model)
    cluster_centers = best_model.cluster_centers_
    labels = best_model.fit_predict(no_na_metrics_best)
    
    #gets the silhouette score and makes cluster table
    sil_score = silhouette_score(no_na_metrics_best, labels)
    sil_data = ["silhouette score", sil_score]
    sil_data_df = pd.DataFrame([sil_data], columns=["Measure", "Value"])
    return (best_clusters, cluster_centers, sil_data_df)


