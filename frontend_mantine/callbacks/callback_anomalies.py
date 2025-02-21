from dash import Output, Input, State, callback, ctx, ALL, get_relative_path
from dash.exceptions import PreventUpdate
from pages.anomalies import elements
import utils.functions_general as FcGen
import pandas as pd
import numpy as np
import utils.functions_analysis as FcAnalysis
import utils.functions_api_data as FcAPI
import utils.functions_plot as FcPlot
from datetime import datetime, timedelta
import dash_mantine_components as dmc

'''Get list of buildings'''
@callback(
    Output("bui_anomalies", "data"),  # Output: A list of building options for the anomaly data
    Output("bui_anomalies", "value"),  # Output: The selected building value, default is the first building
    Input("url_app", "search")  # Input: The search query in the URL (e.g., ?bui_BCGS)
)
def get_building_list(search):
    # Fetch the list of buildings from the API and convert it to a list of building IDs
    buis = FcAPI.get_building_list()['Buis'].tolist()

    # Create a list of options where each option has a 'value' as the building ID and 'label' as the building's name (split by '_')
    options = [{'value': item, 'label': item.split('_')[1]} for item in buis]

    # Check if the URL contains a search parameter (e.g., ?bui_BCGS) and extract the building ID
    if search:
        # If a search query exists, strip the "?" and get the selected building
        buis_selected = search.lstrip("?")
    else:
        # If no search query exists, set the default selected building to the first one in the list
        buis_selected = buis[0]

    # Return the options for building selection and the selected building ID
    return options, buis_selected


# ==================================================================
#                   GET DATA AND GET OUTLIERS
# ==================================================================

@callback(
    Output("data_building", "data"),  # Output: Data containing the cleaned data from outliers, which will be displayed on the front-end.
    Input("url_app", "href"),  # Input: The current URL of the app.
    Input("bui_anomalies", "value")  # Input: The selected building name for anomaly detection.
)
def cleaned_data_from_outliers(url_app, bui_name):
    '''
    elements = [
    {"index":1, "Name":"BCGS", "Sensor":"Air Temperature 1","uuid":"abcd-1234","Value":5,"Time":"12/02/2021 05:15"},
    {"index":2, "Name":"BCGS", "Sensor":"Air Temperature 1","uuid":"abcd-1234", "Value":7,"Time":"12/02/2021 05:15"},
    {"index":3, "Name":"BCGS", "Sensor":"Air Temperature 1","Value":9,"Time":"12/02/2021 05:15"},
    ]
    '''
    # Extract the path from the URL to determine if we are on the correct page
    extracted_path = "/" + FcGen.extract_path(url_app)
    
    # Check if the current URL corresponds to the "/anomalies" page; if not, do nothing
    if extracted_path != get_relative_path("/anomalies"):
        raise PreventUpdate
    else:
        # Fetch building parameters related to temperature and energy meters
        dataP = FcAPI.get_temperature_label_and_uuid(bui_name)
        dataE = FcAPI.get_meter_label_and_uuid(bui_name)
        
        # Create DataFrames for both temperature and energy parameters
        df_P = pd.DataFrame(dataP)
        df_E = pd.DataFrame(dataE)
        
        # Concatenate the two DataFrames into one combined DataFrame
        df = pd.concat([df_P, df_E])
        
        # Filter out rows where the 'label' column contains "Outside" or "External"
        filtered_df = df[~df['label'].str.contains('Outside|External', case=False)]
        
        # Initialize an empty DataFrame to store the outliers
        df_outliers_overall = pd.DataFrame()
        
        # For each parameter in the filtered DataFrame, fetch the data and detect outliers
        for i, row in filtered_df.iterrows():
            label = row['label']
            uuid = row['value']
            
            # Get data for each parameter using its UUID
            df_param = FcAPI.get_data_from_param(uuid, False, "", "")
            
            if df_param is not None and not df_param.empty:
                df_param = df_param.dropna()
                
                # Detect outliers using the Z-score method
                df_outliers = FcAnalysis.detect_outliers(df_param, uuid, "Z_SCORE")
                
                if not df_outliers.empty:
                    # Reset the index and format the data correctly
                    df__ = df_outliers.reset_index()
                    df__['Name'] = bui_name.replace("bui_", "")  # Remove the "bui_" prefix from the building name
                    df__['Sensor'] = label  # Set the sensor label
                    df__['uuid'] = uuid  # Set the UUID for the sensor
                    df__['Value'] = df__[uuid].values[0].round(2)  # Round the value to two decimal places
                    df__['Time'] = df__["time"].values[0]  # Set the timestamp of the anomaly
                    
                    # Select only relevant columns and add the data to the overall outliers DataFrame
                    df_bui = df__.loc[:, ['Name', 'Sensor', "uuid", 'Value', 'Time']]
                    df_outliers_overall = pd.concat([df_outliers_overall, df_bui])
        
        # If outliers were found, remove duplicates based on the 'Time' column and reset the index
        if not df_outliers.empty:
            df_outliers_overall = df_outliers_overall.drop_duplicates(subset="Time").reset_index(drop=True)
            df_outliers_overall = df_outliers_overall.reset_index().to_dict('records')  # Convert DataFrame to list of dictionaries
        else:
            # If no outliers were found, return a predefined list (elements)
            df_outliers_overall = elements
        
        return df_outliers_overall


