import dash
from dash import html, dcc, get_relative_path

import  dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_echarts

from utils.functions_general import bui_feature_compare, make_card,card_navbar
import utils.functions_general as FcGeneral
import utils.functions_plot as FcPlot
from components.header import Header

from datetime import datetime, timedelta,date
import pandas as pd

dash.register_page(__name__,path_template=f"/building")


building_search = dmc.Select(
    data=["BCFS", "BCGJ", "BCGE"],
    searchable=True,
    leftSection=DashIconify(icon="line-md:search"),
    label="Search building"
)


building_card = dmc.Card(
    children = [
        dmc.Grid(
            children = [
                dmc.GridCol(
                    children = [
                        dmc.Image(
                            src="https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-8.png",
                            h="100%",
                            alt="Norway",
                        )
                    ],
                    span=5,
                ),
                dmc.GridCol(
                    children= [
                        dmc.Text("Building BCFS", size="md", c="black", fw=700, mt=10),
                        dmc.Group(
                            children = [
                                DashIconify(icon="stash:pin-place", width=30),
                                dmc.Text("Via del macello 5, Bolzano", size="sm", c="grey", opacity =0.8)
                            ],
                            mt=5
                        ),
                        dmc.Group(
                            children = [
                                dmc.Group(
                                    children = [
                                        DashIconify(icon="mdi:home-temperature", width=20),
                                        dmc.Text("Indoor Temperature - °C", size="sm", c="black"),
                                    ]
                                ),
                                dmc.Text("23", size="lg", c="blue")
                            ],
                            justify="space-between",
                            mt=10
                        ),
                        dmc.Divider(variant="dashed", color="#eeeeee", size="xs",mt=5, mb=0),
                        dmc.Group(
                            children = [
                                dmc.Group(
                                    children = [
                                        DashIconify(icon="carbon:temperature-hot", width=20),
                                        dmc.Text("Outdoor Temperature - °C", size="sm", c="black"),
                                    ]
                                ),
                                dmc.Text("12", size="lg", c="blue")
                            ],
                            justify="space-between",
                            mt=5
                        ),
                        dmc.Divider(variant="dashed", color="#eeeeee", size="xs",mt=5, mb=0),
                        dmc.Group(
                            children = [
                                dmc.Group(
                                    children = [
                                        DashIconify(icon="pepicons-pencil:electricity-circle", width=20),
                                        dmc.Text("HVAC - consumption - kWh", size="sm", c="black"),
                                    ]
                                ),
                                dmc.Text("12", size="lg", c="blue")
                            ],
                            justify="space-between",
                            mt=5
                        ),
                        dmc.Divider(variant="solid", color="#eeeeee", size="xs", mt=5, mb=0),
                        dmc.Flex(
                            dmc.Anchor(
                                "more info >",
                                href=get_relative_path("/analysis"),
                            ),
                            justify = "flex-end",
                            mt=10
                        )
                    ],
                    span=7
                )

            ]
        )
    ],
    radius="lg",
    shadow="lg"
)

list_projects = dmc.Stack(
    children = [
        building_search,
        building_card,
        building_card,
        building_card
    ]
)



building_paper = dmc.Paper(
    children = [
        dmc.Group(
            children = [
                dmc.Group(
                    children = [
                        dmc.Text("Name:", style = {'fontSize':'16px'}, fw=500, c="#868e96"),
                        dmc.Text("BCGJ", style = {'fontSize':'16px'}, fw=500, c="black"),
                    ]
                ),
                dmc.Badge("ACTIVE", variant="light", color="green")
            ],
            justify="space-between",
        ),
        dmc.Button("View details", id="btn_bui_page", 
                   className="btn_home_page",
                   variant="light", 
                   color="violet",
                   leftSection=DashIconify(icon="mynaui:external-link")
                   ),
        # INDOOR TEMPERATURE
        dmc.Group(
            children = [
                dmc.Group(
                    children = [
                        DashIconify(icon="fluent:temperature-16-filled", color="#868e96"),
                        dmc.Text("Indoor Temperature - °C:", style = {'fontSize':'14px'}, fw=500, c="#868e96")
                    ],
                    gap=3
                ),
                dmc.Text("20", style = {'fontSize':'16px'}, fw=500, c="black")
            ],mt=5
        ),
        # ENERGY
        dmc.Group(
            children = [
                dmc.Group(
                    children = [
                        DashIconify(icon="hugeicons:energy-rectangle", color="#868e96"),
                        dmc.Text("Energy consumption - kWh:", style = {'fontSize':'14px'}, fw=500, c="#868e96")
                    ],
                    gap=3
                ),
                dmc.Text("20", style = {'fontSize':'16px'}, fw=500, c="black")
            ],mt=5
        ) ,
        # OUTDOOR TEMPERATURE
        dmc.Group(
            children = [
                dmc.Group(
                    children = [
                        DashIconify(icon="iconoir:home-temperature-out", color="#868e96"),
                        dmc.Text("Outdoor Temperature - °C", style = {'fontSize':'14px'}, fw=500, c="#868e96")
                    ],
                    gap=3
                ),
                dmc.Text("20", style = {'fontSize':'16px'}, fw=500, c="black")
            ],
            mt=5
        ),
         # LAST MEASUREMENT       
        dmc.Group(
            children = [
                dmc.Group(
                    children = [
                        DashIconify(icon="solar:calendar-broken", color="#868e96"),
                        dmc.Text("Last measurement:", style = {'fontSize':'14px'}, fw=500, c="#868e96")
                    ],
                    gap=3
                ),
                dmc.Text("20/05/2023 15:00", style = {'fontSize':'16px'}, fw=500, c="black")
            ],mt=5
        )
    ],
    radius="md",
    shadow="xl",
    p=20
)

main_ = dmc.Container(
    size="xl",
    children = [
        # TITLE
        dmc.Group(
            children = [
                DashIconify(icon="solar:buildings-2-bold-duotone",color=dmc.DEFAULT_THEME["colors"]["gray"][6],width=72),
                dmc.Stack(
                    children = [
                        dmc.Title("Buildings", order=1),
                        dmc.Title("Last monitored data", order=3, c="#dee2e6")
                    ],
                    gap=1
                )
            ]
        ),
        # CONTENT
        dmc.Grid(
            children = [
                dmc.GridCol(
                    children = [
                    html.Div(id="building_list_card")
                    ],
                    span=4
                ),
                dmc.GridCol(
                    id="map_home",
                    span=8
                )
            ],
            mt=10,
        )
    ]
)



layout_ = html.Div(
    children = [
        dcc.Store(id="data_stores"),    
        dmc.AppShell(
            [
                Header,
                dmc.AppShellMain(
                    children=[
                        main_
                    ]
                ),
            ],
            header={"height": 60},
            padding="xl",    
        )
    ],
    style = {'marginBottom':'20px'}
)



def layout():
    return layout_