
import random
from dash import html
import dash_mantine_components as dmc
import dash_echarts
import pandas as pd
import numpy as np

option_white =  {
        'xAxis': {
            'type': 'category',
            'data': [],
            'boundaryGap': False,
            'axisLine': { 'onZero': True },
        },
        'yAxis': [
            {
            'type': 'value',
            'data': []
            }
        ],
        'series': [
            {
            'data': [],
            'type': 'line',
            },          
        ]
    }

color_palette = ['#9A031E',"#071E22","#1D7874","#679289","#F4C095","EE2E31","#20639B","#F6D55C","#ba7ba7",
                 "#b33951", "#f58a07","#2093ad", "#654f6f", "#d0cab1", "#eddecd", "#38ad04", "#d8ac28", "#ed5278", 
                 "#f67695", "#81edad", "#82ddbd", "#83cdcd", "#83cdcd", "#85aded", "#78573a","#564222", "#9c560c", "#682d08"]




def horiz_bar_energy_geopage(source, minBefore, maxAfter, yName):
    '''
    '''
    option = {
    'dataset': {
        'source':source
    },
    'tooltip': {
        'trigger': 'axis'
    },
    'toolbox': {
    'show': True,
    'feature': {
      'dataZoom': {
        'yAxisIndex': 'none'
      },
      'dataView': { 'readOnly': False },
      'magicType': { 'type': ['line', 'bar'] },
      'saveAsImage': {}
    }
    },
    'grid': { 'containLabel': True },
    'xAxis': { 'type': 'category' },
    'yAxis': { 'name': yName},
    # 'visualMap': {
    #     'orient': 'horizontal',
    #     'left': 'center',
    #     'min': minBefore,
    #     'max': maxAfter,
    #     'text': ['High', 'Low'],
    #     'dimension': 0,
    #     'inRange': {
    #     'color': ['#65B581', '#FFCE34', '#FD665F']
    #     }
    # },
    'series': [
        {
        'type': 'bar',
        'encode': {
            'x': 'Building',
            'y': 'value'
        },
        'markLine': {
            'data': [{ 'type': 'average', 'name': 'Avg' }]
        }
        }
    ]
    }
    return option 


def generate_graph(df, label_y, label_y2, legend_position):
    '''
    Param
    -------
    label_y: name of the y axes
    legend_position: position of legend from the top
    '''
    col1 = df.columns[0]

    option = {
        'xAxis': [
            {
            'type': 'category',
            'axisTick': { 'show': 'false '},
            'data': list(df.index),
            }
        ],
        'yAxis': [
            {
            'type': 'value',
            'name': label_y
            },
            {
                "type": 'value',
                "name": label_y2,
                "boundaryGap": [0.2, 0.2]
            }
        ],
        'legend': {
            'data': [col1],
            'top':legend_position
        },
        'toolbox': {
            'show': True,
            'feature': {
            'dataZoom': {
                'yAxisIndex': 'none'
            },
            'dataView': { 'readOnly': False },
            'saveAsImage': {}
            }
        },
        'tooltip': {
            'trigger': 'axis'
        },
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {
            'type': 'shadow'
            }
        },
        'dataZoom': [
            {
            'type': 'inside',
            'start': '0',
            'end': '100'
            },
            {
            'start': '0',
            'end': '100',
            }
        ],
        'series': [
            {
                'name': col1,
                'data': list(df[col1].values),
                'label': 'labelOption',
                'type': 'line',
                'color': color_palette[0],
                'smooth': True,
                'hoverAnimation': True,
                'emphasis': {
                    'focus': 'series'
                },
                'yAxisIndex': 0,
            }
        ]
    }

    
    lenColumnDf = len(df.columns)
    if  lenColumnDf >=1:
        for i,colName in enumerate(df.columns[1:]):
            random_number = random.randint(0,16777215)
            hex_number = str(hex(random_number))
            hex_number ='#'+ hex_number[2:]            
            option['series'].append({
                'name': colName,
                'data': list(df[colName].values),
                'label': 'labelOption',
                # 'color':color_palette[i+1],
                'color':hex_number,
                'type': 'line',
                'smooth': True,
                'hoverAnimation': True,
                'emphasis': {
                    'focus': 'series'
                },
                'yAxisIndex': 1,
            })
        option['legend'] = {
            'data': list(df.columns)
        }
    else:
        option['legend']= {
            'data': [col1]
        },
        option

    return option

