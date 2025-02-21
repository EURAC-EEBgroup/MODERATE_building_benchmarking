# ====================================================
#               PROCESSING DATA
# ====================================================

from dash import callback, Output, Input, State, ctx, html,clientside_callback
from dash.exceptions import PreventUpdate
import pandas as pd
import io
import base64
import dash_mantine_components as dmc
import utils.functions_plot as FcPlot
import utils.functions_analysis as FcAnalysis
import dash_echarts
import numpy as np
from rdflib import Graph, URIRef
import uuid
import dash_cytoscape as cyto
import os 
from utils.brick_generation import generate_brick_ttl
import utils.functions_api_data as FcAPI
from dash_iconify import DashIconify

# ======================================================================
#                       ACCORDION Open
# ======================================================================
'''
Open accordion data processing if file is uoploaded
'''
@callback(
    Output("accordion_processing","value"),
    Input("btn_upload_file","n_clicks"),
    Input("btn_visualize_brick","n_clicks"),
    State("accordion_processing","value"),
)
def open_processing(btn, btn_visualize, state_accordion):
    if ctx.triggered_id == "btn_upload_file":
        if state_accordion == ['brick_graph']:
            return ["data_process", 'brick_graph']
        elif state_accordion == ['data_process']:    
            return ["data_process"]
        else:
            return ["data_process", 'brick_graph']
    
    elif ctx.triggered_id == "btn_visualize_brick":
        if state_accordion == ['brick_graph']:
            return ['brick_graph']
        elif state_accordion == ['data_process']:    
            return ["data_process", 'brick_graph']
        else:
            return ["data_process", 'brick_graph']
    
    else:
        return ["data_process", 'brick_graph']

# Hide or visualize notification upload data
@callback(
    Output("aler_file_upload","hide"),
    Input("uploaded_data","data"),
    prevent_initial_call = True
)
def remove_alert(data):
    df = pd.DataFrame(data)
    if not df.empty:
        return True
    return False



# ======================================================================
#                       GET DATA and visualize in Table
# ======================================================================
clientside_callback(
    """
    function updateLoadingState(n_clicks) {
        return true
    }
    """,
    Output("loading-button", "loading", allow_duplicate=True),
    Input("loading-button", "n_clicks"),
    prevent_initial_call=True,
)

@callback(
    [Output('output-data-upload', 'children'),
     Output('uploaded_data', 'data'),
     Output('data-grid', 'rowData'),
     Output('data-grid', 'columnDefs'),
     Output('btn_upload_file', 'loading'),
     ],
    Input('upload_file', 'contents'),
    State('upload_file', 'filename')
)
def update_output(contents, filename):
    if contents is not None:
        # Decode the uploaded file contents
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            # Read the CSV with specific parsing options
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')),
                sep=';',  # Use semicolon as separator
                decimal = ",",
                parse_dates=[0],  # Parse the first column as datetime
                infer_datetime_format=True
            )
            # Store DataFrame as JSON (for dcc.Store)
            data_store = df.to_dict('records')
            # Generate AG Grid configuration
            columns = [{"headerName": col, "field": col} for col in df.columns]
            return (
                html.Div([
                    html.H5(f"Uploaded File: {filename}"),
                    html.H6("DataFrame Loaded Successfully!"),
                ]),
                data_store,
                df.to_dict('records'),  # AG Grid row data
                columns,                # AG Grid column definitions
                False,
            )
        except Exception as e:
            return (
                html.Div([
                    html.H5(f"Error processing file: {filename}"),
                    html.Pre(str(e))
                ]),
                None,
                [],
                [],
                False
            )
    return "", None, [], [], False

# ======================================================================
#                       ENABLE CHECK Inputs
# ======================================================================

@callback(
    Output("check_visualize_outliers", "disabled"),
    Output("check_remove_outliers", "disabled"),
    Input("uploaded_data","data")
)
def enable_check_and_remove_outliers(data):
    df = pd.DataFrame(data)
    if df.empty:
        return True, True
    return False, False

# ======================================================================
#                      PLOT DATA
# ======================================================================

@callback(
    Output("processing_parameter_temperature","data"),
    Output("processing_parameter_temperature","value"),
    Output("processing_parameter_energy","data"),
    Output("processing_parameter_energy","value"),
    Output("time_index_name","data"),
    Output("time_index_name","value"),
    Input("uploaded_data","data"),
    prevent_initial_call=True
)
def get_parameters_to_be_visualized(data_upl):
    '''
    Parameters to be used by multisect for plotting
    '''
    if data_upl:
        df = pd.DataFrame(data_upl)
        # Initialize lists
        time_list = []
        temperature_list = []
        power_energy_list = []
        other = []

        # Classify columns
        for col in df.columns:
            col_lower = col.lower()  # Convert column name to lowercase for case-insensitive matching
            if "temperature" in col_lower or "temp" in col_lower:
                temperature_list.append(col)
            elif "power" in col_lower or "energy" in col_lower:
                power_energy_list.append(col)
            elif "time" in col_lower or "date" in col_lower:
                time_list.append(col)
            else:
                other.append(col)

        return temperature_list, temperature_list[0],power_energy_list,power_energy_list[0] ,time_list, time_list[0]
    return [],[],[],[],[],[]


