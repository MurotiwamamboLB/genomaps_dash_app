import dash
from dash import dcc
from dash import html
from app import app


layout = html.Div(children=[
	
   # body block starts

   html.Div([

	html.H2(["Welcome to the engineering plasmid and phage maps generator!"]),
    html.P(["Generate annotated engineering plasmid maps."]),
    html.P(["Generate annotated engineered phage maps."]),
    html.P(["All input and out is in the GenBank file format."]),
    html.P(["Download your results real time."]),
    ], className = "body-text"),

   # body block ends

])

