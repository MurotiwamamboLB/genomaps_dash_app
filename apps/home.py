import dash
from dash import dcc
from dash import html
from app import app


layout = html.Div(children=[
	
   # body block starts

   html.Div([

	html.H2(["Welcome to the engineering plasmid and phage maps generator!"]),
    html.H6(["Generate annotated engineering plasmid maps."]),
    html.H6(["Generate annotated engineered phage maps."]),
    html.H6(["All inputs and outputs are in the GenBank file format."]),
    html.H6(["Download your results in real time."]),
    ], className = "body-text"),

   # body block ends

])

