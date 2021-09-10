import dash
import dash_core_components as dcc
import dash_html_components as html
# import plotly.express as px
# import pandas as pd
from app import app


layout = html.Div(children=[

	
   # body block starts

   html.Div([

	html.H1(["Welcome to the engineering plasmid and phage maps generator!"]),
    html.P(["Generate annotated engineering plasmid maps."]),
    html.P(["Generate annotated engineered phage maps."]),
    html.P(["All input and out is in the GenBank file format which  can be imported and exported to Benching and Genius."]),
    html.P(["Download your results real time or find it later in the Locus Store Front."]),
    ], className = "body-text"),

   # body block ends


])

