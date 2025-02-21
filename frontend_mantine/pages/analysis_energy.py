import dash
from dash import html, dcc
import  dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_echarts

from utils.functions_general import bui_feature_compare, make_card,card_navbar
import utils.functions_general as FcGen
from components.header import Header

dash.register_page(__name__,path_template=f"/energy")


data_k = [["kWh", "kWh"], ["kWh_m2", "kWh/m2"]]

sidebar = [
    dmc.Select(
        id="single_bui_energy",
        label="Shops",
        placeholder="Select locations",
        clearable=False,
        searchable=True,
        persistence = True,
        persistence_type = "session",
        allowDeselect = False,
        mt=10
    ),
    dmc.Select(
        id="energy_parameters_analysis",
        label="Energy parameters",
        placeholder="Select parameter",
        clearable=False,
        searchable=True,
        persistence = True,
        persistence_type = "session",
        allowDeselect = False,
        mt=10
    ),
    dmc.Select(
        id="outdoor_parameters_energy",
        label="Weather Parameters",
        placeholder="Select parameter",
        clearable=False,
        searchable=True,
        persistence = True,
        persistence_type = "session",
        allowDeselect = False,
        mt=10
    ),
    dmc.Fieldset(
        children = [
            dmc.Select(
                id="month_heat_map_energy",
                label="Month",
                allowDeselect = False,
                mt=10
            ),
            dmc.Select(
                id="year_heat_map_energy",
                label="year",
                allowDeselect = False,
                mt=10
            ),
        ],
        legend = dmc.Text("Energy profile - carpet plot", fw=300, style = {'fontSize':'14px', "color":"rgb(121, 80, 242)"}),
        mt=10,
        radius="md"
    ),
]



graphs_E_T = html.Div(
    children = [
        dmc.Skeleton(
            id="id_skel_energy_timeline",
            radius="md",
            mt=10,
            mb=10,
            visible=True,
            children = [
                dash_echarts.DashECharts(               
                    id="energy_timeline",
                    style={
                    "width": '100%',
                    "height": '400px',
                    }
                ),       
            ]
        ),
        dmc.Group(
            children = [
                dmc.Group(
                    [
                        FcGen.resample_data("id_btn_15min","15 min","violet"),
                        FcGen.resample_data("id_btn_H","H","violet"),
                        FcGen.resample_data("id_btn_6H","6H","violet"),
                        FcGen.resample_data("id_btn_12H","12H","violet"),
                        FcGen.resample_data("id_btn_Day","Day","violet"),
                        FcGen.resample_data("id_btn_Week","Week","violet"),
                        FcGen.resample_data("id_btn_Month","Month","violet"),
                    ]
                ),
                dmc.Group(
                    [
                        dmc.RadioGroup(
                            children=dmc.Group([dmc.Radio(l, value=k) for k, l in data_k], my=10),
                            id="energy_kwh",
                            value="kWh",
                            size="sm",
                            mb=10,
                        ),
                    ]
                )
            ],
            justify="space-between",
            mt=10
        )
    ]
)


# =============================================================================
#                   MAIN GRAPHS ENERGY
# =============================================================================

data__ = [
{"month": "January", "Energy": 1200, "Temp": 900, "Temp_": 200},
{"month": "February", "Energy": 1900, "Temp": 1200, "Temp_": 400},
{"month": "March", "Energy": 400, "Temp": 1000, "Temp_": 200},
]


