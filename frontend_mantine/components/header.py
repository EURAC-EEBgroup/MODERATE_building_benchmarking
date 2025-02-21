
import  dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dcc, get_relative_path, html

def get_icon(icon, rotate_):
    return DashIconify(icon=icon, height=16, rotate = rotate_, color="rgb(121, 80, 242)")


Header = dmc.AppShellHeader(
    h=60,
    id="header",
    children = [
        dmc.Group(
            id="group_header",
            children= [
                dcc.Link(
                    id="link_iwg5",
                    children = [
                        dmc.Avatar(
                            src=get_relative_path("/assets/moderate_logo.png"), radius=0,
                            style ={
                                'width':'100%',
                                'height': '32px',
                                # 'mar':'3px'
                            }
                        )
                    ],
                    href = get_relative_path("/"),
                ),
                dmc.Group(
                    children = [
                        dmc.Anchor(
                            children = [get_icon(icon="material-symbols-light:home-outline-rounded",rotate_=0),dmc.Text("Building", style={"fontSize": 14}, fw=500, ml=2)],
                            # id="anchor_",
                            className = "anchor_1",
                            href=get_relative_path("/building"),
                        ),
                        dmc.Anchor(
                            children = [get_icon(icon="carbon:text-link-analysis",rotate_=0),dmc.Text("Processing", style={"fontSize": 14}, fw=500, ml=2)], 
                            # id="anchor_",
                            className = "anchor_1",
                            href=get_relative_path("/processing"),
                        ),
                        dmc.Anchor(
                            children = [get_icon(icon="carbon:compare",rotate_=0),dmc.Text("Benchmarking", style={"fontSize": 14}, fw=500, ml=2)],
                            # id="anchor_",
                            className = "anchor_1",
                            href=get_relative_path("/benchmarking"),
                        ),
                        dmc.Menu(
                            id="menu_analysis",
                            children = [
                                dmc.MenuTarget(
                                    dmc.Anchor(
                                        # id="anchor_", 
                                        className = "anchor_1",
                                        underline = "never",
                                        href=get_relative_path("/#"),
                                        children = [
                                            dmc.Group(
                                                children = [
                                                    get_icon(icon="carbon:text-link-analysis",rotate_=0),dmc.Text("Analysis", style={"fontSize": 14}, fw=500, ml=2),
                                                    get_icon(icon="ep:arrow-up-bold",rotate_=2)
                                                ],
                                                gap="2px"
                                            ),
                                        ]
                                    ),
                                ),  
                                dmc.MenuDropdown(
                                    [
                                        dmc.Stack(
                                            children = [
                                                dmc.Text("Analysis", c="black", fs="16px", fw=500, pl=10, pt=10),
                                                dmc.Divider(variant="solid", color="rgb(241, 243, 245)")
                                            ],
                                            
                                        ),
                                        dmc.Anchor(
                                            dmc.MenuItem(
                                                children = [
                                                    dmc.Stack(
                                                        children = [
                                                            dmc.Text("Comfort", style = {'fontSize':'14px', 'lineHeight':'1.55'}, fw=500),
                                                            dmc.Text("Evalute the thermal comfort in the building",style = {'fontSize':'12px', 'lineHeight':'1.55'}, fw=500, c="rgb(134, 142, 150)" )
                                                        ],
                                                        gap=0,
                                                    )
                                                ], 
                                                leftSection=dmc.ThemeIcon(
                                                    DashIconify(icon="iconoir:home-temperature-out", color="rgb(121, 80, 242)", width=22),
                                                    color="rgb(206, 212, 218)",
                                                    size="34px",
                                                    variant="outline",
                                                    radius="md"
                                                ),
                                                p=20
                                            ),
                                            href = get_relative_path("/comfort"),
                                            underline = "never"
                                        ),
                                        dmc.Anchor(
                                            dmc.MenuItem(
                                                children = [
                                                    dmc.Stack(
                                                        children = [
                                                            dmc.Text("Energy", style = {'fontSize':'14px', 'lineHeight':'1.55'}, fw=500),
                                                            dmc.Text("Evalute the energy consumption of the building",style = {'fontSize':'12px', 'lineHeight':'1.55'}, fw=500, c="rgb(134, 142, 150)" )
                                                        ],
                                                        gap=0,
                                                    )
                                                ], 
                                                leftSection=dmc.ThemeIcon(
                                                    DashIconify(icon="hugeicons:sustainable-energy", color="rgb(121, 80, 242)", width=22),
                                                    color="rgb(206, 212, 218)",
                                                    size="34px",
                                                    variant="outline",
                                                    radius="md"
                                                ),
                                                p=20
                                            ),
                                            href = get_relative_path("/energy"),
                                            underline = "never"
                                        ),
                                        dmc.Anchor(
                                            dmc.MenuItem(
                                                children = [
                                                    dmc.Stack(
                                                        children = [
                                                            dmc.Text("Anomalies", style = {'fontSize':'14px', 'lineHeight':'1.55'}, fw=500),
                                                            dmc.Text("Check possible anomalies in the building",style = {'fontSize':'12px', 'lineHeight':'1.55'}, fw=500, c="rgb(134, 142, 150)" )
                                                        ],
                                                        gap=0,
                                                    )
                                                ], 
                                                leftSection=dmc.ThemeIcon(
                                                    DashIconify(icon="mingcute:fault-line", color="rgb(121, 80, 242)", width=22),
                                                    color="rgb(206, 212, 218)",
                                                    size="34px",
                                                    variant="outline",
                                                    radius="md"
                                                ),
                                                p=20
                                            ),
                                            href = get_relative_path("/anomalies"),
                                            underline = "never"
                                        ),

                                    ],
                                    p=0
                                ),
                            ],
                            trigger="hover",
                            # style = {'height':"100%"}
                        )  
                        
                    ],
                    h="100%"
                ),
                html.Div()
                # dmc.Button('Logout', id="btn_login", radius="sm", color="gray")
            ]
        )
    ]
)