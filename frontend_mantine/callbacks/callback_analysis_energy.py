import pandas as pd
from dash import callback, Input, Output, ctx
import utils.functions_plot as FcPlot
import pandas as pd
from pandas.tseries.holiday import Holiday, AbstractHolidayCalendar
from sklearn.metrics import r2_score,mean_absolute_error, mean_squared_error
import numpy as np
import utils.functions_api_data as FcAPI
import dash_mantine_components as dmc
from utils.functions_analysis import calculate_degree_days
import utils.functions_general as FcGen
import json 
# Authenticate API time series and retrieve token

data_test = [
    {"month": "", "value": ""},
    {"month": "", "value": ""},
]

# Month labels
month_mapping = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December",
}
emptydf = pd.DataFrame()

'''Get list of buildings'''
@callback(
    Output("single_bui_energy", "data"),  # Dropdown options for buildings
    Output("single_bui_energy", "value"), # Preselected building
    Input("url_app", "search")            # Query parameter from the URL
)
def get_building_list(search):
    '''
    Retrieves the list of buildings and sets the preselected building based on the URL query parameter.

    Args:
        search (str): Query parameter from the URL (e.g., "?bui_BCGS").

    Returns:
        tuple:
            - A list of dictionaries with building values and labels for the dropdown.
            - The preselected building value.
    '''
    # Fetch the list of buildings
    buis = FcAPI.get_building_list()['Buis'].tolist()
    
    # Create dropdown options with "value" and "label" keys
    options = [{'value': item, 'label': item.split('_')[1]} for item in buis]
    
    if search:
        # Extract the selected building from the query parameter (e.g., "?bui_BCGS" -> "bui_BCGS")
        buis_selected = search.lstrip("?")
    else:
        # Default to the first building in the list if no search parameter is provided
        buis_selected = buis[0]
    
    return options, buis_selected


@callback(
    Output("subtle_energy_cost", "children"),  # Display the text with energy cost info
    Input("electricity_price", "value")        # Electricity price value
)
def subtle_text_energy_price(cost):
    '''
    Generates a subtle message showing the monthly energy cost based on the provided electricity price.

    Args:
        cost (float): The price of electricity in euro per kWh.

    Returns:
        str: A message with the monthly energy cost information.
    '''
    return f"Monthly cost for the energy considering an overall price of {cost} euro/kWh"


@callback(
    Output("year_heat_map_energy", "data"),  # Dropdown options for years
    Output("year_heat_map_energy", "value"), # Preselected year
    Input("date_energy", "data"),            # JSON data containing energy data
    prevent_initial_call=True
)
def get_date(json_data):
    '''
    Extracts the available years from the provided energy data.

    Args:
        json_data (str): JSON string containing energy data, with years as keys.

    Returns:
        tuple:
            - A list of years (extracted from the JSON data).
            - The preselected year (the first year in the list).
    '''
    if json_data:
        result = json.loads(json_data)
        #
        data_w = list(result.keys())  # Extract list of available years (keys in the JSON)
        #
        value_w = data_w[0]  # Preselect the first year
        return data_w, value_w
    return [""], ""


@callback(
    Output("month_heat_map_energy", "data"),  # Dropdown options for months
    Output("month_heat_map_energy", "value"), # Preselected month
    Input("date_energy", "data"),             # JSON data containing energy data
    Input("year_heat_map_energy", "value"),   # Selected year from the previous callback
    prevent_initial_call=True
)
def get_month(json_data, year):
    '''
    Extracts the available months for the selected year from the energy data.

    Args:
        json_data (str): JSON string containing energy data, with years as keys.
        year (str): The selected year for which the months will be extracted.

    Returns:
        tuple:
            - A list of months available for the selected year.
            - The preselected month (the first month in the list).
    '''
    if json_data:
        result = json.loads(json_data)
        # Extract the list of months for the selected year
        months_year = result[year]

        # Generate the desired structure for dropdown options (month number and name)
        data_w = [{"value": str(int(month)), "label": month_mapping[month]} for month in months_year]
        #
        value_w = data_w[0]['value']  # Preselect the first month
        return data_w, value_w
    return [""], ""


# Italian Holidays
class ItalianHolidays(AbstractHolidayCalendar):
    rules = [
        Holiday("New Year's Day", month=1, day=1),
        Holiday("Epiphany", month=1, day=6),
        Holiday("Easter Monday", month=4, day=10, offset=pd.DateOffset(weekday=0)),  # Dynamic Easter
        Holiday("Liberation Day", month=4, day=25),
        Holiday("Labour Day", month=5, day=1),
        Holiday("Republic Day", month=6, day=2),
        Holiday("Assumption Day", month=8, day=15),
        Holiday("All Saints' Day", month=11, day=1),
        Holiday("Immaculate Conception", month=12, day=8),
        Holiday("Christmas Day", month=12, day=25),
        Holiday("St. Stephen's Day", month=12, day=26)
    ]


