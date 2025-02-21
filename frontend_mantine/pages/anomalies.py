import dash
from dash import html, dcc
import  dash_mantine_components as dmc
from dash_iconify import DashIconify
from components.header import Header
import dash_echarts

dash.register_page(__name__,path_template=f"/anomalies")


# =========================================================

elements = [
    {"index":"", "Name":"", "Sensor":"","uuid":"","Value":"","Time":""},
]

main_ = dmc.Container(
    size="xl",
    children = [
        dcc.Store(id="disabled-positions", data=[]),  # Store for disabled positions
        dcc.Store(id="sort-order", data="asc"),  # Store for sorting state
        dcc.Store(id="table-data", data=elements),  # Store for sorting state
        dcc.Store(id="row-to-delete", data=None),  # Store to hold the row index to delete
        dmc.Title("Anomalies", order=1, mb=10),
        dmc.Paper(
            children = [
                dmc.Group(
                    children = [
                        dmc.Group(
                            children = [
                                dmc.Title("Building:", order=2),
                                dmc.Select(
                                    id="bui_anomalies",
                                    clearable=True,
                                    searchable=True,
                                    persistence = True,
                                    persistence_type = "session",
                                ),
                            ]
                        ),
                        dmc.TextInput(
                            id="search-input",
                            placeholder="Search in the table (text or numbers)...",
                            style={"width": "30%"},
                            leftSection=DashIconify(icon="healthicons:magnifying-glass-outline"),
                        ),
                        dmc.Modal(
                            id="delete-confirmation-modal",
                            title=dmc.Text("Do you want to delete the element?", size="md", w=500),
                            centered=True,
                            size="sm",
                            opened=False,  # Modal is initially closed
                            children=[
                                dmc.Group(
                                    children=[
                                        dmc.Button("Cancel", id="cancel-delete", variant="default",color =dmc.DEFAULT_THEME["colors"]["gray"][5] ),
                                        dmc.Button("Confirm", id="confirm-delete", color =dmc.DEFAULT_THEME["colors"]["violet"][5]),
                                    ],
                                    justify="flex-end"
                                ), 
                            ],
                            closeOnClickOutside=False
                        ),   
                    ],
                    justify="space-between",
                    p=20
                ),
                dmc.ScrollArea(
                    mr=20,
                    ml=20,
                    mb=10,
                    pb=10,
                    h=400,
                    children = [
                        dmc.Skeleton(
                            id="skeleton_table",
                            visible=True,
                            height=400,
                            children = [
                                dmc.Table(
                                    id="data-table",
                                    children=[
                                        dmc.TableThead(
                                            dmc.TableTr(
                                                [
                                                    dmc.TableTh("index"),
                                                    dmc.TableTh(
                                                        dmc.Group(
                                                            children=[
                                                                dmc.Text("Name"),
                                                                dmc.ActionIcon(
                                                                    children = DashIconify (icon="mdi:sort"),
                                                                    id="sort-button",
                                                                    variant="outline",
                                                                    size="sm",
                                                                    color="blue",
                                                                    n_clicks=0,
                                                                ),
                                                            ],
                                                        )
                                                    ),
                                                    dmc.TableTh("Sensor"),
                                                    dmc.TableTh("uuid"),
                                                    dmc.TableTh("Value"),
                                                    dmc.TableTh("Time"),
                                                    dmc.TableTh("Selected/Not Selected"),
                                                    dmc.TableTh("Actions"),
                                                ]
                                            )
                                        ),
                                        dmc.TableTbody(id="table-body"),  # Table body
                                    ],
                                ),
                            ]
                        )
                    ],
                    type = "hover",
                ),
                dmc.Space(h="xl"),
                dmc.Text(id="action-output",mt=20),
                html.Div(id="data_deleted"),
            ],
            radius="md",
            shadow="md"
        ),
        dmc.Paper(
            children = [
                dmc.Title("Graph:", order=2),
                dash_echarts.DashECharts(
                    id = 'graph_anomalies',
                    style={
                        "width": '100%',
                        "height": '300px',
                        },
                )
            ],
            radius= "md",
            shadow="md",
            p=20,
            mt=10
        )
    ]
)



layout_ = html.Div(
    children = [
        dmc.AppShell(
            [
                Header,
                dcc.Loading(
                    children = dcc.Store(id="data_building", data=None),
                    custom_spinner = html.Span(className= "loader_spin_2"),
                    style={'marginTop':'0px', 'marginBottom':'10px'},
                ),
                dmc.AppShellMain(
                    children=[      
                        main_
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