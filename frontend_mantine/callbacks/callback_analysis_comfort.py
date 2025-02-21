import pandas as pd
from dash import callback, Input, Output, ctx
import utils.functions_plot as FcPlot
import pandas as pd
from sklearn.metrics import r2_score,mean_absolute_error, mean_squared_error
import numpy as np
import utils.functions_api_data as FcAPI
import dash_mantine_components as dmc
import dash_leaflet as dl
import utils.functions_general as FcGen


# =================================================================================
#                               GENERAL 
# =================================================================================
emptydf = pd.DataFrame()

@callback(
    Output("single_bui", "data"),   # Dropdown options for buildings
    Output("single_bui", "value"), # Preselected building in the dropdown
    Input("url_app", "search")     # Query parameters from the URL
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
        # Extract the selected building from the query parameter
        buis_selected = search.lstrip("?")
    else:
        # Default to the first building in the list
        buis_selected = buis[0]
    
    return options, buis_selected


'''Get list of **TEMPERATURE** Sensors'''
@callback(
    Output("comf_parameters_analysis", "data"),   # Dropdown options for temperature sensors
    Output("comf_parameters_analysis", "value"), # Preselected temperature sensor
    Output("missing_indoor_temperature", "hide"), # Boolean to hide "missing data" warning
    Input("single_bui", "value"),                # Selected building
    prevent_initial_call=True
)
def get_comfort_parameters(bui_name):
    '''
    Retrieves the list of indoor temperature sensors for a specific building.

    Args:
        bui_name (str): The selected building name.

    Returns:
        tuple:
            - A list of dictionaries with sensor labels and values for the dropdown.
            - The preselected sensor value.
            - Boolean indicating whether to hide the "missing data" warning.
    '''
    # Fetch temperature sensor data for the selected building
    dataP = FcAPI.get_temperature_label_and_uuid(bui_name)
    valueP = ""

    if dataP:
        # Filter out sensors labeled as "External" or "Outside"
        dataP_indoor = [item for item in dataP if "External" not in item['label'] and "Outside" not in item['label']]
        
        if dataP_indoor:
            # Preselect the first indoor sensor
            valueP = dataP_indoor[0]['value']
            return dataP_indoor, valueP, True
        
        # No indoor sensors found; provide a "no_data" option
        return [{'label': '', 'value': 'no_data'}], "no_data", False
    
    # No sensors found; return default "no_data" state
    return [{'label': '', 'value': 'no_data'}], "no_data", False


'''Get list of **WETAHER** Sensors'''
@callback(
    Output("outdoor_parameters", "data"),   # Dropdown options for weather sensors
    Output("outdoor_parameters", "value"), # Preselected weather sensor
    Input("single_bui", "value"),          # Selected building
    prevent_initial_call=True
)
def get_weather_parameters(bui_name):
    '''
    Retrieves the list of outdoor weather sensors for a specific building.

    Args:
        bui_name (str): The selected building name.

    Returns:
        tuple:
            - A list of dictionaries with sensor labels and values for the dropdown.
            - The preselected sensor value.
    '''
    # Fetch weather sensor data for the selected building
    dataP = FcAPI.get_meter_label_and_uuid_weather(bui_name)
    valueP = ""

    if dataP:
        # Preselect the first weather sensor
        valueP = dataP[0]['value']
    
    return dataP, valueP



# =================================================================================
#                               MAP WITH BUIDLINGS
# =================================================================================

@callback(
    Output("map_comfort","children"),
    Input("single_bui","value"),
    # prevent_initial_call=True
)
def map_with_building(bui_name):
    if bui_name:
        coordinates = FcAPI.get_latitude_longitude(bui_name)
        if coordinates['latitude'] == 'None':
            return [dl.TileLayer()]
        return [dl.TileLayer(), dl.Marker(position=[float(coordinates['latitude']), float(coordinates['longitude'])])]
    return [dl.TileLayer()]

# =================================================================================
#                               MAIN: DATA TEMPERATURE
# =================================================================================

''' Store selected data'''
@callback(
    # Outputs
    Output("data_shop", "data"),               # The processed shop data to be passed to the app
    Output("loading_data", "children"),        # Placeholder for a loading message or spinner
    Output("missing_data_of_indoor_t", "children"), # Message indicating missing data
    Output("missing_data_of_indoor_t", "hide"),     # Boolean to hide the missing data message

    # Inputs
    Input("comf_parameters_analysis", "value"),    # Selected parameter for comfort analysis
    Input("comf_parameters_analysis", "data"),     # Metadata of comfort parameters

    prevent_initial_call=True  # Prevent triggering this callback on initial page load
)
def get_data_from_bui(param_name, all_parameters):
    '''
    Retrieves and processes data for a selected parameter from the shop sensors.

    Args:
        param_name (str): The name of the selected comfort parameter.
        all_parameters (list): A list of all available comfort parameters, each with a label and value.

    Returns:
        tuple: Processed data, loading placeholder, missing data message, and hide state for the message.
    '''
    # Validate the input parameter
    if not param_name or len(param_name) < 1:
        # No parameter provided; return empty states
        return "", "", "", True
    
    # Process the selected parameter if it's valid and not marked as "no_data"
    if param_name and param_name != "no_data":
        # Retrieve the first and last available timestamps for the parameter
        st_end = FcAPI.get_first_and_last_value(param_name)
        
        # Find the label corresponding to the selected parameter
        label = next((item['label'] for item in all_parameters if item['value'] == param_name), None)

        # Validate that the retrieved timestamps are not None
        if st_end.iloc[0, 0] is not None and st_end.iloc[1, 0] is not None:
            # Extract start and end times from the timestamps
            time_start = st_end['time'][0].split('T')[0]
            time_end = st_end['time'][1].split('T')[0]

            # Fetch the data for the specified parameter and time range
            df = FcAPI.get_data_from_shops(param_name, time_start, time_end)

            # Ensure the label is valid
            if label is None:
                raise ValueError(f"Label not found for parameter: {param_name}")

            # Rename the column with the parameter's label
            df.columns = ['time', label]

            # Add derived columns (e.g., workday and hours) for additional data analysis
            df = FcGen.add_workday_and_hours_columns(df)

            # Return the processed data as a dictionary, and clear any messages or loading states
            return df.to_dict('records'), "", "", True
        else:
            # Handle cases where the parameter has no data available
            return "", "", f"No data available for the sensor {label}", False

    # Return default states for invalid or unselected parameters
    return "", "", "", True


# =================================================================================
#                               INFO CARDS
# =================================================================================
@callback(
    # Min Temperature
    Output("id_skel_info_comfort", "visible"),  # Visibility control for the skeleton component
    Output("id_cw_shop", "children"),          # Card for minimum temperature
    Output("text_card_comfort_1", "children"), # Label for the minimum temperature card

    # Max Temperature
    Output("id_tw_shops", "children"),         # Card for maximum temperature
    Output("text_card_comfort_2", "children"), # Label for the maximum temperature card

    # Average Temperature
    Output("id_ts_shops", "children"),         # Card for average temperature
    Output("text_card_comfort_3", "children"), # Label for the average temperature card

    # Median Temperature
    Output("id_cs_shops", "children"),         # Card for median temperature
    Output("text_card_comfort_4", "children"), # Label for the median temperature card

    # Inputs
    Input("data_shop", "data"),                # Temperature data for the shop
    Input("comf_parameters_analysis", "data"), # Metadata for comfort parameters
    Input("comf_parameters_analysis", "value"),# Selected comfort parameter
    Input("url_app", "href"),                  # Current page URL
    prevent_initial_call=True                  # Prevent triggering on page load
)
def comfort_cards(data, all_parameters, param_name, url_a):
    '''
    Generates values for the comfort cards that display minimum, maximum, average, 
    and median temperatures based on the selected parameter.

    Args:
        data (dict): Temperature data for the shop.
        all_parameters (list): List of available comfort parameters with labels and values.
        param_name (str): Selected comfort parameter name.
        url_a (str): Current page URL.

    Returns:
        tuple: Outputs for visibility control, card content, and card labels.
    '''
    # Extract the current page path from the URL
    extracted_path = "/" + FcGen.extract_path(url_a)
    
    # Check if the user is on the "building_benchmarking/comfort" page
    if extracted_path == "/building_benchmarking/comfort":
        # If no parameter is selected or the parameter name list is empty, show default states
        if not param_name or len([param_name]) < 1:
            return True, "", "", "", "", "", "", "", ""

        # Process the selected parameter
        if param_name:
            # Ensure the input data is not empty
            if data != '':
                # Convert input data to a DataFrame and set the index as datetime
                df_p = pd.DataFrame(data)
                df_p.index = pd.to_datetime(df_p['time'])

                # Assign the label corresponding to the selected parameter
                label = next((item['label'] for item in all_parameters if item['value'] == param_name), None)
                df_p = pd.DataFrame(df_p.loc[:, label])
                df_p.index.name = None
                df_p.columns = [label]

                # Calculate min, max, mean, and median for the selected parameter
                results = FcAPI.get_min_max_in_time_range(df_p, label)

                # Return the results to update the UI
                return (
                    False,                      # Hide the skeleton loader
                    results['overall_min'],     # Minimum temperature
                    label,                      # Label for the minimum temperature card
                    results['overall_max'],     # Maximum temperature
                    label,                      # Label for the maximum temperature card
                    results['overall_mean'],    # Average temperature
                    label,                      # Label for the average temperature card
                    results['overall_median'],  # Median temperature
                    label                       # Label for the median temperature card
                )

            # If the data is empty, return default states
            return True, "", "", "", "", "", "", "", ""
        
        # If no parameter is selected, return default states
        return True, "", "", "", "", "", "", "", ""

    # If the user is not on the "building_benchmarking/comfort" page, return default states
    else:
        return True, "", "", "", "", "", "", "", ""



# =================================================================================
#                               TEMPERATURE PROFILE
# =================================================================================
'''Visualize temperature data in a line-chart'''
@callback(
    Output("id_skel_temp_profile", "visible"),  # Output to control visibility of temperature profile skeleton
    Output("id_skel_heat_map_comfort", "visible"),  # Output to control visibility of heat map skeleton
    Output("shops_timeseries_p", "option"),  # Output for timeseries plot options
    Output("heat_chart", "option"),  # Output for heat map options
    Input("data_shop", "data"),  # Input dataset for the shop
    Input("comf_parameters_analysis", "data"),  # Input: comfort parameters metadata
    Input("comf_parameters_analysis", "value"),  # Input: selected comfort parameter name
    Input("id_btn_T_15min", "n_clicks"),  # Input: Button for 15-minute frequency resampling
    Input("id_btn_T_H", "n_clicks"),  # Input: Button for hourly frequency resampling
    Input("id_btn_T_6H", "n_clicks"),  # Input: Button for 6-hour frequency resampling
    Input("id_btn_T_12H", "n_clicks"),  # Input: Button for 12-hour frequency resampling
    Input("id_btn_T_Day", "n_clicks"),  # Input: Button for daily frequency resampling
    Input("id_btn_T_Week", "n_clicks"),  # Input: Button for weekly frequency resampling
    Input("id_btn_T_Month", "n_clicks"),  # Input: Button for monthly frequency resampling
    Input("url_app", "href"),  # Input: Current application URL
    prevent_initial_call=True  # Prevent callback execution on page load
)
def temperature_and_heatmap(data, all_parameters, param_name, btn15, btnH, btn6H, btn12H, btnD, btnW, btnM, url_a):
    """
    Callback to process temperature data and generate plots (timeseries and heatmap) for the "comfort" section.

    Args:
        data (dict): Data for temperature analysis.
        all_parameters (list): List of all parameters with labels and values.
        param_name (str): Selected parameter name.
        btn15, btnH, btn6H, btn12H, btnD, btnW, btnM: Button click states for different resampling frequencies.
        url_a (str): Current URL to identify the application path.

    Returns:
        tuple: Visibility flags and chart options (timeseries and heatmap).
    """
    # Extract the path from the URL
    extracted_path = "/" + FcGen.extract_path(url_a)

    # Ensure the function is executed only for the "building_benchmarking/comfort" path
    if extracted_path == "/building_benchmarking/comfort":
        # If no parameter is selected or the list is empty, return default values
        if not param_name or len(param_name) < 1:
            return True, True, FcPlot.option_white, FcPlot.option_white
        
        # Proceed if a parameter is selected
        if param_name:
            if data != '':
                # Convert the input data to a DataFrame and set the datetime index
                df_p = pd.DataFrame(data)
                df_p.index = pd.to_datetime(df_p['time'])

                # Extract the label corresponding to the selected parameter name
                label = next((item['label'] for item in all_parameters if item['value'] == param_name), None)

                # Filter the DataFrame to include only the selected parameter's data
                df_p = pd.DataFrame(df_p.loc[:, label])
                df_p.index.name = None
                df_p.columns = [label]

                # Determine the resampling frequency based on the triggered button
                res_freq = {
                    "id_btn_T_H": "H",
                    "id_btn_T_6H": "6H",
                    "id_btn_T_12H": "12H",
                    "id_btn_T_Day": "D",
                    "id_btn_T_Week": "W",
                    "id_btn_T_Month": "M",
                    "id_btn_T_15min": "15T",
                }.get(ctx.triggered_id, "15T")

                # Resample the dataset based on the selected frequency
                df_p = df_p.resample(res_freq).mean()

                # Prepare data for the heat map
                df_hm = df_p.copy()
                df_hm = df_hm.resample('H').mean()  # Resample to hourly frequency for the heat map
                df_p_reset = df_hm.reset_index()
                df_p_reset.columns = ["time", label]
                df_p_reset[label] = df_p_reset[label].round(2)  # Round data to two decimals
                df_p_reset['time'] = pd.to_datetime(df_p_reset['time'])

                # Generate data for the heat map
                dataToPlot = FcGen.data_for_heat_map(df_p_reset, label)

                # Extract unique days (x-axis) and hours (y-axis) for the heat map
                days = sorted(list(set([item[0] for item in dataToPlot])))
                hours = list(range(24))  # 0 to 23 hours

                # Generate and return timeseries plot and heat map
                return (
                    False,  # Hide temperature profile skeleton
                    False,  # Hide heat map skeleton
                    FcPlot.generate_graph(df_p, "Temperature °C", "", -100),  # Timeseries plot
                    FcPlot.overall_heat_map(dataToPlot, days, hours)  # Heat map
                )
            
            # Default return if data is empty
            return True, True, FcPlot.option_white, FcPlot.option_white
        
        # Default return if parameter name is invalid
        return True, True, FcPlot.option_white, FcPlot.option_white

    # Default return if the path does not match "building_benchmarking/comfort"
    return True, True, FcPlot.option_white, FcPlot.option_white



# =================================================================================
#                              OVERHEATING/OVERCOOLING
# =================================================================================
@callback(
    Output("carousel_overheating", "children"),  # Output: Overheating percentage donut chart
    Output("carousel_overheating_month", "children"),  # Output: Monthly distribution of overheating
    Output("carousel_overcooling", "children"),  # Output: Overcooling percentage donut chart
    Output("carousel_overcooling_month", "children"),  # Output: Monthly distribution of overcooling
    Input("data_shop", "data"),  # Input: Data for shop
    Input("comf_parameters_analysis", "data"),  # Input: Comfort parameters metadata
    Input("comf_parameters_analysis", "value"),  # Input: Selected parameter name
)
def chart_hoverheating(data, all_parameters, param_name):
    '''
    Generates donut charts for overheating and overcooling percentages,
    as well as their respective monthly distributions, to be displayed in a carousel.

    Args:
        data (dict): Temperature data from the shop.
        all_parameters (list): List of all parameters with labels and values.
        param_name (str): Selected parameter name.

    Returns:
        tuple: Four components (overheating chart, overheating monthly chart,
               overcooling chart, overcooling monthly chart) for display in the carousel.
    '''
    # Check if a parameter name has been selected
    if param_name:
        # Ensure data is not empty
        if data != '':
            # Convert the input data to a DataFrame and set its index to datetime
            df_p = pd.DataFrame(data)
            df_p.index = pd.to_datetime(df_p['time'])

            # Extract the label corresponding to the selected parameter name
            label = next((item['label'] for item in all_parameters if item['value'] == param_name), None)

            # Filter the DataFrame to include only the selected parameter's data
            df_p = pd.DataFrame(df_p.loc[:, label])
            df_p.index.name = None
            df_p.columns = [label]

            # Calculate overheating percentages and monthly distribution
            exceed_calculation = FcAPI.calculate_exceedance_with_monthly_distribution(df_p)
            perc_over = exceed_calculation[1]  # Percentage of overheating
            perc_under = 100 - perc_over  # Percentage of non-overheating

            # Calculate overcooling percentages and monthly distribution
            exceed_calculation_cool = FcAPI.calculate_exceedance_with_monthly_distribution_overccoling(df_p)
            perc_over_cool = exceed_calculation_cool[1]  # Percentage of overcooling
            perc_under_cool = 100 - perc_over_cool  # Percentage of non-overcooling

            # Determine the season (Winter or Summer) based on the months in the dataset
            Season = FcAPI.determine_season(df_p.index.month.unique().to_list())

            # Extract monthly distribution for overheating
            montly_distribution = exceed_calculation[2]
            distribution_list = [[month, percentage] for month, percentage in montly_distribution.items()]

            # Map month numbers to month names
            month_names = {
                1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"
            }

            # Prepare data for the monthly distribution of overheating
            data__ = [{'value': value, 'name': month_names[month]} for month, value in distribution_list]

            # Extract monthly distribution for overcooling
            montly_distribution_cool = exceed_calculation_cool[2]
            distribution_list_c = [[month, percentage] for month, percentage in montly_distribution_cool.items()]

            # Prepare data for the monthly distribution of overcooling
            data__c = [{'value': value, 'name': month_names[month]} for month, value in distribution_list_c]

            # Define chart titles
            title_2 = "Percentage of overheating (T>24°C)"
            title_3 = "Monthly distribution of overheating"
            title_5 = "Monthly distribution of overcooling"

            # Set specific titles based on the season
            if Season == "Winter":
                title_1 = "Winter Period"
                title_4 = "Percentage of overcooling (T<18°C)"

                # Generate and return the donut charts for Winter
                return (
                    FcPlot.plot_doughnut(title_1, title_2, perc_over, perc_under),
                    FcPlot.plot_doughnut_month(title_1, title_3, data__),
                    FcPlot.plot_doughnut(title_1, title_4, perc_over_cool, perc_under_cool),
                    FcPlot.plot_doughnut_month(title_1, title_5, data__c)
                )

            elif Season == "Summer":
                title_1 = "Summer Period"
                title_4 = "Percentage of overcooling (T<18°C)"

                # Generate and return the donut charts for Summer
                return (
                    FcPlot.plot_doughnut(title_1, title_2, perc_over, perc_under),
                    FcPlot.plot_doughnut_month(title_1, title_3, data__),
                    FcPlot.plot_doughnut(title_1, title_4, perc_over_cool, perc_under_cool),
                    FcPlot.plot_doughnut_month(title_1, title_5, data__c)
                )

        # Return empty values if data is empty
        return "", "", "", ""
    
    # Return empty values if no parameter name is selected
    else:
        return "", "", "", ""



# ==================================================================================================
#                   DATA FOR REGRESSION + PLOT SCATTER WITH REGRESSION + TABLE
# ==================================================================================================
'''Regression Parameters'''
@callback(
    Output("parameter_hist_temp_y","data"),
    Output("parameter_hist_temp_y","value"),
    Input("single_bui","value"),
    prevent_initial_call =True
)
def get_parameters_x_ayxes(bui_name): 
    '''
    Update select component of Y-axes with the available data 
    '''      
      # OUTDOOR TEMPERATURE SENSOR
    dataExT = FcAPI.get_meter_label_and_uuid_weather(bui_name)

    # INDOOR TEMPERATURE SENSORS
    dataP = FcAPI.get_temperature_label_and_uuid(bui_name)
    valueP = ""
     # CHECK IF DATA is available
    if dataP:
        # Filter out items containing 'External' or 'Outside'
        dataP_indoor = [item for item in dataP if "External" not in item['label'] and "Outside" not in item['label']]
        if dataP_indoor:
            valueP = dataP_indoor[0]['value']
            data_overall = dataP_indoor + dataExT
            return data_overall, valueP
        return [{'label':'', 'value':'no_data'}], "no_data"
    return [{'label':'', 'value':'no_data'}], "no_data"


@callback(
    Output("parameter_hist_temp_x","data"),
    Output("parameter_hist_temp_x","value"),
    Input("single_bui","value"),
    prevent_initial_call =True
)
def get_parameters_y_axes(bui_name):
    '''
    Update select component of X-axes with the available data 
    '''
    # OUTDOOR TEMPERATURE SENSORS
    dataExT = FcAPI.get_meter_label_and_uuid_weather(bui_name)

    # INDOOR TEMPERATURE SENSORS
    dataP = FcAPI.get_temperature_label_and_uuid(bui_name)
    valueP = ""
    # CHECK IF DATA is available
    if dataP:
        # Filter out items containing 'External' or 'Outside'
        dataP_indoor = [item for item in dataP if "External" not in item['label'] and "Outside" not in item['label']]
        if dataP_indoor:
            valueP = dataP_indoor[0]['value']
            data_overall = dataP_indoor + dataExT
            return data_overall, valueP
        return [{'label':'', 'value':'no_data'}], "no_data"
    

@callback(
    Output("data_regression","data"),
    Input("parameter_hist_temp_x","value"),
    Input("parameter_hist_temp_y","value"),
)
def save_regression_params(param_x_name, param_y_name):
    '''
    Save X and Y parameters in a dcc.Store
    '''
    if param_x_name !="no_data" and param_y_name !="no_data":
        data = {
            'x_reg':param_x_name,
            'y_reg':param_y_name
            }
        param_name = [param_x_name, param_y_name]
        df = FcAPI.get_values_from_multiparameters(param_name, '2021-09-15', '2024-09-15')
        return df.to_dict('records'), data
    return emptydf.to_dict()


@callback(
    Output("id_skel_regression_comfort","visible"),
    Output("shops_scatter_hist","children"),
    Output("Table_regression_stats","children"),
    Input("data_regression","data"),
    Input("parameter_hist_temp_x","data"),
    Input("parameter_hist_temp_x","value"),
    Input("parameter_hist_temp_y","value"),
    Input("regressionType_T","value"),
    Input("modelOrder_T","value"),
    # Resample data
    Input("id_btn_T_15min_reg","n_clicks"),
    Input("id_btn_T_H_reg","n_clicks"),
    Input("id_btn_T_6H_reg","n_clicks"),
    Input("id_btn_T_12H_reg","n_clicks"),
    Input("id_btn_T_Day_reg","n_clicks"),
    Input("id_btn_T_Week_reg","n_clicks"),
    Input("id_btn_T_Month_reg","n_clicks"),
    prevent_initial_call =True
)
def histogram_plot(data_reg_and_param, param_x, param_x_name, param_y_name, regrType, orderType,
                   btn_15, btn_60, btn_6h, btn_12h, btn_day, btn_week, btn_month):
    """
    Function to generate a histogram and statistical regression analysis.
    
    Args:
        data_reg_and_param (dict): Data for regression and its associated parameters.
        param_x (list): Metadata for the X parameter.
        param_x_name (str): Name of the X-axis parameter.
        param_y_name (str): Name of the Y-axis parameter.
        regrType (str): Type of regression to use.
        orderType (int): Order of the polynomial for regression.
        btn_15, btn_60, btn_6h, btn_12h, btn_day, btn_week, btn_month: Button clicks to select resampling frequency.

    Returns:
        tuple: Visibility flag, histogram with regression chart, and statistical table for regression.
    """
    if param_x_name and param_y_name:
        if data_reg_and_param != {} and data_reg_and_param[0] != []:
            # Convert stored data to a DataFrame
            df = pd.DataFrame(data_reg_and_param[0])
            param_name = [param_x_name, param_y_name]
            # Extract label for X-axis
            label = next((item['label'] for item in param_x if item['value'] == param_x_name), None)
            
            # Change frequency
            if ctx.triggered_id =="id_btn_T_H_reg":
                res_freq = "H"
            elif ctx.triggered_id =="id_btn_T_6H_reg":
                res_freq = "6H"
            elif ctx.triggered_id =="id_btn_T_12H_reg":
                res_freq = "12H"
            elif ctx.triggered_id =="id_btn_T_Day_reg":
                res_freq = "D"
            elif ctx.triggered_id =="id_btn_T_Week_reg":
                res_freq = "W"
            elif ctx.triggered_id =="id_btn_T_Month_reg":
                res_freq = "M"
            elif ctx.triggered_id =="id_btn_T_15min_reg":
                res_freq = "15T"
            else:
                res_freq = "15T"
        
            # Resample dataset
            df_resampled = df.copy()
            df_resampled.index = pd.to_datetime(df_resampled['time'])
            del df_resampled['time']
            df_resampled = df_resampled.resample(res_freq).mean()    
            

            # Getting Labels:
            labels = [
                next((item['label'] for item in param_x if item['value'] == param), param)
                for param in param_name
            ]
            # If same parameter for X and Y return a default table
            if len(df_resampled.columns) == 1:
                r_squared=1.0
                mae=0.0
                rmse=0.0
            else:
                df_resampled.columns = labels
                source = []
                for i,element in df_resampled.iterrows():
                    source.append([
                        round(element[labels[0]],2),
                        round(element[labels[1]],2)
                        ])
                # CALCULATION OF REGRESSION - Statistical values
                data_reg = df_resampled.dropna()
                x = np.array(data_reg[labels[0]])
                y = np.array(data_reg[labels[1]])
                coefficients = np.polyfit(x, y, orderType)  # Linear regression
                regression_line = np.polyval(coefficients, x)
                r_squared = r2_score(y, regression_line)
                mae = mean_absolute_error(y, regression_line)
                rmse = np.sqrt(mean_squared_error(y, regression_line))

             # Statistical analysis table
            Table = dmc.Table(
                data = {
                    "caption":"Statstical values of regression performance",
                    "head":['Coefficient', "value"],
                    "body": [
                        [f"Coefficient of determination - R2", round(r_squared,2)],
                        ["Mean absolute error - MAE", round(mae,2)],
                        ["Root Mean Square Error", round(rmse,2)],
                    ]
                },
                mt=10
            )
            
            child = [
                dmc.Title("Statistical analysis", order=3, fw=700, c="black", mt=10),
                Table
            ]

            # Case: same parameter for X and Y
            if param_x_name == param_y_name:
                data_p = df_resampled.dropna()
                source = []
                for i,element in data_p.iterrows():
                    source.append([
                        round(element[param_x_name],2),
                        round(element[param_y_name],2)
                        ])
                return False, FcGen.general_chart(FcPlot.RegressionChart(source,"",label,label, "", regrType, orderType)), child
            # different parameters for X and Y
            return False, FcGen.general_chart(FcPlot.RegressionChart(source,"",label[0],label[1], "", regrType, orderType)), child
        
        return True, FcGen.general_chart(FcPlot.option_white), [""]
    
    return True, FcGen.general_chart(FcPlot.option_white), [""]