@callback(
    Output("cleaned_data","data"),
    Input("check_remove_outliers","checked"),
    Input("time_index_name","value"),
    Input("processing_parameter_temperature","value"),
    Input("uploaded_data","data"),
)
def cleaned_data_from_outliers(check_removed_out, time_name, T_parameters, data_upl):
    
    if check_removed_out:
        df =  pd.DataFrame(data_upl)
        # Set time index
        df.index = pd.to_datetime(df[time_name])
        # del df[time_name]
        # Select variables 
        df_filtered = pd.DataFrame(df.loc[:, T_parameters]).dropna()
        df_outliers = FcAnalysis.detect_outliers(df_filtered,T_parameters, "Z_SCORE")
        df_filtered = df_filtered[~df_filtered.index.isin(df_outliers.index)]
        return df_filtered.reset_index().to_dict('records')
    else:
        return data_upl


# ========================================================================
#           GRAPH: visualize series and possibile OUTLIERS
# ========================================================================
@callback(
    Output("charts_prtocessing_div","children"),
    Input("processing_parameter_temperature","value"),
    Input("processing_parameter_energy","value"),
    Input("time_index_name","value"),
    Input("uploaded_data","data"),
    Input("check_visualize_outliers","checked"),
    prevent_initial_call=True
)
def plot_variables(T_parameters,E_parameters, time_name, data_upl, check_visualize_outliers):
    '''
    Plot selected parameters
    '''
    
    if data_upl:
        df =  pd.DataFrame(data_upl)
        # Set time index
        df.index = pd.to_datetime(df[time_name])
        # Select variables 
        params = [T_parameters] + [E_parameters]
        df_filtered = df.loc[:, params].dropna(axis=1, how='all') # drop columns with all NA values
        # DA INSERIRE: Se nel nome della variabile c'è temperatura mettere temperature oppure power
        if df_filtered.empty:
            return ""
        else:
            # ====================================
            #           VISUALIZE OUTLIERS
            # ====================================

            if check_visualize_outliers:
                df_outliers = FcAnalysis.detect_outliers(df_filtered,T_parameters, "Z_SCORE")
                # Aggiungere una colonna 'New_Column' a df1 con NaN
                df_filtered['Outliers'] = np.nan
                # Popolare la colonna 'New_Column' di df1 con i valori da 'Power' di df2
                df_filtered['Outliers'] = df_filtered.index.map(df_outliers[T_parameters])
                # plot only data of parameter and outliers
                df_plot_ = df_filtered.loc[:,[T_parameters,'Outliers']]
                return dash_echarts.DashECharts(  
                    id="processing_plot_outliers",             
                    style={
                    "width": '100%',
                    "height": '400px',
                    },
                    option = FcPlot.line_chart_with_effect(df_plot_, "Temperature")
                )
            else:
                return  dash_echarts.DashECharts(  
                            id="processing_plot",             
                            style={
                            "width": '100%',
                            "height": '400px',
                            },
                            option = FcPlot.generate_graph(df_filtered, "Temperature","", -100)
                        )
    return dash_echarts.DashECharts(               
            style={
            "width": '100%',
            "height": '400px',
            },
            option = FcPlot.option_white
        )

# ========================================================================
#           CHART: Visaulize cleaned data
# ========================================================================
@callback(
    Output("chart_removed_ouliers","children"),
    Output("elements_removing_outliers","style"),
    Output("sensor_field_new","display"),
    Output("btn_post_data_in_TS_DB","display"),
    Output("text_update_graph","display"),
    Output("response_uploading","style"),
    Input("check_remove_outliers","checked"),
    Input("cleaned_data", "data"),
)
def vvisualize_cleaned_data(check_remove, data_cleaned):
    '''
    Visualize cleaned data
    '''
    style_block = {'display':'block'}
    style_none = {'display':'none'}
    if check_remove:
        df = pd.DataFrame(data_cleaned)
        df.index = pd.to_datetime(df.index)

        chart = dash_echarts.DashECharts(  
            option = FcPlot.generate_graph(df, "Temperature","", -100),
            style = {
                "width": '100%',
                "height": '400px',
            }
        ),
        
        return chart, style_block, 'block', 'block', 'block', style_block
    return "", style_none , 'none','none', 'none', style_none 

# ========================================================================
#           GEnrate uuid and save sensor-data in the database
# ========================================================================

