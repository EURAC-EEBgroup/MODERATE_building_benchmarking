# GET DATA FROM BUILDING
import requests
import pandas as pd
import numpy as np 
from sklearn.cluster import DBSCAN
from scipy import stats
from globals import url_shops, get_shops_api_token

# ==================================================

# df_metadata = pd.read_json("/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/00_GitHubProject/benchmarking_geoapp/callbacks/metadata.json")
all_temp_param  =['Internal temperature area 1 (Celsius degree)', 'Internal temperature area 2 (Celsius degree)',
    'Internal temperature area 3 (Celsius degree)', 'Internal temperature area 4 (Celsius degree)',
    'Internal temperature area 5 (Celsius degree)', 'Internal temperature area 6 (Celsius degree)',
    'Internal temperature area 7 (Celsius degree)', 'External temperature (Celsius degree)',
]
all_power_param = ['HVAC power (kW)','Global power (kW)']
# ==================================================

def get_data_from_shops(url_shops, id_mesurement, time_start, time_end):
    '''
    Retrieve time-series data for a specific measurement from the shops API.

    Parameters
    ----------
    url_shops : str
        URL of the shops API endpoint (e.g., "api.example.com").
    id_measurement : str or int
        Specific ID of the measurement (retrievable from a JSON or metadata file).
    time_start : str
        Start time for the data query in the format 'YYYY-MM-DD' (e.g., '2022-09-15').
    time_end : str
        End time for the data query in the format 'YYYY-MM-DD' (e.g., '2022-09-15').

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the retrieved data. The DataFrame has:
        - A 'time' column with datetime objects as the index.
        - A column with the measurement values named after the `id_measurement`.
        If no data is retrieved, an empty DataFrame with the same structure is returned.
    '''

    # Construct the API endpoint URL with the measurement ID and time range as query parameters.
    url = f"{url_shops}/store_data/api/v1/measurements/{id_mesurement}?time_from={time_start}&time_to={time_end}"
    
    # Define the authorization header using the provided token.
    token_ = get_shops_api_token()
    headers = {'Authorization': f'Bearer {token_}'}
    
    # Send a GET request to the API and parse the JSON response into a pandas DataFrame.
    response = requests.request("GET", url, headers=headers)
    df_data = pd.DataFrame(response.json())
    
    # If the DataFrame is not empty, preprocess the data.
    if not df_data.empty:
        # Convert the 'time' column to datetime format for easier time-based analysis.
        df_data['time'] = pd.to_datetime(df_data['time'])
        
        # Remove the 'sensor_id' column as it is not relevant to the output structure.
        del df_data['sensor_id']
        
        # Rename columns: 'time' remains as is, and the measurement values are labeled by the `id_measurement`.
        df_data.columns = ['time', id_mesurement]
    else:
        # If no data is retrieved, return an empty DataFrame with the correct structure.
        df_data = pd.DataFrame({
            "time": [],
            f"{id_mesurement}": []
        })

    # Return the processed DataFrame.
    return df_data