'''Get list of **ENERGY** Sensors'''
@callback(
    Output("energy_parameters_analysis", "data"),  # The dropdown options for energy parameters
    Output("energy_parameters_analysis", "value"), # Preselected energy parameter value
    Input("single_bui_energy", "value"),           # The selected building
    prevent_initial_call=True
)
def get_energy_parameters(bui_name):
    '''
    Retrieves a list of indoor energy sensors (excluding "External" and "Outside" sensors) for the selected building.
    
    Args:
        bui_name (str): The name of the selected building.

    Returns:
        tuple:
            - A list of dictionaries containing energy parameters with labels and values.
            - The default selected parameter value (or "no_data" if no indoor sensors are found).
    '''
    dataP = FcAPI.get_meter_label_and_uuid(bui_name)  # Fetch energy sensors for the selected building
    valueP = ""
    
    if dataP:
        # Filter out sensors containing 'External' or 'Outside'
        dataP_indoor = [item for item in dataP if "External" not in item['label'] and "Outside" not in item['label']]
        
        if dataP_indoor:
            valueP = dataP_indoor[0]['value']  # Select the first indoor sensor as the default
            return dataP_indoor, valueP
        # If no indoor sensors found, return a default value
        return [{'label': '', 'value': 'no_data'}], "no_data"
    
    # If no sensors are found for the building, return a default value
    return [{'label': '', 'value': 'no_data'}], "no_data"


'''Get list of **WETAHER** Sensors'''
@callback(
    Output("outdoor_parameters_energy", "data"),  # The dropdown options for outdoor energy parameters
    Output("outdoor_parameters_energy", "value"), # Preselected weather parameter value
    Input("single_bui_energy", "value"),          # The selected building
    prevent_initial_call=True
)
def get_weather_parameters(bui_name):
    '''
    Retrieves a list of outdoor weather sensors for the selected building.

    Args:
        bui_name (str): The name of the selected building.

    Returns:
        tuple:
            - A list of dictionaries containing weather parameters with labels and values.
            - The default selected weather parameter value.
    '''
    dataP = FcAPI.get_meter_label_and_uuid_weather(bui_name)  # Fetch weather sensors for the building
    valueP = ""
    
    if dataP:
        valueP = dataP[0]['value']  # Select the first weather parameter as the default
    return dataP, valueP


@callback(
    Output("date_energy", "data"),  # JSON data containing date ranges for the selected parameter
    Input("energy_parameters_analysis", "value"),  # The selected energy parameter
)
def get_data_param(param_name):
    '''
    Fetches the available date ranges (months and years) for a selected energy parameter.
    
    Args:
        param_name (str): The selected energy parameter.

    Returns:
        str: A JSON string containing the available years and months for the selected parameter.
    '''
    param = param_name
    
    if param and param_name != "no_data":
        # Get the start and end time for the selected parameter
        st_end = FcAPI.get_first_and_last_value(param)
        
        if st_end.iloc[0, 0] != None and st_end.iloc[1, 0] != None:
            # Generate date ranges for months and years
            months_years = pd.date_range(start=st_end['time'][0], end=st_end['time'][1], freq='D').strftime('%Y-%m').unique().tolist()

            df = pd.DataFrame({"date": months_years})
            # Extract year and month
            if not df.empty:
                df["year"] = df["date"].str[:4]  # First 4 characters represent the year
                df["month"] = df["date"].str[5:]  # Remaining characters represent the month

                # Group by year and get list of months for each year
                result = df.groupby("year")["month"].apply(list).to_dict()
                json_data = json.dumps(result, indent=4)  # Convert to JSON format
                return json_data
            else:
                return ""
        return ""
    return ""

# =================================================================================
#                               MAIN: DATA ENERGY
# =================================================================================
''' Store selected data'''
@callback(
    Output("data_shop_energy", "data"),             # Output: Stores the fetched data in the "data_shop_energy" component.
    Output("loading_data", "children", allow_duplicate=True),  # Output: Controls the loading state by changing the "loading_data" component's text.
    Output("no_data_building", "hide"),             # Output: Hides the "no_data_building" component if data is found.
    Input("energy_parameters_analysis", "value"),   # Input: The selected energy parameter.
    Input("energy_parameters_analysis", "data"),    # Input: The list of all energy parameters available.
    prevent_initial_call=True                        # Prevents initial execution of the callback before any input.
)
def get_data_energy_from_bui(param_name, all_parameters):
    '''
    Fetches the data related to a specific energy parameter from the building, 
    processes it, and updates the UI components accordingly.
    
    Args:
        param_name (str): The selected energy parameter (e.g., "temperature").
        all_parameters (list): A list containing all available energy parameters with their metadata.

    Returns:
        tuple:
            - A dictionary of records containing the fetched energy data.
            - A string (empty in the case of success) for the loading state.
            - A boolean indicating whether data was found or not.
    '''
    
    # Validate the input parameter
    if not param_name or len([param_name]) < 1:
        return emptydf.to_dict(), "", ""  # If no parameter is selected, return empty data and hide the "loading" message.
    
    if param_name and param_name != "no_data":
        # Fetch the start and end times for the selected parameter
        st_end = FcAPI.get_first_and_last_value(param_name)
        
        # If both start and end time values are present, proceed with fetching the data
        if st_end.iloc[0,0] is not None and st_end.iloc[1,0] is not None:
            time_start = st_end['time'][0].split('T')[0]  # Extract the date from the start time
            time_end = st_end['time'][1].split('T')[0]    # Extract the date from the end time
            
            # Fetch the actual energy data for the selected parameter
            df = FcAPI.get_data_from_shops(param_name, time_start, time_end)
            
            # Find the label corresponding to the selected parameter
            label = next((item['label'] for item in all_parameters if item['value'] == param_name), None)
            if label is None:
                raise ValueError(f"Label not found for parameter: {param_name}")  # Raise an error if the label cannot be found
            
            # Rename the column to match the parameter label
            df.columns = ['time', label]
            
            # Add additional derived columns like workday and hours using the utility function
            df = FcGen.add_workday_and_hours_columns(df)
            
            # Return the data as a dictionary of records, clear loading text, and indicate that data was found
            return df.to_dict('records'), "", True
        # If no valid data was found (start or end time is None), return empty data and indicate no data
        return emptydf.to_dict(), "", False
    
    # If "no_data" is selected as the parameter, return empty data and hide the "loading" message
    return emptydf.to_dict(), "", False

