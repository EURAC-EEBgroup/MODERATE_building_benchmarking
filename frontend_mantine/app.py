import os
import dash_mantine_components as dmc
from flask import Flask
import dash
from dash import dcc, html
from globals import SHOP_RELATIVE_PATH

# ================================================================================
#                           GENERAL SETTINGS
# ================================================================================

# dash mantine components >= 14.0.1 requires React 18+
dash._dash_renderer._set_react_version("18.2.0")

server = Flask(__name__, root_path=SHOP_RELATIVE_PATH)

external_stylesheets = [
    dmc.styles.DATES,
    dmc.styles.CAROUSEL,   
    dmc.styles.CHARTS,
    dmc.styles.NOTIFICATIONS,
    dmc.styles.CHARTS,
    "https://unpkg.com/@mantine/core@7.4.2/styles.css",
    "https://unpkg.com/@mantine/core@7.4.2/styles.layer.css"
]

app = dash.Dash(
    __name__, 
    server=server, 
    use_pages=True,
    assets_folder='assets',
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets
)
app.title = 'bench'
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

server = app.server
server.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(12)),
    SESSION_COOKIE_NAME='wurth_benchmarking'
)


# ================================================================================
#                           LAYOUT  
# ================================================================================
from callbacks import callback_home, callback_anomalies, callback_analysis_energy, callback_analysis_comfort, callback_processing, callback_benchmarking
app.layout = dmc.MantineProvider(
    children=[
        
        dcc.Loading(
            [
                dcc.Location(id="url_app"),
                dcc.Store(id="data_wurth"),
                dcc.Store(id="store_selected"),
                dcc.Store(id="name_stores"),   
                dcc.Store(id="data_shop"), 
                dcc.Store(id="data_shop_energy"),
                dcc.Store(id="last_data_bui", storage_type="session"),               
            ],
            fullscreen = True,
            color= "rgb(121, 80, 242)",
            overlay_style={"visibility":"visible", "filter": "blur(2px)"},
        ),
        dmc.AppShell(
            id="main_content_app",
            children=[
                html.Div(
                    id="container_body_app",
                    children = [
                        dmc.NotificationProvider(position="top-right"),
                        dash.page_container
                    ],
                ),
            ]
        )
    ],
)



if __name__ == '__main__':
    app.run_server(debug=False, port=8099, dev_tools_hot_reload=True)