def create_table(df):
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rowsdf = [html.Tr([html.Td(cell) for cell in rowsdf]) for rowsdf in values]
    rowsNewName = [
        html.Tr(
            [
                html.Td(
                    children = dmc.Select(
                        id={'type':'paramName', 'index':col},
                        data=[
                            {'value':'time','label':'Time'},
                            {'value':'temperature','label':'Temperature °C'},
                            {'value':'humidity', 'label':'Humdity - %'},
                            {'value':'co2', 'label':'CO2 - ppm'},
                            {'value':'thermal_energy', 'label':'Thermal Energy - kWh'},
                            {'value':'electricity', 'label':'Electricity - kWh'},
                            {'value':'water', 'label':'Water - l'},
                            {'value':'gas', 'label':'Gas - m3/h'},
                        ],
                        value = 'temperature',
                        persistence=True                
                    )
                ) for col in columns
            ]
        )
    ]
    rows = rowsNewName+rowsdf
    table = [html.Thead(header), html.Tbody(rows)]
    return table


def create_table_degree_days(years):
    '''
    Create a table with the year available in the dataframe
    '''
    table_rows = []
    for i, value in enumerate(years):
        table_rows.append(
            html.Tr([
                html.Td(value),
                html.Td(dmc.NumberInput(id=f'dd_input-{i}', value=1000, min=10))
            ])
        )
    
    table = html.Table([
        html.Thead(
            id="table_year",
            children = [html.Tr([html.Th("Year"), html.Th("DD")])]
        ),
        html.Tbody(table_rows)
    ])

    return table


# ======================================================
#                       HEAT MAP
# ======================================================
def heatmap(title,subTitle, data1, days, hours, minSeries, maxSeries, maxDaySeries):
    option = {
    "tooltip": {
        "position": "top"
    },
    # 'title': {
    #     'text':title,
    #     "subtext": subTitle,
    #     "left": 'center'
    # },
    "grid": {
        "height": '50%',
        "top": '20%'
    },
    'toolbox': {
        'show': True,
        'feature': {
        'dataZoom': {
            'yAxisIndex': 'none'
        },
        'dataView': { 'readOnly': False },
        'saveAsImage': {}
        }
    },
    "xAxis": {
        "type": 'category',
        "data": days,
        "splitArea": {
            "show": False
        },
        'axisLine' : {
            'show': False,
        },
        'axisTick' : { 
            'show': False,
        }, 
        'name':'Days',
        "min":0,
        "max":maxDaySeries
    },  
    "yAxis": {
        "type": 'category',
        "data": hours,
        "splitArea": {
            "show": False
        },
        'axisLine' : {
            'show': False,
        },
        'axisTick' : { 
            'show': False,
        }, 
        'name':'Hour',
        "min":0,
        "max":23
    },
    "visualMap": {
        "min": minSeries,
        "max": maxSeries,
        "calculable": True,
        "orient": 'horizontal',
        "left": 'center',
        "bottom": '5%',
        "inRange": {
            "color": [
                '#313695',
                '#4575b4',
                '#74add1',
                '#abd9e9',
                '#e0f3f8',
                '#ffffbf',
                '#fee090',
                '#fdae61',
                '#f46d43',
                '#d73027',
                '#a50026'
                ]
        }
    },
    "series": [
        {
        # "name": 'Punch Card',
        "type": 'heatmap',
        "data": data1,
        "emphasis": {
            "itemStyle": {
            "shadowBlur": 10,
            "shadowColor": 'rgba(0, 0, 0, 0.5)'
            }
        }
        }
    ]
    }
    return option