# =================================================================================
#                               MAIN: OUTSIDE TEMPERATURE
# =================================================================================
''' Weather data'''
@callback(
    Output("weather_data", "data"),                   # Output: The weather data is passed as the "data" to the "weather_data" component.
    Input("outdoor_parameters_energy", "value"),       # Input: The selected parameter (e.g., weather-related parameter).
    Input("outdoor_parameters_energy", "data"),        # Input: The list of all available outdoor parameters.
    prevent_initial_call=True                            # Prevents the callback from running when the app is initially loaded without any inputs.
)
def get_data_from_bui(param_name, all_parameters):
    '''
    Fetches the weather data related to a specific outdoor parameter from the building,
    processes it, and returns the data to the UI component.

    Args:
        param_name (str): The selected outdoor parameter (e.g., "temperature", "humidity").
        all_parameters (list): A list of all outdoor parameters with their associated metadata.

    Returns:
        list: The weather data as a dictionary of records to be displayed on the frontend.
    '''
    
    # Validate the input parameter
    if not param_name or len([param_name]) < 1:
        return emptydf.to_dict(), ""  # If no parameter is selected, return empty data.

    param = param_name  # Assign the selected parameter name to 'param'
    
    # Fetch the first and last value (timestamps) for the selected parameter from the API
    st_end = FcAPI.get_first_and_last_value(param)
    
    # Check if both start and end times are available
    if st_end.iloc[0, 0] is not None and st_end.iloc[1, 0] is not None:
        time_start = st_end['time'][0].split('T')[0]  # Extract start date
        time_end = st_end['time'][1].split('T')[0]    # Extract end date
        
        # Fetch the actual data for the selected parameter between the start and end times
        df = FcAPI.get_data_from_shops(param, time_start, time_end)
        
        # Find the label corresponding to the selected parameter from the 'all_parameters' list
        label = next((item['label'] for item in all_parameters if item['value'] == param), None)
        if label is None:
            raise ValueError(f"Label not found for parameter: {param}")  # Raise error if the label is not found
        
        # Rename the data column to the parameter label
        df.columns = ['time', label]
        
        # Add additional columns like workday and hour of the day using a utility function
        df = FcGen.add_workday_and_hours_columns(df)
        
        # Return the processed data as a dictionary of records
        return df.to_dict('records')
    
    # If the data is unavailable (either the start or end time is None), return empty data
    return emptydf.to_dict()  # Return empty data if no valid start and end times

# =================================================================================
#                               GRAPHS
# =================================================================================

# '''Bar chart on top energy/cost'''
'''Bar chart on top energy/cost'''
@callback(
    Output("skeleton_energy_cost", "visible"),       # Controls visibility of the skeleton loader (loading state).
    Output("id_skel_daily", "visible"),               # Controls visibility of the daily skeleton loader (loading state).
    Output("bar_chart_price_energy","data"),         # Output: Data for the bar chart showing energy price over time.
    Output("bar_chart_price_energy","series"),       # Output: The series data for the bar chart (used for visualization).
    Output("daily_kwh", "children"),                 # Output: Display the daily kWh value.
    Output("daily_kwh_m2", "children"),              # Output: Display the daily kWh per square meter.
    Input("data_shop_energy", "data"),               # Input: The energy consumption data for the shop/building.
    Input("energy_parameters_analysis", "data"),     # Input: A list of all energy parameters available.
    Input("energy_parameters_analysis", "value"),    # Input: The selected energy parameter.
    Input("electricity_price", "value"),              # Input: The price of electricity (in euro per kWh).
    Input("single_bui_energy","value"),               # Input: The building selected for analysis.
    prevent_initial_call = True                       # Prevent the callback from firing during initial load without user interaction.
)
def bar_chart_energy_and_cost(data, all_energy_params, energy_param, energy_price, bui_name):
    '''
    Generates a bar chart of energy costs and displays daily energy consumption data.
    The function computes energy cost per day based on selected energy parameters and price,
    and visualizes them as a bar chart.

    Args:
        data (list): Energy data for the shop/building.
        all_energy_params (list): All available energy parameters.
        energy_param (str): The selected energy parameter for analysis.
        energy_price (float): The price of electricity per kWh.
        bui_name (str): The name of the building for which data is being analyzed.

    Returns:
        tuple: The function returns multiple outputs to update the UI components accordingly.
    '''
    if data:
        # If data is available, process it:
        df = pd.DataFrame(data)  # Convert the raw data into a pandas DataFrame.
        
        df_1 = df.copy()  # Make a copy of the DataFrame.
        df_1 = df_1.reset_index()  # Reset the index for easier manipulation.

        # Get the label associated with the selected energy parameter
        label = FcGen.get_label_by_value(all_energy_params, [energy_param])

        # Compute monthly data based on the energy price and label
        df_month__ = FcGen.get_monthly_data(df_1.dropna().loc[:, ['time', label[0]]], energy_price, label)

        # Get the area of the building (used to calculate energy usage per square meter)
        area_bui = FcAPI.extract_numeric_value(FcAPI.get_area_from_bui(bui_name))
        print(area_bui)

        # Return the necessary outputs to update the UI:
        return (
            False,  # Make the skeleton loader for energy cost invisible (data has been loaded).
            False,  # Make the skeleton loader for daily data invisible (data has been loaded).
            df_month__[0],  # Data for the bar chart showing energy price over time.
            [{"name": "value", "color": "rgb(121, 80, 242)"}],  # Bar chart series with custom color.
            df_month__[1],  # The daily kWh value (energy consumption per day).
            round(df_month__[1] / area_bui, 2)  # Daily kWh per square meter of the building.
        )
    else:
        # If no data is available:
        return (
            True,  # Make the skeleton loader for energy cost visible (waiting for data).
            True,  # Make the skeleton loader for daily data visible (waiting for data).
            data_test,  # Placeholder data for the bar chart (if no valid data).
            [{"name": "value", "color": "rgb(121, 80, 242)"}],  # Default series for bar chart.
            "",  # Placeholder for daily kWh value.
            ""   # Placeholder for daily kWh per square meter.
        )
    


