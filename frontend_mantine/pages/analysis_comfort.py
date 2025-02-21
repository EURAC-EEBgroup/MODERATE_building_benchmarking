import dash
from dash import html, dcc
import dash_leaflet as dl
import  dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_echarts
import utils.functions_general as FcGen
from components.header import Header


dash.register_page(__name__,path_template=f"/comfort")

# ====================================================
#                   SIDEBAR
# ====================================================


sidebar = [
    dmc.Select(
        id="single_bui",
        label="Name",
        clearable=False,
        searchable=True,
        persistence = True,
        persistence_type = "session",
        allowDeselect = False,
        mt=10
    ),
    dmc.Select(
        id="comf_parameters_analysis",
        label="Indoor Sensors",
        placeholder="Select parameter",
        clearable=False,
        searchable=True,
        persistence = True,
        persistence_type = "session",
        allowDeselect = False,
        mt=10
    ),
    dmc.Select(
        id="outdoor_parameters",
        label="Outdoor Temperature",
        placeholder="Select parameter",
        clearable=False,
        searchable=True,
        persistence = True,
        persistence_type = "session",
        allowDeselect = False,
        mt=10
    ),
]


# ====================================================
#                   COMFORT TAB
# ====================================================
comfort_tab = dmc.Paper(
    children = [
        # ========================================
        #               INFO
        # ========================================
        dmc.Skeleton(
            id="id_skel_info_comfort",
            visible = True, 
            h=400,
            radius="md",
            mb=10,
            children =[
                dmc.Grid(
                    children = [
                        dmc.GridCol(
                            children = [
                                FcGen.card_summary_value_period("text_card_comfort_1", "Coldest Temperature","id_cw_shop","", "cold_t_winter"),
                                FcGen.card_summary_value_period("text_card_comfort_2", "Hottest Temperature","id_tw_shops","", "hot_t_winter"),
                                FcGen.card_summary_value_period("text_card_comfort_3", "Average Temperature","id_ts_shops","","hot_t_summer"),
                                FcGen.card_summary_value_period("text_card_comfort_4", "Median Temperature","id_cs_shops","","cold_t_summer")
                            ], 
                            span=5,
                            
                        ),
                        dmc.GridCol(
                            dl.Map(
                                id="map_comfort",
                                # children =[dl.TileLayer()],
                                style={'width': '100%', "height": '95%', 'zIndex':'0','borderRadius':'20px', 'marginTop':'20px'},
                                center=[41.90586515496108, 12.487919956158356],  # Center the map initially
                                zoom=5,
                                maxZoom=7,
                                minZoom=5,      
                            ),
                            # html.Div(id="map_comfort", children = [d]
                            span=7
                        )  
                    ],
                    mb=10
                ),
            ]
        ),
        
        # =======================================
        #           TEMPERATURE PROFILE
        # =======================================
        dmc.Paper(
            children = [
                dmc.Title("Temperature profile", order=3, mb=10, mt=10),
                dmc.Skeleton(
                    id="id_skel_temp_profile",
                    visible=True,
                    radius="md",
                    mb=10,
                    h=600,
                    children = [
                        dash_echarts.DashECharts(
                            id="shops_timeseries_p",
                            style={
                            "width": '100%',
                            "height": '500px',
                            }
                        ),
                        dmc.Group(
                            children = [
                                dmc.Group(
                                    [
                                        FcGen.resample_data("id_btn_T_15min","15 min","violet"),
                                        FcGen.resample_data("id_btn_T_H","H","violet"),
                                        FcGen.resample_data("id_btn_T_6H","6H","violet"),
                                        FcGen.resample_data("id_btn_T_12H","12H","violet"),
                                        FcGen.resample_data("id_btn_T_Day","Day","violet"),
                                        FcGen.resample_data("id_btn_T_Week","Week","violet"),
                                        FcGen.resample_data("id_btn_T_Month","Month","violet"),
                                    ],
                                )
                            ],
                            justify="flex-start",
                            mt=10
                        )
                    ]
                ),                
            ],
            shadow="md",
            radius="md",
            p=20, mt=10, mb=10
        ),
        # =====================================
        #           HEAT MAP
        # =====================================
        dmc.Paper(
            children = [
                dmc.Title("Yearly temperature profile", order=3, mb=10, mt=10),
                dmc.Skeleton(
                    id="id_skel_heat_map_comfort",
                    visible=True,
                    radius="md",
                    mb=10,
                    h=500,
                    children = [
                        dash_echarts.DashECharts(
                            id="heat_chart",
                            style={
                            "width": '100%',
                            "height": '500px',
                            }
                        )
                    ]
                ),      
            ],
            shadow="md",
            radius="md",
            p=20, mt=10, mb=10
        ),
        # ======================================
        #           OVERHEATING/OVERCCOLING
        # ======================================
        dmc.Paper(
            children = [
                dmc.SimpleGrid(
                    mt=10,
                    cols = 2,
                    spacing="md",
                    verticalSpacing="md",
                    children = [
                        dmc.Paper(
                            children = [
                                dmc.Carousel(
                                    [
                                        dmc.CarouselSlide(
                                            id="carousel_overheating",
                                        ),
                                        dmc.CarouselSlide(
                                            id="carousel_overheating_month",
                                        ),
                                    ],
                                    draggable=True,
                                    withIndicators = True,
                                ),
                            ],
                            radius="xl",
                            shadow="md",
                            p="md",
                            mt=20,mb=20
                        ),
                        dmc.Paper(
                            children = [
                                dmc.Carousel(
                                    [
                                        dmc.CarouselSlide(
                                            id="carousel_overcooling",
                                        ),
                                        dmc.CarouselSlide(
                                            id="carousel_overcooling_month",
                                        ),
                                    ],
                                    draggable=True,
                                    withIndicators = True,
                                ),
                            ],
                            radius="xl",
                            shadow="md",
                            p="md",
                            mt=20,mb=20
                        )
                    ]
                ),
            ],
            shadow="md",
            radius="md",
            p=20, mt=10, mb=10
        ),
        # ================================================================================
        #               INDOOR TEMPERATURE VS OUTDOOR TEMPERATURE
        # ================================================================================
        dmc.Paper(
            children = [
                dmc.Text("Indoor Temperature vs Outdoor Temperature",opacity=0.7, fw=700, c="black"),
                dmc.Title("Regression", order=3, fw=700, c="black"),
                
                dmc.Grid(
                    children = [
                        dmc.GridCol(
                            children = [
                                dmc.Select(
                                    label="Parameter - y",
                                    placeholder="Parameter in the y axes",
                                    id="parameter_hist_temp_y",
                                    mt=5,
                                    allowDeselect=False,
                                ),
                            ],
                            span=6
                        ),
                        dmc.GridCol(
                            children = [
                                dmc.Select(
                                    label="Parameter - x",
                                    placeholder="Parameter in the x axes",
                                    id="parameter_hist_temp_x",
                                    mt=5,
                                    allowDeselect=False,
                                ),
                            ],
                            span=6
                        )
                    ]
                ),
                # ================================================================================
                #               REGRESSION: Indoor Temperature vs Outdoor temperature
                # ================================================================================
                dmc.Skeleton(
                    id="id_skel_regression_comfort",
                    radius="md",
                    mt=10,
                    mb=10,
                    visible=True,
                    h = 500,
                    children = [
                        dcc.Store(id="data_regression"),
                        html.Div(id="shops_scatter_hist"),
                        dmc.Group(
                            [
                                FcGen.resample_data("id_btn_T_15min_reg","15 min","violet"),
                                FcGen.resample_data("id_btn_T_H_reg","H","violet"),
                                FcGen.resample_data("id_btn_T_6H_reg","6H","violet"),
                                FcGen.resample_data("id_btn_T_12H_reg","12H","violet"),
                                FcGen.resample_data("id_btn_T_Day_reg","Day","violet"),
                                FcGen.resample_data("id_btn_T_Week_reg","Week","violet"),
                                FcGen.resample_data("id_btn_T_Month_reg","Month","violet"),
                            ],
                            justify = 'flex-start',
                            mt=10
                        ),
                    ],
                ),
                dmc.Grid(
                    children = [
                        dmc.GridCol(
                            children = [
                                dmc.Select(
                                id="regressionType_T",
                                label = "Regression type",
                                data = ['linear','polynomial','exponential', 'logarithmic'],
                                value= "linear"
                                )
                            ],
                            span=6
                        ),
                        dmc.GridCol(
                            children = [
                                dmc.NumberInput(
                                    id="modelOrder_T",
                                    label="Model Order",
                                    value=1,
                                    min=0,
                                    step=1,
                                    disabled=False
                                ),
                            ],
                            span=6
                        ),
                    ],
                    mt=10
                ),
                html.Div(id= "Table_regression_stats"),
                
            ],
            radius="md",
            shadow="md",
            p="md",
            mt=20,mb=20
        )
    ],
    radius="md",
    shadow="md",
    p="md"
)


