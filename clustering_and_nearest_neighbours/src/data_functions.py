from typing import Dict, Sequence
import pandas as pd
import numpy as np
import geopandas
import os

########################################################################################################################################################################
########################################################################################################################################################################
########################################################################################################################################################################
#### Data import and export

def get_table_from_path(
    table_name: str,
    path: str = "",
    create_geodataframe: bool = False,
    cols_to_select: Sequence[str] = "",
) -> pd.DataFrame:
    """
    Reads a table from a local file path 

    Parameters
    ----------
    table_name : str
        Name of the table to be read..
    path : str, optional
        Location of folder for reading data locally. The default is "".
    create_geodataframe : bool, optional
        Specifies whether to create a GeoDataFrame. The default is False.
    cols_to_select : Sequence[str], optional
        Desired columns to be imported. The default is "".

    Returns
    -------
    df : pd.DataFrame
        Loaded dataframe with specified columns.

    """
    
    if create_geodataframe:
        df = geopandas.read_file(f"{path}/{table_name}.shp")
    else:
        df = pd.read_csv(f"{path}/{table_name}.csv")
    if cols_to_select is not None:
        df = df.loc[:, cols_to_select]

    return df

def get_custom_metrics(
    df: pd.DataFrame,
    custom_metrics: Sequence[str],
) -> Sequence[pd.DataFrame]:
    """
    Creates DataFrames group of metrics specified in config.

    Parameters
    ----------
    df : pd.DataFrame
       Contains the loaded data.
    custom_metrics : Sequence[str]
        Sequence of metrics specified in the config.

    Returns
    -------
    metrics_dict :  Sequence[pd.DataFrame]
        List containing a DataFrame for each metric.

    """
    metrics = []
    for metric in custom_metrics:
        metrics.append(extract_single_metric(df, metric))
    
    metrics = [metric for metric in metrics if metric is not None]
    metrics_dict = {"custom_metrics": metrics}
    
    return metrics_dict

def extract_single_metric(
    df: pd.DataFrame,
    metric_name: str,
    indicator_column: str = "Indicator",
) -> pd.DataFrame:
    """
    Extracts a single metric from long-form input dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.
    metric_name : str
        Name of the metric to extract.
    indicator_column : str, optional
        Column containing metric names. The default is "Indicator".

    Returns
    -------
    extracted_metric : pd.DataFrame
        Single extracted metric.

    """
    if metric_name in df[indicator_column].unique():
        extracted_metric = df.loc[df[indicator_column] == metric_name]
        return extracted_metric
    else:
        print(f"{metric_name} not found in {indicator_column} column")


def combine_datasets(
    loaded_config: Dict,
    cols_to_select: Sequence[str],
) -> pd.DataFrame:
    """
    Loads and concatentates all data files in a folder.

    Parameters
    ----------
    loaded_config : Dict
        Saved config file.
    cols_to_select : Sequence[str]
        Columns that should be selected from the table.

    Returns
    -------
    df: pd.DataFrame
        DataFrame containing all data in folder location.

    """
    filenames_to_load = os.listdir(loaded_config['inputs_file_path'])
    filenames_to_load = [filename[:-4] for filename in filenames_to_load if filename.endswith(".csv")]
    
    df = pd.DataFrame()
    df = get_table_from_path(
        table_name=loaded_config["subnational_indicators_table_name"],
        path=loaded_config["inputs_file_path"],
        create_geodataframe=False,
        cols_to_select = None,
)

    return df


def import_data(
    loaded_config: Dict,
    cols_to_select: Sequence[str],
    table_name: str,
) -> Sequence[pd.DataFrame]:
    """
    Combines import functions and boundary update to create metrics dataframes

    Parameters
    ----------
    loaded_config : Dict
        Saved config file.
    cols_to_select : Sequence[str]
        Columns that should be selected from the table.
    table_name : str
        Name of the table containing the data.

    Returns
    -------
    metric_dfs : Sequence[pd.DataFrame]
        Sequence of processed metric dataframes.

    """

    df = combine_datasets(loaded_config, cols_to_select)

    df.loc[:, 'Value'] = pd.to_numeric(df['Value'], errors='coerce')

    metric_dfs = get_custom_metrics(df, loaded_config["custom_metrics_to_run"])

    return metric_dfs

