import dash
from dash import html, dcc
import dash_leaflet as dl
import  dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_echarts
import dash_ag_grid as dag
# from dash_mantine_react_table import DashMantineReactTable

from utils.functions_general import bui_feature_compare, make_card,card_navbar
import utils.functions_general as FcGeneral
import utils.functions_plot as FcPlot
from components.header import Header

from datetime import datetime, timedelta,date
import pandas as pd

dash.register_page(__name__,path_template=f"/benchmarking")


main_ = dmc.Container(
    size="xl",
    children = [
        # TITLE
        dmc.Group(
            children = [
                DashIconify(icon="proicons:branch-compare",color=dmc.DEFAULT_THEME["colors"]["gray"][6],width=72),
                dmc.Stack(
                    children = [
                        dmc.Title("Benchmarking buildings", order=1),
                        dmc.Title("Evalute the energy performance of all buildings", order=3, c="#dee2e6")
                    ],
                    gap=1
                )
            ]
        ),

        dmc.Stack(
            children = [ 
                dmc.Alert(
                    children = [
                        dmc.Group(
                            [
                                dmc.Loader(color="violet", size="md", variant="oval"),
                                dmc.Text("Collecting data from buildings..")
                            ]
                        )
                    ],
                    title="Analysing data!",
                    id="alert_table_data",
                    color="violet",
                    withCloseButton=False
                ),
                dmc.Paper(
                    children = [
                        dmc.Group(
                            children = [
                                dmc.Group(
                                    children = [
                                        dmc.Text("Electricity Price - euro:", fw=500, mt=10, style = {"fontSize":"var(--input-label-size, var(--mantine-font-size-sm))"}),
                                        dmc.NumberInput(
                                            id="price_electricity_bench",
                                            min=0.01,
                                            value=0.2,
                                            step=0.05,
                                            disabled=True,
                                            persistence=True,
                                            persistence_type="session"
                                        ),
                                    ]
                                ),
                                dmc.Button("UPDATE", id="btn_update_table", radius="md", color="violet", disabled=True, variant="light")
                            ],
                            justify="space-between",
                            mt=20,
                            mb=20
                        ),
                        dmc.Skeleton(
                            id = "id_skel_bench_0",
                            radius="md",
                            visible = True,
                            mt=10,
                            mb=10,
                            h = 700,
                            children = html.Div(id="table_buis"),
                        ),  
                    ],
                    p="md",
                    radius="lg",
                    shadow="xl"
                )
            ]
        ),
        # BAR distribution 
        dmc.Paper(
            children = [
                dmc.Title("Compare all buildings", order=2, mb=2, mt=5),
                dmc.Title("Select KPIs and evalute the performance of all buildings", order=3, mb=10, c="lightgrey"),
                dmc.Skeleton(
                    id = "id_skel_bench_1",
                    radius="md",
                    visible = True,
                    mt=10,
                    mb=10,
                    h = 400,
                    children = [
                        dmc.Select(
                            id="parameter_table_for_chart",
                            label = "Parameter",
                            data = [
                                {'value':'overallCons', 'label':'Overall energy consumption'},
                                {'value':'sum_night', 'label':'Closing hours consumption'},
                                {'value':'sum_day', 'label':'Opening hours consumption'},
                                {'value':'night_cost', 'label':'Incidence of night cost %'},
                                {'value':'mean_day', 'label':'Hourly mean consumption during opening hours'},
                                {'value':'mean_night', 'label':'Hourly mean consumption during closing hours'},
                                {'value':'count_day', 'label':'Number of available hours'},
                            ],
                            value = "mean_day",
                            w="40%",
                            mb=10
                        ),
                        dash_echarts.DashECharts(               
                            id="barchart_overallBuilding",
                            style={
                                "width": '100%',
                                "height": '400px',
                            }
                        ),
                    ]
                )
            ],
            radius="lg",
            shadow="lg",
            mt=10,
            p=10
        ),
        dmc.Paper(
            children = [
                dmc.Title("Compare buildings", order=2, mb=2, mt=5),
                dmc.Title("Evalute the performance of 2 buildings", order=3, mb=10, c="lightgrey"),
                dmc.Grid(
                    children = [
                        dmc.GridCol(
                            children = [
                                dmc.Select(
                                    id="building_compare_1",
                                    label="Building 1",
                                    data = ["bui_BCGS"],
                                    value="bui_BCGS",
                                    mt=10
                                ),
                            ],
                            span=6
                        ),
                        dmc.GridCol(
                            children = [
                                dmc.Select(
                                    id="building_compare_2",
                                    label="Building 2",
                                    data = ["bui_BCGS"],
                                    value="bui_BCGS",
                                    mt=10
                                ),
                            ],
                            span=6
                        ),
                    ],
                    justify="space-around",
                    mb=10
                ),
                # ================================================
                # BAR CHART AND TABLE COMPARISON 2 BUILDINGs
                # ================================================
                dcc.Loading(
                    children = html.Div(id="bar_chart_comparison"),
                    overlay_style={"visibility":"visible", "filter": "blur(2px)"},
                    color= "rgb(121, 80, 242)",
                ),
                dmc.Table(
                    id="table_result",
                    striped=True,
                    highlightOnHover=True,
                    withTableBorder=True,
                    withColumnBorders = True,
                    mt=10,
                    mb=10
                )
               
            ],
            shadow="lg",
            radius="lg",
            mt=10,
            p=10
        ),
        html.Div(id="test_table"),
        
    ],
    style = {'marginTop':'10px'}
)



layout_ = html.Div(
    children = [
        dcc.Store(id="data_table", storage_type="session"),
        dcc.Store(id="time_data_table", storage_type="session", data={'timestamp': None}),
        dcc.Store(id="bui_and_uuid", storage_type="session"),
        dmc.AppShell(
            [
                Header,
                dcc.Loading(
                    children = html.Div(id="loading_data_benchmarking"),  
                    custom_spinner = html.Span(className= "loader_spin_2"),
                    style={'marginTop':'0px', 'marginBottom':'10px'},
                ),
                dmc.AppShellMain(children=[
                        main_
                    ],
                ),
            ],
            header={"height": 60},
        )
    ],
    style = {'marginBottom':'20px'}
)


def layout():
    return layout_