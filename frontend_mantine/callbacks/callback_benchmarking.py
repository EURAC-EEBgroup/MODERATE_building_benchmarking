import pandas as pd
from dash import callback, Input, Output, State, get_relative_path
from dash.exceptions import PreventUpdate
import pandas as pd
import datetime
import numpy as np
import utils.functions_api_data as FcAPI
import dash_mantine_components as dmc
import json
import utils.functions_api_data as FcAPI
from dash_mantine_react_table import DashMantineReactTable
import utils.functions_general as FcGen
from datetime import datetime, timedelta
# Authenticate API time series and retrieve token


# =================================================================
#           List of buildings for comparison 
# =================================================================
@callback(
    Output("building_compare_1","data"),
    Output("building_compare_1","value"),
    Output("building_compare_2","data"),
    Output("building_compare_2","value"),
    Input("url_app", "search")
)
def get_building_list(search):
    buis = FcAPI.get_building_list()['Buis'].tolist()
    options = [{'value': item, 'label': item.split('_')[1]} for item in buis]
    if search:
        # Extract the value after "?" (e.g., "?bui_BCGS" -> "bui_BCGS")
        buis_selected = search.lstrip("?")
    else:
        buis_selected = buis[0]
    
    return options,buis_selected, options,buis_selected




# =======================================================================================
#   TABLE OVERALL 
# =======================================================================================

@callback(
    Output("price_electricity_bench", "disabled"),
    Output("btn_update_table", "disabled"),
    Input("data_table","data"),
)
def enable_disable_button(data):
    df = pd.read_json(data)
    if not df.empty: 
        return False, False
    return True, True




@callback(
    Output("data_table","data"),
    Output("time_data_table","data"),
    Output("loading_data_benchmarking", "children"),
    Input("btn_update_table","n_clicks"),
    State("price_electricity_bench", "value"),
    State("data_table", "data"),
    State("time_data_table","data"),
)
def get_table_consumption_data(n_click, electricity_price, data_last, time_last):
    
    columns_name = [
                "shops",
                "Overall consumption opening hours [kWh/m2]", 
                "Overall consumption closing hours [kWh/m2]",
                "Hourly mean opening hours [kWh/m2]", 
                "Hourly mean closing hours [kWh/m2]",
                "Number of opening hours", 
                "number of closing hours",
                "area building",
                "overall electrictiy cost [euro]",
                "electrictiy cost closing hours [euro]",
                "electrictiy cost opening hours[euro]",
            ]
    current_time = datetime.now()
    last_timestamp = time_last.get('timestamp')
    if last_timestamp:
        # Converti il timestamp salvato in oggetto datetime
        last_timestamp = datetime.fromisoformat(last_timestamp)
        # Controlla se la differenza di tempo è inferiore a 15 minuti
        if current_time - last_timestamp < timedelta(minutes=60):
            return data_last, time_last, ""
            
    
    df = FcAPI.table_overview(time_col_name="time", el_price=electricity_price)
    df.columns = columns_name
    new_date = {'timestamp': current_time.isoformat()}

    # df = pd.read_csv("/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/00_GitHubProject/dashboard_analytics/frontend/dash_app/utils/night_shop_analysis.csv", index_col=0)

    return df.to_json(orient="records"), new_date, ""




def table(df):
    Table_react = DashMantineReactTable(
        data=df.to_dict("records"),
        columns=[{"accessorKey": i, "header": i} for i in df.columns],
        mrtProps={
            "enableHiding": True,
            "enableColumnFilters": True,
            "initialState": {"density": "sm"},
            "mantineTableProps": {"fontSize": "sm"},
            "mantineTableHeadCellProps": {"style": {"fontWeight": 500}},
            "highlightOnHover": True,
            "enableColumnResizing":True,
            "enableSorting":True,
            "enablePinning":True
        }
    )
    return Table_react


@callback(
    Output("id_skel_bench_0", "visible"),   
    Output("table_buis", "children"),   
    Output("alert_table_data", "hide"),
    # Input("loading-overlay", "visible"),  # Input could be any event, such as a button click 
    Input("data_table","data"),
    Input("btn_update_table","n_clicks"),
    prevent_initial_call=True
)
def table_definition(data_, btn):
    '''
    Generate table with energy consumptions
    '''
    # df = pd.read_csv("/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/00_GitHubProject/dashboard_analytics/frontend/dash_app/utils/night_shop_analysis.csv", index_col=0)
    df = pd.read_json(data_)
    return False, table(df), True



