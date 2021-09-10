import functions
import base64
#import datetime
import io
import dash
from dash import dcc
from dash import html
# import dash_core_components as dcc
# import dash_html_components as html
# import plotly.express as px
# import pandas as pd
from app import app
from dash.dependencies import Input, Output, State
from random import randint
from datetime import datetime
import os
import logging 




layout = html.Div(children=[

   # body block starts

  html.Div(children=[

    # logo
    html.Div([
      html.P(children = "GENO-MAPS Instructions")], className="instructions-header"),
    html.Div([

      html.P("Please note that we can only support the GenBank file format at this time. Make sure that all your files are GenBank files before submiting."),
      html.P("Your results will be provided as GenBank files that can be imported and exported to Benching and Genius."),
      html.P("We also preserve all your annotations. "),
      ], className = "instructions"),
      ],className = "body-block"),
      

    # body block ends

  html.Div([html.P(children = "Upload Your GenBank INPUT files")],className="instructions-header"),


  #   # body block ends
  
    #upload-block starts

    html.Div([

   
      html.Div([
        # upload HAs

        dcc.Upload(
        id='upload-data-HAs-both_maps',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The HOMOLOGY ARMS GenBank File"
        ]),
        multiple = False,
        className = "upload"),

        
        # upload Insert

        dcc.Upload(
        id='upload-data-insert-both_maps',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The INSERT GenBank File"
        ]),
        multiple = False,
        className = "upload"),

        # upload plasmid backbone

        dcc.Upload(
        id='upload-data-plasmid_backbone-both_maps',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The PLASMID BACKBONE GenBank File"
        ]),
        multiple = False,
        className = "upload"),


        # upload phage

        dcc.Upload(
        id='upload-data-phage-both_maps',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The PHAGE GenBank File"
        ]),
        multiple = False,
        className = "upload"),

        
        # updates - simple hidden elements to help when i need functions that dont neccessarily have required output
        html.Div(id = "updates-both_maps", className = "updates",hidden ='HIDDEN'),
        html.Div(id = "reset-both_maps", className = "updates", hidden ='HIDDEN'),


        #html.Button([dcc.Download(id="download-component")],id = "download-button", className = "submit-button", n_clicks = 0),
        
        ]),
      

  ], className = "upload-block"),

  #upload and down load block  stast 

  html.Div([
      # the submit button 
      html.Button([dcc.Download(id="download-component-both_maps"), "Download Maps"], id = "download-button-both_maps", n_clicks = 0),# disabled = 'disabled'),

      # the download button 
      # html.Button([dcc.Download(id="download-component"), "Download Maps"],id = "download-button", className = "download-button", n_clicks = 0),

      ], className = "submit-download-block")

  # results block begins 
  #html.Div(id = "map-results"),


]) 


#################uploads manual and validation checks######################


@app.callback(
    [Output("updates-both_maps", "children"),
    Output("download-button-both_maps", "className"),
    Output('upload-data-HAs-both_maps', 'style'),
    Output('upload-data-insert-both_maps', 'style'),
    Output('upload-data-plasmid_backbone-both_maps', 'style'),
    Output('upload-data-phage-both_maps', 'style')],
    [Input('upload-data-HAs-both_maps', 'contents'),Input('upload-data-HAs-both_maps', 'filename'),
    Input('upload-data-insert-both_maps', 'contents'),Input('upload-data-insert-both_maps', 'filename'),
    Input('upload-data-plasmid_backbone-both_maps', 'contents'),Input('upload-data-plasmid_backbone-both_maps', 'filename'),
    Input('upload-data-phage-both_maps', 'contents'),Input('upload-data-phage-both_maps', 'filename'),
    ])
