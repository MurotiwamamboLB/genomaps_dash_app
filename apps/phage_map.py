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
        id='upload-data-HAs-phage_map',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The HOMOLOGY ARMS GenBank File"
        ]),
        multiple = False,
        className = "upload"),

        
        # upload Insert

        dcc.Upload(
        id='upload-data-insert-phage_map',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The INSERT GenBank File"
        ]),
        multiple = False,
        className = "upload"),



        # upload phage

        dcc.Upload(
        id='upload-data-phage-phage_map',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The PHAGE GenBank File"
        ]),
        multiple = False,
        className = "upload"),

        
        # updates - simple hidden elements to help when i need functions that dont neccessarily have required output
        html.Div(id = "updates-phage_map", className = "updates", hidden ='HIDDEN'),
        html.Div(id = "reset-phage_map", className = "updates", hidden ='HIDDEN'),


        #html.Button([dcc.Download(id="download-component")],id = "download-button", className = "submit-button", n_clicks = 0),
        
        ]),
      

  ], className = "upload-block"),

  #upload and down load block  stast 

  html.Div([
      # the submit button 
      html.Button([dcc.Download(id="download-component-phage_map"), "Download Maps"], id = "download-button-phage_map", className = "download-button", n_clicks = 0, disabled = 'disabled'),

      # the download button 
      # html.Button([dcc.Download(id="download-component"), "Download Maps"],id = "download-button", className = "download-button", n_clicks = 0),

      ], className = "submit-download-block")

  # results block begins 
  #html.Div(id = "map-results"),


]) 


#################uploads manual and validation checks######################

@app.callback(
    [Output("updates-phage_map", "children"),
    Output("download-button-phage_map", "disabled"),
    Output('upload-data-HAs-phage_map', 'style'),
    Output('upload-data-insert-phage_map', 'style'),
    Output('upload-data-phage-phage_map', 'style')],
    [Input('upload-data-HAs-phage_map', 'contents'),Input('upload-data-HAs-phage_map', 'filename'),
    Input('upload-data-insert-phage_map', 'contents'),Input('upload-data-insert-phage_map', 'filename'),
    Input('upload-data-phage-phage_map', 'contents'),Input('upload-data-phage-phage_map', 'filename'),
    ])
def generate_maps(HA_content, HA_fname, INSERT_content, INSERT_fname, PHAGE_content, PHAGE_fname):
  input_ids = ['upload-data-HAs-phage_map', 'upload-data-insert-phage_map',  'upload-data-phage-phage_map']

  inputs= {'upload-data-HAs-phage_map': (HA_fname,HA_content), 'upload-data-insert-phage_map': (INSERT_fname,INSERT_content),'upload-data-phage-phage_map':(PHAGE_fname,PHAGE_content)}
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

    #functions.set_log_file_path(f'./{DATA_FOLDER_NAME}/Run_log.log')

    
    for k,v in valid_inputs_dict.items():
      encoded_text = v["filecontent"] # contents 
      new_gb_file_name = "./{}/{}".format(DATA_FOLDER_NAME, k+'.gb')
      functions.process_uploads(encoded_text, new_gb_file_name) # decoding from base 64 and then converting to g.b file
    
    # start logging 
    #functions.start_logging(f'./{DATA_FOLDER_NAME}/Run_log.log')
    #functions.set_log_file_path(f'./{DATA_FOLDER_NAME}/Run_log.log')
    # generate plasmid and phage maps 
    functions.create_phage_map(f'./{DATA_FOLDER_NAME}/upload-data-HAs-phage_map.gb', f'./{DATA_FOLDER_NAME}/upload-data-insert-phage_map.gb', f'./{DATA_FOLDER_NAME}/upload-data-phage-phage_map.gb', DATA_FOLDER_NAME)

    # generate a zip file 
    functions.write_zip_file(["_phage_map.gb", ".log"],f'./{DATA_FOLDER_NAME}', f'./{DATA_FOLDER_NAME}/phage_maps.zip')

    updates_message = DATA_FOLDER_NAME


  return updates_message, submit_state, output_dict['upload-data-HAs-phage_map'], output_dict['upload-data-insert-phage_map'], output_dict['upload-data-phage-phage_map']

@app.callback(
  [Output('url-phage_map', 'pathname'),
  Output("download-component-phage_map", "data")],
  Input("download-button-phage_map", "n_clicks"),
  State("updates-phage_map", "children"),
  prevent_initial_call=True)
def download_maps(n, DATA_FOLDER_NAME):

  # preventing intial call backs not working so im preventing updates if Data folder is not yet created.
  if DATA_FOLDER_NAME == None:
        raise dash.exceptions.PreventUpdate

  else:
    final = dcc.send_file(f'./{DATA_FOLDER_NAME}/phage_maps.zip') # downloading a zip file 
    pathname = '/apps/phage_map' # redirecting to an unfilled both maps page to mimic reloading the page
    os.system(f"rd /s /q {DATA_FOLDER_NAME}") # deleting the file from the system

    return pathname, final