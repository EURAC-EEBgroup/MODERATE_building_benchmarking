import dash
from dash import html, dcc, get_relative_path

import  dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_echarts

from utils.functions_general import bui_feature_compare, make_card,card_navbar
import utils.functions_general as FcGeneral
import utils.functions_plot as FcPlot
from components.header import Header
from components.footer import Footer

from datetime import datetime, timedelta,date
import pandas as pd

dash.register_page(__name__,path_template=f"/")

main_ = dmc.Container(
    size="xl",
    style = {'marginTop':'10rem'},
    children = [
        dmc.Flex(
            children = [
                dmc.Stack(
                    children = [
                        dmc.Stack(
                            children = [
                                dmc.Group(
                                    children = [
                                        dmc.Title("BENCHMARKING  ", c="rgb(121, 80, 242)", order=1),
                                        dmc.Title(" Tool", order=1)
                                    ],
                                    gap="12px"
                                ),
                                dmc.Text(children = ["Process, Visualize and analyze your buildings"], c="rgb(134, 142, 150)",fw=500),
                            ],
                            gap="2px"
                        ),
                        dmc.Center(
                            dmc.Anchor(
                                children = [
                                    dmc.Button("Check our buildings!", color= "black", variant="outline", size="lg", leftSection=DashIconify(icon="tabler:external-link", width=24, color="rgb(121, 80, 242)"))
                                ],
                                href=get_relative_path("/building"),
                            )
                        )
                    ]
                )
                
                
            ],
            align="center",
            justify="center"
        ),
       
    ]
)

layout_ = html.Div(
    children = [
        dmc.AppShell(
            [
                Header,
                dmc.AppShellMain(
                    children=[
                        main_
                    ],style = {'backgroundColor':'#f1f3f5'}
                ),
                Footer
            ],
            header={"height": 60},   
        )
    ],
    style = {'marginBottom':'20px'}
)



def layout():
    return layout_