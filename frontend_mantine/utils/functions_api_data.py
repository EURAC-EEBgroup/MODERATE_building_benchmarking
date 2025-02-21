import requests
from globals import url_api_data_metadata, url_shops, get_shops_api_token
import pandas as pd
import json 
import numpy as np
from workalendar.europe import Italy
import re


def get_building_list() -> pd.DataFrame:
    '''
    Fetches the list of buildings stored in a TTL file from a specified API endpoint.

    Returns:
    --------
    pd.DataFrame
        A pandas DataFrame containing the list of buildings. The DataFrame has one column named 'Buis'.
    '''
    # Construct the API URL for fetching the building list
    url = f"{url_api_data_metadata}/moderate/api/v1/building_list"

    # Send a GET request to the API endpoint
    response = requests.request("GET", url)

    # Convert the JSON response into a pandas DataFrame
    building = pd.DataFrame(response.json())

    # Rename the column to 'Buis' (possibly short for 'Building IDs' or a specific naming convention)
    building.columns = ['Buis']

    # Return the DataFrame containing the building list
    return building


def get_elements_from_ttl(bui_name, brick_type):
    '''
    Fetches elements of a specific building and brick type from the TTL definition.

    Parameters:
    -----------
    bui_name : str
        Name of the building whose elements are to be retrieved.
    brick_type : str
        Type of brick element to retrieve (e.g., 'Zone', 'Room').

    Returns:
    --------
    dict
        JSON response containing the requested building elements.
    '''
    # Construct the API URL for fetching the building elements based on name and brick type
    url = f"{url_api_data_metadata}/moderate/api/v1/building/{bui_name}&{brick_type}"

    # Send a GET request to the API endpoint
    response = requests.request("GET", url, headers={}, data={})

    # Return the JSON response from the API
    return response.json()

    

def upload_file(file_path):
    '''
    Uploads a file to the specified API endpoint.

    Parameters:
    -----------
    file_path : str
        Path to the file to be uploaded.

    Returns:
    --------
    None
        Prints the status code and response body from the server.
    '''
    # Construct the API URL for uploading a file
    url = f"{url_api_data_metadata}/moderate/api/v1/upload_file"

    # Make a POST request to the API with the file path as a query parameter
    response = requests.post(url, params={"file_path": file_path})

    # Print the HTTP status code of the response
    print("Status Code:", response.status_code)

    # Try to print the JSON response; fallback to plain text if JSON is not valid
    try:
        print("Response Body:", response.json())
    except Exception as e:
        print("Response Body:", response.text)

        
def get_ttl_fil_from_bui_name(bui_name):
    '''
    Retrieve the TTL (Turtle) file content for a specific building.
    
    Parameters:
    -----------
    bui_name : str
        The name of the building in the backend's `bui_structure` of all TTL files.
    
    Returns:
    --------
    str
        The content of the TTL file as plain text if the request is successful.
    '''
    # API endpoint URL for retrieving building TTL files
    url = f"{url_api_data_metadata}/moderate/api/v1/building_ttl"

    # Query parameters: specify the file name of the desired building
    params = {
        "file_name": bui_name  
    }

    # Send a GET request to the endpoint with the provided parameters
    response = requests.get(url, params=params)

    # Check the response status and print the TTL content or an error message
    if response.status_code == 200:
        print(response.text)  # Output the TTL file content as plain text
    else:
        print(f"Error: {response.status_code}, {response.json()}")  # Print error details

    # Return the response content (TTL file text)
    return response.text


def get_elements_and_labels(bui_name):
    '''
    Retrieve the elements and labels associated with a specific building.

    Parameters:
    -----------
    bui_name : str
        The name of the building for which elements and labels are being retrieved.

    Returns:
    --------
    dict
        A dictionary containing "elements" and "labels" if the request is successful.
        Otherwise, returns the error text from the API response.
    '''
    # API endpoint URL for retrieving building graph information
    url = f"{url_api_data_metadata}/moderate/api/v1/building_graph"

    # Query parameters: specify the building name
    params = {"file_name": bui_name}

    # Send a GET request to the endpoint with the provided parameters
    response = requests.get(url, params=params)

    # Check the response status and process the result
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Print the elements and labels for debugging purposes
        print("Elements:", data["elements"])
        print("Labels:", data["labels"])
        
        # Return the data dictionary
        return data
    else:
        # Print error details if the request fails
        print(f"Error: {response.status_code}, {response.json()}")
        
        # Return the raw response text as an error message
        return response.text


def get_temperature_label_and_uuid(name_bui):
    '''
    Retrieve temperature-related sensor information for a specific building.

    Parameters:
    -----------
    name_bui : str
        The name of the building for which temperature sensor data is required.

    Returns:
    --------
    dict
        A dictionary containing the sensor information if the request is successful.
    '''
    # API endpoint URL for retrieving building sensors
    url = f"{url_api_data_metadata}/moderate/api/v1/building_sensors"

    # Query parameters: specify the building name
    params = {"file_name": name_bui}

    # Send a GET request to the endpoint with the provided parameters
    response = requests.get(url, params=params)

    # Check the response status and process the result
    if response.status_code == 200:
        # Print sensor data for debugging purposes
        print("Sensors:", response.json())
    else:
        # Print error details if the request fails
        print(f"Error {response.status_code}: {response.json()}")

    # Return the JSON response (sensor information)
    return response.json()


def get_meter_label_and_uuid(name_bui):
    '''
    Retrieve meter sensor data for a specific building, using the building's name to request the information.

    Parameters:
    -----------
    name_bui : str
        The name of the building for which meter data is to be fetched.

    Returns:
    --------
    dict
        The JSON response from the API, containing meter sensor data (labels, UUIDs, etc.) for the specified building.
    '''
    # Construct the URL for the API request, including the endpoint and query parameter for the building name
    url = f"{url_api_data_metadata}/moderate/api/v1/meter_sensors"
    
    # Set the query parameters, including the building name to filter the request
    params = {"file_name": name_bui}

    # Perform the GET request to the FastAPI endpoint with the specified parameters
    response = requests.get(url, params=params)

    # Check the HTTP response status
    if response.status_code == 200:
        # If the request was successful (status code 200), print the received sensor data (for debugging or information)
        print("Sensors:", response.json())
    else:
        # If the request failed, print the error code and the error message
        print(f"Error {response.status_code}: {response.json()}")

    # Return the JSON response data (which contains meter sensor information)
    return response.json()