def heat_map_graph(days, hours, minValue, maxValue, dataToPlot, title):
        
    options = {
        # "tooltip": {
        #     "position": "top"
        # },
        'title': {
            'text':title,
            # "subtext": subTitle,
            "left": 'center'
        },
        "grid": {
            "height": "50%",
            "top": "10%"
        },
        'toolbox': {
            'show': True,
            'feature': {
            'dataZoom': {
                'yAxisIndex': 'none'
            },
            'dataView': { 'readOnly': False },
            'saveAsImage': {}
            }
        },
        "xAxis": {
            "type": "category",
            "data": days,
            "splitArea": {"show": True},
            'min':0,
            'max':31
        },
        "yAxis": {
            "type": "category",
            "data": hours,
            "splitArea": {"show": True}
        },
        "visualMap": {
            "min": minValue,
            "max": maxValue,
            "calculable": True,
            "orient": 'horizontal',
            "left": 'center',
            "bottom": '5%',
            "inRange": {
                "color": [
                    '#313695',
                    '#4575b4',
                    '#74add1',
                    '#abd9e9',
                    '#e0f3f8',
                    '#ffffbf',
                    '#fee090',
                    '#fdae61',
                    '#f46d43',
                    '#d73027',
                    '#a50026'
                    ]
            }
        },
        "series": [{
            "name": "Time Series",
            "type": "heatmap",
            "data": dataToPlot,
            "label": {
                "show": False
            },
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            }
        }]
    }

    return options

def month_slider(id_slider):
    slider_m = dmc.Slider(
        id= id_slider,
        min=1, 
        max=12, 
        step=1,
        value=9,
        showLabelOnHover= False,
        marks=[
            {"value": 1, "label": "Jan"},
            {"value": 2, "label": "Feb"},
            {"value": 3, "label": "Mar"},
            {"value": 4, "label": "Apr"},
            {"value": 5, "label": "May"},
            {"value": 6, "label": "Jun"},
            {"value": 7, "label": "Jul"},
            {"value": 8, "label": "Aug"},
            {"value": 9, "label": "Sep"},
            {"value": 10, "label": "Oct"},
            {"value": 11, "label": "Nov"},
            {"value": 12, "label": "Dec"},
        ], 
        mb=20
    )
    return slider_m

def create_carpet_plot(df, selected_month, minValue, maxValue):
    sensors = df.columns
    heat_mamps_graph = []
    for name in sensors:
        df_sens = pd.DataFrame(df[name])
        # Hourly reseample
        df_sens = df_sens.resample('h').mean()
        
        # Add columns of hours and day
        df_sens['day'] = df_sens.index.day
        df_sens['hour'] = df_sens.index.hour
        df_sens['month'] = df_sens.index.month
        # Filtering selecting month
        data_month = df_sens.loc[df_sens['month'] ==selected_month,:]
        # float and round variable values 
        data_month[name] = [round(num, 1) for num in list(map(float,(data_month[name].to_list())))]
        # data for plot
        dataToPlot = []
        for i, element in data_month.iterrows():
            dataToPlot.append([int(element['day'])-1,int(element['hour']),element[name]])
        #
        y= data_month['hour'].values
        # x = df_sens['day'].values
        days = list(range(1,31))
        days = [str(i) for i in days]
        hours = list(dict.fromkeys(y))
        hours = [str(i) for i in hours]
        # Heat map
        title = f"profile of {name}"
        # subtitle = "heat map:"
        heat_graph = heat_map_graph(days, hours, minValue, maxValue, dataToPlot, title)
        #
        dash_graph = dash_echarts.DashECharts(
            option = heat_graph,
            style={
                "width": '100%',
                "height": '400px',
                }
        )        
        heat_mamps_graph.append(dash_graph)

    return heat_mamps_graph



