import dash
from dash import html as dhtml
from dash import dcc, Input, Output, State
from dash.dash_table.Format import Format, Scheme
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
# import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash_leaflet as dl

from pprint import pprint

#non-plotly imports
import open_nc
import numpy as np

'''
========================================================================================================================
Data
'''

# files = {
#     'temp_max': "C:\\Datasets\\Weather Data\\Copernicus\\Temp Max\\tasmaxAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20160101-20201231.nc",
#     'temp_mean': "C:\\Datasets\\Weather Data\\Copernicus\\Temp Mean\\tasAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20160101-20201231.nc",
#     'temp_min': "C:\\Datasets\\Weather Data\\Copernicus\\Temp Min\\tasminAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20160101-20201231.nc",
#     'precip': "C:\\Datasets\\Weather Data\\Copernicus\\Precip Flux\\prAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20160101-20201231.nc"
#     }
files = {
    'temp_max': "/media/disc1/Datasets/Weather Data/Copernicus/Temp Max/tasmaxAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc",
    'temp_mean': "/media/disc1/Datasets/Weather Data/Copernicus/Temp Mean/tasAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc",
    'temp_min': "/media/disc1/Datasets/Weather Data/Copernicus/Temp Min/tasminAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc",
    'precip': "/media/disc1/Datasets/Weather Data/Copernicus/Precip Flux/prAdjust_day_GFDL-ESM2G_SMHI-DBSrev930-GFD-1981-2010-postproc_rcp45_r1i1p1_20010101-20051231.nc"
}
var_names = {'temp_max': 'tasmaxAdjust',
             'temp_min': 'tasminAdjust',
             'temp_mean': 'tasAdjust',
             'precip': 'prAdjust'}

dropdown_datasets = [#{'label':  '',     'value':   'none'},
             {'label':  'Temp Max',     'value':   'temp_max'},
             {'label':  'Temp Min',     'value':   'temp_min'},
             {'label':  'Temp Mean',    'value':   'temp_mean'},
             {'label':  'Precip',       'value':   'precip'}
             ]

default_group = open_nc.NCSet(files['temp_mean'], var_names['temp_mean'])
df = default_group.flatten_to_latlons()

'''
========================================================================================================================
Dashboard

There are two options for mapping: using the mapping funcitons in Plotly, but these are slow

And using a heatmap, which is fast. Maybe giving the user the option to swtich between these would be good?
'''

graph_config = {'modeBarButtonsToRemove' : ['hoverCompareCartesian', 'select2d', 'lasso2d'],
                'doubleClick':  'reset+autosize', 'toImageButtonOptions': { 'height': None, 'width': None, },
                'displaylogo': False}

colors = {'background': '#111111', 'text': '#7FDBFF'}

app = dash.Dash(__name__,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                external_stylesheets=[dbc.themes.SLATE])
# server = app.server

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

            # dhtml.H2(),
            # dcc.Tabs(
            #     children=[
            #     dcc.Tab(label='Primary', id='primary_var',
            #         children=[
            #         dash_table.DataTable(id='analysis_table1',
            #                              cell_selectable=False,
            #                              style_table={'backgroundColor': colors['background'],
            #                                           'overflow'       :'auto'},
            #                              style_cell={'backgroundColor': colors['background'],
            #                                          'textColor':       colors['text']}
            #                              )
            #             ]),
            # dcc.Tab(label='Secondary', id='secondary_var',
            #         children=[
            #             dash_table.DataTable(id='analysis_table2',
            #                                  cell_selectable=False,
            #                                  style_table={'backgroundColor': colors['background'],
            #                                               'overflow': 'auto'},
            #                                  style_cell={'backgroundColor': colors['background'],
            #                                              'textColor': colors['text']}
            #                                  )
            #         ])
            # ])

map = go.Figure()
map.add_scattergeo(
#map.add_scattermapbox(
        lat=df[:, 2], lon=df[:, 1], text=df[:, 0], marker_color=df[:, 0]
)


# prawl_map = go.Figure(data=px.scatter_geo(
#     # data_frame=lat_lon_df,
#     data_frame=default_group.data[0,:,:],
#     lat=default_group.lats,
#     lon=default_group.lons,
#     # size=lat_lon_df['size'],
#     size_max=5,
#     opacity=1,
#     # hover_name='name'
#     # hover_data={'lat': False, 'lon': False},
#
# #     hover_data={'size': False},
# #    color=df['type'],
# #    color_discrete_sequence=px.colors.qualitative.D3
# ))


map.update_layout(
    autosize=True,
    #width=1200,
    #height=700,
    margin=dict(l=5, r=5, b=5, t=5),
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text'],
    legend_title_text='',
    legend=dict(
        yanchor='top',
        y=0.99,
        xanchor='right',
        x=0.99
    ),
    geo=dict(
        showland=True,
        landcolor="slategray",
        showocean=True,
        oceancolor='gray',
        subunitcolor="slategray",
        countrycolor="slategray",
        showlakes=True,
        lakecolor="slategray",
        showsubunits=True,
        showcountries=True,
        showframe=False,
        scope='world',
        resolution=50,
        projection=dict(
            #type='conic conformal',    # the conda version doesn't have this one.
            type='transverse mercator'
            #rotation_lon=-100
        ),
        lonaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            range=[-130.0, -60.0],
            dtick=5
        ),
        lataxis=dict(
            showgrid=True,
            gridwidth=0.5,
            range=[20.0, 50.0],
            dtick=5
        )
    )
)

analysis_tab = dbc.Card(
    dbc.CardBody(id='analysis-card',
        children=[
            dbc.Row([
                dhtml.Button('Print', id='printer', n_clicks=0),
                dcc.Textarea(id='text', value='Ready')
            ])
        ]
    )
)

map_page = dbc.Card(
    dbc.CardBody(id='map_container',
        children=[
            dbc.Row([
                #dbc.Col(analysis_tools_card, width=4),
                dbc.Col(analysis_tab, width=4),
                dbc.Col(dcc.Graph(id='mapbox', figure=map), width=8)
            ])
        ]
    )
)

app.layout = dhtml.Div([
    dbc.CardBody(
        id='main_card',
        children=[
            dbc.Card(
                map_page
            )
        ]
    )
])

'''
========================================================================================================================
Callbacks
'''


@app.callback(
    Output(component_id='text', component_property='value'),
    #Input(component_id='printer', component_property='n_clicks'),
    Input(component_id='mapbox', component_property='figure')
    #State(component_id='mapbox', component_property='figure')
)
def info_dump(mapbox):
    # n += 1
    # pprint(mapbox['data'].keys(), mapbox['layout'].keys())
    # return f'{n} clicks \n' \
    return f'{mapbox["layout"]["geo"]["lonaxis"]["range"]}\n{mapbox["layout"]["geo"]["lataxis"]["range"]}'

if __name__ == '__main__':
    #app.run_server(host='0.0.0.0', port=8050, debug=True)
    app.run_server(debug=True)