# ==================================================================
#                   VISUALIZE OUTLIERS 
# ==================================================================
@callback(
    Output("graph_anomalies", "option"),  # Output: Chart option for the graph visualization of anomalies.
    Input({"type": "action-button", "index": ALL}, "n_clicks"),  # Input: Click events for all action buttons (indexed).
    Input("data_building", "data")  # Input: Data containing building sensor readings.
)
def visualize_anomalies(btn, data):
    df = pd.DataFrame(data)  # Convert the input data into a DataFrame.
    
    if not any(btn):  # If no button was clicked, return a default (empty) chart.
        return FcPlot.option_white
    
    # Use dash.callback_context to determine which button triggered the callback.
    triggered_id = ctx.triggered_id  # Get the ID of the button that was clicked.
    
    if triggered_id and "index" in triggered_id:
        # When a button is clicked, get the row of outlier data corresponding to the button index.
        selected_outliers = pd.DataFrame(df.iloc[triggered_id['index'], :]).T

        # Get the date of the anomaly from the selected outlier data.
        date_str = selected_outliers['Time'].values[0]
        provided_date = datetime.fromisoformat(date_str)  # Convert the date to a datetime object.

        # Calculate the date range for 2 days before and 2 days after the provided anomaly time.
        two_days_before = provided_date - timedelta(days=2)
        two_days_after = provided_date + timedelta(days=2)
        
        uuid_ = selected_outliers['uuid'].values[0]  # Get the UUID of the parameter associated with the anomaly.
        
        # Fetch data for the parameter (uuid_) within the date range of two days before and after the anomaly.
        df_param = FcAPI.get_data_from_param(
            uuid_, True, 
            two_days_before.strftime("%Y-%m-%d %H:%M"), 
            two_days_after.strftime("%Y-%m-%d %H:%M")
        ).dropna()

        # Highlight the specific anomaly value in the fetched data by marking it in a new 'Outliers' column.
        df_param["Outliers"] = df_param[uuid_].where(
            df_param["time"] == selected_outliers['Time'].values[0].replace('T', ' '), 
            None
        )

        # Set the index of the data frame to the 'time' column for better plotting.
        df_param.index = df_param['time']
        del df_param['time']  # Remove the 'time' column as it's now the index.
        
        # Generate a line chart for the parameter data, marking the outlier point.
        option_chart = FcPlot.line_chart_with_effect(df_param, uuid_)
        
        return option_chart

    # If no button was clicked, return a default empty chart.
    return FcPlot.option_white