from math import pi
from bokeh.models import DatetimeTickFormatter
from bokeh.plotting import figure, output_file, save
import itertools
from bokeh.palettes import Dark2_5 as palette
colors = itertools.cycle(palette)
def Time_line_chart(df:pd.DataFrame, yaxis__name:str, xaxis_name:str, chart_title:str,plot_category:bool,
                    x_axis_time_type:bool,x_var_name:str, graph_indoor_operative_T:bool,real_t_op_name:str,
                    file_name:str, dir_graph_folder:str, width_p:int, height_p:int,yRange:list):
    '''
    UNI 16798-1:2016
     Default design values of the indoor operative temperature in winter and summer
    for buildings with mechanical cooling systems
    
    Type of Builidng:               Category        Operative Temperature
                                                    Minimum for hetaing(1.0 clo)        Minimu for cooling (5.0 clo)
                                           
    Residential building,               I               21                                  25.5
    living spaces (bed room's,          II              20                                  26
    living rooms, kitchems )            III             18                                  27
    Sedentary activities: 1.2 met       IV              16                                  28
   
    INPUT:
    df:  dataframe with DateTime index
    yaxis__name: title of the y_axis
    chart_title: title of the chart
    plot_category: True or False. If True the category og the UNI 16798 will be shown
    
    x_axis_time_type: True or False (True:x axis is time)
    x_var_name:  if not time series the x axes should be defined by the user giving name of the column
    
    graph_indoor_operative_T:  True or False. True if plot the graph H.2 of UNI EN 16798-1:2016 related to acceptable
                                Indoor Temperature for buildings without mechanical ventilation
    real_t_op_name: name of the column in whcih there are the monitored indoor temperature
    dir_graph_folder: directory of the folder to save graph
    
    '''
    TOOLTIPS = [
        ("values","@y{1.1}"),
    ]   
    # create a new plot with a title and axis labels
    p = figure(title=chart_title, tooltips=TOOLTIPS, width=width_p, height = height_p, align = 'center',
               y_range = yRange)
 
    # ============
    # Select if the xaxis should be a time series or not. If not provide the name of the df column to be used as xaxis
    if x_axis_time_type == True:
        x_axis = df.index
        p.xaxis.formatter=DatetimeTickFormatter(
                hours=["%d %B %Y"],
                days=["%d %B %Y"],
                months=["%d %B %Y"],
                years=["%d %B %Y"],
            )
        p.xaxis.major_label_orientation = pi/4
        columns_name = df.columns.tolist()
    else:
        x_axis = df[x_var_name]
        columns_name = df.columns.tolist()
        columns_name.remove(x_var_name)
    # ============
 
    # Name of y_axis
    p.yaxis[0].axis_label = yaxis__name
    p.xaxis[0].axis_label = xaxis_name
 
    # ============
    # Select if visualize the categoray defined in the table H.2 of UNI EN 16798-1:2016
    if plot_category == True:
    # Set categories on the dataset
        df['category_1'] = np.repeat(21, len(df)).tolist()
        df['category_2'] = np.repeat(20, len(df)).tolist()
        df['category_3'] = np.repeat(18, len(df)).tolist()
        df['category_4'] = np.repeat(17, len(df)).tolist()
        df['left'] = df.index
        df['right'] = df.index
       
    # create category area    
        p.quad(top='category_3', bottom='category_4', left='left', right='right',
                fill_color='cornflowerblue', alpha = 0.2, source=df)  
        p.quad(top='category_2', bottom='category_3', left='left', right='right',
                color='darkcyan', source=df, alpha = 0.2)   
        p.quad(top='category_1', bottom='category_2', left='left', right='right',
                color='forestgreen', alpha = 0.2, source=df)
        # ADD HORIZONTAL LINE OF COOMFORT
        p.ray(x=df.index, y=[21], length=0, angle=0, line_width=1, color="green", legend_label = "category_1_limit"),
        p.ray(x=df.index, y=[20], length=0, angle=0, line_width=1, color = "darkcyan", legend_label = "category_2_limit")
        p.ray(x=df.index, y=[18], length=0, angle=0, line_width=1, color="cornflowerblue", legend_label = "category_3_limit")
        p.ray(x=df.index, y=[17], length=0, angle=0, line_width=1, color="cornflowerblue", legend_label = "category_4_limit")
 
    # =============
 
    # ADD lines to plot
    if  graph_indoor_operative_T==True:
        p.line(x=x_axis, y =df['cat_1_upper'], color ='green', line_dash= "dotdash" ,legend_label = 'cat_1_upper')
        p.line(x=x_axis, y =df['cat_2_upper'], color ='darkorange', line_dash= "dashed" ,legend_label = 'cat_2_upper')
        p.line(x=x_axis, y =df['cat_3_upper'], color ='crimson', line_dash= "solid" ,legend_label = 'cat_3_upper')
        p.line(x=x_axis, y =df['cat_3_lower'], color ='crimson', line_dash= "solid" ,legend_label = 'cat_3_lower')
        p.line(x=x_axis, y =df['cat_2_lower'], color ='darkorange', line_dash= "dashed" ,legend_label = 'cat_2_lower')
        p.line(x=x_axis, y =df['cat_1_lower'], color ='green', line_dash= "dotdash" ,legend_label = 'cat_1_lower')
        p.line(x=x_axis, y =df['optimal_opt_term'], color ='black', line_dash= "7 7" ,legend_label = 'optimal_opt_term')
        # columns_name.remove(real_t_op_name)
        # for element in columns_name:
        #     p.line(x=x_axis, y =df[element], color =next(colors), legend_label = element)
        p.circle(x=x_axis, y=df[real_t_op_name], size = 10, color = "navy", alpha=0.5)  
 
    else:
        for element in columns_name:
            p.circle(x=x_axis, y =df[element], color =next(colors), legend_label = element)
       
    # ============
    # GRAPH PROPRIETIES
    # Remove logo
    p.toolbar.logo = None
    # Legened position
    p.legend.location = "top_right"
    # Allow select and descelt lines from legend
    p.legend.click_policy="hide"
    # set legened outside graph area
    p.add_layout(p.legend[0], 'right')
       
    # output to static HTML file
    output_file(dir_graph_folder+file_name+".html")
    save(p,dir_graph_folder+file_name+".html" )
    # show(p)
    return p



