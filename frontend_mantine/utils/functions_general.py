from dash import html, dcc, get_relative_path
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from urllib.parse import urlparse
import pandas as pd
from pandas.tseries.holiday import Holiday, AbstractHolidayCalendar
import dash_echarts

def card_summary_value_period(id_title_1, title_2, id_text_value, value_1, id_action_value):
    '''
    The card shows a value to be highlighted for a specific period.
    It includes a title, a highlighted value, and an action icon with a loading effect.
    '''
    card_ = dmc.Card(
        children = [
            dmc.Group(
                children = [
                    dmc.Stack(
                        [dmc.Text("", id=id_title_1, opacity=0.7, fw=700, c="black", style = {'fontSize':'small'}),
                         dmc.Title(title_2, id="text2", order=4, mt=0, fw=700, c="black"),
                        ],
                        gap="0px"
                    ),
                    dmc.ActionIcon(
                        id=id_action_value,
                        children = dcc.Loading(
                            dmc.Text(
                                id=id_text_value,
                                children = value_1,
                                fw=800, 
                                style={"fontSize": 18}, 
                                c="rgb(121, 80, 242)"
                            ),
                            color="rgb(206, 212, 218)",
                            overlay_style={"visibility":"visible", "filter": "blur(2px)"},
                        ), 
                        size="45px", 
                        color = "rgb(206, 212, 218)",
                        radius="md",
                        variant="subtle",
                        p=4
                    ),
                ],
            )
        ],
        mt=20,
        withBorder=True,
        shadow="sm",
        radius="md",
    )

    return card_


def card_navbar(title, category, btn_children, btn_id, input_analysis):
    '''
    This function generates a navbar card with a title, category, input fields, and a button.
    '''
    content = html.Div(
        children = [
            dmc.Text(category, c="333333", opacity=0.7, fw=700),
            dmc.Title(title, lh=1.2, order=3, mt="xs", fw=900, c="black"),
            dmc.Divider(variant = "solid", size="lg", mt=20),
            html.Div(children = input_analysis),
            dmc.Button(id = btn_id, children = btn_children, fullWidth=True, radius="md", style = {'backgroundColor':'#071e31'}, mt=20)
        ]
    )
    return content


def make_card(image, title, category, btn_children, btn_id, input_analysis):
    '''
    Generates a paper card with an image background, title, category, and a button.
    '''
    return dmc.Paper(
        [
            html.Div(
                className="row",
                style = {'width':'100%'},
                children = [
                    html.Div(
                        className="col-lg-12 col-md-12 col-sm-12",
                        children = [
                            dmc.Text(category, c="white", opacity=0.7, fw=700),
                            dmc.Title(title, lh=1.2, order=3, mt="xs", fw=900, c="white"),
                            dmc.Divider(variant = "solid", size="lg", mt=20),
                            html.Div(children = input_analysis),
                            dmc.Button(id = btn_id, children = btn_children, fullWidth=True, radius="md", style = {'backgroundColor':'#e12024'}, mt=20)
                        ]
                    ),
                ]
            ),
        ],
        shadow="md",
        p="xl",
        mt= 20,
        radius="md",
        style={
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-between",
            "alignItems": "flex-start",
            "backgroundSize": "cover",
            "backgroundPosition": "center",
        },
    )


def bui_feature_compare(id_component, data_s, value_selected):
    '''
    Segemented control for multiple choices
    '''

    feature_compare = html.Div(
        [
            dmc.SegmentedControl(                
                id = id_component,
                value=value_selected,
                data=[
                    {
                        "value": v,
                        "label": dmc.Center(
                            [DashIconify(icon=icon, width=30, color="#0059ad"), html.Span(label)],
                            style={"gap": 10},
                        ),
                    }
                    for v,label, icon in data_s
                ],
                size="sm",
                fullWidth=True,
                mb=20,
                mt=20,
                persistence = True,
            )
        ]
    )
    return feature_compare


def extract_path(url):
    # Parsing the URL and extracting the path
    parsed_url = urlparse(url)

    # Extracting and cleaning the path by removing the leading "/"
    path = parsed_url.path
    extracted = path.lstrip("/")  # Removes only the first "/"

    return extracted


def resample_data(id_t, time, color_):
    return dmc.Button(
        dmc.Text(time),
        id=id_t,
        mb=10,
        radius="md",
        color=color_,
        variant="light"
    )