@callback(
    Output("text_input_uuid", "value"),
    Input("btn_generate_uuid", "n_clicks"),
    prevent_intial_call = True
)
def generate_uuid(btn):
    # Generate a random UUID
    if ctx.triggered_id == "btn_generate_uuid":
        random_uuid = uuid.uuid4()
        return str(random_uuid)
    return ""

def is_valid_uuid(name_sensor):
    try:
        # Try to create a UUID from the string
        uuid_obj = uuid.UUID(name_sensor, version=4)  # You can change the version as needed
        # If successful, return True
        return True
    except ValueError:
        # If a ValueError is raised, it means the input is not a valid UUID
        return False

# Create a csv file
@callback(
    Output("response_uploading","children"),
    Input("cleaned_data","data"),
    Input("text_input_uuid","value"),
    Input("btn_post_data_in_TS_DB","n_clicks"),
)
def post_data_to_database(data, name_sensor, btn):
    
    if btn is None or data is None:
        return ""
    else:
        if is_valid_uuid(name_sensor):
            sens_name = name_sensor
        else:
            sens_name = str(uuid.uuid4())
        # Load the DataFrame
        df = pd.DataFrame(data)
        # Inser column sensor_id
        file_name = sens_name
        df.insert(loc=1, column="sensor_id", value=file_name)
        #
        df.columns = ['time','sensor_id','value']

        # Ensure columns are as required
        required_columns = ["time", "sensor_id", "value"]
        if not all(col in df.columns for col in required_columns):
            return "The data is missing required columns: time, sensor_id, value."
        
        # Folder where CSVs will be saved
        output_folder = "./data/csv_output"
        os.makedirs(output_folder, exist_ok=True)
        
        # Save the CSV
        file_name_csv = file_name + ".csv"
        file_path = os.path.join(output_folder, file_name_csv)
        df.to_csv(file_path, index=False, sep=",", decimal=".")
        os.getcwd()

        # POST IN THE DATABASE
        # ======================
        csv_path = os.getcwd()+f"/data/csv_output/{file_name_csv}"
        response_uploaded = FcAnalysis.post_data(csv_path, file_name )
        # ======================
        result = dmc.Notification(
            title="Process Ended",
            message=f"After checkig the sensor name is: {sens_name}. {response_uploaded} and the metadata has updating..",
            loading=False,
            color="update",
            action="show",
            autoClose=2000,
            icon=DashIconify(icon="icon-park:check-one"),
        )
        return result






# ========================================================================
#           BRICK SHCEMA GRAPH: visualize ttl
# ========================================================================

#                       List of available buildings
# ======================================================================
@callback(
    Output("bui_ttl_file","data"),
    Output("bui_ttl_file","value"),
    Output("buis_update_metadata","data"),
    Output("buis_update_metadata","value"),
    Input("url_app", "href"),
    Input("btn_post_data_in_TS_DB",'n_clicks')
)
def get_list_of_buildings(href, btn):
    buis = FcAPI.get_building_list()['Buis'].tolist()
    buis_selected = buis[0]
    if ctx.triggered_id == "btn_post_data_in_TS_DB":
        buis = FcAPI.get_building_list()['Buis'].tolist()
        buis_selected = buis[0]
    
    return buis, buis_selected, buis, buis_selected

#                       List of components
# ======================================================================
@callback(
    Output("element_brick_highlight","data"),
    Output("element_brick_highlight","value"),
    Input("bui_ttl_file","value"),
    prevent_initial_call=True
)
def get_element_from_bui(bui):
    '''
    Get element from bui
    '''
    data = [
        {
            "group": "Building",
            "items": [{"value": item, "label": item.replace('_', ' ')} for item in FcAPI.get_elements_from_ttl(bui,"Building")]
        },
        {
            "group": "Zone",
            "items": [{"value": item, "label": item.replace('_', ' ')} for item in FcAPI.get_elements_from_ttl(bui,"Zone")]
        },
        {
            "group": "Meter",
            "items": [{"value": item, "label": item.replace('_', ' ')} for item in FcAPI.get_elements_from_ttl(bui,"Meter")]
        },
        {
            "group": "Zone_Air_Temperature_Sensor",
            "items": [{"value": item, "label": item.replace('_', ' ')} for item in FcAPI.get_elements_from_ttl(bui,"Zone_Air_Temperature_Sensor")]
        },
        {
            "group": "Outside_Air_Temperature_Sensor",
            "items": [{"value": item, "label": item.replace('_', ' ')} for item in FcAPI.get_elements_from_ttl(bui,"Outside_Air_Temperature_Sensor")]
        },
    ]
    
    value_selected = data[0]['items'][0]['value']
    return data, value_selected


# ======================================================================
# Helper function to remove URIRef prefix
def simplify_uri(uri):
    return uri.split('#')[-1] if isinstance(uri, URIRef) else str(uri)