def doughnut_chart(value_1, value_2):

    option = {
    "tooltip": {
        "trigger": 'item'
    },
    "legend": {
        "top": '5%',
        "left": 'center'
    },
    "series": [
        {
        "name": 'Access From',
        "type": 'pie',
        "radius": ['40%', '70%'],
        "avoidLabelOverlap": False,
        "itemStyle": {
            "borderRadius": 10,
            "borderColor": '#fff',
            "borderWidth": 2
        },
        "label": {
            "show": False,
            "position": 'center'
        },
        "emphasis": {
            "label": {
            "show": True,
            "fontSize": 40,
            "fontWeight": 'bold'
            }
        },
        "labelLine": {
            "show": False
        },
        "data": [
            { "value": value_1, "name": 'Over' },
            { "value": value_2, "name": 'Under' },
        ]
        }
    ]
    }
    return option

def doughnut_chart_monthly(data:list):

    option = {
    "tooltip": {
        "trigger": 'item'
    },
    "legend": {
        "top": '5%',
        "left": 'center'
    },
    "series": [
        {
        "name": 'Access From',
        "type": 'pie',
        "radius": ['40%', '70%'],
        "avoidLabelOverlap": False,
        "itemStyle": {
            "borderRadius": 10,
            "borderColor": '#fff',
            "borderWidth": 2
        },
        "label": {
            "show": False,
            "position": 'center'
        },
        "emphasis": {
            "label": {
            "show": True,
            "fontSize": 40,
            "fontWeight": 'bold'
            }
        },
        "labelLine": {
            "show": False
        },
        # "data": [
        #     { "value": values[0], "name": 'May' },
        #     { "value": values[1], "name": 'June' },
        #     { "value": values[2], "name": 'July' },
        #     { "value": values[3], "name": 'August' },
        #     { "value": values[4], "name": 'September' },
        # ]
        "data": data
        }
    ]
    }
    return option


def line_chart_with_effect(df,label_y):
    col1 = df.columns[0]
    col2 = df.columns[1]

    option = {
        'xAxis': [
            {
            'type': 'category',
            'axisTick': { 'show': 'false '},
            'data': list(df.index),
            }
        ],
        'yAxis': [
            {
            'type': 'value',
            'name': label_y
            }
        ],
        'legend': {
            'data': [col1]
        },
        'tooltip': {
            'trigger': 'axis'
        },
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {
            'type': 'shadow'
            }
        },
        'dataZoom': [
            {
            'type': 'inside',
            'start': '0',
            'end': '100'
            },
            {
            'start': '0',
            'end': '100',
            }
        ],
        'series': [
            {
                'name': col1,
                'data': list(df[col1].values),
                'label': 'labelOption',
                'type': 'line',
                'color': color_palette[0],
                'smooth': True,
                'hoverAnimation': True,
                'emphasis': {
                    'focus': 'series'
                },
            },
            {
                "type": 'effectScatter',
                "symbolSize": 20,
                "data": list(df[col2].values)
            }
        ]
    }

    return option