def get_data_multiple_param(selected_param, df_metadata, selected_bui, time_start, time_end):
    '''
    Retrieve and process data for multiple parameters (e.g., temperature and energy) from sensors.

    Parameters
    ----------
    selected_param : list
        List of selected parameters to retrieve data for (e.g., ['temperature', 'energy']).
    df_metadata : pd.DataFrame
        Metadata DataFrame that maps buildings and parameters to sensor IDs.
    selected_bui : str
        Selected building identifier from which to retrieve data.
    time_start : str
        Start time for the data query in the format 'YYYY-MM-DD'.
    time_end : str
        End time for the data query in the format 'YYYY-MM-DD'.

    Returns
    -------
    tuple
        - df__ : pd.DataFrame
            Filtered metadata for the selected parameters and building.
        - merged_df_temp : pd.DataFrame
            Merged time-series data for temperature parameters.
        - merged_df_power : pd.DataFrame
            Merged time-series data for energy parameters.
    '''

    # Filter the metadata for the selected building
    df_ = df_metadata[selected_bui]
    
    # Further filter metadata for the selected parameters
    df__ = df_.loc[selected_param]

    # Identify temperature and energy parameters from the selected ones
    temp_p = [item for item in all_temp_param if item in selected_param]
    power_p = [item for item in all_power_param if item in selected_param]

    # TEMPERATURE DATA
    # ========================
    if temp_p:
        # Filter metadata for temperature parameters
        df__t = df_.loc[temp_p]

        # Retrieve temperature data from sensors
        data_sensors = []
        for sens in df__t.values.flatten().tolist():
            data_sensors.append(get_data_from_shops(url_shops, sens, time_start, time_end))

        # Merge the retrieved DataFrames for temperature data
        merged_df_temp = data_sensors[0]
        for df__s in data_sensors[1:]:
            merged_df_temp = pd.merge(merged_df_temp, df__s, on='time', how='outer')

        # Format the resulting DataFrame
        if not merged_df_temp.empty:
            merged_df_temp.index = pd.to_datetime(merged_df_temp['time'])
            del merged_df_temp['time']
    else:
        # If no temperature parameters, return an empty DataFrame
        merged_df_temp = pd.DataFrame()

    # ENERGY DATA
    # ========================
    if power_p:
        # Filter metadata for energy parameters
        df__p = df_.loc[power_p]

        # Retrieve energy data from sensors
        data_sensors_power = []
        for sens_p in df__p.values.flatten().tolist():
            data_sensors_power.append(get_data_from_shops(url_shops, sens_p, time_start, time_end))

        # Merge the retrieved DataFrames for energy data
        merged_df_power = data_sensors_power[0]
        for df__s in data_sensors_power[1:]:
            merged_df_power = pd.merge(merged_df_power, df__s, on='time', how='outer')

        # Format the resulting DataFrame
        if not merged_df_power.empty:
            merged_df_power.index = pd.to_datetime(merged_df_power['time'])
            del merged_df_power['time']
    else:
        # If no energy parameters, return an empty DataFrame
        merged_df_power = pd.DataFrame()

    # Return the metadata, merged temperature data, and merged energy data
    return df__, merged_df_temp, merged_df_power


def detect_outliers(df: pd.DataFrame, colName: str, method: str):
    '''
    Detect outliers in a time series dataset using specified methods.

    Parameters
    ----------
    df : pd.DataFrame
        Pandas DataFrame containing time series data.
    colName : str
        Name of the column to be analyzed for outliers.
    method : str
        Method to detect outliers. Supported options are:
        - "DBSCAN": Uses the DBSCAN clustering algorithm to detect outliers.
        - "Z_SCORE": Uses Z-score analysis to identify outliers.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing rows identified as outliers based on the selected method.
    '''

    # Check which method is selected for outlier detection
    if method == "DBSCAN":
        # Initialize DBSCAN with predefined parameters
        dbscan = DBSCAN(eps=0.5, min_samples=20)  # `eps` and `min_samples` can be tuned based on the dataset

        # Fit DBSCAN on the specified column and generate cluster labels (-1 indicates outliers)
        dbscan_labels = dbscan.fit_predict(df[[colName]])
        
        # Filter rows where DBSCAN labels are -1 (outliers)
        outliers = df[dbscan_labels == -1]

    elif method == "Z_SCORE":
        # Calculate Z-scores for the specified column
        z_scores = np.abs(stats.zscore(df[colName]))
        
        # Identify rows where the Z-score exceeds the threshold of 3 (common threshold for outliers)
        outliers = df[(z_scores > 3)]
    
    # If an unsupported method is provided, return an empty DataFrame or raise an error
    else:
        raise ValueError(f"Unsupported method '{method}'. Use 'DBSCAN' or 'Z_SCORE'.")

    return outliers