# ========================================================================================
#                           BARCHART TABLE
# ========================================================================================
# Function to get the label for a specific value
def get_label(value, data):
    for item in data:
        if item['value'] == value:
            return item['label']
    return None 

@callback(
    Output("id_skel_bench_1", "visible"),
    Output("barchart_overallBuilding", "option"),
    Input("data_table","data"),
    Input("parameter_table_for_chart", "value"),
    Input("parameter_table_for_chart", "data"),
    prevent_initial_call = True
)
def visualize_table_as_chart(data_t, parameter, parameterData):
    '''
    '''
    # df = pd.read_json(data_t)
    df =pd.read_csv("callbacks/night_shop_analysis.csv",  index_col=0)
    # df = pd.read_csv("/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/00_GitHubProject/dashboard_analytics/frontend/dash_app/utils/night_shop_analysis.csv", index_col=0)
    label = get_label(parameter, parameterData)
    # [parameterData['value'] == parameter, 'label']
    if parameter == "overallCons":
        sort_param = "Overall"
    else:
        sort_param = parameter
    
    # label of y axes
    df_y_label = pd.DataFrame(
        {
            "Name": ["overallCons", "sum_night", "sum_day", "night_cost", "mean_day", "mean_night", "day_cost"],
            "Y_label" : ["Energy - kWh/m2", "Energy - kWh/m2", "Energy - kWh/m2", "euro", "Energy - kWh/m2", "Energy - kWh/m2", "n°"]
        }
    ) 

    y_label = df_y_label.loc[df_y_label['Name']==parameter, "Y_label"]

    columns_subset = ["shops","sum_day","sum_night","mean_day","mean_night","count_day", "count_night","overall_cost","night_cost","day_cost"]
    # columns_name_subset = [
    #     "shops",
    #     "Overall consumption opening hours [kWh]", 'sum_day'
    #     "Overall consumption closing hours [kWh]", "sum_night"
    #     "Hourly mean opening hours [kWh]", "mean_day"
    #     "Hourly mean closing hours [kWh]", "count_day"
    #     "Number of opening hours", "c"
    #     "number of closing hours",
    #     "overall electrictiy cost [euro]",
    #     "electrictiy cost closing hours [euro]",
    #     "electrictiy cost opening hours[euro]",
    # ]
    # subset dataset to be used by the table:
    # df_plot.iloc[:, ["Overall consumption opening hours [kWh]"]]
    # Sort values
    df.columns = columns_subset
    df_plot = df.sort_values(by=sort_param, ascending=True).reset_index(drop=True)
    
    # Plot 
    option = {
        "title": {
            "text": label,
            "left": "center"
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"}
        },
        "xAxis": {
            "type": "category",
            "data": df_plot['shops'].tolist(),
            "axisLabel": {"rotate": 45}  # Rotate x-axis labels for better readability
        },
        "yAxis": {
            "type": "value",
            "name": y_label
        },
        "series": [
            {
                "data": df_plot[sort_param].tolist(),
                "type": "bar",
                "itemStyle": {"color": "#6495ED"},  # Light blue color
                "name": "Sum Night"
            }
        ],
        "grid": {
            "bottom": "15%",  # Adjust bottom margin for x-axis labels
            "containLabel": True
        }
    }
    return False, option 