# ====================================================
#                   MAIN
# ====================================================

alerts = dmc.Center([
    dmc.Alert(
        id="missing_indoor_temperature",
        title = "Missing data",
        children = "No indoor temperature sensor available",
        hide = True, 
        radius="md",
        color = "red",
        variant="filled",
        style = {"width": "50%"}
    ),
    dmc.Alert(
        id="missing_data_of_indoor_t",
        title = "Missing data",
        # children = "No indoor temperature available",
        hide = True, 
        radius="md",
        color = "red",
        mt=10,
        variant="filled",
        style = {"width": "50%"}

    ),
])

main_ = dmc.Container(
    size="xl",
    children = [
        # TITLE
        dmc.Group(
            children = [
                DashIconify(icon="hugeicons:soil-temperature-field",color=dmc.DEFAULT_THEME["colors"]["gray"][6],width=72),
                dmc.Stack(
                    children = [
                        dmc.Title("Comfort", order=1),
                        dmc.Title("Evalute the thermal comfort in the building", order=3, c="#dee2e6")
                    ],
                    gap=1
                )
            ]
        ),
        # SIDEBAR
        dmc.Grid(
            children = [
                dmc.GridCol(
                    children = [
                        dmc.Fieldset(
                            children = sidebar,
                            legend = dmc.Text("Building", fw=500, style = {'fontSize':'18px'}),
                            mt=10,
                            radius="md"
                        )
                    ],
                    span=4
                ),
                dmc.GridCol(
                    children = [
                        comfort_tab
                    ],
                    span=8
                ),
            ]
        )
    ]
)



layout_ = html.Div(
    children = [
        dcc.Store(id="data_stores"), 
        dmc.AppShell(
            [
                Header,
                dcc.Loading(
                    children = html.Div(id="loading_data"),  
                    custom_spinner = html.Span(className= "loader_spin_2"),
                    style={'marginTop':'0px', 'marginBottom':'10px'},
                    overlay_style={"visibility":"visible", "filter": "blur(2px)"},
                ),
                alerts,
                dmc.AppShellMain(
                    children=[      
                        main_
                    ]
                ),
            ],
            header={"height": 60},
            # padding="xl",    
        )
    ],
    style = {'marginBottom':'20px'}
)

def layout():
    return layout_