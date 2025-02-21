from dash import Output, Input, State, get_relative_path, callback, ALL
import utils.functions_api_data as FcAPI
import pandas as pd
import dash_mantine_components as dmc
import dash_leaflet as dl
import json
from dash.exceptions import PreventUpdate
from datetime import datetime, timedelta
from urllib.parse import urlparse
import utils.functions_general as FcGen
import utils.functions_api_data as FcAPI



@callback(
    Output("name_stores", "data"),
    Input("url_app", "href")
)
def fetch_building_list(url):
    """
    Extract the base path from the URL and fetch the building list if the path matches the root.
    """
    extracted_path =  "/" + FcGen.extract_path(url)
    # Fetch building list if the path matches the root
    if extracted_path == get_relative_path("/building"):
        building_list = FcAPI.get_building_list()['Buis'].tolist()
        
        return json.dumps(building_list)
    raise PreventUpdate


# Callback 2: Generate cards for the building list
@callback(
    Output("building_list_card", "children"),
    Input("name_stores", "data"),
)
def generate_building_cards(data):
    """
    Generate a list of building cards based on the fetched building list.
    """
    if data:
        # Load building list from the input data
        building_list = json.loads(data)

        # Remove prefix (e.g., "bui_") from building names
        building_names = [name[4:] for name in building_list]

        # Create a card for each building
        building_cards = [
            FcGen.card_building_home(
                building_name=building, 
                
                index_=i,
            ) 
            for i, building in enumerate(building_names)
        ]

        # Wrap the cards in a scrollable container
        return dmc.Stack(
            children=[
                dmc.ScrollArea(
                    id="scroll_area_building",
                    h=800,
                    children=building_cards
                )
            ]
        )
    return ""  # Return an empty string if no data



'''Save data loaded in a store'''
@callback(
    Output("last_data_bui", "data"),
    Input("name_stores", "data"),
    Input("url_app", "href"),
    State("last_data_bui", "data"),
)
def get_last_values(data, url, last_d):
    # Extract path from the URL to determine which route is active
    extracted_path = "/" + FcGen.extract_path(url)

    # If the path doesn't match '/building', prevent callback update
    if extracted_path != get_relative_path("/building"):
         raise PreventUpdate
    else:
        # Check if there is any previous data in the last_d variable
        if last_d:
            # Get the current time
            now = datetime.now()
            
            # Try to parse the previous time from the 'last_d' data to compare with current time
            try:
                before = datetime.strptime(last_d['time'], "%Y-%m-%dT%H:%M:%S.%f")
            except:
                # In case the format is incorrect, attempt to parse the time from the first item in a list
                before = datetime.strptime(last_d[0]['time'], "%Y-%m-%dT%H:%M:%S.%f")

            # Calculate the difference in time between now and the last time the data was updated
            time_difference = now - before
            
            # If the data was updated more than 60 minutes ago, fetch new data
            if time_difference > timedelta(minutes=60):
                # Load the building list from the input data (the 'name_stores' component)
                building_list = json.loads(data)
                
                # Fetch the latest data (indoor temperature, external temperature, and HVAC power)
                indoor_temperature, external_temperature, hvac_powers = FcAPI.get_building_data_last(building_list)
                
                # Prepare the new data to return (building list, temperatures, HVAC data, and current time)
                data = {
                    'buis': building_list,
                    'indoor_temp': indoor_temperature,
                    'ext_temp': external_temperature,
                    'hvac': hvac_powers,
                    'time': datetime.now()
                }

                # Return the new data to update the 'last_data_bui' component
                return data

            # If data is not older than 60 minutes, return the existing 'last_d' data
            return last_d
        
        # If there's no previous data, fetch the latest data
        else: 
            if data:
                # Load the building list from the input data (the 'name_stores' component)
                building_list = json.loads(data)
                
                # Fetch the latest data (indoor temperature, external temperature, and HVAC power)
                indoor_temperature, external_temperature, hvac_powers = FcAPI.get_building_data_last(building_list)
                
                # Prepare the new data to return (building list, temperatures, HVAC data, and current time)
                data = {
                    'buis': building_list,
                    'indoor_temp': indoor_temperature,
                    'ext_temp': external_temperature,
                    'hvac': hvac_powers,
                    'time': datetime.now()
                }

                # Return the new data to update the 'last_data_bui' component
                return data
            
            # If no data is provided, prevent any update
            raise PreventUpdate

   