def post_data(csv_path, file_name):
    '''
    Post time-series data to a TimescaleDB using the API.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file that contains the time-series data to be uploaded.
    file_name : str
        Name of the file to be uploaded, as it will appear in the API.

    Returns
    -------
    str
        The response text from the API after attempting to upload the data.
    '''

    # API endpoint for uploading time-series data
    url = f"{url_shops}/store_data/api/v1/measurements"

    # Open the CSV file in binary mode for upload
    with open(csv_path, 'rb') as file:
        # Prepare the file as a multipart/form-data payload for the POST request
        files = [
            ('file', (file_name, file, 'text/csv'))
        ]
        
        # Headers for the request, including the Bearer token for authentication
        bearerAuth = get_shops_api_token()
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + bearerAuth  # Add the authentication token
        }

        # Send the POST request with the file and headers
        response = requests.post(url, headers=headers, files=files)
    
    # Return the response from the server as plain text
    return response.text


def calculate_degree_days(df, temperature_label='temperature'):
    '''
    Calculate Heating Degree Days (HDD) and Cooling Degree Days (CDD) from temperature data, 
    and compute additional metrics such as the mean temperature-to-HDD and temperature-to-CDD ratios.

    Parameters:
    -----------
    df : pd.DataFrame
        A DataFrame containing at least a 'time' column (datetime format) and a temperature column.
    temperature_label : str, optional
        The name of the column representing temperature values (default is 'temperature').

    Returns:
    --------
    tuple
        - df : pd.DataFrame
            The original DataFrame with added 'HDD' and 'CDD' columns.
        - mean_ratio : float
            The mean ratio of temperature to HDD for rows where HDD > 0.
        - mean_ratio_CDD : float
            The mean ratio of temperature to CDD for rows where CDD > 0.
    '''

    # Ensure the 'time' column is in datetime format for proper handling
    df['time'] = pd.to_datetime(df['time'])
    
    # Extract the month from the 'time' column for seasonal calculations
    df['month'] = df['time'].dt.month

    # Initialize 'HDD' (Heating Degree Days) and 'CDD' (Cooling Degree Days) to zero
    df['HDD'] = 0
    df['CDD'] = 0

    # Calculate HDD for the heating season (October to April: months 10, 11, 12, 1, 2, 3, 4)
    # HDD is calculated as max(0, 18 - temperature), where 18°C is the base temperature for heating.
    df.loc[df['month'].isin([10, 11, 12, 1, 2, 3, 4]), 'HDD'] = \
        df.loc[df['month'].isin([10, 11, 12, 1, 2, 3, 4]), temperature_label].apply(lambda t: max(0, 18 - t))

    # Calculate CDD for the cooling season (May to September: months 5, 6, 7, 8, 9)
    # CDD is calculated as max(0, temperature - 26), where 26°C is the base temperature for cooling.
    df.loc[df['month'].isin([5, 6, 7, 8, 9]), 'CDD'] = \
        df.loc[df['month'].isin([5, 6, 7, 8, 9]), temperature_label].apply(lambda t: max(0, t - 26))
    
    # Calculate the mean ratio of temperature to HDD for rows where HDD > 0
    # Filter rows where 'HDD' is greater than 0
    filtered_df = df[df['HDD'] > 0]

    # Compute the temperature-to-HDD ratio for these rows
    filtered_df['temperature_to_HDD_ratio'] = filtered_df[temperature_label] / filtered_df['HDD']

    # Calculate the mean of the temperature-to-HDD ratio
    mean_ratio = filtered_df['temperature_to_HDD_ratio'].mean()

    # Calculate the mean ratio of temperature to CDD for rows where CDD > 0
    # Filter rows where 'CDD' is greater than 0
    filtered_df_CDD = df[df['CDD'] > 0]

    # Compute the temperature-to-CDD ratio for these rows
    filtered_df_CDD['temperature_to_CDD_ratio'] = filtered_df_CDD[temperature_label] / filtered_df_CDD['CDD']

    # Calculate the mean of the temperature-to-CDD ratio
    mean_ratio_CDD = filtered_df_CDD['temperature_to_CDD_ratio'].mean()

    # Return the updated DataFrame, mean HDD ratio, and mean CDD ratio
    return df, mean_ratio, mean_ratio_CDD
