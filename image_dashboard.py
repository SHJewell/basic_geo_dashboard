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

# server
files = {
    'temp_max': "/data/tasmaxAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc",
    'temp_mean': "/data/tasAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc",
    'temp_min': "/data/tasminAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc",
    'precip': "/data/prAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc"
}
# for vm
# files = {
#     'temp_max': "./data/tasmaxAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc",
#     'temp_mean': "./data/tasAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc",
#     'temp_min': "./data/tasminAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc",
#     'precip': "./data/prAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc"
# }

var_names = {'temp_max': 'tasmaxAdjust',
             'temp_min': 'tasminAdjust',
             'temp_mean': 'tasAdjust',
             'precip': 'prAdjust'}

human_names = {'temp_max':      'Temperature Max',
               'temp_min':      'Temperature Min',
               'temp_mean':     'Temperature Mean',
               'precip':        'Precipitation'}

dropdown_datasets = [#{'label':  '',     'value':   'none'},
             {'label':  'Temperature Max',     'value':   'temp_max'},
             {'label':  'Temperature Min',     'value':   'temp_min'},
             {'label':  'Temperature Mean',    'value':   'temp_mean'},
             {'label':  'Precipitation',       'value':   'precip'}
             ]

default_group = open_nc.NCSet(files['temp_mean'], var_names['temp_mean'])
df = default_group.flatten_at_single_time()
dat = default_group.t
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
            dbc.Col([
                dbc.Row([
                    dcc.Slider(id='time_slider',
                               min=default_group.dates.index.min(),
                               max=default_group.dates.index.max(),
                               marks=default_group.slider_dict(),
                               value=default_group.dates.index.min())
                ])
            ]),
            dbc.Row([dhtml.H2(f'No point selected', id='loc_label')]),
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
                        dhtml.H2(f'Date: {default_group.dates["dt"].min().date()}', id='map-date'),
                        dcc.Dropdown(id='set-select', options=dropdown_datasets, value='temp_mean'),
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

    new_group = open_nc.NCSet(files[set], var_names[set])
    ts = new_group.ret_time_series(points['points'][0]['x'], points['points'][0]['y'])

    axis_label = 'Precipitiation (kg m-2 s-1)'
    hovertxt = '%{x|%m/%d/%Y}<br>%{y:.5f} kg m-2 s-1'

    if 'temp' in set:
        hovertxt = '%{x|%m/%d/%Y}<br>%{y:.2f}°C'
        axis_label = 'Temperature (°C)'

    plt = go.Figure(go.Scatter(y=ts['dat'], x=new_group.dates['dt'],
                               mode='markers', hovertemplate=hovertxt,
                               name='Daily'))
    #plt.add_trace(go.Scatter(y=ts['5day'], x=new_group.dates['dt'], hovertemplate=hovertxt))
    plt.add_trace(go.Scatter(y=ts['14day'], x=new_group.dates['dt'], hovertemplate=hovertxt, name='14-day Average'))

    plt.update_layout(paper_bgcolor='#515960', plot_bgcolor='#515960',
                      font_color='white',
                      margin=dict(l=5, r=5, t=5, b=5), yaxis_title=axis_label,
                      hovermode='x', legend=dict(yanchor='top', y=0.95, xanchor='right', x=0.99))

    label = f'{human_names[set]} at {points["points"][0]["x"]}, {points["points"][0]["y"]}'

    return plt, label

@app.callback(
    [Output('map-date', 'children'),
     Output('mapbox', 'figure')],
    [Input('time_slider', 'value'),
     Input('set-select', 'value')]
)
def map_single_time(date, set):

    new_group = open_nc.NCSet(files[set], var_names[set])
    new_df = new_group.flatten_at_single_time(date)
    lats = new_group.lats
    lons = new_group.lons

    hovertxt = 'Precip: %{z:.5f} kg m-2 s-1<br>Lat: %{y:.2f}<br>Lon: %{x:.2f}'

    if 'temp' in set:
        hovertxt = 'Temp: %{z:.2f}°C<br>Lat: %{y:.2f}<br>Lon: %{x:.2f}'

    map = go.Figure(data=go.Heatmap(x=lons, y=lats, z=new_df,
                                    hovertemplate=hovertxt))
    map.update_layout(paper_bgcolor='#515960', plot_bgcolor='#515960',
                      font_color='white',
                      margin=dict(l=5, r=5, t=5, b=5))

    map_date = f'Date: {new_group.dates.at[date, "dt"].date()}'

    return map_date, map

if __name__ == '__main__':
    app.run_server(debug=True)

# tools_card = dbc.Card([
#     dbc.CardBody(
#         dash_table.DataTable(id='map-table',
#                              row_selectable='single',
#                              cell_selectable=False,
#                              style_table={'backgroundColor': colors['background'],
#                                           'overflow'       :'auto'},
#                              style_cell={'backgroundColor': colors['background'],
#                                          'textColor':       colors['text']}
#                              )
#     )]
# )

#
# table_card = dbc.Card([
#     dbc.CardBody(
#         children=[dcc.Textarea(id='t_mean',
#                                value='',
#                                readOnly=True,
#                                style={'width': '100%', 'height': 40,
#                                       'textColor':       colors['text']},
#                                ),
#                   dash_table.DataTable(id='dtable',
#                                        style_table={'backgroundColor': colors['background'],
#                                                     'height'         :'380px',
#                                                     'overflowY'       :'auto'},
#                                        style_cell={'backgroundColor': colors['background'],
#                                                    'textColor':       colors['text']}
#                   )
#         ])
# ])

# analysis_graph_card = dbc.Card(
#     [dbc.CardBody([
#         dcc.Loading(
#             dcc.Graph(id='analysis_graph')
#         )
#     ])]
# )

# analysis_tools_card = dbc.Card([
#     dbc.CardBody(
#         children=[
#             dhtml.H5('Datasets'),
#             dcc.Dropdown(id='datasets',
#                          options=dropdown_datasets,
#                          value='temp_mean'
#                         )
#         ]
#     )]
# )