@callback(
    Output("id_skel_normalized", "visible"),  # Controls visibility of the skeleton loader for normalized data
    Output("kwh_m2_DD_overall", "children"),  # Output: Displays the calculated HDD value per square meter
    Output("kwh_m2_DD_overall_day", "children"),  # Output: Displays the calculated CDD value per square meter
    Input("data_shop_energy", "data"),  # Input: Energy data for the selected building
    Input("weather_data", "data"),  # Input: Weather data, including outdoor temperature
    Input("energy_parameters_analysis", "data"),  # Input: Data for energy parameters (e.g., HVAC energy, temperature, etc.)
    Input("energy_parameters_analysis", "value"),  # Input: Selected energy parameter value
    Input("outdoor_parameters_energy", "data"),  # Input: Data for outdoor parameters (e.g., HDD, CDD)
    Input("outdoor_parameters_energy", "value"),  # Input: Selected outdoor temperature parameter value (e.g., HDD, CDD)
    Input("single_bui_energy", "value"),  # Input: Name or ID of the selected building
    prevent_initial_call=True  # Prevent callback from triggering on page load
)
def get_HDD_and_CDD(data_energy, weather_data, all_parameters_energy, name_param_energy, all_parameters_temp, name_ext_temp, bui_name):
    # Convert the energy data into a DataFrame
    df_energy = pd.DataFrame(data_energy)
    if not df_energy.empty:
        # Retrieve the label for the selected energy parameter
        label = next((item['label'] for item in all_parameters_energy if item['value'] == name_param_energy), None)
        # Retrieve the label for the selected outdoor temperature parameter (HDD or CDD)
        label_temp = next((item['label'] for item in all_parameters_temp if item['value'] == name_ext_temp), None)
        
        # Convert the weather data into a DataFrame
        df_weather = pd.DataFrame(weather_data)
        
        # Extract relevant columns: time and the selected energy parameter for the building
        df_e = df_energy.loc[:, ['time', label]]
        df_t = df_weather.loc[:, ['time', label_temp]]
        
        # Convert the time columns to datetime format for both energy and weather data
        df_e["time"] = pd.to_datetime(df_e["time"])
        df_t["time"] = pd.to_datetime(df_t["time"])

        # Merge the energy and weather data on the 'time' column
        merged_df = pd.merge(df_e, df_t, on="time", how="outer", suffixes=('_df1', '_df2'))

        # Sort the merged data by time
        merged_df = merged_df.sort_values(by="time").reset_index(drop=True)

        # Calculate degree days (HDD and CDD) using the outdoor temperature data
        df_DD, HDD_daymean, CDD_daymean = calculate_degree_days(df_t, label_temp)

        # Calculate the energy usage normalized by the HDD (Heating Degree Days) for the building
        energy_per_HDD = df_e[label].dropna().sum() / HDD_daymean

        # Extract the building's area using the FcAPI
        area_bui = FcAPI.extract_numeric_value(FcAPI.get_area_from_bui(bui_name))

        # Initialize indicators for HDD and CDD
        ind_HDD = np.NaN
        if HDD_daymean:
            # Normalize the HDD by the building's area (in square meters)
            ind_HDD = round(HDD_daymean / area_bui, 2)

        ind_CDD = np.NaN
        if CDD_daymean:
            # Normalize the CDD by the building's area (in square meters)
            ind_CDD = round(CDD_daymean / area_bui, 2)

        # Return the results: Hide skeleton loader, and return the normalized HDD and CDD values
        return False, ind_HDD, ind_CDD

    # Return default values if the energy data is empty
    return True, "", ""

    