# =================================================================
#           Comaprison of building: Energy Analysis
# =================================================================
''' BUILDING LIST '''
@callback(
    Output("bui_and_uuid", "data"),
    Input("url_app", "href")
)
def list_of_buildings_and_uuids(url):
    '''
    
    '''
    extracted_path =  "/" +FcGen.extract_path(url)
    # Fetch building list if the path matches the root
    if extracted_path == get_relative_path("/benchmarking"):
        building_list = FcAPI.get_building_list()['Buis'].tolist()
        power_meters = []
        external_temperature_uuids = []
        buildings_with_uuid = []

        # Getting UUID
        for building in building_list:
            # Extract UUIDs for energy and temperature meters
            energy_uuid = FcAPI.extract_values_with_keywords(FcAPI.get_meter_label_and_uuid(building))
            temperature_uuid = FcAPI.get_meter_label_and_uuid_weather(building)
            
            if energy_uuid: 
                # Append the building and associated UUIDs to the respective lists
                buildings_with_uuid.append(building)
                external_temperature_uuids.append(temperature_uuid[0]['value'])
                power_meters.append(energy_uuid[0])

        df_uuids = pd.DataFrame(
            {
                'building':buildings_with_uuid,
                'energy_shop_uuid':power_meters,
                'ext_temp':external_temperature_uuids
            }
        )
        return df_uuids.to_json(orient="records")
    raise PreventUpdate



# Preprocess the data to round the float values
def preprocess_data(data, decimals=4):
    for row in data:
        for key, value in row.items():
            if isinstance(value, float):
                row[key] = round(value, decimals)
    return data



# Create the Mantine Table component
def create_table(data):
    columns = [{"Header": key, "accessor": key} for key in data[0].keys()]
    rows = [
        {col["accessor"]: row[col["accessor"]] for col in columns}
        for row in data
    ]
    return [
            dmc.TableThead(dmc.TableTr([dmc.TableTh(col["Header"]) for col in columns])),
            dmc.TableTbody([
                dmc.TableTr([dmc.TableTd(row[col["accessor"]]) for col in columns])
                for row in rows
            ]),
            dmc.TableCaption("Summary of energy performance")
        ]
        

@callback(
    Output("table_result", "children"),
    Output("bar_chart_comparison", "children"),
    # Input("btn_compare_building", "n_clicks"),
    Input("building_compare_1", "value"),
    Input("building_compare_2", "value"),
    Input("bui_and_uuid", "data"),
    prevent_initial_call = True
)
def buis_comparison(bui_1, bui_2, data_bui_uuid):
    '''
    
    '''
    # if ctx.triggered_id == 'btn_compare_building':
    df_uuids = pd.read_json(data_bui_uuid)
    bui_selected = [bui_1,bui_2]
    bui_selected_uuids = df_uuids[df_uuids['building'].isin(bui_selected)]
    building_area = []
    energy_HDD = []
    energy_CDD = []
    number_of_day = []
    bui_with_data = []
    for i,bui in bui_selected_uuids.iterrows():
        id_power = bui['energy_shop_uuid']
        id_ext_temp = bui['ext_temp']

        st_end = FcAPI.get_first_and_last_value(id_ext_temp)

        if st_end.iloc[0,0] != None and st_end.iloc[1,0] != None:
            time_start = st_end['time'][0].split('T')[0]
            time_end = st_end['time'][1].split('T')[0]
            # ================================
            # Get External Temperature    
            # ================================
            df = FcAPI.get_data_from_shops(id_ext_temp, time_start, time_end)
            df.index = pd.to_datetime(df['time'])
            del df['time']
            df_daily = df.resample('D').mean()
            df_daily = df_daily.reset_index()
            # Rename columns
            df_daily.columns = ['time','temperature']
            # Calculate HDD
            df_DD = FcAPI.calculate_degree_days(df_daily)


            # ================================
            # Get Power data    
            # ================================
            df_power = FcAPI.get_data_from_shops(id_power, time_start, time_end)
            if not df_power.empty: 
                df_power.columns = ['time','power']
                df_power.index = pd.to_datetime(df_power['time'])
                # From power to energy
                df_power['energy'] = df_power['power']/4
                # from ENergy overall to energy to m2
                building_area = FcAPI.extract_numeric_value(FcAPI.get_area_from_bui(bui['building']))
                df_power['energy'] = df_power['energy']/building_area
                del df_power['time']
                del df_power['power']
                df_power_daily = df_power.resample('D').sum()

                # ================================
                # MERGE data
                # ================================
                df_power_daily = df_power_daily.reset_index()
                df_DD = FcAPI.safe_merge(df_DD, df_power_daily, 'time', how='inner')
                df_DD = df_DD.dropna().reset_index(drop=True)
                # df_DD['energy'] = round(df_power_daily['energy'],2).values.tolist()
                
                
                # ================================
                # OVERALL VALUES
                # ================================
                energy_HDD_bui = np.NaN
                if sum(df_DD['HDD']) !=0:
                    energy_HDD_bui = sum(df_DD['energy'])/sum(df_DD['HDD'])
                    note_HDD = "no HDD"
                energy_HDD.append(energy_HDD_bui)
                
                energy_CDD_bui = np.NaN
                if sum(df_DD['CDD']) !=0:
                    energy_CDD_bui = sum(df_DD['energy'])/sum(df_DD['CDD'])
                    note_CDD = "no CDD"
                energy_CDD.append(energy_CDD_bui)
                
                number_of_day.append(len(df_DD))

                bui_with_data.append(bui['building'])


    df_result =pd.DataFrame(
        {
            'Building Name':bui_with_data,
            'number of available_days': number_of_day,
            'Energy Normalized in Winter' : energy_HDD,
            'Energy Normalized in Summer' : energy_CDD
        }
    ).to_json(orient="records")
    print(df_result)
    # Preprocess the data
    processed_data = preprocess_data(json.loads(df_result))

    # =============================
    # DATA FOR BAR CHART
    # =============================
    bar_chart = dmc.BarChart(
        h=400,
        dataKey="Building Name",
        data=json.loads(df_result),
        series=[
            {"name": "Energy Normalized in Winter", "color": "violet.6"},
            {"name": "Energy Normalized in Summer", "color": "blue.6"}
        ],
        xAxisLabel="Building",
        highlightHover=True,
        withLegend=True,
        yAxisLabel="Energy [kWh/DD]",
        mt=20,
        mb=10
    )
    
    return create_table(processed_data),  bar_chart