def basic_scatter_plot(data,xAxisLabel,yAxisLabel):
    option = {
        "xAxis": {
            'name':xAxisLabel,
            'splitLine': {
                'lineStyle': {
                    'type': 'dashed'
                }
            },
            'nameTextStyle': {
                'align': 'right',
                'verticalAlign': 'top',
                'padding': [30, 0, 0, 0],
            }
        },
        "yAxis": {
            'name': yAxisLabel,
            'nameRotate': 90,
            'splitLine': {
                'lineStyle': {
                    'type': 'dashed'
                }
            },
            "nameTextStyle": {
                "align": 'right',
                "verticalAlign": 'top',
                
                "padding": [10, 0, 0, 10],
            }  
        },
        "series": [
                {
                "symbolSize": "20",
                "data": data,
                "type": 'scatter',
                'symbolSize': 5,
                'symbol': 'circle',
                }
            ],
        'toolbox': {
            'show': True,
            'feature': {
            'dataZoom': {
                'yAxisIndex': 'none'
            },
            'dataView': { 'readOnly': False },
            'magicType': { 'type': ['line', 'bar'] },
            'saveAsImage': {}
            }
        },
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {
            'type': 'cross'
            }
        },
        }
    return option


def RegressionChart(source, title, xName,yName, namePoint, regressionType, order):
    option = {
    'dataset': [
        {
        'source': source
        },
        {
        'transform': {
            'type': 'ecStat:regression',
            # // 'linear' by default.
            'config': {
                'method': regressionType,
                'order':order,
                'formulaOn': 'end'}
        }
        }
    ],
    'toolbox': {
        'show': True,
        'feature': {
        'dataZoom': {
            'yAxisIndex': 'none'
        },
        'dataView': { 'readOnly': False },
        'magicType': { 'type': ['line', 'bar'] },
        'saveAsImage': {}
        }
    },
    'title': {
        "text": title,
        # "subtext": "regression building model"
    },
    'legend': {
        'bottom': 5
    },
    'tooltip': {
        'trigger': 'axis',
        'axisPointer': {
        'type': 'cross'
        }
    },
    'xAxis': {
        'name':xName,
        'splitLine': {
            'lineStyle': {
                'type': 'dashed'
            }
        },
        'nameTextStyle': {
            'align': 'right',
            'verticalAlign': 'top',
            'padding': [30, 0, 0, 0],
        }
    },
    'yAxis': {
        'name': yName,
        'splitLine': {
            'lineStyle': {
                'type': 'dashed'
            }
        },
        "nameTextStyle": {
            "align": 'right',
            "verticalAlign": 'top',
            "padding": [10, 0, 0, 10],
        }   
    },
    'series': [
        {
            'name': namePoint,
            'type': 'scatter'
        },
        {
            'name': 'regression',
            'type': 'line',
            'datasetIndex': 1,
            'symbolSize': 0.1,
            'symbol': 'circle',
            'label': { 'show': True, 'fontSize': 16 },
            'labelLayout': { 'dx': -20 },
            'encode': { 'label': 2, 'tooltip': 1 }
        }
    ]
    }
    return option



def scatter_with_histogram(data):
    '''
    Scatter plot with histogram of frequency of values in ranges
    '''
    option = {
        "dataset": [
            {
            "source": data
            },
            {
            "transform": {
                "type": 'ecStat:histogram',
                "config": {}
            }
            },
            {
            "transform": {
                "type": 'ecStat:histogram',
                "config": { "dimensions": [1] }
            }
            }
        ],
        "tooltip": {},
        "grid": [
            {
            "top": '50%',
            "right": '50%'
            },
            {
            "bottom": '52%',
            "right": '50%'
            },
            {
            "top": '50%',
            "left": '52%'
            }
        ],
        "xAxis": [
            {
            "scale": True,
            "gridIndex": 0
            },
            {
            "type": 'category',
            "scale": True,
            "axisTick": { "show": False },
            "axisLabel": { "show": False },
            "axisLine": { "show": False },
            "gridIndex": 1
            },
            {
            "scale": True,
            "gridIndex": 2
            }
        ],
        "yAxis": [
            {
            "gridIndex": 0
            },
            {
            "gridIndex": 1
            },
            {
            "type": 'category',
            "axisTick": { "show": False },
            "axisLabel": { "show": False },
            "axisLine": { "show": False },
            "gridIndex": 2
            }
        ],
        "series": [
            {
            "name": 'origianl scatter',
            "type": 'scatter',
            "xAxisIndex": 0,
            "yAxisIndex": 0,
            "encode": { "tooltip": [0, 1] },
            "datasetIndex": 0
            },
            {
            "name": 'histogram',
            "type": 'bar',
            "xAxisIndex": 1,
            "yAxisIndex": 1,
            "barWidth": '100%',
            "label": {
                "show": True,
                "position": 'top'
            },
            "encode": { "x": 0, "y": 1, "itemName": 4 },
            "datasetIndex": 1
            },
            {
            "name": 'histogram',
            "type": 'bar',
            "xAxisIndex": 2,
            "yAxisIndex": 2,
            "barWidth": '100%',
            "label": {
                "show": True,
                "position": 'right'
            },
            "encode": { "x": 1, "y": 0, "itemName": 4 },
            "datasetIndex": 2
            }
        ]
    }
    return option



