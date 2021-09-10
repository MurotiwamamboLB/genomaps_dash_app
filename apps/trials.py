import functions
import base64
#import datetime
import io
import dash
import dash_core_components as dcc
import dash_html_components as html
# import plotly.express as px
# import pandas as pd
from app import app
from dash.dependencies import Input, Output, State
from random import randint
from datetime import datetime
import os



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
        id='upload-data-HAs',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The HOMOLOGY ARMS GenBank File"
        ]),
        multiple = False,
        className = "upload"),

        
        # upload Insert

        dcc.Upload(
        id='upload-data-insert',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The INSERT GenBank File"
        ]),
        multiple = False,
        className = "upload"),

        # upload plasmid backbone

        dcc.Upload(
        id='upload-data-plasmid_backbone',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The PLASMID BACKBONE GenBank File"
        ]),
        multiple = False,
        className = "upload"),


        # upload phage

        dcc.Upload(
        id='upload-data-phage',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The PHAGE GenBank File"
        ]),
        multiple = False,
        className = "upload"),

        
        # updates - simple hidden elements to help when i need functions that dont neccessarily have required output
        html.Div(id = "updates", className = "updates", hidden ='HIDDEN'),
        html.Div(id = "reset", className = "updates", hidden ='HIDDEN'),


        #html.Button([dcc.Download(id="download-component")],id = "download-button", className = "submit-button", n_clicks = 0),
        
        ]),
      

  ], className = "upload-block"),

  #upload and down load block  stast 

  html.Div([
      # the submit button 
      html.Button([dcc.Download(id="download-component"), "Download Maps"], id = "download-button", className = "download-button", n_clicks = 0, disabled = 'disabled'),

      # the download button 
      # html.Button([dcc.Download(id="download-component"), "Download Maps"],id = "download-button", className = "download-button", n_clicks = 0),

      ], className = "submit-download-block")

  # results block begins 
  #html.Div(id = "map-results"),


]) 

# parsing files content from the uploads 
# def parse_contents(contents, filename):
#     content_type, content_string = contents.split(',')

#     decoded = base64.b64decode(content_string)
    
#     data_file = io.StringIO(decoded.decode('utf-8'))

#     return data_file

# upload buttons respond to content being uploaded. 
# input_ids = ['upload-data-HAs', 'upload-data-insert', 'upload-data-plasmid_backbone', 'upload-data-phage']

# input_data_content = {}

#################uploads manual and validation checks######################

# HAs
@app.callback(
    [Output("updates", "children"),
    Output("download-button", "disabled"),
    Output('upload-data-HAs', 'style'),
    Output('upload-data-insert', 'style'),
    Output('upload-data-plasmid_backbone', 'style'),
    Output('upload-data-phage', 'style')],
    [Input('upload-data-HAs', 'contents'),Input('upload-data-HAs', 'filename'),
    Input('upload-data-insert', 'contents'),Input('upload-data-insert', 'filename'),
    Input('upload-data-plasmid_backbone', 'contents'),Input('upload-data-plasmid_backbone', 'filename'),
    Input('upload-data-phage', 'contents'),Input('upload-data-phage', 'filename'),
    ])
def generate_maps(HA_content, HA_fname, INSERT_content, INSERT_fname, BB_content, BB_fname, PHAGE_content, PHAGE_fname):
  input_ids = ['upload-data-HAs', 'upload-data-insert', 'upload-data-plasmid_backbone', 'upload-data-phage']

  inputs= {'upload-data-HAs': (HA_fname,HA_content), 'upload-data-insert': (INSERT_fname,INSERT_content), 'upload-data-plasmid_backbone':(BB_fname,BB_content), 'upload-data-phage':(PHAGE_fname,PHAGE_content)}
  valid_inputs_dict = {}
  output_dict = {}
  submit_state = True # true mean the button is disabled
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

    # controlling the submit file 
    submit_state = False # activating the submit button 

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
    functions.create_plasmid_map(f'./{DATA_FOLDER_NAME}/upload-data-HAs.gb', f'./{DATA_FOLDER_NAME}/upload-data-insert.gb', f'./{DATA_FOLDER_NAME}/upload-data-plasmid_backbone.gb', DATA_FOLDER_NAME)
    #functions.create_phage_map(f'./{DATA_FOLDER_NAME}/upload-data-HAs.gb', f'./{DATA_FOLDER_NAME}/upload-data-insert.gb', f'./{DATA_FOLDER_NAME}/upload-data-phage.gb', DATA_FOLDER_NAME)

    # generate a zip file 
    functions.write_zip_file(["plasmid_map.gb", "phage_map.gb"],f'./{DATA_FOLDER_NAME}', f'./{DATA_FOLDER_NAME}/plasmid_and_phage_maps.zip')

    updates_message = DATA_FOLDER_NAME


  return updates_message, submit_state, output_dict['upload-data-HAs'], output_dict['upload-data-insert'], output_dict['upload-data-plasmid_backbone'], output_dict['upload-data-phage']

@app.callback(
  [Output('url', 'pathname'),
  Output("download-component", "data")],
  Input("download-button", "n_clicks"),
  State("updates", "children"),
  prevent_initial_call=True)
def download_maps(n, DATA_FOLDER_NAME):

  final = dcc.send_file(f'./{DATA_FOLDER_NAME}/plasmid_and_phage_maps.zip')
  os.system(f"rd /s /q {DATA_FOLDER_NAME}")
  pathname = '/apps/both_map'

  return pathname, final