''' Card summury'''
@callback(
    Output("id_skel_overall", "visible"),           # Controls visibility of the skeleton loader for overall energy data.
    Output("kwh_overall", "children"),              # Output: The total energy consumption (in kWh).
    Output("kwh_overall_m2", "children"),           # Output: The total energy consumption per square meter (kWh/m²).
    Input("data_shop_energy", "data"),              # Input: The energy data for the shop/building.
    Input("energy_parameters_analysis", "data"),    # Input: A list of all available energy parameters.
    Input("energy_parameters_analysis", "value"),   # Input: The selected energy parameter.
    Input("single_bui_energy", "value"),            # Input: The name of the selected building for analysis.
    prevent_initial_call = True                      # Prevent the callback from firing during initial load without user interaction.
)
def value_of_energy(data, all_energy_params, energy_param, bui_name):
    '''
    Calculates the total energy consumption and energy consumption per square meter for a selected building.
    It processes the energy data, computes the total consumption, and normalizes it by the building's area.
    
    Args:
        data (list): Energy consumption data for the shop/building.
        all_energy_params (list): List of all available energy parameters for the building.
        energy_param (str): The selected energy parameter for analysis (e.g., electricity usage).
        bui_name (str): The name of the building being analyzed.
    
    Returns:
        tuple: The function returns visibility states and energy consumption data.
    '''
    # Convert the raw input data into a pandas DataFrame
    df = pd.DataFrame(data)

    if not df.empty:
        # If data is available, proceed with processing:
        df_1 = df.copy()  # Make a copy of the DataFrame to avoid modifying the original.
        
        # Fetch the label associated with the selected energy parameter
        label = FcGen.get_label_by_value(all_energy_params, [energy_param])
        
        # Set the 'time' column as the DataFrame index and remove the 'time' column
        df_1.index = pd.to_datetime(df_1['time'])
        del df_1['time']
        
        # Compute the total energy consumption for the selected parameter, summing non-NaN values
        energy = df_1.dropna().loc[:, label].sum() / 4  # Energy consumption is averaged by dividing by 4.
        
        # Fetch the area of the building to normalize energy consumption
        area_bui = FcAPI.extract_numeric_value(FcAPI.get_area_from_bui(bui_name))
        
        # Return the calculated values and hide the skeleton loader since the data is ready
        return False, round(energy, 1), round(energy / area_bui, 1)  # Return total energy and per square meter values

    # If no data is available:
    return True, "", ""  # Show skeleton loader and return empty values for energy data




'''GRAPH TIMELINE'''
@callback(
    Output("energy_timeline", "option"),             # Controls the options for the energy timeline chart.
    Output("id_skel_energy_timeline", "visible"),    # Controls the visibility of the skeleton loader for energy timeline chart.
    Input("id_btn_15min", "n_clicks"),               # Input: Button for 15-minute data frequency.
    Input("id_btn_H", "n_clicks"),                   # Input: Button for hourly data frequency.
    Input("id_btn_6H", "n_clicks"),                  # Input: Button for 6-hour data frequency.
    Input("id_btn_12H", "n_clicks"),                 # Input: Button for 12-hour data frequency.
    Input("id_btn_Day", "n_clicks"),                 # Input: Button for daily data frequency.
    Input("id_btn_Week", "n_clicks"),                # Input: Button for weekly data frequency.
    Input("id_btn_Month", "n_clicks"),               # Input: Button for monthly data frequency.
    Input("energy_kwh", "value"),                   # Input: Selected energy consumption metric (kWh or kWh/m²).
    Input("data_shop_energy", "data"),              # Input: Energy data for the shop/building.
    Input("weather_data", "data"),                  # Input: External temperature data.
    Input("single_bui_energy", "value"),            # Input: Name of the selected building for analysis.
    prevent_initial_call=True                        # Prevent the callback from firing on initial load.
)
def graph_timeline(btn15, btnH, btn6H, btn12H, btnD, btnW, btnM, kwh_m2, data_energy, data_ext_temperature, bui_name):
    '''
    Generates a timeline chart for energy and external temperature data at different frequencies (e.g., hourly, daily, etc.)
    Based on user selection of data frequency, this callback processes the data and updates the chart accordingly.
    '''
    # Convert the raw energy data and external temperature data into pandas DataFrames
    df_energy = pd.DataFrame(data_energy)

    if not df_energy.empty:
        # Prepare external temperature data for merging with energy data
        df_ext_temp = pd.DataFrame(data_ext_temperature)
        
        # Merge the energy and external temperature data on the 'time' column
        df = pd.merge(df_energy.iloc[:, [0, 1]], df_ext_temp.iloc[:, [0, 1]], on="time", how="inner")
        
        # Set the time column as the index for easier time-based operations
        df.index = pd.to_datetime(df['time'])
        
        # Drop the 'time' column now that it's used as the index
        del df['time']
        
        # Rename columns for clarity
        df.columns = ['HVAC power (kW)', 'External temperature (Celsius degree)']
        
        # Get the area of the building (to normalize the energy data later)
        area = FcAPI.extract_numeric_value(FcAPI.get_area_from_bui(bui_name))
        
        # Select the x-axis and y-axis variables for plotting
        xaxes = 'External temperature (Celsius degree)'
        yaxes = 'HVAC power (kW)'
        
        # Create a DataFrame with only the selected x and y axes for plotting
        dfToPlot = pd.DataFrame(df.loc[:, [xaxes, yaxes]])
        
        # Convert HVAC power to energy (by dividing by 4, likely based on scaling or units)
        dfToPlot['HVAC power (kW)'] = dfToPlot['HVAC power (kW)'] / 4
        
        # Rename the columns for clarity
        dfToPlot.columns = ['External temperature [°C]', "HVAC Energy [kWh]"]
        
        # Drop any rows with missing values
        dfToPlot = dfToPlot.dropna()

        # Set the label for the y-axis based on user selection of energy units
        label_y = "Energy kWh"
        if kwh_m2 == "kWh_m2":
            # Normalize energy consumption by the building's area if kWh/m² is selected
            dfToPlot['HVAC Energy [kWh]'] = dfToPlot['HVAC Energy [kWh]'] / area
            label_y = "Energy kWh/m2"

        # Determine the time frequency for resampling based on the button pressed
        if ctx.triggered_id == "id_btn_H":
            res_freq = "H"  # Hourly
        elif ctx.triggered_id == "id_btn_6H":
            res_freq = "6H"  # Every 6 hours
        elif ctx.triggered_id == "id_btn_12H":
            res_freq = "12H"  # Every 12 hours
        elif ctx.triggered_id == "id_btn_Day":
            res_freq = "D"  # Daily
        elif ctx.triggered_id == "id_btn_Week":
            res_freq = "W"  # Weekly
        elif ctx.triggered_id == "id_btn_Month":
            res_freq = "M"  # Monthly
        elif ctx.triggered_id == "id_btn_15min":
            res_freq = "15T"  # Every 15 minutes
        else:
            res_freq = "15T"  # Default frequency (15 minutes)

        # Resample the data based on the selected frequency
        dfToPlot = dfToPlot.resample(res_freq).agg({
            'HVAC Energy [kWh]': 'sum',  # Sum of HVAC energy for each time interval
            'External temperature [°C]': 'mean'  # Mean external temperature for each time interval
        })

        # Generate and return the plot using the resampled data
        return FcPlot.generate_graph(dfToPlot, label_y, "Temp °C", 0), False
    
    # If no data is available, return an empty chart option and show the skeleton loader
    return FcPlot.option_white, True