def get_meter_label_and_uuid_weather(name_bui):
    '''
    Get outdoor temperature data providing the name of the building.
    
    Parameters:
    -----------
    name_bui : str
        The name of the building to retrieve outdoor temperature data for.
    
    Returns:
    --------
    dict
        JSON response from the API containing outdoor temperature data and related metadata.
    '''

    # Construct the URL to query the outdoor temperature data based on the building name
    url = f"{url_api_data_metadata}/moderate/api/v1/outdoor_temperature"
    
    # Set up parameters to pass to the API request, including the building name
    params = {"file_name": name_bui}

    # Make the GET request to the FastAPI endpoint with the specified parameters
    response = requests.get(url, params=params)

    # Return the JSON response from the API, which contains the temperature data
    return response.json()


def get_area_from_bui(name_bui):
    '''
    Get area from the building's metadata.
    
    Parameters:
    -----------
    name_bui : str
        The name of the building to retrieve area information for.
    
    Returns:
    --------
    dict
        JSON response from the API containing building area data.
    '''

    # Construct the URL to query the building area data based on the building name
    url = f"{url_api_data_metadata}/moderate/api/v1/building_area?file_name={name_bui}"

    # Make the GET request to retrieve the area information for the specified building
    response = requests.request("GET", url)

    # Return the JSON response containing the building's area information
    return response.json()


def extract_numeric_value(data):
    """
    Extracts the numeric value from the 'value' field if it contains 'square meter'.
    
    Parameters:
    -----------
    data : list
        A list of dictionaries that may contain a 'value' field with a string including 'square meter'.
    
    Returns:
    --------
    int or None
        The extracted numeric value (in square meters), or None if no valid value is found.
    """
    
    # Iterate through each item in the input data list
    for item in data:
        # Retrieve the 'value' field from each dictionary
        value = item.get("value", "")
        
        # Check if the value contains the substring "square meter"
        if "square meter" in value:
            # Use regex to extract the numeric part of the value
            match = re.search(r"\d+", value)
            if match:
                # Return the extracted numeric value as an integer
                return int(match.group())  # Convert the extracted value to an integer
    
    # Return None if no value matching the criteria is found
    return None


# ================================================================================
#                              TIME SERIES DATA
# ================================================================================
'''
Query to the timescale API to get time series data
'''
def get_first_and_last_value(id_measurement):
    '''
    Retrieves the first and last value of a measurement.

    Parameters:
    -----------
    id_measurement: ID of the measurement for which you want to obtain the first and last values.

    Returns:
    --------
    DataFrame containing the measurement data.
    '''
    # Constructs the URL to request the summary data for the measurement
    url = f"{url_shops}/store_data/api/v1/measurements/{id_measurement}/summary"
    
    # Sets the request headers with the authentication token
    token_ = get_shops_api_token()
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token_}"
    }

    # Sends a GET request to retrieve the data
    response = requests.get(url, headers=headers)
    
    # Prints the response status code (useful for debugging)
    print(response.status_code)

    # If the response is successful (status 200), converts the data into a DataFrame
    df_data = pd.DataFrame()
    if response.status_code == 200:
        df_data = pd.DataFrame(response.json())

    # Returns the DataFrame with the obtained data
    return df_data


    
def get_data_from_shops(id_mesurement, time_start, time_end):
    '''
    Retrieves data from a TimescaleDB where sensor data is stored.

    Parameters:
    -----------
    id_mesurement: ID of the measurement (e.g., a unique sensor identifier).
    time_start: Start date (e.g., '2022-09-15').
    time_end: End date (e.g., '2022-09-16').

    Returns:
    --------
    DataFrame with the measurement data for the specified time period.
    '''
    # Constructs the URL to obtain the measurement data
    url = f"{url_shops}/store_data/api/v1/measurements/{id_mesurement}?time_from={time_start}&time_to={time_end}"
    
    # Sets the header to include the authentication token
    token_ = get_shops_api_token()
    headers = {'Authorization': f'Bearer {token_}'}
    
    # Sends a GET request to retrieve the data
    response = requests.request("GET", url, headers=headers)
    
    # Converts the response into a DataFrame
    df_data = pd.DataFrame(response.json())
    
    # If the data is not empty, processes the DataFrame to set the 'time' column as the index
    if not df_data.empty:
        df_data['time'] = pd.to_datetime(df_data['time'])  # Converts 'time' column to datetime format
        del df_data['sensor_id']  # Removes the 'sensor_id' column
        df_data.columns = ['time', id_mesurement]  # Renames columns for clarity
    else:
        # If there is no data, returns an empty DataFrame with the appropriate column names
        df_data = pd.DataFrame({
            "time": [],
            f"{id_mesurement}": []
        })

    # Returns the DataFrame with the data
    return df_data


def get_values_from_multiparameters(id_measurements:list, time_start:str, time_end:str)->pd.DataFrame:
    '''
    Retrieves data from multiple measurements in a single DataFrame.

    Parameters:
    -----------
    id_measurements: List of measurement IDs (e.g., ['ce2bea9e...', '0c20c529...']).
    time_start: Start date (e.g., '2022-09-15').
    time_end: End date (e.g., '2022-09-15').

    Returns:
    --------
    DataFrame with data from all measurements for the specified time period.
    '''
    # Creates a list to collect the DataFrames for each measurement
    dataframes = []
    
    # Iterates over each measurement ID and retrieves the data
    for id_measure in id_measurements:
        df = get_data_from_shops(id_measure, time_start, time_end)
        dataframes.append(df)

    # If there are DataFrames in the list, concatenate the obtained data
    if dataframes:
        # Merges the DataFrames on the 'time' column
        merged_df = pd.concat(dataframes, axis=1).drop_duplicates(subset=['time']).reset_index(drop=True)
        # Removes duplicated columns
        merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]
    else:
        # If no data, returns an empty DataFrame
        merged_df = pd.DataFrame()

    # Removes any rows with NaN values
    merged_df = merged_df.dropna()

    # Returns the merged DataFrame with data from all measurements
    return merged_df