# Helper function to add derived columns
class ItalianHolidays(AbstractHolidayCalendar):
    rules = [
        Holiday("New Year's Day", month=1, day=1),
        Holiday("Epiphany", month=1, day=6),
        Holiday("Easter Monday", month=4, day=10, offset=pd.DateOffset(weekday=0)),  
        Holiday("Liberation Day", month=4, day=25),
        Holiday("Labour Day", month=5, day=1),
        Holiday("Republic Day", month=6, day=2),
        Holiday("Assumption Day", month=8, day=15),
        Holiday("All Saints' Day", month=11, day=1),
        Holiday("Immaculate Conception", month=12, day=8),
        Holiday("Christmas Day", month=12, day=25),
        Holiday("St. Stephen's Day", month=12, day=26)
    ]


def add_workday_and_hours_columns(df):
    """
    Adds workday, weekend, holiday, and working hours information to a DataFrame.
    """
    # Ensure the 'time' column is datetime
    df['time'] = pd.to_datetime(df['time'])

    # Instantiate ItalianHolidays calendar
    italian_holidays = ItalianHolidays().holidays(start=df['time'].min(), end=df['time'].max())

    # Add columns for weekend, holiday, workday, and working hours
    df['is_weekend'] = df['time'].dt.weekday >= 5  # Saturday=5, Sunday=6
    df['is_holiday'] = df['time'].dt.date.isin(italian_holidays.date)
    df['is_workday'] = ~df['is_weekend'] & ~df['is_holiday']
    df['is_working_hours'] = df['time'].dt.hour.between(8, 19).astype(int)  # 8am to 8pm = 1; else = 0

    return df


def data_for_heat_map(df, name_col):
    '''
    Prepare data for carpet plot
    Param
    ------
    df: Dataframe with col time and values
    '''
    # ========
    # CREATAE DATA FOR HEAT MAP
    # Filter data for a specifc month 
    dataToPlot = []
    df['day'] = df['time'].dt.date
    df['hour'] = df['time'].dt.hour
    for i, element in df.iterrows():
        dataToPlot.append([str(element['day']), element['hour'], element[name_col]])

    return dataToPlot



def switch_static(position):
    return dmc.Switch(
        id={"type": "row-switch", "position": position},  # Static switch ID tied to position
        size="sm",
        persistence=True
    )

def action_icon_table( id_,icon_, color_, color_border, classIcon):
    return dmc.ActionIcon(
                children = DashIconify(icon=icon_, color=color_, width=22),
                size="30px",
                variant="outline",
                radius="md",
                id=id_,
                color=color_border,
                className=classIcon
            )
            

def actions_icons(position):
    action_buttons = dmc.Group(
        children=[
            action_icon_table(
                id_={"type": "delete-button", "index": position},
                icon_="weui:delete-outlined",
                color_="red",
                classIcon="color_grey_icon",
                color_border="rgb(206, 212, 218)"
            ),
            action_icon_table(
                id_={"type": "action-button", "index": position},
                icon_="material-symbols:manage-search",
                color_="rgb(121, 80, 242)",
                classIcon="color_grey_icon",
                color_border="rgb(206, 212, 218)"
            )
        ],
    )
    return action_buttons

def get_label(value, data):
    for item in data:
        if item['value'] == value:
            return item['label']
    return None 

def content_carousel(option_chart):
    return dash_echarts.DashECharts(               
        option = option_chart,
        style={
            "width": '100%',
            "height": '400px',
        }
    )

def create_empty_table(data):
    return dmc.TableTr(
            [
                dmc.TableTd(""),
                dmc.TableTd(""),
                dmc.TableTd(""),
                dmc.TableTd(""),
                dmc.TableTd(""),
                dmc.TableTd(""),
                dmc.TableTd(""),  
                dmc.TableTd(""),  
            ]
        )

def create_table_rows(data, disabled_positions):
    '''
    Create Table in Amomalies having Header:
    index, Name, Sensor, Value, Time
    '''
    rows = []
    for element in data:
        index_ = element["index"]
        is_disabled = index_ in disabled_positions  # Check if the position is disabled
        style = {"color": "grey", "pointer-events": "none"} if is_disabled else {}

        row = dmc.TableTr(
            [
                dmc.TableTd(element["index"], style=style),
                dmc.TableTd(element["Name"], style=style),
                dmc.TableTd(element["Sensor"], style=style),
                dmc.TableTd(element["uuid"], style=style),
                dmc.TableTd(element["Value"], style=style),
                dmc.TableTd(element["Time"], style=style),
                dmc.TableTd(switch_static(index_)),  # Static switch
                dmc.TableTd(actions_icons(index_)),  # Buttons
            ]
        )
        rows.append(row)
    return rows