# @callback(
#     Output("energy_table_day_night", "rowData"),
#     Output("energy_table_day_night", "columnDefs"),
#     Input("url_app", "href")
# )
# def table_definition(href_):
#     '''
#     Generta etable with consumptions
#     '''
#     df = pd.read_csv("/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/00_GitHubProject/dashboard_analytics/frontend/dash_app/utils/night_shop_analysis.csv", index_col=0)
#     rowData_ = df.to_dict('records')
#     columnDefs_ = [
#         {"headerName": "Shop", "field": "shops", "sortable": True, "pinned":"left"},
#         {
#             'headerName': 'Energy consumption - Overall [kWh]',
#             'children': [
#                 {'field': 'sum_day', 'headerName': 'from 7:00 to 20:00'},
#                 {'field': 'sum_night', 'headerName': "from 20:01 to 6:59"},
#             ]
#         },
#         {
#             'headerName': 'Energy consumption - Mean [kWh]',
#             'children': [
#                 {'field': 'mean_day', 'headerName': "from 7:00 to 20:00"},
#                 {'field': 'mean_night', 'headerName': "from 20:01 to 6:59"},
#             ]
#         },
#         {
#             'headerName': 'Energy - Number of Hours',
#             'children': [
#                 {'field': 'count_day', 'headerName': "from 7:00 to 20:00"},
#                 {'field': 'count_night', 'headerName': "from 20:01 to 6:59"},
#             ]
#         },
#         {
#             'headerName': 'Overall cost', 'field':'overall_cost',
#          },
#         {'headerName': 'Night cost', 'field':'night_cost'},
#         {'headerName': 'Night cost impact', 'field':'cost night %',
#          'cellStyle': {
#                 "styleConditions": [
#                     {
#                         "condition": "params.value = 0 ",
#                         "style": {"backgroundColor": "#ffcbd1"},
#                     },
#                     {
#                         "condition": "0 < params.value && params.value <= 10",
#                         "style": {"backgroundColor": "#f69697"},
#                     },
#                      {
#                         "condition": "10 < params.value && params.value <= 20",
#                         "style": {"backgroundColor": "#ee6b6e"},
#                     },
#                     {
#                         "condition": "params.value > 20",
#                         "style": {"backgroundColor": "#de0a26"},
#                     }
                    
#                 ],
#                 # "function": "params.value && {'backgroundColor': 'rgb(255,0,0,' + params.value/15 + ')'}"
#             },
#             'pinned':'left'
#          },
#     ]

   









