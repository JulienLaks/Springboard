import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np

from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
from datetime import timedelta

import base64

app = dash.Dash(__name__)


#Load Dataframe
df=pd.read_csv("paris_traffic_2016.csv")


#Convert timestamp and date to timestamp
df["timestamp"]=pd.to_datetime(df["timestamp"])
df["date"]=pd.to_datetime(df["date"])

#drop flow rate
#df=df.drop("flow_rate",axis=1)

#Mapbox Token
mapbox_token="pk.eyJ1IjoibWF6ZXBwIiwiYSI6ImNrYmdudnlhbDBsMm4ycm1sdnAzY3RvN2IifQ.MKMZZ8WP8JJ1CCcUOv0XGw"

image_filename = 'PARIS_LOGO.jpg' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read()).decode('ascii')



app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="twelve columns div-for-title",
                    children=[

                        html.Div(
                            className="two columns div-for-title",
                            children=[
                                html.Img(
                                className="logo", src=app.get_asset_url("image3.png")
                                 ),
                            ],
                        ),


                        html.Div(
                            className="four columns div-for-title",
                            children=[
                                html.H1(
                                "PARIS TRAFFIC DASHBAORD"
                                ),
                            ],style={"padding-top":32,"padding-left":30}
                        ),

                    ],

                ),

	            # Div for map
                html.Div(
                    className="seven columns div-for-map",
                    children=[

                        html.Div(
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    min_date_allowed=dt(2016, 1, 1),
                                    max_date_allowed=dt(2016, 3, 30),
                                    initial_visible_month=dt(2016, 1, 15),
                                    date=dt(2016, 1, 15).date(),
                                    display_format="MMMM D, YYYY",
                                                    )
                            ],
                        ),

                        html.Div([
                            dcc.Graph(
                                id="map-graph",
                                hoverData={'points': [{'customdata': 5786}]}
                            )
                        ]),

                        html.Div([
                            dcc.Slider(
                                    id="hour-slider",
                                    min=0,
                                    max=23,
                                    step=1,
                                    marks={ i: {"label": str(i) + ":00" , 'style':{'transform':'rotate(60deg)'}} for i in range(24)},
                                    value=12,                            
                             ),
                        ],style={
                            'padding-top':20,
                            'padding-bottom':10,
                            "border":"0.5px solid #dbdbdb44",
                            "background": "#31302F",
                            "border-radius": "3px"}            
                        ),

                        html.Div(" ",
                            style={
                            "background": "#1a1c23",
                            'padding-left':10,
                            'padding-top':8,
                            'padding-bottom':8,
                            }),

                    ],
                ),

                # Div for charts
                html.Div(
                    className="four columns div-for-charts",
                    children=[

                        html.Div("Traffic rate of hover location",
                            style={
                                "background": "#31302F",
                                "border":"0.5px solid #dbdbdb44",
                                'padding-left':10,
                                'padding-top':8,
                                'padding-bottom':8,
                                "border-radius": "3px"}),

                        html.Div([
                            dcc.Graph(id="time-series"),
                        ],style={
                            "background": "#1E1E1E",
                            "border":"0.5px solid #dbdbdb44",
                            'padding-top':25,
                            'padding-left':15,
                            'padding-right':15,
                            },
                        ),


                        html.Div("Traffic distribution plot",
                            style={
                            "background": "#31302F",
                            "border":"0.5px solid #dbdbdb44",
                            'padding-left':10,
                            'padding-top':8,
                            'padding-bottom':8,
                            "border-radius": "3px"}),

                         html.Div([
                            dcc.Graph(id="histogram"),
                        ],style={
                            "background": "#1E1E1E",
                            "border":"0.5px solid #dbdbdb44",
                            'padding-top':25,
                            'padding-left':15,
                            'padding-right':15},
                        ),
                    ],
                ),
            ],
        )
    ]
)

@app.callback(
    Output("map-graph", "figure"),
    [
        Input("date-picker", "date"),Input("hour-slider","value")
    ],
)
def update_graph(date_picked,hour_picked):
    zoom = 12
    latInitial = 48.8566
    lonInitial = 2.3522
    bearing = 0

    picked_df=df[(df["date"]==date_picked) & (df["hour"]==hour_picked)].dropna()

    return go.Figure(
        data=[
            # Data for all rides based on date and time
             go.Scattermapbox(
                lon = picked_df["longitude"],
                lat = picked_df["latitude"],
                mode = 'markers',
                marker = dict(
                size= abs(picked_df["occupation_rate"])/3,
                color=picked_df["occupation_rate"],
                #colorscale=[[0, 'rgb(175, 238, 238)'],[0.5, 'rgb(175, 238, 238)']],
                colorscale='RdBu',
        		cmax=60,
        		cmin=0,
        		#reversescale=True
        		),
                text=picked_df["road_name"],
                customdata=picked_df["location_ID"]

            ),
        ],

        layout=Layout(
                height=400,
                margin=go.layout.Margin(l=0, r=0, t=0, b=0),
                showlegend = False,
                mapbox = {
                    'accesstoken' : mapbox_token,
                    'center': {'lon': 2.3522, 'lat': 48.8566},
                    'style' : "dark",
                    'zoom': 10.5},

               ),
        )

@app.callback(
    Output("histogram", "figure"),
    [
        Input("date-picker", "date"),Input("hour-slider","value")
    ],
)
def update_histogram(date_picked,hour_picked):
    picked_df=df[(df["date"]==date_picked) & (df["hour"]==hour_picked)].dropna()

    picked_df["category"]=pd.cut(picked_df["occupation_rate"], bins=np.linspace(0, 60, 21),labels=np.linspace(5, 60, 20))
    picked_df=pd.DataFrame(picked_df.groupby("category").size()).reset_index()

    import plotly.express as px

    fig = go.Figure()

    fig.add_trace(go.Bar(
                    x=picked_df["category"],
                    y=picked_df[0],
                    marker_color='indianred'
                ))

    fig.update_layout(
        height=185, 
        margin=go.layout.Margin(l=0, r=0, t=0, b=0),
        yaxis=dict(color="grey"),
        xaxis=dict(color="grey"),

        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    ),

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(zeroline=False,gridwidth=0.1, gridcolor='grey')
 
    return fig



@app.callback(
    Output("time-series", "figure"),
    [
        Input("map-graph", "hoverData"),Input("date-picker","date")
    ],
)
def update_times_series(hoverData,date):
    location_ID = hoverData['points'][0]['customdata']
    picked_df=df[df["location_ID"]==location_ID].dropna()

    picked_df=picked_df[(picked_df["date"] >= pd.Timestamp(date)-pd.Timedelta(2,unit="D")) & (picked_df["date"] <= pd.Timestamp(date) + pd.Timedelta(2,unit="D"))]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=picked_df["timestamp"], 
            y=picked_df["occupation_rate"],
            mode='lines',
            name='lines',
            line=dict(color="#ec7063", width=1.2),
        ))

    fig.update_layout(
        height=190, 
        margin=go.layout.Margin(l=0, r=0, t=0, b=0),
        yaxis=dict(color="grey"),
        xaxis=dict(color="grey"),

        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    ),

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(zeroline=False,gridwidth=0.1, gridcolor='grey')



    return fig


if __name__ == "__main__":
    app.run_server(host = '127.0.0.1')