def typical_day_chart(df, Title, min_y, max_y):
    '''
    Typical day with minomum, maximum, average consumption 
    time	value	date	hour	day_type
    2022-02-01 00:00:00+00:00	1.688250	2022-02-01	0.00	Workday
    2022-02-01 00:15:00+00:00	1.271972	2022-02-01	0.25	Workday
    2022-02-01 00:30:00+00:00	0.002556	2022-02-01	0.50	Workday
    2022-02-01 00:45:00+00:00	0.963417	2022-02-01	0.75	Workday
    2022-02-01 01:00:00+00:00	2.078722	2022-02-01	1.00	Workday
    '''

    # Ensure correct types
    df['time'] = pd.to_datetime(df['time'])
    df['hour'] = df['hour'].astype(float)

    # Group data for profiles
    grouped_by_hour = df.groupby('hour')['value']
    typical_profile = grouped_by_hour.mean()
    min_profile = grouped_by_hour.min()
    max_profile = grouped_by_hour.max()

    # Prepare daily series for light gray plots
    all_daily_series = []
    for date, group in df.groupby('date'):
        all_daily_series.append({
            "name": f"{date}",
            "type": "line",
            "data": group['value'].tolist(),
            "lineStyle": {"color": "lightgray", "width": 1},
            "showSymbol": False
        })

    option={
            "title": {
                "text": Title,
                "left": "center"
            },
            "tooltip": {"trigger": "axis"},
            "legend": {
                "data": ["Typical Profile", "Min Values", "Max Values"],
                "top": 30
            },
            "xAxis": {
                "type": "category",
                "name": "Hour",
                "data": sorted(df['hour'].unique())
            },
            "yAxis": {
                "type": "value",
                "name": "Value",
                "min":min_y,
                "max":max_y
            },
            "grid": {
                "left": "10%", "right": "10%", "bottom": "10%", "containLabel": True
            },
            "series": all_daily_series + [
                {
                    "name": "Typical Profile",
                    "type": "line",
                    "data": typical_profile.tolist(),
                    "lineStyle": {"color": "red", "width": 2},
                    "symbol": "none"
                },
                {
                    "name": "Min Values",
                    "type": "line",
                    "data": min_profile.tolist(),
                    "lineStyle": {"color": "blue", "type": "dashed", "width": 1},
                    "symbol": "none"
                },
                {
                    "name": "Max Values",
                    "type": "line",
                    "data": max_profile.tolist(),
                    "lineStyle": {"color": "green", "type": "dashed", "width": 1},
                    "symbol": "none"
                },
                # Daytime highlighting
                {
                    "type": "line",
                    "markArea": {
                        "silent": True,
                        "itemStyle": {"color": "yellow", "opacity": 0.2},
                        "data": [
                            [{"xAxis": 7}, {"xAxis": 20}]
                        ]
                    }
                }
            ]
        }
    
    return option



