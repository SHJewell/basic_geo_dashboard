import dash
from dash import html as dhtml
from dash import dcc, Input, Output, State
from dash.dash_table.Format import Format, Scheme
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
# import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from pprint import pprint

#non-plotly imports
import open_nc
import numpy as np

'''
========================================================================================================================
Data
'''

# laptop
# files = {
#     'temp_max': "C:\\Datasets\\Weather Data\\Copernicus\\Temp Max\\tasmaxAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20160101-20201231.nc",
#     'temp_mean': "C:\\Datasets\\Weather Data\\Copernicus\\Temp Mean\\tasAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20160101-20201231.nc",
#     'temp_min': "C:\\Datasets\\Weather Data\\Copernicus\\Temp Min\\tasminAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20160101-20201231.nc",
#     'precip': "C:\\Datasets\\Weather Data\\Copernicus\\Precip Flux\\prAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20160101-20201231.nc"
#     }
# desktop
# files = {
#     'temp_max': "/media/disc1/Datasets/Weather Data/Copernicus/Temp Max/tasmaxAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc",
#     'temp_mean': "/media/disc1/Datasets/Weather Data/Copernicus/Temp Mean/tasAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc",
#     'temp_min': "/media/disc1/Datasets/Weather Data/Copernicus/Temp Min/tasminAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc",
#     'precip': "/media/disc1/Datasets/Weather Data/Copernicus/Precip Flux/prAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc"
# }

# small files
# files = {
#     'temp_max': "./data/tasmaxAdjust_20010101-20010201.nc",
#     'temp_mean': "./data/tasAdjust_20010101-20010201.nc",
#     'temp_min': "./data/tasminAdjust_20010101-20010201.nc",
#     'precip': "./data/prAdjust_20010101-20010201.nc"
# }

# var_names = {'temp_max': 'tasmaxAdjust',
#              'temp_min': 'tasminAdjust',
var_names = {'temp_mean': 'tasAdjust',
             'precip': 'prAdjust'}

# human_names = {'temp_max':      'Temperature Max',
#                'temp_min':      'Temperature Min',
human_names = {'temp_mean':     'Temperature Mean',
               'precip':        'Precipitation'}

# dropdown_datasets = [#{'label':  '',     'value':   'none'},
#              {'label':  'Temperature Max',     'value':   'temp_max'},
#              {'label':  'Temperature Min',     'value':   'temp_min'},
#              {'label':  'Temperature Mean',    'value':   'temp_mean'},
#              {'label':  'Precipitation',       'value':   'precip'}
#              ]

dropdown_datasets = [#{'label':  '',     'value':   'none'},
             {'label':  'Temperature Mean',    'value':   'temp_mean'},
             {'label':  'Precipitation',       'value':   'precip'}
             ]

#default_group = open_nc.multiVarNCSet('./data/master_20010101-20010201.nc', var_names)
#default_group = open_nc.multiVarNCSet('/home/shjewell/PycharmProjects/basic_geo_dashboard/data/master_20010101-20051231.nc', var_names)
#default_group = open_nc.multiVarNCSet('./data/master-20200101-1-20201231.nc', var_names)
default_group = open_nc.multiVarNCSet('/media/disc1/Datasets/Weather Data/Processed/stats-20200101-1-20201231.nc', var_names)
df = default_group.flatten_at_single_time('temp_mean')
lats = default_group.lats
lons = default_group.lons

'''
========================================================================================================================
Dashboard

There are two options for mapping: using the mapping functions in Plotly, but these are slow

And using a heatmap, which is fast. Maybe giving the user the option to switch between these would be good?
'''

graph_config = {'modeBarButtonsToRemove' : ['hoverCompareCartesian', 'select2d', 'lasso2d'],
                'doubleClick':  'reset+autosize', 'toImageButtonOptions': { 'height': None, 'width': None, },
                'displaylogo': False}

colors = {'background': '#111111', 'text': '#7FDBFF'}

app = dash.Dash(__name__,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                external_stylesheets=[dbc.themes.SLATE])
# server = app.server

ts = go.Figure()
ts.update_layout(paper_bgcolor='#515960', plot_bgcolor='#515960',
                 font_color='white',
                 margin=dict(l=5, r=5, t=5, b=5))

analysis_tab = dbc.Card(
    dbc.CardBody(id='analysis-card',
        children=[
            dbc.Row([dhtml.H2(f'Click map to plot time series', id='loc_label')]),
            dbc.Row([
                dcc.Loading(dcc.Graph(id='time_series', figure=ts))
            ])
        ]
    )
)