def export_to_xlsx(
        loaded_config: Dict,
        frames: Sequence[str],
        file_name:str,
        include_maps=True
 ):
    """
    Function to export data in xlsx format

    Parameters
    ----------
    loaded_config : Dict
        Saved config file.
    frames : Sequence[str]
        A list of items to export and corresponding sheet names.
    file_name : str
        Desired export file name.
    include_maps : TYPE, optional
        Boolean operator for whether to include clustering maps and radar plot
        in the export. The default is True.

    Returns
    -------
    Exported table.

    """
    path=loaded_config["outputs_file_path"]
    writer = pd.ExcelWriter(f"{path}/{file_name}.xlsx", engine="xlsxwriter")
    for sheet, frame in frames.items():
        frame.to_excel(writer, sheet_name=sheet)
    else:
        if include_maps:
            path=loaded_config["outputs_file_path"]
            workbook = writer.book
            worksheet = workbook.add_worksheet("Cluster_map")
            worksheet.insert_image("A1", f"{path}/Cluster_map.jpeg")
            worksheet = workbook.add_worksheet("Radar_plot")
            worksheet.insert_image("A1", f"{path}/radar_plot.jpeg")
        writer.close()
    return "table exported"

########################################################################################################################################################################
########################################################################################################################################################################
########################################################################################################################################################################
#### Data cleaning

def get_code_column(
    df: pd.DataFrame,
    flag: str = 'E0',
) -> str:
    """
    Gets column containing specified substring.

    Parameters
    ----------
    df : pd.DataFrame
        Contains the loaded data.
    flag : str, optional
        Substring to filter area codes by. The default is 'E0'.

    Returns
    -------
    str
        Name of column with matching substring.

    """
    col = pd.Index(["AREACD"])
    for column in df.columns:
        if df.loc[df[column].astype(str).str.contains(flag), column].any():
            col = pd.Index([column])
    if len(col) == 0:
        print("ERROR: No columns that look like the contain geography codes found. Checking if the flag entered matches the expected pattern")

    return col


def UT_metric_to_LT(
    metric: pd.DataFrame,
    upper_to_lower_tier_lookup: pd.DataFrame,
    upper_tier_col: str,
    lower_tier_col: str,
    loaded_config: Dict,
) -> pd.DataFrame:
    """
    Imputes missing LTLA data with corresponding UTLA data

    Parameters
    ----------
    metric : pd.DataFrame
        Dataframe containing the metric to impute.
    upper_to_lower_tier_lookup : pd.DataFrame
        Contains the upper to lower tier lookup data.
    upper_tier_col : str
        Name of column containing upper tier local authority codes.
    lower_tier_col : str
        Name of column containing lower tier local authority codes.
    loaded_config : Dict
        Saved loaded config. 

    Returns
    -------
    full_metric : pd.DataFrame
        Metric containing imputed LTLA data.

    """
    upper_tier_col= loaded_config["upper_tier_code_column_name"]
    lower_tier_col= loaded_config["lower_tier_code_column_name"]
    
    #Se
    UT_list = upper_to_lower_tier_lookup[upper_tier_col].tolist()
    UT_metrics_to_join = metric[metric['AREACD'].isin(UT_list)]
    UT_metrics_to_join.reset_index()
    upper_to_lower_tier_lookup = upper_to_lower_tier_lookup.rename(columns={upper_tier_col: 'AREACD'})
    UT_metric_join = upper_to_lower_tier_lookup.merge(UT_metrics_to_join, on='AREACD', how='left')
    UT_metric = UT_metric_join
    UT_metric["AREANM"] = ""
    UT_metric = UT_metric[[lower_tier_col,"AREANM","Indicator", "Period", "Measure", "Unit", "Value"]]
    UT_metric = UT_metric.rename(columns={lower_tier_col: 'AREACD'})
    metric = metric.dropna(subset=['Value'])
    metric = metric[["AREACD", "AREANM","Indicator", "Period", "Measure", "Unit", "Value"]]
    UT_metric = UT_metric[~UT_metric['AREACD'].isin(metric['AREACD'])]
    full_metric = pd.concat([metric, UT_metric],ignore_index=True)

    
    return full_metric


def drop_index_column(
    df: pd.DataFrame,
    col_to_drop: str = 'index',
) -> pd.DataFrame:
    """
    Drops the index column from the data.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame including index to drop.
    col_to_drop : str, optional
        Name of column to remove. The default is 'index'.

    Returns
    -------
    df : pd.DataFrame
        DataFrame without dropped column.

    """
    if col_to_drop in df.columns:
        df = df.drop(columns=col_to_drop)

    return df


