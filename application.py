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

var_names = {'temp_max': 'tasmaxAdjust',
             'temp_min': 'tasminAdjust',
             'temp_mean': 'tasAdjust',
             'precip': 'prAdjust'}

human_names = {'temp_max':      'Temperature Max',
               'temp_min':      'Temperature Min',
               'temp_mean':     'Temperature Mean',
               'precip':        'Precipitation'}

dropdown_datasets = [{'label':  'Temperature Max',     'value':   'temp_max'},
             {'label':  'Temperature Min',     'value':   'temp_min'},
             {'label':  'Temperature Mean',    'value':   'temp_mean'},
             {'label':  'Precipitation',       'value':   'precip'}
             ]

default_group = open_nc.multiVarNCSet('master-20200101-1-20200131.nc', var_names)
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
application = app.server
app.title = "Basic Geospatial Dashboard"


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
                                   #min=default_group.sliderDF.min(),
                                   #max=default_group.t[-1],
                                   #marks=default_group.t,
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

header = dhtml.Div([
    dbc.Collapse(
        dbc.Card(
            dbc.CardBody(id="header",
                         children=[
                             dbc.Row([
                                 dhtml.H5("Hello! Thank you for visiting my Kalman filter dashboard."),
                                 dhtml.H5("I have recieved a large increase in traffic recently. While this is flattering, it "
                                          "is also increasing the cost to host these demos. As such, I am going to to have to "
                                          "limit the resources available to run them. Reliability and responsivity may suffer "
                                          "as a result."),
                                 dhtml.H5("Sorry for any inconvenience"),
                                 dhtml.H5(""),
                                 dbc.Row([
                                     dhtml.H5("The source code is available on my github: "),
                                     dcc.Link(href="https://github.com/SHJewell/kalman_dashboard")
                                 ]),
                                 dhtml.H5("Feel free to rehost but please let me know. ATTN: Dashboards, scott.hjewell@gmail.com"),
                                 dhtml.H5(""),
                                 dhtml.H5("If you would like a custom dashboard, my firm is available to discuss your needs"),
                                 dcc.Link("Jewell GeoServices", href="https://jewellgeo.services"),
                                 dhtml.H5(""),
                                 dcc.Link("Otherwise, feel free to buy me a coffee.", href="https://www.buymeacoffee.com/shjewell")
                         ])
                     ])
        ),
        id="collapse",
        is_open=True
    ),
    dbc.Button(
        "Hide",
        id="hide-button",
        color="primary",
        n_clicks=0
    )
])


app.layout = dhtml.Div([
    dbc.CardBody(
        id='main_card',
        children=[header,
                  dbc.Card(map_page),
                  dcc.Link('By SHJewell', href=f'https://shjewell.com'),
                  dhtml.H6(f'Built using Python and Plotly Dash'),
                  dcc.Link('Source code', href=f'https://github.com/SHJewell/basic_geo_dashboard')
                  ]
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
    plt.add_trace(go.Scatter(y=ts['5day'], x=default_group.t, hovertemplate=hovertxt, name='5-day Average'))
    #plt.add_trace(go.Scatter(y=ts['14day'], x=default_group.t, hovertemplate=hovertxt, name='14-day Average'))

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


@app.callback(
    Output("collapse", "is_open"),
    [Input("hide-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



if __name__ == '__main__':
    #app.run_server(debug=True)
    application.run(port=8080)