def get_label_by_value(data, values):
    """
    Retrieve labels for the provided values from the given list of dictionaries.
    
    :param data: List of dictionaries with 'value' and 'label' keys
    :param values: List of values to search for
    :return: List of corresponding labels
    """
    value_to_label = {item['value']: item['label'] for item in data}
    return [value_to_label.get(value) for value in values]


def get_monthly_data(df, energy_price, label):
    '''
    Get monthly data and energy price.
    
    Parameters:
    ----------
    df: DataFrame with energy consumption with 15-minute time steps.
    energy_price: Price per unit of energy.
    label: Column in the dataframe representing energy consumption.
    '''
    
    # Convert the 'time' column to datetime format
    df['time'] = pd.to_datetime(df['time'])

    # Extract the year and month from the 'time' column for grouping
    df['year_month'] = df['time'].dt.to_period('M')

    # Apply a transformation to the specified 'label' column, calculating energy cost for each 15-minute period
    df['transformed_meter'] = (df[label] * energy_price) / 4  # Energy cost for 15-minute intervals

    # Group data by 'year_month' and compute the sum of the transformed energy consumption for each month
    monthly_sum = df.groupby('year_month')['transformed_meter'].sum()
    
    # Convert the result into a DataFrame and reset the index for better readability
    monthly_sum = pd.DataFrame(monthly_sum).reset_index()
    monthly_sum.columns = ["month", "value"]  # Rename columns to 'month' and 'value'

    # Calculate the number of days in each month and add it as a new column
    monthly_sum['days_in_month'] = monthly_sum['month'].apply(lambda x: x.days_in_month)

    # Calculate the daily average energy cost for each month
    daily_average = monthly_sum['value'] / monthly_sum['days_in_month']

    # Convert 'month' back to string format for easier interpretation
    monthly_sum['month'] = monthly_sum['month'].astype(str)

    # Return the monthly summary as a list of dictionaries and the rounded daily average value
    return monthly_sum.to_dict('records'), round(daily_average.mean(), 2)


def add_workday_and_hours_columns(df):
    """
    Adds workday, weekend, holiday, and working hours information to a DataFrame.
    """
    # Ensure the 'time' column is datetime
    df['time'] = pd.to_datetime(df['time'])

    # Instantiate ItalianHolidays calendar
    italian_holidays = ItalianHolidays().holidays(start=df['time'].min(), end=df['time'].max())

    # Add columns for weekend, holiday, workday, and working hours
    df['is_weekend'] = df['time'].dt.weekday >= 5  # Saturday=5, Sunday=6
    df['is_holiday'] = df['time'].dt.date.isin(italian_holidays.date)
    df['is_workday'] = ~df['is_weekend'] & ~df['is_holiday']
    df['is_working_hours'] = df['time'].dt.hour.between(8, 19).astype(int)  # 8am to 8pm = 1; else = 0

    return df


def general_chart(option_):
    return [dash_echarts.DashECharts(   
        option = option_,
        style={
            "width": '100%',
            "height": '400px',
        },
    )]


from urllib.parse import urlparse

def extract_path(url):
    # Parsing dell'URL
    parsed_url = urlparse(url)

    # Estrarre il percorso (path)
    path = parsed_url.path

    # Rimuovere la parte iniziale "/"
    extracted = path.lstrip("/")  # Rimuove solo il primo "/"

    return extracted