# ============================================================================
#                               CARPET PLOT
# ============================================================================
@callback(
    Output("data_bui_heat_map_energy", "data"),    # Output: Heatmap data for energy consumption.
    Output("data_bui_heat_map_energy_all", "data"), # Output: Full energy consumption data.
    Input("energy_parameters_analysis", "value"),   # Input: Selected energy parameter(s) for analysis.
    Input("data_shop_energy", "data"),              # Input: Energy data for the shop/building.
    prevent_initial_call = True                      # Prevent the callback from firing initially when the page loads.
)
def get_data_bui(id_mesurement, data_energy):
    # Fetch the first and last value of the selected energy parameter
    if id_mesurement and id_mesurement != "no_data":
        st_end = FcAPI.get_first_and_last_value(id_mesurement)
        
        # If the start and end values are not None, proceed with data processing
        if st_end.iloc[0, 0] != None and st_end.iloc[1, 0] != None:
            # Extract the start and end time
            time_start = st_end['time'][0].split('T')[0]
            time_end = st_end['time'][1].split('T')[0]
            time_column_name = "time"
            
            # Convert the input energy data into a pandas DataFrame
            df = pd.DataFrame(data_energy)
            
            # Group the data by month (using the 'time' column, with the specified start and end times)
            data_grouped = FcAPI.group_data_by_month(df, time_column_name, time_start, time_end)
            
            # Convert the grouped data into a JSON-compatible structure
            json_compatible_dict = {
                str(key): value
                .assign(
                    time=value["time"].dt.strftime("%Y-%m-%dT%H:%M:%S%z"),  # Format time as a string
                    year_month=value["year_month"].astype(str),            # Convert period to a string format
                )
                .to_dict(orient="records")                                  # Convert the DataFrame to a list of records
                for key, value in data_grouped.items()                      # Process each group of data by month
            }
            
            # Convert the JSON-compatible structure to a JSON string
            json_data = json.dumps(json_compatible_dict, indent=4)
            
            # Format the time column of the main DataFrame for output
            df["time"] = df["time"].dt.strftime("%Y-%m-%dT%H:%M:%S%z")
            
            # Return the processed JSON data and the full energy data as JSON
            return json_data, df.to_json(orient="records")
        
        # If no valid data is found, return empty data for both outputs
        return emptydf.to_json(), emptydf.to_json()
    
    # If the selected measurement ID is invalid or not selected, return empty data for both outputs
    return emptydf.to_json(), emptydf.to_json()


