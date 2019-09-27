import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import grade_dict, mapbox_access_token
from processing import make_sql_request, filter_area, loc_list, clean_text

app = dash.Dash(__name__)
server = app.server

init_query = "select id, loc from boulders;"

df = make_sql_request(init_query)

df['loc_list'] = df['loc'].apply(loc_list)

loc_set = set()
for i in range(len(df)):
    for j in df.iloc[i]['loc_list']:
        if j not in loc_set:
            loc_set.add(j)

locations = sorted(list(loc_set),key=len)

def build_upper_left_panel():
    return html.Div(
        id="upper-left",
        className="six columns",
        children=[
            html.Div(
                id="grade-select-outer",
                className="control-row-2",
                children=[
                    html.Label("Select grade range"),
                    html.Div(
                        id="grade-select-rangeslider",
                        children=[
                            dcc.RangeSlider(
                                id="grade-select",
                                min=-1,
                                max=14,
                                step=1,
                                marks=grade_dict,
                                value=[1,3]
                            ),
                        ]
                    ),
                ],
            ),
            html.Div(
                id="region-select-outer",
                className="control-row-2",
                children=[
                    html.Label("Select areas"),
                    html.Div(
                        id="region-select-dropdown-outer",
                        children=[
                            dcc.Dropdown(
                                id="region-select",
                                options=[{"label": i, "value": i} for i in locations],
                                multi=True,
                                searchable=True,
                                value=['California']
                            ),
                        ]
                    ),
                ],
            ),
            html.Div(
                id="desc-container",
                className="control-row-2",
                children=[
                    html.Label("Enter a climb description or simply space-separated keywords"),
                    html.Div(
                        id="desc-input",
                        children=[
                            dcc.Input(
                                id='desc-text',
                                type='text',
                                debounce=True,
                                value='example: classic highball with mantle finish'
                            )
                        ],
                    ),
                ],
            ),
            html.Div(
                id="order-container",
                className="control-row-2",
                children=[
                    html.Label("Order by:"),
                    html.Div(
                        id="order-input",
                        children=[
                            dcc.RadioItems(
                                id='order-items',
                                options=[{'label': i, 'value': i} for i in ['Closest Match', 'Most Popular', 'Highest Rated']],
                                value='Closest Match',
                                labelStyle={'display': 'inline-block', 'margin': '10px'}
                            )
                        ],
                    ),
                ],
            ),
        ],
    )


def generate_geo_map(df, order):
    if order=='Most Popular':
        df.sort_values(by=['stars'],inplace=True)
    elif order=='Highest Rated':
        df.sort_values(by=['score'], inplace=True)

    lat = df['lat'].tolist()
    lon = df['lon'].tolist()

    zoom_scale = [5,8,11]
    deg_range = max([max(lat)-min(lat), max(lon)-min(lon)])
    if deg_range>1.5:
        zoom = zoom_scale[0]
    elif deg_range<0.5:
        zoom = zoom_scale[2]
    else:
        zoom = zoom_scale[1]

    routes = []

    for i in range(len(lat)):
        route = go.Scattermapbox(
            lat=[lat[i]],
            lon=[lon[i]],
            mode='markers',
            marker=dict(
                color="#76f2ff",
                size=10 + (10-i/2)
            ),
            opacity=0.8,
            hoverinfo="text",
            text=df.iloc[i]['name'] +', '+df.iloc[i]['rating']
            +"<br>"
            +"Stars: {}".format(df.iloc[i]['score'])
            +"<br>"
            +', '.join(df.iloc[i]['loc'][-2:])
        )
        routes.append(route)

    layout = go.Layout(
        margin=dict(l=10, r=10, t=20, b=10, pad=5),
        plot_bgcolor="#171b26",
        paper_bgcolor="#171b26",
        clickmode="event+select",
        hovermode="closest",
        showlegend=False,
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=10,
            center=go.layout.mapbox.Center(
                lat=df.lat.mean(), lon=df.lon.mean()
            ),
            pitch=5,
            zoom=zoom,
            style="mapbox://styles/plotlymapbox/cjvppq1jl1ips1co3j12b9hex",
        ),
    )

    return {"data": routes, "layout": layout}