def harmonise_area_col_name(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Ensures area code column named "AREACD" and move to left of DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing subnational data.

    Returns
    -------
    df : pd.DataFrame
        DataFrame with harmonised area column.

    """
    area_col=get_code_column(df)[0]
    col = df.pop(area_col)
    df.insert(0, "AREACD", col)

    return df


def ensure_value_numeric(
    df: pd.DataFrame,
    value_col: str = "Value"
):
    """
    Ensures that the Value column is numeric.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing subnational data.
    value_col : str, optional
        Name of column containing numerical data. The default is "Value".

    Returns
    -------
    df : pd.DataFrame
        DataFrame with specified column changed to numeric type.

    """
    if not np.issubdtype(df[value_col].dtypes, np.number):
        df.loc[:, value_col] = pd.to_numeric(df[value_col], errors='coerce')

    return df


def all_cleaning(
    loaded_config: Dict,
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Applies all cleaning functions to the data.

    Parameters
    ----------
    loaded_config : Dict
        Saved loaded config. 
    df : pd.DataFrame
        DataFrame containing subnational data.

    Returns
    -------
    df : pd.DataFrame
        DataFrame with all cleaning applied.

    """
    ut_to_lt_lookup = get_table_from_path(
        table_name=loaded_config["lower_tier_to_upper_tier_lookup"],
        path=loaded_config["inputs_file_path"],
        create_geodataframe=False,
        cols_to_select=[loaded_config["upper_tier_code_column_name"], loaded_config["lower_tier_code_column_name"]],
    )
    #all unique area codes and names
    df_cdlm = df[["AREACD", "AREANM"]]
    df = UT_metric_to_LT(
         metric = df,
         upper_to_lower_tier_lookup=ut_to_lt_lookup,
         loaded_config=loaded_config,
         upper_tier_col= loaded_config["upper_tier_code_column_name"],
         lower_tier_col= loaded_config["lower_tier_code_column_name"],
    )
    df = drop_index_column(df)
    df = drop_index_column(df, col_to_drop='YEAR')
    df = harmonise_area_col_name(df)
    df = ensure_value_numeric(df)

    
    return df

def clean_groups(
    loaded_config: Dict,
    group: Sequence[pd.DataFrame],
) -> Sequence[pd.DataFrame]:
    """
    Cleans a group of metrics

    Parameters
    ----------
    loaded_config : Dict
        Saved loaded config. 
    group : Sequence[pd.DataFrame]
        Sequence of metrics to be cleaned.

    Returns
    -------
    group : Sequence[pd.DataFrame]
        Sequence of cleaned metrics.

    """

    for metric in range(len(group)):
            group[metric] = all_cleaning(loaded_config, group[metric])
    
    return group



def get_desired_geography(
    loaded_config: Dict,
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Subsets the loaded data for the desored geography.

    Parameters
    ----------
    loaded_config : Dict
        saved config containing model parameters.
    df : pd.DataFrame
        data frame containing all of the metrics.
    geography_col : str
        The name of the desired geography column in the lookup.

    Returns
    -------
    df : pd.dataframe
        A dataframe with all of the metrics at desired geography.

    """
    lookup = get_table_from_path(
        table_name=loaded_config["Geog_repo"],
        path=loaded_config["inputs_file_path"],
        create_geodataframe=False,
        cols_to_select=[loaded_config["desired_geog"]],
    )

    lookup = lookup.rename(columns={loaded_config['desired_geog']: 'AREACD'})
    df = lookup.merge(df, on = 'AREACD', how='left')
    return df


def metrics_to_table(
        metrics: Sequence[pd.DataFrame]
) -> pd.DataFrame:
    """
    Combines metrics into one pivot table.

    Parameters
    ----------
    metrics : Sequence[pd.DataFrame]
        List of DataFrames, each containing a metric.

    Returns
    -------
    metrics : pd.DataFrame
        Pivot table containing all metrics.

    """
    if len(metrics) > 0:
        metrics = pd.concat(metrics)
        metrics = pd.pivot_table(metrics, values="Value", columns="Indicator", index="AREACD")
    return metrics

########################################################################################################################################################################
########################################################################################################################################################################
########################################################################################################################################################################
#### Data tranformation

def get_winsorization_thresholds(
    df: pd.DataFrame,
    lower_threshold: float,
    upper_threshold: float,
) -> pd.DataFrame:
    """
    Creates table of Winsorization thresholds for data    

    Parameters
    ----------
    df : pd.DataFrame
        dataframe containing raw metrics.
    lower_threshold : float
        percentile threshold for lower bound in 0-1 format.
    upper_threshold : float
        percentile threshold for upper bound in 0-1 format.

    Returns
    -------
    df_thresholds : pd.dataframe
        Dataframe of the winsorization thresholds.

    """
    df = df.set_index("AREACD")
    df_thresholds = df.quantile([lower_threshold, upper_threshold])
    df_thresholds = df_thresholds.reset_index()
    return df_thresholds

def winsorize(
    df: pd.DataFrame,
    lower_threshold: float,
    upper_threshold: float,
) -> pd.DataFrame:
    """
    Applies Winsorization to the data at the specified thresholds.    

    Parameters
    ----------
    df : pd.DataFrame
        dataframe containing raw metrics.
    lower_threshold : float
        percentile threshold for lower bound in 0-1 format.
    upper_threshold : float
        percentile threshold for upper bound in 0-1 format.

    Returns
    -------
    df : pd.dataframe
        dataframe of winsorized data.

    """
    df = df.set_index("AREACD")
    df = df.clip(lower=df.quantile(lower_threshold), upper=df.quantile(upper_threshold), axis=1)
    df = df.reset_index()
    return df