# ====================================================================================
#                           UPDATE CARD WITH LAST VALUES
# ====================================================================================
@callback(
    Output({'type': 'indoor_temp', 'index': ALL}, "children"),  # Updates all components with 'indoor_temp' type and an index
    Output({'type': 'outdoor_temp', 'index': ALL}, "children"),  # Updates all components with 'outdoor_temp' type and an index
    Output({'type': 'HVAC_power', 'index': ALL}, "children"),    # Updates all components with 'HVAC_power' type and an index
    Input("last_data_bui", "data")  # Takes the data from the 'last_data_bui' component as input
)
def card_inputs(last_d):
    if last_d:  # Check if data from the 'last_data_bui' component exists
        try:
            # Attempt to return the indoor temperature, outdoor temperature, and HVAC power from the data (if it's structured correctly)
            return last_d['indoor_temp'], last_d['ext_temp'], last_d['hvac']
        except:
            # If an error occurs (for example, if the data is a list instead of a dictionary), return the first item in the list
            return last_d[0]['indoor_temp'], last_d[0]['ext_temp'], last_d[0]['hvac']
    raise PreventUpdate  # If there is no data (last_d is None), prevent the update and don't change the components



'''create list of cards from the building list'''
@callback(
    Output("map_home", "children"),
    Input("name_stores", "data"),
)
def create_list_of_cards(data):
    # Check if data is available (building list passed via 'name_stores')
    if data:
        # Parse the building list from JSON data
        buis_list = json.loads(data)
        locations = []  # Initialize an empty list to store building locations

        # Modify the building names (slice the first 4 characters from each name)
        modified_strings_bui = [s[4:] for s in buis_list]
        
        # Loop through each modified building name
        for building in modified_strings_bui:
            try: 
                # Attempt to fetch coordinates for the building
                coordinates = FcAPI.get_latitude_longitude(f"bui_{building}")
            except:
                # If coordinates are not found, set to empty values
                coordinates = {'latitude': "", 'longitude': ""}
            
            # If the latitude is valid (not "None"), add it to the locations list
            if coordinates['latitude'] != "None":
                locations.append({'lat': coordinates['latitude'], "lon": coordinates['longitude'], "label": building})
            
        # Create markers for the map based on the locations
        markers = [
            dl.Marker(
                position=(loc["lat"], loc["lon"]),  # Position each marker at the corresponding coordinates
                children=dl.Tooltip(loc["label"])  # Show the building name as a tooltip on hover
            )
            for loc in locations
        ]
        
        # Create the map with the markers and tile layer
        Map = dl.Map(
            children=[
                dl.TileLayer(),  # Add a tile layer for the map
                dl.LayerGroup(markers)  # Add the markers to the map as a layer
            ],
            maxZoom=7,  # Set maximum zoom level
            minZoom=5,  # Set minimum zoom level
            style={'width': '100%', "height": '95%', 'zIndex': '0', 'borderRadius': '20px', 'marginTop': '20px'},  # Map styling
            center=[41.90586515496108, 12.487919956158356],  # Initial map center (latitude, longitude)
            zoom=5,  # Initial zoom level
        )

        # Return the map with the markers
        return Map
    
    # If no data is provided, return an empty map with no markers
    return dl.Map(
        children=[dl.TileLayer()],  # Only add the tile layer (no markers)
        style={'width': '100%', "height": '95%', 'zIndex': '0', 'borderRadius': '20px', 'marginTop': '20px'},  # Map styling
        center=[41.90586515496108, 12.487919956158356],  # Initial map center (latitude, longitude)
        zoom=5,  # Initial zoom level
    )