def card_building_home(index_, building_name):
    '''
    Generate card of building showinf the last measurement
    Param
    -----
    building_name: name of the building to collect data
    index_ : index for each parmaeters, changes according to the number of building form 1 to n 
    '''
    building_paper = dmc.Paper(
        children = [
            dmc.Group(
                children = [
                    dmc.Group(
                        children = [
                            dmc.Text("Name:", style = {'fontSize':'16px'}, fw=500, c="#868e96"),
                            dmc.Text(children=building_name, style = {'fontSize':'16px'}, fw=500, c="black"),
                        ]
                    ),
                    dmc.Badge("ACTIVE", variant="light", color="green")
                ],
                justify="space-between",
            ),
            dmc.Anchor(
                children =  dmc.Button("View details", id="btn_bui_page", 
                    className="btn_home_page",
                    variant="light", 
                    color="violet",
                    leftSection=DashIconify(icon="mynaui:external-link")
                    ),
                href= get_relative_path(f"/comfort?bui_{building_name}")
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
                    dmc.Text(id={"type":"indoor_temp","index":index_}, style = {'fontSize':'16px'}, fw=500, c="black")
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
                    dmc.Text(id={"type":"HVAC_power","index":index_}, style = {'fontSize':'16px'}, fw=500, c="black")
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
                    dmc.Text(id={"type":"outdoor_temp","index":index_}, style = {'fontSize':'16px'}, fw=500, c="black")
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
            ),
            # CHECK ANOMALIES
            dmc.Group(
                children = [
                    dmc.Group(
                        children = [
                            DashIconify(icon="oui:ml-outlier-detection-job", color="#868e96"),
                            dmc.Text("Chek anomalies:", style = {'fontSize':'14px'}, fw=500, c="#868e96")
                        ],
                        gap=3
                    ),
                    dmc.Anchor(
                        children = [
                            dmc.ActionIcon(
                                id="btn_bui_anomalies",
                                children = DashIconify(icon="fluent-mdl2:linked-database"), 
                                color="violet", variant="light",
                                radius="lg"
                            )               
                        ],  
                        href= get_relative_path(f"/anomalies?bui_{building_name}")
                    ),
                ],
                justify="space-between",
            )
        ],
        radius="md",
        shadow="xl",
        p=20,
        m=10
    )

    return building_paper


def card_energy_carousel(id_skeleton_card,id_text_value,id_text_value_m2, child_text, unit_1, unit_2):
    '''
    Card energy parameter
    Param
    ------
    id_text_value: id of the  textvalue
    '''
    card_ = dmc.Card(
        children = [
            dmc.Skeleton(
                id=id_skeleton_card,
                h=100,
                radius="md",
                mb=5,
                visible=True,
                children = [
                    dmc.CardSection(
                        dmc.Text(children = child_text, opacity=0.7, fw=700, c="black",mb=5),
                        pt="md", pr="md", pl="md"
                    ),
                    dmc.CardSection(
                        dmc.Carousel(
                            classNames={"controls": "dmc-controls", "root": "dmc-root"},
                            children = [
                                dmc.CarouselSlide(
                                    dmc.Group (
                                        children = [
                                            dmc.Text(id=id_text_value,opacity=0.7, fw=700, c="black",mb=5, size="30px"),
                                            dmc.Text(children = unit_1,opacity=1, fw=400, c="grey",mb=5, size="xs")
                                        ],
                                        justify="center",
                                        gap="sm",
                                        style = {'alignItems':'baseline'}
                                    )
                                ),
                                dmc.CarouselSlide(
                                    dmc.Group (
                                        children = [
                                            dmc.Text(id=id_text_value_m2,opacity=0.7, fw=700, c="black",mb=5, size="30px"),
                                            dmc.Text(children = unit_2,opacity=1, fw=400, c="grey",mb=5, size="xs")
                                        ],
                                        justify="center",
                                        gap="sm",
                                        style = {'alignItems':'baseline'}
                                    )
                                )
                            ],
                            withIndicators=False,
                            slideGap="sm",
                            loop=True,
                            align="start",
                            p=0,
                            h=40
                        ),
                        p="sm"
                    ),        
                ]
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        p="md"
    )
    return card_


def standard_alert(text, title_, id_alert):
    return dmc.Center( 
        dmc.Alert(
            children = text, 
            title=title_,
            id=id_alert,
            color="red",
            hide=True,
            variant="filled",
            withCloseButton=True,
            mt=10,
            style = {"width": "50%"}
        )
    )


def compare_building_grid():

    colGrid = dmc.GridCol(
        children = [
            dmc.Paper(
                children = [
                    dmc.Group(
                        children = [
                            dmc.Text("Energy/HDD [kWh/HDD]:"),
                            dmc.Text("100")
                        ],
                        justify="space-between",
                        mt=10
                    ),
                    dmc.Group(
                        children = [
                            dmc.Text("Total HDD [-]:"),
                            dmc.Text("100")
                        ],
                        justify="space-between",
                        mt=10
                    ),
                    dmc.Group(
                        children = [
                            dmc.Text("Number of hours:"),
                            dmc.Text("100")
                        ],
                        justify="space-between",
                        mt=10
                    )
                ],
                p=10,mt=10, radius="md"
            )
        ],
        span=6
    )

    return colGrid