@callback(
    Output("id_skel_heat_map", "visible"),               # Output: Controls the visibility of the skeleton loader for the heatmap.
    Output("energy_heat_map", "option"),                  # Output: Generates the heatmap for energy consumption.
    Output("title_heat_map_energy", "children"),          # Output: Title of the heatmap.
    Input("data_bui_heat_map_energy", "data"),           # Input: Grouped energy data for the heatmap.
    Input("data_bui_heat_map_energy_all", "data"),       # Input: Full energy data for the building/shop.
    Input("energy_parameters_analysis", "value"),        # Input: Selected energy parameter for analysis.
    Input("energy_parameters_analysis", "data"),         # Input: Energy measurement data.
    Input("month_heat_map_energy", "value"),             # Input: Selected month for heatmap analysis.
    Input("year_heat_map_energy", "value"),              # Input: Selected year for heatmap analysis.
    prevent_initial_call = True                           # Prevent the callback from firing initially when the page loads.
)
def heat_map(data_grouped, data_all, id_mesurement, data_energy_measurement, month_, year_):
    '''
    This function generates a heatmap of energy consumption data based on the selected month and year.
    It processes the data to group and visualize energy consumption across different days and hours.
    '''
    if month_ != "" and year_ != "":
        # Load the JSON data as a dictionary
        df = pd.read_json(data_all, orient='records')           # Convert the full energy data to a DataFrame
        loaded_data = json.loads(data_grouped)                  # Parse the grouped energy data (monthly data)

        # Convert the loaded data back into a dictionary of DataFrames
        data_dict = {
            eval(key): pd.DataFrame(value).assign(
                time=pd.to_datetime(pd.DataFrame(value)["time"]),  # Convert time back to a Timestamp
                year_month=pd.DataFrame(value)["year_month"].astype("period[M]")  # Convert 'year_month' to a Period
            )
            for key, value in loaded_data.items()  # Process each group in the loaded data
        }

        # Get the label for the selected energy measurement
        sensor_name = FcGen.get_label(id_mesurement, data_energy_measurement)
        
        # Process the data for the heatmap based on the selected month and year
        dataToPlot, df_energy = FcAPI.process_dat_for_heat_map(sensor_name, data_dict, int(month_), int(year_))

        # Extract days and hours from the data to prepare for plotting
        days_int = [int(value) for value in list({row[0] for row in dataToPlot})]   # Extract unique days
        hours_int = [int(value) for value in list({row[1] for row in dataToPlot})]  # Extract unique hours
        
        # Generate a title for the heatmap
        title_graph = f"Energy profile for {month_} of {year_}",

        # Generate the heatmap chart
        heatChart = FcPlot.heatmap(
            title="Energy profile",                                # Main title of the heatmap
            subTitle=f"Heat map of energy consumption for {month_} of {year_}",  # Subtitle with month and year
            data1=dataToPlot,                                       # Data for the heatmap visualization
            days=[value + 1 for value in days_int],                  # Days to display on the heatmap (shifted to 1-based index)
            hours=hours_int,                                        # Hours to display on the heatmap
            minSeries=min(list(dict.fromkeys(df_energy['Energy']))),  # Minimum energy value for the heatmap scale
            maxSeries=max(list(dict.fromkeys(df_energy['Energy']))),  # Maximum energy value for the heatmap scale
            maxDaySeries=31                                         # Maximum number of days to show on the heatmap (31 days)
        )

        # Distribution of energy based on day vs. night periods
        def assign_period(row):
            hour = row.time.hour
            if 7 <= hour <= 20:
                return "Day (7 AM - 8 PM)"
            elif 20 < hour <= 23 or 0 <= hour < 7:
                return "Night (9 PM - 5 AM)"
            else:
                return "Excluded"

        # Apply the period assignment to the energy data
        df_dist = pd.DataFrame(df_energy).reset_index()
        df_dist["period"] = df_dist.apply(assign_period, axis=1)

        # Group by period and calculate summary statistics (sum, mean, count)
        grouped = df_dist.groupby("period")["Energy"].agg(["sum", "mean", "count"]).reset_index()

        # Return the heatmap, the title, and the visibility flag
        return False, heatChart, title_graph
    
    # If no valid month or year is selected, return a default state (empty heatmap and hidden skeleton)
    return True, FcPlot.option_white, ""  # Default return with a white option and no title


# ========================================================================================
#                           TYPICAL DAY
# ========================================================================================
@callback(
    Output("id_skel_typical_day", "visible"),   # Output: Controls the visibility of the skeleton loader for the typical day chart.
    Output("chart_typical_day", "children"),    # Output: Displays the typical day chart with workdays, weekends, and holidays.
    Input("energy_parameters_analysis", "value"),  # Input: The selected energy measurement parameter for analysis.
    Input("month_heat_map_energy", "value"),    # Input: The selected month for the typical day chart.
    Input("year_heat_map_energy", "value"),     # Input: The selected year for the typical day chart.
    Input("single_bui_energy", "value"),        # Input: The selected building for the energy analysis.
)
def graph_typical_day(id_measurement, month_, year_, bui_name):
    try: 
        # Call the FcAPI.typical_day() function to obtain data for workdays, weekends, holidays, and y-axis range
        workdays, weekends, holidays, y_min, y_max = FcAPI.typical_day(id_measurement, "time", year_selected=int(year_), month_selected=int(month_))
        
        # Round y-axis min and max values to 2 decimal places
        y_min = round(y_min, 2)
        y_max = round(y_max, 2)
        
        # Return the visibility of the skeleton loader and the typical day chart with workdays, weekends, and holidays
        return False, dmc.Stack(
            children = [
                FcGen.content_carousel(FcPlot.typical_day_chart(workdays, "Typical workday", y_min, y_max)),
                FcGen.content_carousel(FcPlot.typical_day_chart(weekends, "Typical weekend", y_min, y_max )),
                FcGen.content_carousel(FcPlot.typical_day_chart(holidays, "Typical holiday", y_min, y_max ))
            ],
            mt=10,  # Margin-top of 10 units
            mb=10   # Margin-bottom of 10 units
        )
    except:
        # In case of an error, return the skeleton loader to be visible and no chart
        return True, ""