def generate_climb_list(df,order):
    if order=='Most Popular':
        df.sort_values(by=['stars'],ascending=False,inplace=True)
    elif order=='Highest Rated':
        df.sort_values(by=['score'],ascending=False,inplace=True)

    div_list = []
    for i in range(len(df)):
        route = df.iloc[i]
        curr_div = html.Div(
            className='img-table-outer',
            children=[
                html.P(
                    children=[
                        dcc.Link(
                            href=route['url'],
                            style={'target': '_blank'},
                            children=[
                                html.Img(
                                    className='img-table',
                                    src=route['imgsmall'],
                                )
                            ]
                        ),
                        html.P(route['name']+', '+route['rating']),
                        html.P("Stars: {}".format(route['score'])),
                        html.P(', '.join(route['loc'][-2:])),
                        html.P(route['description'])
                    ]
                )
            ]
        )
        div_list.append(curr_div)

    return div_list


app.layout = html.Div(
    className='container scalable',
    children=[
        html.Div(
            id='banner',
            className='banner',
            children=[
                html.H2("Route Scout"),
            ]
        ),
        html.Div(
            id='intro',
            children=[
                html.H6("A tool for helping climbers find their perfect route.")
            ]
        ),
        html.Div(
            id='upper-container',
            className='row',
            children=[
                build_upper_left_panel(),
                html.Div(
                    id="geo-map-outer",
                    className="six columns",
                    children=[
                        html.P(
                            id="map-title",
                            children="Locations of recommended climbs"
                        ),
                        html.Div(
                            id="geo-map-loading-outer",
                            children=[
                                dcc.Loading(
                                    id="loading",
                                    children=dcc.Graph(
                                        id="geo-map",
                                        figure={
                                            "data": [],
                                            "layout": dict(
                                                plot_bgcolor="#171b26",
                                                paper_bgcolor="#171b26",
                                            ),
                                        },
                                    ),
                                )
                            ],
                        ),
                    ],
                ),
            ]
        ),
        html.Div(
            id="lower-container",
            children=[
                html.Div(
                    id='climb-list',
                )
            ],
        ),
    ]
)

@app.callback(
    [
    Output('geo-map', 'figure'),
    Output('climb-list','children')
    ],
    [
    Input('grade-select', 'value'),
    Input('region-select', 'value'),
    Input('desc-text', 'value'),
    Input('order-items', 'value')
    ]
)
def filter_and_process_df(grade_range, region_list, desc, order):
    if not region_list:
        region_list = ['California']

    grade_min = grade_range[0]
    grade_max = grade_range[1]

    df['loc_bool'] = df['loc_list'].apply(lambda x: filter_area(region_list, x))
    id_list = list(df.loc[df['loc_bool'],'id'])
    id_str = '(' + ','.join([str(i) for i in id_list]) + ')'

    filter_query = """
        SELECT ID, IMGSMALL, NAME, LAT, LON, LOC, RATING, DESCRIPTION, SCORE, STARS, URL
        FROM boulders WHERE ID IN {} AND RATING_NUM BETWEEN {} AND {}
        """.format(id_str, grade_min, grade_max)

    df_filtered = make_sql_request(filter_query)

    df_filtered['cleansed'] = df_filtered['description'].apply(clean_text)

    desc_series = df_filtered['cleansed'].append(pd.Series(clean_text(desc),index=[999999999]))

    vectorizer = TfidfVectorizer(decode_error='ignore')
    counts = vectorizer.fit_transform(desc_series)

    cs = cosine_similarity(counts)
    last_idx = cs.shape[0] - 1

    df_filtered['cs'] = cs[last_idx,:last_idx]
    df_filtered.sort_values(by='cs',ascending=False,inplace=True)

    return generate_geo_map(df_filtered.head(20), order), generate_climb_list(df_filtered.head(20), order)


if __name__ == '__main__':
    app.run_server(debug=True)