def get_min_max_in_time_range(df, column_name):
    """
    Calculate the overall min and max values of a column in a DataFrame and also 
    the min and max values during a specific time range (8 AM - 6 PM).

    Parameters:
    - df (pd.DataFrame): A time series DataFrame with a datetime index.
    - column_name (str): The name of the column to calculate min and max.

    Returns:
    - dict: A dictionary with the overall and time-range-specific min and max values.
    """
    # Ensure the 'time' column is datetime if not already set as the index
    # This check ensures that the DataFrame's index is a DatetimeIndex for proper time-based filtering
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("The DataFrame index must be a DatetimeIndex.")

    # Calculate overall min, max, mean, and median values of the specified column
    overall_min = df[column_name].min()  # Minimum value in the entire column
    overall_max = df[column_name].max()  # Maximum value in the entire column
    overall_mean = df[column_name].mean()  # Mean value of the entire column
    overall_median = df[column_name].median()  # Median value of the entire column

    # Filter the DataFrame for the time range 8 AM - 6 PM
    # This will focus on the period from 8 AM to 6 PM for specific analysis
    time_filtered = df.between_time("08:00", "18:00")

    # Calculate the min and max values within the 8 AM - 6 PM time range
    range_min = time_filtered[column_name].min()
    range_max = time_filtered[column_name].max()

    # Return the calculated values in a dictionary with rounded values for overall min, max, mean, and median
    return {
        "overall_min": round(overall_min, 1),
        "overall_max": round(overall_max, 1),
        "overall_mean": round(overall_mean, 1),
        "overall_median": round(overall_median, 1),
        "range_min": range_min,
        "range_max": range_max
    }


def calculate_exceedance_with_monthly_distribution(dataframe, threshold_cold=24, threshold_warm=28):
    """
    Calculates the number of times values in the first column exceed a threshold,
    the percentage of exceedances, and the monthly distribution of exceedances.
    
    Parameters:
    - dataframe (pd.DataFrame): A timeseries DataFrame with a datetime index.
    - threshold_cold (int): Threshold for October to April (inclusive).
    - threshold_warm (int): Threshold for May to September.
    
    Returns:
    - exceedance_count (int): The number of exceedances.
    - exceedance_percentage (float): The percentage of exceedances.
    - monthly_distribution (dict): The distribution of exceedances across months.
    """
    # If the dataframe is empty, return default values (0 exceedances, 0% exceedances, and empty monthly distribution)
    if dataframe.empty:
        return 0, 0.0, {}  

    # Ensure the DataFrame's index is of datetime type for proper time-based operations
    if not isinstance(dataframe.index, pd.DatetimeIndex):
        raise ValueError("The DataFrame index must be a DatetimeIndex.")

    # Extract the first column of the dataframe to analyze exceedances
    column = dataframe.iloc[:, 0]

    # Create a series of thresholds based on the month of each entry
    # Use different thresholds for cold months (October to April) and warm months (May to September)
    thresholds = column.index.to_series().apply(
        lambda dt: threshold_cold if dt.month in [10, 11, 12, 1, 2, 3, 4] else threshold_warm
    )

    # Check where the values in the column exceed the thresholds
    exceedances = column > thresholds

    # Count the number of exceedances
    exceedance_count = exceedances.sum()

    # Calculate the percentage of exceedances
    total_values = len(column)
    exceedance_percentage = (exceedance_count / total_values) * 100 if total_values > 0 else 0.0

    # Calculate the monthly distribution of exceedances
    if exceedance_count > 0:
        # Get the data where exceedances occurred
        exceedance_data = column[exceedances]
        # Calculate the percentage of exceedances per month and sort by month
        monthly_distribution = (
            exceedance_data.index.to_series().dt.month.value_counts(normalize=True) * 100
        ).sort_index().to_dict()  # Convert to dictionary with month as the key and percentage as the value
    else:
        monthly_distribution = {}

    # Return the total number of exceedances, the percentage, and the monthly distribution
    return exceedance_count, exceedance_percentage, monthly_distribution


def calculate_exceedance_with_monthly_distribution_overccoling(dataframe, threshold_cold=18, threshold_warm=25):
    """
    Calculates the number of times values in the first column exceed a threshold,
    the percentage of exceedances, and the monthly distribution of exceedances.
    
    Parameters:
    -----------
    dataframe (pd.DataFrame): A timeseries dataframe with a datetime index containing sensor data.
    threshold_cold (int): Threshold for October to April (inclusive) (default is 18).
    threshold_warm (int): Threshold for May to September (default is 25).
    
    Returns:
    --------
    exceedance_count (int): The total number of exceedances where values go below the cold threshold 
                             or above the warm threshold.
    exceedance_percentage (float): Percentage of exceedances relative to the total number of values.
    monthly_distribution (dict): A dictionary representing the distribution of exceedances across months as 
                                 percentages.
    """

    # Check if the dataframe is empty and return default values if it is
    if dataframe.empty:
        return 0, 0.0, {}  # Return default values if the dataframe is empty

    # Ensure the DataFrame's index is a DatetimeIndex for proper date handling
    if not isinstance(dataframe.index, pd.DatetimeIndex):
        raise ValueError("The DataFrame index must be a DatetimeIndex.")

    # Extract the first column of data to analyze
    column = dataframe.iloc[:, 0]

    # Create a series of thresholds based on the month
    thresholds = column.index.to_series().apply(
        lambda dt: threshold_cold if dt.month in [10, 11, 12, 1, 2, 3, 4] else threshold_warm
    )

    # Identify the exceedances where values are below the cold threshold or above the warm threshold
    exceedances = column < thresholds

    # Count the total number of exceedances
    exceedance_count = exceedances.sum()

    # Calculate the percentage of exceedances based on the total number of values
    total_values = len(column)
    exceedance_percentage = (exceedance_count / total_values) * 100 if total_values > 0 else 0.0

    # Calculate the monthly distribution of exceedances (as percentages)
    if exceedance_count > 0:
        # Filter the data to only include exceedances and calculate the monthly distribution
        exceedance_data = column[exceedances]
        monthly_distribution = (
            exceedance_data.index.to_series().dt.month.value_counts(normalize=True) * 100
        ).sort_index().to_dict()  # Convert to a dictionary with month-wise percentage distribution
    else:
        monthly_distribution = {}

    # Return the results: exceedance count, exceedance percentage, and monthly distribution
    return exceedance_count, exceedance_percentage, monthly_distribution