def generate_maps(HA_content, HA_fname, INSERT_content, INSERT_fname, BB_content, BB_fname, PHAGE_content, PHAGE_fname):
  input_ids = ['upload-data-HAs-both_maps', 'upload-data-insert-both_maps', 'upload-data-plasmid_backbone-both_maps', 'upload-data-phage-both_maps']

  inputs= {'upload-data-HAs-both_maps': (HA_fname,HA_content), 'upload-data-insert-both_maps': (INSERT_fname,INSERT_content), 'upload-data-plasmid_backbone-both_maps':(BB_fname,BB_content), 'upload-data-phage-both_maps':(PHAGE_fname,PHAGE_content)}
  valid_inputs_dict = {}
  output_dict = {}
  download_button_class_name = "hidden-download-button"
  #submit_state = True # true mean the button is disabled
  updates_message = None  

  # validating the input files 
  for k, v in inputs.items():
    input_label = k
    f_name = v[0]
    content = v[1]
    if content is not None and f_name.lower().endswith(".gb") == True:
      valid_inputs_dict[input_label] = {"filecontent":f_name,"filecontent":content}
      # current_dict["filecontent"] = content
      # input_data_content[input_id] = current_dict
      #return {"backgroundColor": "rgb(140,198,141)"}
      output_dict[input_label] = {"backgroundColor": "rgb(140,198,141)"}

    elif content is not None and f_name.lower().endswith(".gb") == False:
      output_dict[input_label] = {"backgroundColor": "rgb(255,175,175)"}
    else:
      output_dict[input_label] = {"backgroundColor":"white"}


  # activate the submit button when all input has been provided 
  if len(valid_inputs_dict) == len(input_ids):

    # controlling the appearence and disapearance of the download button 
    download_button_class_name = "download-button"

    # making a folder named based on the current time and a random number in memory to store the transitionary pdfs
    now = datetime.now()

    rand_value = randint(0, 10000000)
    DATA_FOLDER_NAME = f"temp_data_{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}_{now.microsecond}_{rand_value}"

    os.system(f"mkdir {DATA_FOLDER_NAME}")
    
    for k,v in valid_inputs_dict.items():
      encoded_text = v["filecontent"] # contents 
      new_gb_file_name = "./{}/{}".format(DATA_FOLDER_NAME, k+'.gb')
      functions.process_uploads(encoded_text, new_gb_file_name) # decoding from base 64 and then converting to g.b file

    # generate plasmid and phage maps 
    #logging.basicConfig(filename = f'./{DATA_FOLDER_NAME}/Mapping_Log.log', level = logging.DEBUG, format = '%(asctime)s:%(levelname)s:%(message)s')
    functions.create_plasmid_map(f'./{DATA_FOLDER_NAME}/upload-data-HAs-both_maps.gb', f'./{DATA_FOLDER_NAME}/upload-data-insert-both_maps.gb', f'./{DATA_FOLDER_NAME}/upload-data-plasmid_backbone-both_maps.gb', DATA_FOLDER_NAME)
    functions.create_phage_map(f'./{DATA_FOLDER_NAME}/upload-data-HAs-both_maps.gb', f'./{DATA_FOLDER_NAME}/upload-data-insert-both_maps.gb', f'./{DATA_FOLDER_NAME}/upload-data-phage-both_maps.gb', DATA_FOLDER_NAME)
    #logging.basicConfig(filename = "Overall_log.log", level = logging.DEBUG, format = '%(asctime)s:%(levelname)s:%(message)s')

    # generate a zip file 
    functions.write_zip_file(["_plasmid_map.gb", "_phage_map.gb", ".log"],f'./{DATA_FOLDER_NAME}', f'./{DATA_FOLDER_NAME}/plasmid_and_phage_maps.zip')

    updates_message = DATA_FOLDER_NAME


  return updates_message, download_button_class_name, output_dict['upload-data-HAs-both_maps'], output_dict['upload-data-insert-both_maps'], output_dict['upload-data-plasmid_backbone-both_maps'], output_dict['upload-data-phage-both_maps']

@app.callback(
  [Output('url-both_maps', 'pathname'),
  Output("download-component-both_maps", "data")],
  Input("download-button-both_maps", "n_clicks"),
  State("updates-both_maps", "children"),
  prevent_initial_call=True)
def download_maps(n, DATA_FOLDER_NAME):

  # preventing intial call backs not working so im preventing updates if Data folder is not yet created.
  if DATA_FOLDER_NAME == None:
        raise dash.exceptions.PreventUpdate

  else:
    final = dcc.send_file(f'./{DATA_FOLDER_NAME}/plasmid_and_phage_maps.zip') # downloading a zip file 
    pathname = '/apps/both_map' # redirecting to an unfilled both maps page to mimic reloading the page
    os.system(f"rd /s /q {DATA_FOLDER_NAME}") # deleting the file from the system

    return pathname, final