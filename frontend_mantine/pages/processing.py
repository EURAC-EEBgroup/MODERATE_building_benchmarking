import dash_mantine_components as dmc
import dash 
from dash import dcc, html
from components.header import Header
import dash_echarts
import dash_ag_grid as dag
from dash_iconify import DashIconify


dash.register_page(__name__,path_template=f"/processing")


data_processing= dmc.Container(
    size="xl",
    children = [
        html.Div(id='output-data-upload'),
        dmc.Alert(
            id= "aler_file_upload",
            children =" Upload a file to analyze possible outliers. Use the buttons on the sidebar ",
            title="Upload file!",
            mb=10,
            mt=10,
            color="violet",
            # style = {"border":'1px solid darkblue'},
            withCloseButton=True,
            radius="md"
        ),
        
        dmc.Paper(
            children = [
                dag.AgGrid(
                    id='data-grid',
                    columnDefs=[],  # Columns will be dynamically set
                    rowData=[],     # Rows will be dynamically set
                    style={'height': '500px', 'width': '100%'},
                )
            ],
            radius="md",
            shadow="lg",
            p=10
        ),
        dmc.Grid(
            children = [
                dmc.GridCol(
                    children = [
                        dmc.Paper(
                            children = [
                                dmc.Select(
                                    id="time_index_name",
                                    label = "Time",
                                    description = "Select the name of 'time' parameter"
                                ),
                                dmc.Select(
                                    label="Temperature Parameter",
                                    id="processing_parameter_temperature",
                                    description="select temperature parameter/s to be visualized",
                                    mt=10
                                ),
                                dmc.Select(
                                    label="Energy/Power Parameter",
                                    id="processing_parameter_energy",
                                    description="select energy and power parameter/s to be visualized",
                                    mt=10
                                ),
                                dmc.Text("Outliers", fw=500, mt=10, style = {"fontSize":"var(--input-label-size, var(--mantine-font-size-sm))"}),
                                dmc.Checkbox(
                                    id="check_visualize_outliers", label="Visualize outliers", checked=False, mt=10
                                ),
                                dmc.Checkbox(
                                    id="check_remove_outliers", label="Remove outliers", checked=False, mt=10
                                ),
                            ],
                            radius="md",
                            shadow="lg",
                            p=10
                        ),
                    ],
                    span=3
                ),
                dmc.GridCol(
                    children = [
                        dmc.Paper(
                            children = [
                                html.Div(id="charts_prtocessing_div")
                            ],
                            radius="md",
                            shadow = "lg",
                            p=10
                        )
                    ], 
                    span=9
                )
            ],
            mt=10
        ),
        html.Div(
            id="elements_removing_outliers",
            children = [
                dmc.Paper(
                    children = [
                        dmc.Text("Cleaned Dataset", opacity=0.9, fw=700, c="#333333",mt=3, size="md"),
                        html.Div(id="chart_removed_ouliers"),
                    ],
                    radius="md",
                    shadow="lg",
                    p=10,
                    mt=10
                ),
                dcc.Loading(
                    id="loading_overlay", type="default", color = "rgb(121, 80, 242)",
                    children = dmc.Paper(
                        children = [
                            dmc.Divider(variant="solid", size="lg", mt=10, mb=10, label = dmc.Text("Update Time series", c=dmc.DEFAULT_THEME["colors"]["violet"][6], size="sm", fw=500), color=dmc.DEFAULT_THEME["colors"]["violet"][3]),
                            dmc.Fieldset(
                                id="sensor_field_new",
                                children=[
                                    dmc.TextInput(label="Sensor name", id="text_input_uuid", placeholder="shoudl be a universally unique identifier (e.g. 0ca577f2-665e-43fe-b7c6-ccc3293a5858)"),
                                    dmc.Group([dmc.Button("Generate", id="btn_generate_uuid")], justify="flex-end", mt=10),
                                ],
                                legend="New sensor data",
                                disabled=False,
                                mt=10,
                                display= "none"
                            ),

                            dmc.Divider(variant="solid", size="lg", mt=10, mb=10, label = dmc.Text("Update Metadata", c=dmc.DEFAULT_THEME["colors"]["violet"][6], size="sm", fw=500), color=dmc.DEFAULT_THEME["colors"]["violet"][3]),
                            dmc.Select(
                                id="buis_update_metadata",
                                label="Building",
                                description = "select the building in which you want to apply the metadata updates",
                                mt=10,
                                persistence=True,
                                persistence_type="session"
                            ),
                            dmc.TextInput(label="OPENAI API KEI", w=200, error=True, required=True, id="open_ai_api_key"),
                            dmc.Textarea(
                                label = "Update metadata",
                                description = " Update brick schema using LLM",
                                id="text_update_graph",
                                minRows = 4,
                                autosize=True,
                                display= "none", 
                                mt=10
                            ),
                            dmc.Button(
                                id="btn_post_data_in_TS_DB",
                                fullWidth= True,
                                radius="md",
                                children = "POST data and UPDATE metadata",
                                mt=10,
                                mb=10,
                                display= "none",
                                variant="light",
                                color="violet",
                                leftSection=DashIconify(icon = "tabler:upload", width=20,color=dmc.DEFAULT_THEME["colors"]["violet"][6] )
                            ),
                            html.Div(id="response_uploading", style = {'display':'none'}),
                            html.Div(id="output_brickllm")
                        ],
                        radius="md",
                        shadow="lg",
                        p=10,
                        mt=10
                    )
                )
            ]            
        )
    ]
)