# ========================================================================================
#                           TYPICAL WEEK
# ========================================================================================

@callback(
    Output("id_skel_typical_week", "visible"),  # Controls visibility of skeleton loader for typical week chart
    Output("id_skel_regression", "visible"),    # Controls visibility of skeleton loader for regression chart
    Output("chart_typical_week", "option"),     # Output: Displays typical week chart
    Output("energy_regression", "option"),      # Output: Displays regression chart
    Output("Table_regression_stats_energy", "children"),  # Output: Displays statistical analysis table for regression
    Input("energy_parameters_analysis", "value"),  # Input: Selected energy parameter for analysis
    Input("outdoor_parameters_energy", "value"),  # Input: Outdoor parameter selected (e.g., HDD or CDD)
    Input('regressionType', 'value'),            # Input: Type of regression model selected (linear, polynomial, etc.)
    Input('modelOrder', 'value'),                # Input: Order of regression model (e.g., degree for polynomial)
    Input('hdd_or_cdd_energy', 'value'),        # Input: Select whether to use HDD or CDD for regression
    Input("data_shop_energy", "data"),          # Input: Energy data for the selected building
    prevent_initial_call = True                  # Prevent initial callback execution
)
def plot_chart_typical_week(id_measurement_power, out_parameter, regType, orderModel, hdd_or_cdd, data_energy):
    try:
        # Convert the input data into a pandas DataFrame
        df_energy = pd.DataFrame(data_energy)

        # Check if the data is not empty
        if not df_energy.empty:
            # Get typical week data and corresponding HDD (Heating Degree Days) or CDD (Cooling Degree Days)
            df, HDD, CDD = FcAPI.typical_week(out_parameter, id_measurement_power)

            # Set up regression data based on HDD or CDD selection
            if hdd_or_cdd == 'HDD':
                df_reg = HDD.copy()
                df_reg.index = HDD["time"]
                xaxes = 'HDD'  # X-axis: Heating Degree Days (HDD)
                columnsName = ['HDD', "HVAC Energy [kWh]"]
                title = ""
            else:
                df_reg = CDD.copy()
                df_reg.index = CDD["time"]
                xaxes = 'CDD'  # X-axis: Cooling Degree Days (CDD)
                columnsName = ['CDD', "HVAC Energy [kWh]"]
                title = ""

            # Prepare data for plotting
            dfToPlot = pd.DataFrame(df_reg.loc[:, [xaxes, 'energy']])  # Extract relevant columns
            dfToPlot.columns = columnsName  # Rename columns
            dfToPlot = dfToPlot.dropna()  # Remove rows with NaN values

            # Prepare data for regression plot
            source = []
            for i, element in dfToPlot.iterrows():
                source.append([element[xaxes], element['HVAC Energy [kWh]']])

            # Create regression chart using the selected regression type and model order
            yaxesPlot = "Energy [kWh]"
            echartsGraph = FcPlot.RegressionChart(source, title, xaxes, yaxesPlot, "", regType, orderModel)

            # Statistical analysis: Perform regression and calculate metrics
            data_reg = dfToPlot
            labels = dfToPlot.columns
            x = np.array(data_reg[labels[0]])  # X-axis data (HDD or CDD)
            y = np.array(data_reg[labels[1]])  # Y-axis data (Energy)
            coefficients = np.polyfit(x, y, orderModel)  # Linear regression (or polynomial based on order)
            regression_line = np.polyval(coefficients, x)  # Generate regression line
            r_squared = r2_score(y, regression_line)  # R-squared value (coefficient of determination)
            mae = mean_absolute_error(y, regression_line)  # Mean Absolute Error
            rmse = np.sqrt(mean_squared_error(y, regression_line))  # Root Mean Squared Error

            # Create a table displaying the statistical results of the regression
            Table = dmc.Table(
                data={
                    "caption": "Statistical values of regression performance",
                    "head": ['Coefficient', "value"],
                    "body": [
                        [f"Coefficient of determination - R2", round(r_squared, 2)],
                        ["Mean absolute error - MAE", round(mae, 2)],
                        ["Root Mean Square Error", round(rmse, 2)],
                    ]
                },
                mt=10
            )

            # Construct content for the output
            child = [
                dmc.Divider(variant="solid", color='rgb(121, 80, 242)', size="md", mb=10, mt=20),
                dmc.Title("Statistical analysis", order=4, fw=700, c="black", mt=10),
                Table
            ]

            # Return outputs: Hide skeleton loaders, display charts and statistical table
            return False, False, FcPlot.typical_week_chart(df), echartsGraph, child

        # If data is empty, return default values
        source = [[0, 0], [0, 0], [0, 0]]  # Empty source data
        echartsGraph = FcPlot.RegressionChart(source, "_", "_", "_", "", 'linear', 1)  # Default empty regression chart
        return True, True, FcPlot.option_white, echartsGraph, ""  # Display skeleton loaders and empty chart

    except Exception as e:
        # Handle errors and return skeleton loaders and empty chart
        print(f"Error: {e}")
        return True, True, FcPlot.option_white, FcPlot.RegressionChart([[0, 0]], "_", "_", "_", "", 'linear', 1), ""