energy_tab = dmc.Paper(
    children = [
        # BAR CHART OMONTHLY CONSUMPTION
        html.Div(id="hdd"),
        dmc.Group(
            children = [
                dmc.Stack(
                    children = [
                        dmc.Title("Energy", order=2),
                        dmc.Title(id="subtle_energy_cost", order=6, c="grey"),
                    ],
                    gap="2px",
                    mb=10,
                    mt=10
                ),
                dmc.Flex(
                    children = [
                        dmc.Menu(
                            [
                                dmc.MenuTarget(
                                    dmc.ActionIcon(
                                        DashIconify(icon="clarity:settings-line", color="rgb(121, 80, 242)", width=25),
                                        size="lg",
                                        variant="subtle",
                                        id="action-icon",
                                        color="rgb(206, 212, 218)",
                                        mb=0,
                                        radius="md"
                                    ),
                                ),
                                dmc.MenuDropdown(
                                    [
                                        dmc.NumberInput(
                                            id="electricity_price",
                                            label="Electricity price", 
                                            description  ="average price for 1kWh", 
                                            rightSection=DashIconify(icon="solar:euro-broken"),
                                            value=0.15
                                            ),

                                    ],
                                    p=10
                                ),
                            ]
                        ),
                    ],
                    justify = "flex-end"
                ),
            ],
            justify="space-between",
        ),
        dmc.Skeleton(
            id="skeleton_energy_cost",
            visible=True,
            height=300,
            pb=10,
            radius="md",
            mb=10,
            children = [
                dmc.BarChart(
                    id="bar_chart_price_energy",
                    h=300,
                    dataKey="month",
                    maxBarWidth = 10,
                    gridAxis = None, 
                    data=data__,
                    textColor = "rgb(121, 80, 242)",
                    orientation="horizontal",
                    yAxisProps={"color": "rgb(121, 80, 242)"},
                    xAxisProps={"color":"rgb(121, 80, 242)","width": 40},
                    barProps={"radius": 50, "color":"rgb(121, 80, 242)"},
                    mt=20,
                    mb=10,
                    series= [{"name": "Energy", "color": "rgb(121, 80, 242)"}],
                    style = {
                        "border-radius":"20px", "padding":"10px"
                    }
                ),
            ]
        ),
        # CARD ENERGY        
        dmc.Grid(
            children = [
                dmc.GridCol(FcGen.card_energy_carousel("id_skel_overall","kwh_overall", "kwh_overall_m2", "Overall","kWh", "kWh/m2"), span=4),
                dmc.GridCol(FcGen.card_energy_carousel("id_skel_daily","daily_kwh", "daily_kwh_m2","Daily", "kWh", "kWh/m2"), span=4),
                dmc.GridCol(FcGen.card_energy_carousel("id_skel_normalized","kwh_m2_DD_overall", "kwh_m2_DD_overall_day","Normalized  by Degree Days", "kWh/m2*HDD", "kWh/m2*CDD"), span=4),
            ]
        ),
        # GRAPHS
        # =================================================================
        # GENERAL
        # =================================================================
        dmc.Paper(
            children = [
                dmc.Title("Energy consumption and Outdoor temperature", order=3, mb=10, mt=10),
                graphs_E_T,
            ],
            radius="lg",
            shadow="lg",
            p=20,mt=10,mb=10
        ),
        # =================================================================
        # HEAT MAP - ENERGY
        # =================================================================
        dmc.Paper(
            children = [
                dmc.Title(id="title_heat_map_energy", order=3, mb=10, mt=10),
                dmc.Skeleton(
                    id="id_skel_heat_map",
                    visible=True,
                    radius="md",
                    h=400,
                    mb=10,
                    children = [
                        dash_echarts.DashECharts(               
                            id="energy_heat_map",
                            style={
                            "width": '100%',
                            "height": '400px',
                            }
                        )
                    ]
                ),
            ],
            radius="lg",
            shadow="lg",
            p=20,mt=10,mb=10
        ),
        # =================================================================
        # TYPICAL DAY
        # =================================================================
        dmc.Paper(
            children = [
                dmc.Title("Typical workday, weekend and holiday", order=3, mb=10, mt=10),
                dmc.Skeleton(
                    id = "id_skel_typical_day",
                    radius="md",
                    mb=10,
                    mt=10,
                    h=1200,
                    visible = True,
                    children = [
                        html.Div(id="chart_typical_day"),
                    ]
                ),
            ],
            radius="lg",
            shadow="lg",
            p=20,mt=10,mb=10
        ),
        # =================================================================
        # TYPICAL WEEK
        # =================================================================
        dmc.Paper(
            children = [
                dmc.Title("Typical week", order=3, mb=10, mt=10),
                dmc.Skeleton(
                    id = "id_skel_typical_week",
                    radius="md",
                    mb=10,
                    mt=10,
                    h=400,
                    visible = False,
                    children = [
                        dash_echarts.DashECharts(               
                            id="chart_typical_week",
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
            p=30,
            mt=10,
            mb=10
        ),
        # =================================================================
        # REGRESSION
        # =================================================================   
        dmc.Paper(
            children = [
                dmc.Title("Energy consumption vs Heting Degree Days", order=3, mb=10, mt=10),
                dmc.Skeleton(
                    id="id_skel_regression",
                    visible=True, 
                    h=700, 
                    radius="md",
                    mt=10, 
                    mb=10, 
                    children = [
                        dmc.Grid(
                            children = [
                                dmc.GridCol(
                                    children = [
                                        dmc.Select(
                                        id="regressionType",
                                        label = "Regression type",
                                        data = ['linear','polynomial','exponential', 'logarithmic'],
                                        value= "linear"
                                        )
                                    ],
                                    span=4
                                ),
                                dmc.GridCol(
                                    children = [
                                        dmc.NumberInput(
                                            id="modelOrder",
                                            label="Model Order",
                                            value=1,
                                            min=0,
                                            step=1,
                                            disabled=False
                                        ),
                                    ],
                                    span=4
                                ),
                                dmc.GridCol(
                                    children = [
                                        dmc.Select(
                                            id="hdd_or_cdd_energy",
                                            label="Heating or cooling degree days",
                                            data = ['HDD','CDD'],
                                            value='HDD',
                                            disabled=False
                                        ),
                                    ],
                                    span=4
                                ),
                            ],
                            mb=10
                        ),
                        dash_echarts.DashECharts(               
                            id="energy_regression",
                            style={
                            "width": '100%',
                            "height": '400px',
                            }
                        ),
                        
                        html.Div(id= "Table_regression_stats_energy"),
                    ]
                ),  
            ],
            radius="lg",
            shadow="lg",
            p=20,mt=10,mb=10
        ),  
    ],
    radius="xl",
    shadow="xl",
    p="md"
)


main_ = dmc.Container(
    size="xl",
    children = [
        # TITLE
        dmc.Group(
            children = [
                DashIconify(icon="hugeicons:soil-temperature-field",color=dmc.DEFAULT_THEME["colors"]["gray"][6],width=72),
                dmc.Stack(
                    children = [
                        dmc.Title("Energy", order=1),
                        dmc.Title("Evalute the energy performance of the building", order=3, c="#dee2e6")
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
                        ),
                    ],
                    span=4
                ),
                dmc.GridCol(
                    children = [
                        energy_tab
                    ],
                    span=8
                ),
            ]
        )
    ]
)


alerts = html.Div(
    children = [
        FcGen.standard_alert(id_alert="data_missing_carpet", title_ = "Missing data!", text="No data available"),
        FcGen.standard_alert(id_alert="no_data_building", title_ = "Missing data!",text="No data available"),
    ]
)

layout_ = html.Div(
    children = [
        dcc.Store(id="data_stores"), 
        dcc.Store(id="date_energy"), 
        dcc.Store(id="weather_data"),
        dcc.Store(id="data_bui_heat_map_energy"),
        dcc.Store(id="data_bui_heat_map_energy_all"),
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
                        main_,
                        html.Div(id="data_test")
                    ]
                ),
            ],
            header={"height": 60},   
        )
    ],
    style = {'marginBottom':'20px'}
)

def layout():
    return layout_