ttl_file = '/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/00_GitHubProject/dashboard_analytics/frontend/dash_app/data/ttl_files/bui_BCFS.ttl'
def get_nodes_and_edges(ttl_file):
    
    # GET TTL FILE OF BUILDING
    g = Graph()
    g.parse(ttl_file, format='turtle')

    # Extract nodes and edges
    nodes = set()
    edges = []
    for s, p, o in g:
        nodes.add(simplify_uri(s))
        nodes.add(simplify_uri(o))
        edges.append({'data': {'source': simplify_uri(s), 'target': simplify_uri(o), 'label': simplify_uri(p)}})

    # Prepare Cytoscape elements
    cyto_nodes = [{'data': {'id': node, 'label': node}} for node in nodes]
    cyto_edges = edges
    # labels = [item['data']['label'] for item in data]
    # Combine nodes and edges
    elements = cyto_nodes + cyto_edges
    labels = [item['data']['label'] for item in cyto_nodes]
    return elements, labels

#           eneable/disable node to be highlighted
# ========================================================================
@callback(
    Output("element_brick_highlight","disabled"),
    Input("check_highlight_ele_brick","checked"),
)
def enabl_disable(check_h):
    '''
    '''
    if check_h:
        return False
    return True


#           Visualize graphs brick
# ========================================================================
@callback(
    Output("graph_brick_","children"),
    Input("btn_visualize_brick","n_clicks"),
    Input("bui_ttl_file","value"),
    Input("check_highlight_ele_brick","checked"),
    Input("element_brick_highlight","value"),
)
def visualize_ttl_file(btn, bui_name, check_highl,elemnt_highl):

    styles = [
        {'selector': 'node', 'style': {'label': 'data(label)', 'background-color': 'lightblue', 'color': 'black','fontSize':'10px'}},
        {
            'selector': 'edge',
            'style': {
                'label': 'data(label)',
                'width': 1,
                'line-color': '#7FDBFF',
                'target-arrow-color': '#7FDBFF',
                'target-arrow-shape': 'triangle',
                'fontSize':'7px'
            }
        }
    ]
    
    if ctx.triggered_id == "btn_visualize_brick":

        if check_highl:
            styles.append({'selector': f'[label = "{elemnt_highl}"]', 'style': {'background-color': 'red', 'color': 'black'}})

        elements_label =FcAPI.get_elements_and_labels(bui_name)
        chart = dmc.Center(
            cyto.Cytoscape(
                id='cytoscape_brick',
                stylesheet=styles,
                elements=elements_label['elements'],
                style={'width': '100%', 'height': '600px','paddingLeft':'10px'},
                layout={'name': 'cose'},  # Use a force-directed layout
            )
        )
        return chart
    else:
        raise PreventUpdate 
        
#           Update brick using brickllm
# ========================================================================
@callback(
    Output("output_brickllm","children"),
    Input("btn_post_data_in_TS_DB","n_clicks"),
    State("text_update_graph","value"),
    State("buis_update_metadata","value"),
    State("open_ai_api_key","value"),
    prevent_initial_call=True
)
def update_ttl_file(btn, textInput, bui_name, api_KEY):
    
    if ctx.triggered_id == "btn_post_data_in_TS_DB":
        # File path to the .ttl file
        
        # Get ttl file description of the building selected 
        bui_ding_ttl = FcAPI.get_ttl_fil_from_bui_name(bui_name)
    
        # text variable written by user
        # existing_text = "Da questo brick schema cambiare il valore dell'UUID della Zone_Air_Temperature_Sensor_1 con il seguente uuid '1f4a4fba-351a-400e-8831-b3af425f0c25'"
        existing_text = textInput
        try:
            existing_text += bui_ding_ttl
                # Read the .ttl file and append its content
        except FileNotFoundError:
            print(f"The file of {bui_name} is not available")
        except Exception as e:
            print(f"An error occurred: {e}")

        # Output the combined content if needed
        print(existing_text)
        #
        # Generate teh new ttl file using brickllm
        path_save_file = os.getcwd()+f"/data/ttl_files/{bui_name}.ttl"
        if api_KEY:
            generate_brick_ttl(existing_text, path_save_file, api_KEY)
            return dmc.Notification(
                title="Process Ended",
                message=f"provided an api key of openAI to update the schema",
                loading=False,
                color="update",
                action="show",
                autoClose=2000,
                icon=DashIconify(icon="line-md:check-list-3-twotone"),
            )

        # Upload file in the building structure of ttl 
        FcAPI.upload_file(path_save_file)

        return dmc.Notification(
            title="Process Ended",
            message=f"the brick schema of {bui_name} is updated!",
            loading=False,
            color="update",
            action="show",
            autoClose=2000,
            icon=DashIconify(icon="line-md:check-list-3-twotone"),
        )
    return ""