def typical_week_chart(typical_week):

   
    typical_week['hour_of_week'] = typical_week['day_of_week'] * 24 + typical_week['hour']


    # Prepare data for Dash ECharts
    x_axis = typical_week['hour_of_week'].tolist()
    mean_energy = typical_week['mean'].tolist()
    max_energy = typical_week['max'].tolist()
    min_energy = typical_week['min'].tolist()
    mean_temp = typical_week['mean_temp'].tolist()

    # Define the ECharts option
    echarts_options = {
        "title": {
            "text": "Typical Week: Energy Profiles (Mean, Max, Min) and Temperature",
            "left": "center"
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "cross"}
        },
        "legend": {
            "data": ["Mean Energy", "Max Energy", "Min Energy", "Mean Temperature"],
            "top": "5%"
        },
        "xAxis": {
            "type": "category",
            "data": x_axis,
            "name": "Hour of the Week",
            "nameLocation": "middle",
            "nameGap": 25
        },
        "yAxis": [
            {
                "type": "value",
                "name": "Energy (kWh)",
                "axisLine": {"lineStyle": {"color": "red"}},
                "splitLine": {"show": True}
            },
            {
                "type": "value",
                "name": "Temperature (°C)",
                "axisLine": {"lineStyle": {"color": "orange"}},
                "splitLine": {"show": False}
            }
        ],
        "series": [
            {
                "name": "Mean Energy",
                "type": "line",
                "data": mean_energy,
                "color": "red",
                "lineStyle": {"width": 2}
            },
            {
                "name": "Max Energy",
                "type": "line",
                "data": max_energy,
                "color": "blue",
                "lineStyle": {"type": "dashed", "width": 2}
            },
            {
                "name": "Min Energy",
                "type": "line",
                "data": min_energy,
                "color": "green",
                "lineStyle": {"type": "dashed", "width": 2}
            },
            {
                "name": "Mean Temperature",
                "type": "line",
                "data": mean_temp,
                "color": "orange",
                "yAxisIndex": 1
            }
        ],
        "dataZoom": [
            {"type": "inside", "start": 0, "end": 100},
            {"type": "slider", "start": 0, "end": 100}
        ],
        # "visualMap": [
        #     {
        #         "show": False,
        #         "type": "piecewise",
        #         "pieces": [
        #             {"gte": 7, "lte": 20, "color": "rgba(200, 200, 200, 0.1)"}
        #         ],
        #         "outOfRange": {"color": "transparent"}
        #     }
        # ]
    }

    return echarts_options



def overall_heat_map(df, days, hours):
    option = {
        "tooltip": {
            'trigger': 'item'
        },
        "grid": {
            "top": "10%",
            "left": "5%",
            "right": "5%",
            "bottom": "15%"
        },
        "xAxis": {
            "type": "category",
            "data": days,  # X-axis is now the days
            "name": "Day",
            "boundaryGap": True,
            "splitLine": {"show": True},
        },
        "yAxis": {
            "type": "category",
            "data": [str(h) for h in hours],  # Y-axis is now the hours
            "name": "Hour",
            "splitLine": {"show": True},
        },
        "visualMap": {
            "min": min([item[2] for item in df]),
            "max": max([item[2] for item in df]),
            "orient": "horizontal",
            "left": "center",
            "bottom": "0%",
            "text": ["High", "Low"],
            "calculable": True,
        },
        "series": [
            {
                "name": "Value",
                "type": "heatmap",
                "data": [[days.index(item[0]), item[1], item[2]] for item in df],
                "label": {"show": False},
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }
        ]
    }

    return option


def plot_doughnut(title_1, title_2, perc_over, perc_under):
    '''
    
    '''
    children_ = [
        dmc.Text(title_1, opacity=0.7, fw=700, c="black",mt=5),
        dmc.Title(title_2, order=3, mt=0, fw=700, c="black"),
        dash_echarts.DashECharts(
                option = doughnut_chart(round(perc_over,2),round(perc_under,2)),
                style={
                "width": '100%',
                "height": '400px',
                }
            )
    ]
    return children_

def plot_doughnut_month(title_1, title_2, data_):
    '''
    
    '''
    children_ = [
        dmc.Text(title_1, opacity=0.7, fw=700, c="black",mt=5),
        dmc.Title(title_2, order=3, mt=0, fw=700, c="black"),
        dash_echarts.DashECharts(
                option = doughnut_chart_monthly(data_),
                style={
                "width": '100%',
                "height": '400px',
                }
            )
    ]
    return children_