graph_brick = html.Div(
    id= "graph_brick_",
    children = [
        dmc.Alert(
            id= "alert_metadata_graph",
            children ="Select Building and click 'Visualize' to see the graph model of your building in the sidebar",
            title="Visualize building graph!",
            mb=10,
            mt=10,
            color= "violet",
            withCloseButton=True,
            radius="md"
        )
    ]
)


# ================================================================
#                       PROCESSING GRAPHS
# ================================================================
processing_ = dmc.Accordion(
    id="accordion_processing",
    children = [
        dmc.AccordionItem(
            children = [
                dmc.AccordionControl(
                    children = ["Data Analysis"],
                    icon=DashIconify(
                        icon="streamline:code-analysis",
                        color=dmc.DEFAULT_THEME["colors"]["violet"][6],
                        width=20,
                    ),
                ),
                dmc.AccordionPanel(data_processing)
            ],
            value="data_process"
        ),
        dmc.AccordionItem(
            children = [
                dmc.AccordionControl(
                    children = ["Metadata Graph"],
                    icon=DashIconify(
                        icon="ph:graph",
                        color=dmc.DEFAULT_THEME["colors"]["violet"][6],
                        width=20,
                    ),
                ),
                dmc.AccordionPanel(
                    graph_brick
                )
            ],
            value="brick_graph"
        )
    ],
    multiple=True,
    value=["data_process"]
)

# ================================================================
#                       SIDEBAR
# ================================================================

sidebar_content = html.Div(
    children = [
        #                       DATA
        # ================================================================
        dmc.Text("Uplad file to be analyzed", c="333333", opacity=0.7, fw=700),
        dmc.Title("DATA", lh=1.2, order=3, fw=900, c="black",mb=20,mt=0),
        dmc.Select(
            label="Data type",
            placeholder="Select one",
            id="data_type_processing",
            value="csv_file",
            data=[
                {"value": "csv_file", "label": "File(e.g. CSV)"},
                # {"value": "database_processing", "label": "Database"},
            ],
            mt=10,
            clearable=False,
            searchable=True,
            persistence = True,
            persistence_type = "session",
            allowDeselect = False
        ),
        html.Div(
            id="widgets_type_connection"
        ),
        # dmc.Text("Time series File"),
        dcc.Upload(
            id="upload_file",
            children = [
                dmc.Button("Upload", id="btn_upload_file", radius="md", color="violet", fullWidth=True, mt=15,
                           leftSection=DashIconify(icon="material-symbols:upload"), variant = "light",
                           loaderProps={"type": "dots"})
            ]
        ),
        dmc.Divider(variant = "solid", size="lg", mt=20, mb=20),
        #                       METADATA
        # ================================================================
        dmc.Text("Building Brick-schema", c="333333", opacity=0.7, fw=700),
        dmc.Title("METADATA", lh=1.2, order=3, fw=900, c="black",mb=20,mt=0),
        dmc.Select(
            id="bui_ttl_file",
            label="Building",
            description = "list of .ttl buildings",
            mt=10,
            persistence=True,
            persistence_type="session"

        ),
        dmc.Checkbox(
            id="check_highlight_ele_brick", label="Highlight element in brick model", checked=False, mt=20
        ),
        dmc.Select(
            id="element_brick_highlight",
            mt=10,
            persistence=True,
            persistence_type="session"
        ),
        dmc.Button("Visualize",id="btn_visualize_brick", color="violet", radius="md", mt=10, fullWidth=True, variant="light",
                   leftSection=DashIconify(icon="mdi:show-outline"))
        
    ]
)

main_ = dmc.Container(
    size="xl",
    children = [
        # TITLE
        dmc.Group(
            children = [
                DashIconify(icon="ix:analyze",color=dmc.DEFAULT_THEME["colors"]["gray"][6],width=72),
                dmc.Stack(
                    children = [
                        dmc.Title("Processing", order=1),
                        dmc.Title("Modify,Visualize,Check and Update data", order=3, c="#dee2e6")
                    ],
                    gap=1
                )
            ]
        ),
        dmc.Grid(
            children = [
                # SIDEBAR
                dmc.GridCol(
                    children = [
                        dmc.Fieldset(
                            id="fieldset_proc_2",
                            children = sidebar_content,
                            legend = dmc.Text("Inputs", fw=500, style = {'fontSize':'18px'}),
                            mt=10,
                            radius="md"
                        ),
                    ],
                    span=3
                ),
                dmc.GridCol(
                    children = [
                        processing_
                    ],
                    span=9
                ),
            ]
        )
        
    ]
)

# ================================================================
#                       LAYOUT DEFINITION
# ================================================================
# import dash_bootstrap_components as dbc
layout_ = html.Div(
    children = [
        dcc.Loading(
            [
                dcc.Store(id="uploaded_data"),
                dcc.Store(id="outliers_"),
                dcc.Store(id="cleaned_data"),
            ],
            fullscreen = True,
            color = "rgb(121, 80, 242)",
        ),
        dmc.AppShell(
            [
                Header,
                dmc.AppShellMain(children=[
                    main_]
                ),
            ],
            header={"height": 60}, 
        )
    ],
    style = {'marginBottom':'20px'}
)



def layout():
    return layout_