# ==================================================================
#                  CREATE, SORT TABLE
# ==================================================================
@callback(    
    Output("skeleton_table", "visible"),
    Output("table-body", "children"),
    Output("sort-order", "data"),  # Update sorting state
    Input("sort-button", "n_clicks"),  # Triggered by sort button
    Input({"type": "row-switch", "position": ALL}, "checked"),  # State of switches
    Input("data_building","data"),
    Input("table-data", "data"),
    Input("search-input", "value"),
    State("sort-order", "data"),  # Current sort state
    # prevent_initial_call=True,  # Ensure no execution on load
)
def update_table(n_clicks, switch_states, data_bui, data_, search_value, current_order):
    if data_bui:
        data_table = data_bui
    else:
        data_table = elements

    if data_table == elements:
        return False, dmc.TableTr([dmc.TableTd("") for _ in range(8)]), "asc"
   

    # Trigger source: Identify if the sort button was clicked
    if ctx.triggered_id == "sort-button":
        # Determine disabled positions
        disabled_positions = [
            switch["id"]["position"]  # Extract "position" from switch ID
            for switch, state in zip(ctx.inputs_list[1], switch_states)
            if state  # Only include active switches
        ]


        # Apply sorting based on the current state
        if current_order == "asc":
            sorted_data = sorted(data_table, key=lambda x: x["Name"], reverse=False)
            next_order = "desc"
        else:
            sorted_data = sorted(data_table, key=lambda x: x["Name"], reverse=True)
            next_order = "asc"

        # Return sorted rows and update the sorting state
        return False,FcGen.create_table_rows(sorted_data, disabled_positions), next_order#, sorted_data
    else:
        # If not the sort button, keep the current state
        disabled_positions = [
            switch["id"]["position"]  # Extract "position" from switch ID
            for switch, state in zip(ctx.inputs_list[1], switch_states)
            if state  # Only include active switches
        ]
        # Search values in the table
        if not search_value:
            sorted_data = data_table
        else:
            search_value = str(search_value).lower()
            sorted_data = [
                row
                # for row in data_data_bui
                for row in data_bui
                if any(
                    search_value in str(value).lower()
                    for value in row.values()
                )
            ]
        

        # Return rows with the original data and the same order
        return False, FcGen.create_table_rows(sorted_data, disabled_positions), current_order#, sorted_data

@callback(
    Output("delete-confirmation-modal", "opened"),
    Output("row-to-delete", "data"),  # Store the row index to delete
    Output("table-data", "data"),  # Update the data store after deletion
    Output("action-output", "children"),  # Show confirmation message
    Input({"type": "delete-button", "index": ALL}, "n_clicks"),  # Listen to all delete buttons
    Input("confirm-delete", "n_clicks"),  # Confirm button click
    Input("cancel-delete", "n_clicks"),  # Cancel button click
    State("row-to-delete", "data"),  # Get the row index to delete
    State("table-data", "data"),  # Get the current data
    State({"type": "delete-button", "index": ALL}, "id"),  # Get button IDs
    prevent_initial_call=True,  # Prevent callback from firing on load
)
def handle_delete_modal(delete_clicks, confirm_clicks, cancel_clicks, row_index, data_, ids):
    # Check if a delete button was clicked
    if ctx.triggered_id and isinstance(ctx.triggered_id, dict) and ctx.triggered_id["type"] == "delete-button":
        for n, id_ in zip(delete_clicks, ids):
            if n:  # If this button was clicked
                row_index = int(id_["index"]) - 1  # Adjust for 1-based index to 0-based list index
                return True, row_index, data_, ""  # Open modal and store the row index

    # Check if the confirm button was clicked
    if ctx.triggered_id == "confirm-delete" and row_index is not None and data_ is not None:
        # Ensure row_index is within valid bounds
        if 0 <= row_index <= len(data_):
            # Delete the row by matching the "index" field in the dataset
            data_ = [row for row in data_ if row["index"] != (row_index + 1)]
            return False, None, data_, f"Deleted row with index {row_index + 1}."

    # Check if the cancel button was clicked
    if ctx.triggered_id == "cancel-delete":
        return False, None, data_, "Deletion cancelled."

    # Default case
    return False, None, data_, ""