map = go.Figure()
map.add_heatmap(x=lons, y=lats, z=df, hovertemplate='Temp: %{z:.2f}°C<br>Lat: %{y:.2f}<br>Lon: %{x:.2f}')
map.update_layout(paper_bgcolor='#515960', plot_bgcolor='#515960',
                  font_color='white',
                  margin=dict(l=5, r=5, t=5, b=5))

map_page = dbc.Card(
    dbc.CardBody(id='map_container',
        children=[
            dbc.Row([
                dbc.Col(
                    children=[
                        dcc.Dropdown(id='set-select', options=dropdown_datasets, value='temp_mean'),
                        dhtml.H2(f'Date: {default_group.t[0]}', id='map-date'),
                        dcc.Slider(id='time_slider',
                                   min=default_group.slider_dict[default_group.t[0]],
                                   max=default_group.slider_dict[default_group.t[-1]],
                                   marks=default_group.slider_marks,
                                   value=0,
                                   tooltip={"always_visible": False}
                                   ),
                        dcc.Loading(dcc.Graph(id='mapbox', figure=map))],
                        width=6),
                dbc.Col(analysis_tab, width=6)
            ])
        ]
    )
)


app.layout = dhtml.Div([
    dbc.CardBody(
        id='main_card',
        children=[dbc.Card(map_page)]
    )
])

'''
========================================================================================================================
Callbacks
'''

@app.callback(
    [Output('time_series', 'figure'),
    Output('loc_label', 'children')],
    Input('mapbox', 'clickData'),
    State('set-select', 'value')
)
def plot_time_series(points, set):

    if points == None:
        return dash.no_update

    ts = default_group.ret_time_series(set, points['points'][0]['x'], points['points'][0]['y'])

    axis_label = 'Precipitiation (kg m-2 s-1)'
    hovertxt = '%{x|%m/%d/%Y}<br>%{y:.5f} kg m-2 s-1'

    if 'temp' in set:
        #hovertxt = '%{x|%m/%d/%Y}<br>%{y:.2f}°C'
        hovertxt = '%{x|%m/%d/%Y}<br>%{y:.2f}K'
        #axis_label = 'Temperature (°C)'
        axis_label = 'Temperature (K)'

    plt = go.Figure(go.Scatter(y=ts['dat'], x=default_group.t,
                               mode='markers', hovertemplate=hovertxt,
                               name='Daily'))
    #plt.add_trace(go.Scatter(y=ts['5day'], x=default_group.dates['dt'], hovertemplate=hovertxt))
    plt.add_trace(go.Scatter(y=ts['14day'], x=default_group.t, hovertemplate=hovertxt, name='14-day Average'))

    plt.update_layout(paper_bgcolor='#515960', plot_bgcolor='#515960',
                      font_color='white',
                      margin=dict(l=5, r=5, t=5, b=5), yaxis_title=axis_label,
                      hovermode='x', legend=dict(yanchor='top', y=0.95, xanchor='right', x=0.99))

    label = f'{human_names[set]} at {points["points"][0]["x"]}, {points["points"][0]["y"]}'

    return plt, label

@app.callback(
    [Output('map-date', 'children'),
     Output('mapbox', 'figure'),
     Output('time_slider', 'value')],
    [Input('time_slider', 'value'),
     Input('set-select', 'value')]
)
def map_single_time(date, set):

    date = round(date)
    new_df = default_group.flatten_at_single_time(set, default_group.t[date])
    lats = default_group.lats
    lons = default_group.lons

    hovertxt = 'Precip: %{z:.5f} kg m-2 s-1<br>Lat: %{y:.2f}<br>Lon: %{x:.2f}'

    if 'temp' in set:
        #hovertxt = 'Temp: %{z:.2f}°C<br>Lat: %{y:.2f}<br>Lon: %{x:.2f}'
        hovertxt = 'Temp: %{z:.2f}K<br>Lat: %{y:.2f}<br>Lon: %{x:.2f}'

    map = go.Figure(data=go.Heatmap(x=lons, y=lats, z=new_df,
                                    hovertemplate=hovertxt))
    map.update_layout(paper_bgcolor='#515960', plot_bgcolor='#515960',
                      font_color='white',
                      margin=dict(l=5, r=5, t=5, b=5))

    map_date = f'Date: {default_group.t[date]}'

    return map_date, map, date

if __name__ == '__main__':
    app.run_server(debug=True)
