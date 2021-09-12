import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect to app pages
from apps import home,plasmid_map, phage_map, both_map


app.layout = html.Div([

    # header block starts

    html.Div(children = [

        # logo block starts 

        html.Img(src="assets/logo_1.png", className = "logo"),


        # menu bar begins
        dcc.Location(id='url', refresh=False),
        dcc.Location(id='url-phage_map', refresh=False),
        dcc.Location(id='url-plasmid_map', refresh=False),
        dcc.Location(id='url-both_maps', refresh=False),

        html.Div([
            dcc.Link('HOME', href='/apps/home', id = "home-link"),
            dcc.Link('GENERATE PLASMID MAPS', href='/apps/plasmid_map', id = "plasmid_map_link"),
            dcc.Link('GENERATE PHAGE MAPS', href='/apps/phage_map', id = "phage_map_link"),
            dcc.Link('GENERATE BOTH MAPS', href='/apps/both_map', id = "both_map_link"),
        ], className="menu-bar"),
        # menu bar ends 

    ], className = "header"),
    # header block ends 

    # body block starts 
    html.Div(id='page-content')
    # body block ends 

], className = "main-container")



@app.callback([
    Output('page-content', 'children'),
    Output('home-link', 'className'),
    Output('plasmid_map_link', 'className'),
    Output('phage_map_link', 'className'),
    Output('both_map_link', 'className')],
    [Input('url', 'pathname'),
    Input('url-phage_map', 'pathname'),
    Input('url-plasmid_map', 'pathname'),
    Input('url-both_maps', 'pathname')])
def display_page(pathname, path_phage_map, path_plasmid_map, path_both_map):
    if pathname == '/apps/home':
        return home.layout, "current-link", "", "", ""
    if pathname == '/apps/plasmid_map' or path_plasmid_map == '/apps/plasmid_map':
        return plasmid_map.layout, "", "current-link", "", ""
    if pathname == '/apps/phage_map' or path_phage_map == '/apps/phage_map':
        return phage_map.layout, "", "", "current-link", ""
    if pathname == '/apps/both_map' or path_both_map == '/apps/both_map':
        return both_map.layout, "", "", "", "current-link"
    else:
        return home.layout,"current-link", "", "", ""


if __name__ == '__main__':
    app.run_server(debug=True)