def determine_season(data):
    """
    Determines whether the majority of values in the input list correspond to Winter or Summer.
    
    - Winter: Months [10, 11, 12, 1, 2, 3, 4]
    - Summer: Months [5, 6, 7, 8, 9]

    Parameters:
    -----------
    data (list): A list of integers representing month numbers (1 to 12) for which the season is to be determined.

    Returns:
    --------
    str: "Winter" if the majority of months are from the Winter period, "Summer" if the majority are from the Summer period.
    """
    
    # Return a message if no data is provided
    if not data:
        return "No data provided"  # Handle the case of an empty list
    
    # Define the sets of months representing Winter and Summer
    winter_months = {10, 11, 12, 1, 2, 3, 4}
    summer_months = {5, 6, 7, 8, 9}
    
    # Count the occurrences of Winter and Summer months
    winter_count = sum(1 for month in data if month in winter_months)
    summer_count = sum(1 for month in data if month in summer_months)
    
    # Determine the season based on the majority of values
    if winter_count > summer_count:
        return "Winter"  # More values fall into Winter months
    elif summer_count > winter_count:
        return "Summer"  # More values fall into Summer months
    else:
        return "Equal counts for Winter and Summer, select specific period"  # Handle the case of a tie


def get_latitude_longitude(building_name):
    '''
    Get latitude and longitude for a specific building by querying an API.
    
    Parameters:
    -----------
    building_name : str
        The name of the building for which to retrieve latitude and longitude.

    Returns:
    --------
    dict
        A JSON response containing the latitude and longitude of the building if successful, 
        otherwise an error message.
    '''
    # Define the URL of the API endpoint for building location data
    url = f"{url_api_data_metadata}/moderate/api/v1/building_location"

    # Set up the query parameters with the building name in TTL format
    params = {
        "file_name": f"{building_name}.ttl"
    }

    # Send a GET request to the API with the specified parameters
    response = requests.get(url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # If successful, print and return the response in JSON format
        print("Response JSON:", response.json())
    else:
        # If there was an error, print the status code and the error message
        print(f"Error: {response.status_code}, {response.json()}")

    # Return the response data (latitude and longitude in JSON format)
    return response.json()


def group_data_by_month(df, time_column, start_time, end_time):
    """
    Groups data from a time-series dataset by each month within the given time range.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame containing the time-series data.
    time_column : str
        The name of the column containing datetime information.
    start_time : str or datetime
        The start of the time range (inclusive) for grouping data.
    end_time : str or datetime
        The end of the time range (inclusive) for grouping data.

    Returns:
    --------
    dict
        A dictionary where keys are (year, month) tuples, and values are DataFrames for each month 
        containing the data within the specified time range.
    """
    # Ensure the time column is converted to datetime format for correct processing
    df[time_column] = pd.to_datetime(df[time_column])

    # Filter the DataFrame to include only data within the specified time range
    df_filtered = df[(df[time_column] >= start_time) & (df[time_column] <= end_time)]

    # Create a new column to represent the year and month as a Period object (e.g., 2025-01)
    df_filtered['year_month'] = df_filtered[time_column].dt.to_period('M')

    # Group the DataFrame by the 'year_month' column and store the groups in a dictionary
    grouped = {
        (period.year, period.month): group
        for period, group in df_filtered.groupby(df_filtered['year_month'])
    }

    # Return the grouped data
    return grouped


def process_dat_for_heat_map(id_mesurement, data_grouped, month, year):
    '''
    Process and prepare energy data for a heat map visualization.

    This function takes the grouped data for a specific month and year and processes it to generate hourly energy data.
    It also creates data in a format suitable for plotting on a heat map, where the data represents energy consumption
    over a specific time period (day and hour).

    Parameters:
    -----------
    id_mesurement : str
        The column name for the measurement data (e.g., energy consumption).
    data_grouped : dict
        A dictionary where keys are tuples (year, month), and values are DataFrames containing the grouped data for that period.
    month : int
        The month for which the data is being processed (e.g., 1 for January, 2 for February).
    year : int
        The year for which the data is being processed.

    Returns:
    --------
    tuple
        A tuple containing two elements:
        - filled_data : list
            A list of lists, each representing a day, hour, and energy value for the heat map.
        - df_energy : pd.DataFrame
            A DataFrame containing the hourly energy data for the given month and year.
    '''

    # Extract the data for the specific year and month
    df = data_grouped[(year, month)]
    
    # Set the 'time' column as the DataFrame index, ensuring it's in datetime format
    df.index = pd.to_datetime(df["time"])

    # Calculate energy by dividing the power measurement by 4 (since data is in 15-minute intervals)
    df['Energy'] = (df[id_mesurement] / 4).round(1)

    # Remove the 'time' and 'id_measurement' columns to keep only the energy data
    del df['time']
    del df[id_mesurement]

    # Resample the energy data to hourly intervals, summing the values within each hour
    df_energy = pd.DataFrame(df['Energy'].resample("H").sum())

    # Prepare data for heat map plotting
    dataToPlot = []
    df_energy['day'] = df_energy.index.day.tolist()  # Extract the day of the month
    df_energy['hour'] = df_energy.index.hour.tolist()  # Extract the hour of the day
    for i, element in df_energy.iterrows():
        dataToPlot.append([element['day']-1, element['hour'], element['Energy']])

    # Determine the first data point's day and hour to fill missing data before this point
    start_day, start_hour, _ = dataToPlot[0]
    start_day = int(start_day)
    start_hour = int(start_hour)

    # Create a list to store the filled data
    filled_data = []

    if start_day > 0:
        # If the data doesn't start on the first day or hour, fill in the missing data
        for day in range(0, start_day + 1):  # Iterate over the missing days
            for hour in range(0, 24):  # Iterate over all hours in a day
                # If this day-hour combination is before the first data point, append [day, hour, 0] (NaN)
                if (day < start_day) or (day == start_day and hour < start_hour):
                    filled_data.append([day, hour, 0])

        # Append the remaining data points
        filled_data.extend(dataToPlot)
    else:
        filled_data = dataToPlot

    # Return the filled data and the hourly energy DataFrame
    return filled_data, df_energy


def get_list_energy_meters_all_shops():
    '''
    Get a list of all energy meters installed in the shops.

    This function makes an API call to retrieve a list of all energy meters from a given endpoint.

    Returns:
    --------
    dict
        A dictionary containing the response data, parsed from the JSON returned by the API.
    '''

    # Define the API endpoint to retrieve energy meter data
    url = f"{url_api_data_metadata}/moderate/api/v1/energy_meters"

    # Send a POST request to the API
    response = requests.request("POST", url)

    # Parse and return the JSON response
    return json.loads(response.json())


def assign_period(row):
    '''
    Assigns a period (Day or Night) based on the hour of the timestamp.
    
    Parameters:
    -----------
    row : pandas.Series
        A row from the DataFrame containing a 'time' column (datetime).
        
    Returns:
    --------
    str
        "Day (7 AM - 8 PM)" if the time is between 7 AM and 8 PM,
        "Night (9 PM - 5 AM)" if the time is between 9 PM and 5 AM,
        "Excluded" if the time doesn't match any of the above periods.
    '''
    hour = row.time.hour  # Extract hour from the 'time' column
    
    if 7 <= hour <= 20:
        # Day period: From 7 AM to 8 PM
        return "Day (7 AM - 8 PM)"
    elif 20 < hour <= 23 or 0 <= hour < 7:
        # Night period: From 9 PM to 5 AM
        return "Night (9 PM - 5 AM)"
    else:
        # Excluded period (this case might not be needed, as time is always within a 24-hour range)
        return "Excluded"


def get_mean_sum_count_energy_periods(id_measurement, shop_name, time_col_name):
    '''
    For each energy meter, calculates the sum, mean, and count of energy usage in two periods:
    1. From 7 AM to 8 PM (Day period)
    2. From 9 PM to 5 AM (Night period)
    
    Parameters:
    -----------
    id_measurement : str
        The ID of the measurement to be analyzed.
    shop_name : str
        The name of the shop.
    time_col_name : str
        The name of the time column in the data.

    Returns:
    --------
    tuple
        A tuple containing:
        - grouped : pd.DataFrame
            A DataFrame with the sum, mean, and count of energy usage for each period.
        - df : pd.DataFrame
            The original DataFrame with an added 'period' column that specifies whether each row is in the Day or Night period.
    '''
    # Retrieve the first and last value of data from the time series
    st_end = get_first_and_last_value(id_measurement)
    colName = st_end.columns
    
    # Initialize empty DataFrames
    grouped = pd.DataFrame()
    df = pd.DataFrame()
    
    if not st_end.empty:
        # Check that the first and last values are valid
        if st_end[colName[0]][0] not in [None, ''] and st_end[colName[0]][1] not in [None, '']:
            # Extract the start and end dates from the time series
            time_start = st_end[time_col_name][0].split('T')[0]
            time_end = st_end[time_col_name][1].split('T')[0]
            
            # Retrieve the data for the specified measurement
            df = get_data_from_shops(id_measurement, time_start, time_end)
            
            # Add a new column for the period (Day or Night)
            df["period"] = df.apply(assign_period, axis=1)
            
            # Group data by the period and calculate sum, mean, and count for each period
            grouped = df.groupby("period")[id_measurement].agg(["sum", "mean", "count"]).reset_index()

            # Round the values in 'sum', 'mean', and 'count' columns
            try:
                # Try to extract the building area for normalization
                area_building = extract_numeric_value(get_area_from_bui(f"bui_{shop_name}"))
            except:
                # In case of an error, set the area as None
                area_building = None
            
            # If area data is available, normalize the energy data by area
            if area_building:
                grouped['sum'] = round(grouped['sum'] / area_building, 4)  # Normalize and round the sum
                grouped['mean'] = round(grouped['mean'] / area_building, 4)  # Normalize and round the mean
                grouped['count'] = grouped['count'].round(0)  # Round the count to the nearest whole number
                grouped['shops'] = shop_name  # Add the shop name to the DataFrame
                grouped['area building'] = area_building  # Add the building area to the DataFrame
            else:
                # If no area data, don't normalize, just round the values
                grouped['sum'] = round(grouped['sum'], 4)
                grouped['mean'] = round(grouped['mean'], 4)
                grouped['count'] = grouped['count'].round(0)
                grouped['shops'] = shop_name
                grouped['area building'] = np.NaN  # Set area as NaN if not available

    # Return the grouped DataFrame and the original DataFrame
    return grouped, df



# ========================================================
#               ANALYSIS ALL BUIDLIONGS 
# ========================================================
def table_overview(time_col_name, el_price):
    '''
    Summry table to get overall information of building HVAC consumption 
    Param
    ------
    time_col_name: Name of the time coluns
    el_price: elctricity price in euro
    '''
    # Get meter UUID
    energy_meter_shops = pd.DataFrame(get_list_energy_meters_all_shops())

    df = pd.DataFrame()
    for i,bui in energy_meter_shops.iterrows():
        stat_bui, df__ = get_mean_sum_count_energy_periods(bui['uuid'], bui['shops'], time_col_name)
        df = pd.concat([df,stat_bui])
    # 
    areas = df[df.index == 0]["area building"].tolist()

    # Pivot and reshape the data
    df_reshape = df.copy()
    grouped_df = df_reshape.pivot(index="shops", columns="period", values=["sum", "mean", "count"]).reset_index()
    grouped_df['area building'] = areas
    # Rename the columns for clarity
    grouped_df.columns = [
        "shops",
        "sum_day", "sum_night",
        "mean_day", "mean_night",
        "count_day", "count_night","area building"
    ]

    # Reorder and clean the DataFrame
    final_df = grouped_df[[
        "shops",
        "sum_day", "sum_night",
        "mean_day", "mean_night",
        "count_day", "count_night", "area building"
    ]].fillna(0)

    # 
    final_df['overall_cost'] = round(((final_df['sum_day']+ final_df['sum_night'])*el_price),2)
    final_df['night_cost'] = round(final_df['sum_night']*el_price,2)
    final_df["cost night %"] = round((final_df['night_cost']/final_df['overall_cost'])*100,2)
    
    return final_df


def calculate_degree_days(df, temperature_label='temperature'): 
    '''
    Calculate Heating Degree Days (HDD) and Cooling Degree Days (CDD)
    Parameters:
    -----------
    df: DataFrame with at least a 'time' column and a temperature column. Df should be on daily level, mean outdoor temperature 
    temperature_label: Name of the column representing temperature values.
    
    Returns:
    --------
    DataFrame with HDD and CDD columns.
    '''
    # Convert 'time' to datetime if not already
    df['time'] = pd.to_datetime(df['time'])
    
    # Extract the month
    df['month'] = df['time'].dt.month

    # Initialize HDD and CDD to 0
    df['HDD'] = 0
    df['CDD'] = 0

    # Calculate HDD for October to April (months 10, 11, 12, 1, 2, 3, 4)
    df.loc[df['month'].isin([10, 11, 12, 1, 2, 3, 4]), 'HDD'] = \
        df.loc[df['month'].isin([10, 11, 12, 1, 2, 3, 4]), temperature_label].apply(lambda t: max(0, 18 - t))

    # Calculate CDD for May to September (months 5, 6, 7, 8, 9)
    df.loc[df['month'].isin([5, 6, 7, 8, 9]), 'CDD'] = \
        df.loc[df['month'].isin([5, 6, 7, 8, 9]), temperature_label].apply(lambda t: max(0, t - 26))

    return df



def typical_day(id_measurement, time_col_name, year_selected=2022, month_selected=2):
    """
    Process and analyze daily energy consumption, categorizing into workdays, weekends, and holidays.

    Parameters:
        id_measurement (int): Measurement ID.
        time_col_name (str): Column name for the timestamp.
        year_selected (int): Year to filter the data. Default is 2022.
        month_selected (int): Month to filter the data. Default is February.

    Returns:
        tuple: Workdays, weekends, holidays DataFrames, and y-axis range (y_min, y_max).
    """
    def load_and_preprocess():
        """Retrieve and preprocess the data."""
        grouped, df_day = get_mean_sum_count_energy_periods(id_measurement, "", time_col_name)
        df_day = df_day.drop(columns=['period'])  # Remove unnecessary column
        df_day.columns = ['time', 'value']  # Rename columns for clarity
        df_day['time'] = pd.to_datetime(df_day['time'])  # Ensure datetime format
        return df_day

    def resample_to_hourly(df):
        """Resample the data to hourly intervals and convert power to energy."""
        df = df.set_index('time').resample('H').sum().reset_index()
        df['value'] = df['value'] / 4  # Convert power to energy
        return df

    def filter_by_year_and_month(df, year, month):
        """Filter data for the selected year and month."""
        return df[(df['time'].dt.year == year) & (df['time'].dt.month == month)]

    def classify_day_type(df):
        """Classify days into workdays, weekends, or holidays."""
        italy_calendar = Italy()
        holidays = {
            holiday[0] for holiday in italy_calendar.holidays(2021)
        }.union({
            holiday[0] for holiday in italy_calendar.holidays(2022)
        })
        
        def day_type(date):
            if date in holidays:
                return 'Holiday'
            return 'Weekend' if pd.Timestamp(date).weekday() >= 5 else 'Workday'
        
        df['date'] = df['time'].dt.date
        df['hour'] = df['time'].dt.hour + df['time'].dt.minute / 60  # Fractional hour
        df['day_type'] = df['date'].apply(day_type)
        return df

    # Load and preprocess the data
    df_day = load_and_preprocess()

    # Resample data to hourly intervals and process energy values
    df_day = resample_to_hourly(df_day)

    # Filter by year and month
    df_filtered = filter_by_year_and_month(df_day, year_selected, month_selected)

    # Classify days into workdays, weekends, and holidays
    df_classified = classify_day_type(df_filtered)

    # Split data into categories
    workdays = df_classified[df_classified['day_type'] == 'Workday']
    weekends = df_classified[df_classified['day_type'] == 'Weekend']
    holidays = df_classified[df_classified['day_type'] == 'Holiday']

    # Calculate y-axis range
    y_min, y_max = df_classified['value'].min(), df_classified['value'].max()

    return workdays, weekends, holidays, y_min, y_max

def safe_merge(df1, df2, on_column, how='inner'):
    """
    Safely merge two DataFrames, handling timezone-naive and timezone-aware mismatches.
    
    Parameters:
        df1 (pd.DataFrame): First DataFrame.
        df2 (pd.DataFrame): Second DataFrame.
        on_column (str): Column name to merge on.
        how (str): Type of merge ('inner', 'outer', 'left', 'right'). Default is 'inner'.
    
    Returns:
        pd.DataFrame: Merged DataFrame.
    """
    # Check if the column is datetime and identify timezone awareness
    if pd.api.types.is_datetime64_any_dtype(df1[on_column]) and pd.api.types.is_datetime64_any_dtype(df2[on_column]):
        tz_aware_df1 = pd.api.types.is_datetime64tz_dtype(df1[on_column])
        tz_aware_df2 = pd.api.types.is_datetime64tz_dtype(df2[on_column])

        # Handle timezone mismatch
        if tz_aware_df1 and not tz_aware_df2:
            df2[on_column] = df2[on_column].dt.tz_localize('UTC')  # Localize df2 to UTC
        elif not tz_aware_df1 and tz_aware_df2:
            df1[on_column] = df1[on_column].dt.tz_localize('UTC')  # Localize df1 to UTC
    
    # Perform the merge
    return pd.merge(df1, df2, on=on_column, how=how)


def typical_week(id_temperature, id_power, time_col_name="time"):
    '''
    Analyze temperature and power data for a typical week by calculating degree days, energy consumption,
    and other statistics, including hourly and daily aggregation, and grouping by day of the week and hour.
    
    Parameters:
    -----------
    id_temperature : str
        The ID of the temperature data sensor.
    id_power : str
        The ID of the power data sensor.
    time_col_name : str, optional, default="time"
        The name of the time column in the data (if different).
        
    Returns:
    --------
    tuple
        - typical_week_ : pd.DataFrame
            DataFrame containing the typical weekly energy consumption, with mean, min, and max values for each 
            day of the week and hour.
        - hdd_positive : pd.DataFrame
            DataFrame containing Heating Degree Days (HDD) for positive values.
        - cdd_positive : pd.DataFrame
            DataFrame containing Cooling Degree Days (CDD) for positive values.
    '''
    
    # Get the first and last values of temperature data for defining the time range
    st_end = get_first_and_last_value(id_temperature)
    
    colName = st_end.columns
    
    # Check if the first and last temperature values are valid (not None or empty)
    if st_end[colName[0]][0] not in [None, ''] and st_end[colName[0]][1] not in [None, '']:
        # Extract start and end time from the temperature data
        time_start = st_end[time_col_name][0].split('T')[0]
        time_end = st_end[time_col_name][1].split('T')[0]
        
        # ================================
        # Get Outdoor Temperature data    
        # ================================
        df = get_data_from_shops(id_temperature, time_start, time_end)
        
        # Calculate daily mean temperature
        df_daily = df.copy()
        df_daily.index = pd.to_datetime(df['time'])
        del df_daily['time']
        df_daily = df_daily.resample('D').mean()
        df_daily = df_daily.reset_index()
        
        # Rename columns for clarity
        df_daily.columns = ['time', 'temperature']
        
        # Calculate Heating Degree Days (HDD) and Cooling Degree Days (CDD)
        df_DD = calculate_degree_days(df_daily)

        # ================================
        # Get Power data    
        # ================================
        df_power = get_data_from_shops(id_power, time_start, time_end)
        df_power.columns = ['time', 'power']
        df_power.index = pd.to_datetime(df_power['time'])
        
        # Calculate energy consumption (power divided by 4)
        df_power['energy'] = df_power['power'] / 4
        del df_power['time']
        del df_power['power']
        
        # Aggregate power data by day (sum of energy per day)
        df_power_daily = df_power.resample('D').sum()

        # ================================
        # Merge Temperature and Power data
        # ================================
        try: 
            df_DD['energy'] = df_power_daily['energy'].values.tolist()
        except:
            # Handle merging of data if the direct merge fails
            df2 = df_power_daily.reset_index()
            df2['time'] = pd.to_datetime(df2['time'])
            df1 = df_DD
            df1['time'] = pd.to_datetime(df1['time'])
            
            # Merge temperature and power dataframes on 'time'
            merge_df = pd.merge(df1, df2, on='time', how='outer')
            df_DD['energy'] = merge_df['energy'].values.tolist()
        
        # ================================
        # Hourly values
        # ================================
        df_hour = df.copy()
        df_hour.index = pd.to_datetime(df_hour['time'])
        del df_hour['time']
        
        # Calculate hourly average temperature and energy consumption
        df_hour = df_hour.resample('H').mean()
        df_hour_energy = df_power['energy'].resample('H').sum()
        
        # Merge hourly temperature and energy data
        df_hour_t_e = pd.merge(df_hour, df_hour_energy, left_index=True, right_index=True, how='inner')
        df_hour_t_e.columns = ["temperature", "energy"]

        # Filter data where HDD and CDD are positive
        hdd_positive = df_DD[df_DD['HDD'] > 0]
        cdd_positive = df_DD[df_DD['CDD'] > 0]

        # Add columns for Day of Week and Hour
        df_hour_t_e['day_of_week'] = df_hour_t_e.index.dayofweek  # 0 = Monday, 6 = Sunday
        df_hour_t_e['hour'] = df_hour_t_e.index.hour

        # Group data by (day_of_week, hour) and calculate mean, min, max for energy, and mean for temperature
        grouped__ = df_hour_t_e.groupby(['day_of_week', 'hour'])
        typical_week_ = grouped__['energy'].agg(['mean', 'min', 'max']).reset_index()

        # Calculate mean temperature per (day_of_week, hour)
        typical_week_temp = grouped__['temperature'].mean().reset_index(name='mean_temp')

        # Merge the two dataframes for plotting
        typical_week_ = typical_week_.merge(typical_week_temp, on=['day_of_week', 'hour'])

        return typical_week_, hdd_positive, cdd_positive

    
def overall_analysis_buis(energy_price: float, time_col_name):
    '''
    Perform an overall analysis of energy consumption data across multiple buildings,
    calculating total energy consumption, mean energy usage, and energy cost per building.
    
    Parameters:
    -----------
    energy_price : float
        The price per kilowatt-hour of energy (e.g., 0.15).
    time_col_name : str
        The name of the time column used for aggregations (if different).
        
    Returns:
    --------
    pd.DataFrame
        A DataFrame containing energy consumption statistics and costs for each building, 
        including energy usage during day and night periods, mean values, and the associated costs.
    '''
    
    # Fetch energy meter data for all shops/buildings
    energy_meter_shops = pd.DataFrame(get_list_energy_meters_all_shops())
    stats_analysis = pd.DataFrame()

    # Iterate through each building/shop and perform analysis
    for i, bui in energy_meter_shops.iterrows():
        stat_bui, df__ = get_mean_sum_count_energy_periods(bui['uuid'], bui['shops'], time_col_name)
        stats_analysis = pd.concat([stats_analysis, stat_bui])

    # Pivot the data to organize it by shops and periods (day and night)
    grouped_df = stats_analysis.pivot(index="shops", columns="period", values=["sum", "mean", "count"]).reset_index()

    # Rename columns for clarity
    grouped_df.columns = [
        "shops", 
        "sum_day", "sum_night", 
        "mean_day", "mean_night", 
        "count_day", "count_night"
    ]

    # Reorder the DataFrame and fill any missing values with 0
    final_df = grouped_df[[
        "shops", 
        "sum_day", "sum_night", 
        "mean_day", "mean_night", 
        "count_day", "count_night"
    ]].fillna(0)

    # Calculate the overall cost based on energy consumption
    final_df['overall_cost'] = round((final_df['sum_day'] + final_df['sum_night']) * energy_price, 2)
    
    # Calculate the night-time energy cost (assuming night cost is 0.15)
    final_df['night_cost'] = round(final_df['sum_night'] * 0.15, 2)
    
    # Calculate the percentage of the overall cost spent on night-time energy
    final_df["cost night %"] = round((final_df['night_cost'] / final_df['overall_cost']) * 100, 2)

    return final_df

def extract_values_with_keywords(sensors, keywords=None):
    """
    Extracts the 'value' of sensors whose 'label' contains any of the specified keywords.

    Args:
        sensors (list): A list of dictionaries, each containing 'value' and 'label' keys.
        keywords (list): A list of keywords to search for in the 'label'. Default is ['Shop', 'HVAC', 'Meter_2'].

    Returns:
        list: A list of 'value' strings that match the keyword condition.
    """
    if keywords is None:
        keywords = ['Shop', 'HVAC', 'Meter_2']  # Default keywords if none provided
    
    # Create a lowercased version of the keywords for case-insensitive matching
    keywords_lower = [keyword.lower() for keyword in keywords]
    
    # Extract values whose 'label' contains any of the keywords
    matching_values = [
        sensor['value'] for sensor in sensors  # Loop through the list of sensors
        if any(keyword in sensor['label'].lower() for keyword in keywords_lower)  # Check if label contains any of the keywords
    ]
    
    # Return the list of values that match the condition
    return matching_values


def get_data_from_param(param, time_manual, time_start, time_end):
    """
    Fetches data from the shop API based on the given parameters, time range, and token.

    Args:
        param (str): The parameter to fetch data for.
        time_manual (bool): If True, manual start and end times are used; otherwise, automatic times are derived.
        time_start (str): The start time in 'YYYY-MM-DD' format.
        time_end (str): The end time in 'YYYY-MM-DD' format.

    Returns:
        pd.DataFrame or None: A DataFrame with the data or None if no data is found.
    """
    # Fetch the first and last values for the given parameter
    st_end = get_first_and_last_value(param)
    
    # Check if valid values exist for start and end times
    if st_end.iloc[0, 0] != None and st_end.iloc[1, 0] != None:
        if time_manual:  # If manual time range is provided
            # Fetch data within the provided manual time range
            df = get_data_from_shops(param, time_start, time_end)
        else:  # Use automatic time range based on the first and last available values
            time_start = st_end['time'][0].split('T')[0]  # Extract the date part of the timestamp
            time_end = st_end['time'][1].split('T')[0]
            df = get_data_from_shops(param, time_start, time_end)
        return df
    else:
        return None  # Return None if no valid start/end values are found


def get_building_data_last(building_list):
    '''
    Fetches the last values of indoor temperature, outdoor temperature, and HVAC power for each building in the list.
    
    Args:
        building_list (list): A list of buildings to fetch data for.

    Returns:
        tuple: A tuple of three lists containing last values for indoor temperature, outdoor temperature, and HVAC power.
    '''
    # Lists to store last values for each data type
    external_temperatures = []
    hvac_powers = []
    indoor_temperature = []

    # Loop through each building in the provided list
    for building in building_list:
        try:
            # INDOOR TEMPERATURE
            # Get the label and UUID for indoor temperature
            ind_temp_uuid = get_temperature_label_and_uuid(building)
            if ind_temp_uuid:
                # Filter out sensors that mention "External" or "Outside" in their label
                ind_temp_uuid = [item for item in ind_temp_uuid if "External" not in item['label'] and "Outside" not in item['label']]
                # Fetch the first and last value of indoor temperature
                df_indoor = get_first_and_last_value(ind_temp_uuid[0]['value'])
                last_ind_temp_value = round(list(df_indoor['value'])[-1], 2)  # Round the last value to 2 decimal places
            else:
                last_ind_temp_value = np.NaN  # Assign NaN if no indoor temperature data is available
        except:
            last_ind_temp_value = np.NaN  # Handle any error and assign NaN
        
        try:
            # EXTERNAL TEMPERATURE
            # Get the UUID for external temperature data
            ext_temp_uuid = get_meter_label_and_uuid_weather(building)[0]['value']
            df = get_first_and_last_value(ext_temp_uuid)
            last_temp_value = list(df['value'])[-1]  # Get the last external temperature value
        except:
            last_temp_value = np.NaN  # Assign NaN if no external temperature data is available
        
        try:
            # HVAC POWER: Fetch the first matching HVAC sensor
            havc_1 = extract_values_with_keywords(get_meter_label_and_uuid(building))[0]
            if havc_1:
                # Fetch the first and last value of HVAC power
                df_HVAC = get_first_and_last_value(havc_1)
                last_hvac_value = round(list(df_HVAC['value'])[-1], 2)  # Round the last HVAC value to 2 decimal places
            else:
                last_hvac_value = np.NaN  # Assign NaN if no HVAC data is available
        except Exception:
            last_hvac_value = np.NaN  # Use NaN if fetching fails
        
        # Append the fetched values to the respective lists
        external_temperatures.append(last_temp_value)
        hvac_powers.append(last_hvac_value)
        indoor_temperature.append(last_ind_temp_value)

    # Return the lists with last values for each data type
    return indoor_temperature, external_temperatures, hvac_powers