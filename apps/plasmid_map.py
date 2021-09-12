import functions
import base64
import io
import dash
from dash import dcc
from dash import html
from app import app
from dash.dependencies import Input, Output, State
from random import randint
from datetime import datetime
import os
import simplejson as json




layout = html.Div(children=[

  # instructions block starts

  html.Div(children=[

    html.Div([
      html.P(children = "GENO-MAPS Instructions")], className="instructions-header"),

    html.Div([

      html.Ul([

        html.Li([ "Make sure that all your input files are GenBank files before submiting. Note that you can make GenBank files from Benchling or Genius."]),
        html.Li([ "When making the Homology Arms GenBank file, ensure that the 'feature' is set to 'Homology_arm'."]),
        html.Li([ "For each Homology Arms Pair, ensure that they are named according to the following format: phageName_siteName_(LHA or RHA)"]),
        html.Li([ "When none-GenBank files are provided, the field will turn red. When valid input is provided the field will turn green."]),
        html.Li([ "When all input files are provided and valid, a 'DOWNLOAD MAPS' button will appear." ]),
        html.Li([ "When you click the 'DOWNLOAD MAPS' button, your maps will be downloaded as a zip file and the input fields will reset." ]),
        html.Li([ "The downloaded zip file contains each map as a GenBank file and a log file with information about the mapping run." ]),
        html.Li([ "Check the log file to find successful and failed mapping attempts." ]),

        ], className = "instructions"),
      ]),
      ],className = "body-block"),
      

  # instructions block ends

  #upload-block starts

  html.Div([html.P(children = "Upload Your GenBank INPUT files")],className="instructions-header"),
  
  
    html.Div([

   
      html.Div([
        # upload HAs

        dcc.Upload(
        id='upload-data-HAs-plasmid_maps',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The HOMOLOGY ARMS GenBank File",
          
        ]),
        multiple = False,
        className = "upload"),

        
        # upload Insert

        dcc.Upload(
        id='upload-data-insert-plasmid_maps',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The INSERT GenBank File"
        ]),
        multiple = False,
        className = "upload"),

        # upload plasmid backbone

        dcc.Upload(
        id='upload-data-plasmid_backbone-plasmid_maps',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The PLASMID BACKBONE GenBank File"
        ]),
        multiple = False,
        className = "upload"),


        # updates - simple hidden elements to help when i need functions that dont neccessarily have required output
        html.Div(id = "updates-plasmid_maps", className = "updates",hidden ='HIDDEN'),
        html.Div(id = "reset-plasmid_maps", className = "updates", hidden ='HIDDEN'),
        
        ]),
      

  ], className = "upload-block"),

  #upload-block  ends

  html.Div([
      # the download button 
      dcc.Loading(id="spinner-phage-plasmid_maps",type="dot", color="rgb(43,75,111)",className = "spinner",
          children=html.Div(
            html.Button([dcc.Download(id="download-component-plasmid_maps"), "Download Maps"], id = "download-button-plasmid_maps", n_clicks = 0),
          )),

      ], className = "submit-download-block")

]) 


############################################### CALL BACKS BEGIN #################################################

@app.callback(
    [Output("updates-plasmid_maps", "children"),
    Output("download-button-plasmid_maps", "className"),
    Output('upload-data-HAs-plasmid_maps', 'style'),
    Output('upload-data-insert-plasmid_maps', 'style'),
    Output('upload-data-plasmid_backbone-plasmid_maps', 'style')],
    [Input('upload-data-HAs-plasmid_maps', 'contents'),Input('upload-data-HAs-plasmid_maps', 'filename'),
    Input('upload-data-insert-plasmid_maps', 'contents'),Input('upload-data-insert-plasmid_maps', 'filename'),
    Input('upload-data-plasmid_backbone-plasmid_maps', 'contents'),Input('upload-data-plasmid_backbone-plasmid_maps', 'filename'),
    ], prevent_initial_call=False)
def process_input(HA_content, HA_fname, INSERT_content, INSERT_fname, BB_content, BB_fname):
  """
  Processes the input GenBank files and provide contents as dict thrugh the updates component. 

  """
  input_ids = ['upload-data-HAs-plasmid_maps', 'upload-data-insert-plasmid_maps', 'upload-data-plasmid_backbone-plasmid_maps']

  inputs= {'upload-data-HAs-plasmid_maps': (HA_fname,HA_content), 'upload-data-insert-plasmid_maps': (INSERT_fname,INSERT_content), 'upload-data-plasmid_backbone-plasmid_maps':(BB_fname,BB_content)}
  valid_inputs_dict = {}
  output_dict = {}
  download_button_class_name = "hidden-download-button"
  updates_message = None  

  # validating the input files 
  for k, v in inputs.items():
    input_label = k
    f_name = v[0]
    content = v[1]
    if content is not None and f_name.lower().endswith(".gb") == True:
      valid_inputs_dict[input_label] = {"filecontent":f_name,"filecontent":content}
      output_dict[input_label] = {"backgroundColor": "rgb(140,198,141)"}

    elif content is not None and f_name.lower().endswith(".gb") == False:
      output_dict[input_label] = {"backgroundColor": "rgb(255,175,175)"}
    else:
      output_dict[input_label] = {"backgroundColor":"white"}


  # activate the submit button when all input has been provided 
  if len(valid_inputs_dict) == len(input_ids):

    # controlling the appearence and disapearance of the download button 
    download_button_class_name = "download-button"

    # updating the updates component with a dict of valid input
    updates_message = json.dumps(valid_inputs_dict)


  return updates_message, download_button_class_name, output_dict['upload-data-HAs-plasmid_maps'], output_dict['upload-data-insert-plasmid_maps'], output_dict['upload-data-plasmid_backbone-plasmid_maps']




@app.callback(
  [Output('url-plasmid_map', 'pathname'),
  Output("download-component-plasmid_maps", "data")],
  Input("download-button-plasmid_maps", "n_clicks"),
  State("updates-plasmid_maps", "children"),
  prevent_initial_call=True)
def download_maps(n, DATA_FOLDER_NAME):
  """
  Accepts as input the dict file in the updates component. Generates maps, downloads them and reset the form. 

  """

  # preventing intial call backs not working so im preventing updates if Data folder is not yet created.
  if DATA_FOLDER_NAME == None:
        raise dash.exceptions.PreventUpdate

  else:
    valid_inputs_dict = json.loads(DATA_FOLDER_NAME)

    # making a folder named based on the current time and a random number in memory to store the transitionary pdfs
    now = datetime.now()

    rand_value = randint(0, 10000000)
    DATA_FOLDER_NAME = f"temp_data_{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}_{now.microsecond}_{rand_value}"

    os.system(f"mkdir {DATA_FOLDER_NAME}")
    
    for k,v in valid_inputs_dict.items():
      encoded_text = v["filecontent"] # contents 
      new_gb_file_name = "./{}/{}".format(DATA_FOLDER_NAME, k+'.gb')
      functions.process_uploads(encoded_text, new_gb_file_name) # decoding from base 64 and then converting to g.b file

    # generate plasmid maps 
    functions.create_plasmid_map(f'./{DATA_FOLDER_NAME}/upload-data-HAs-plasmid_maps.gb', f'./{DATA_FOLDER_NAME}/upload-data-insert-plasmid_maps.gb', f'./{DATA_FOLDER_NAME}/upload-data-plasmid_backbone-plasmid_maps.gb', DATA_FOLDER_NAME)

    # generate a zip file 
    functions.write_zip_file(["_plasmid_map.gb", ".log"],f'./{DATA_FOLDER_NAME}', f'./{DATA_FOLDER_NAME}/plasmid_maps.zip')


    final = dcc.send_file(f'./{DATA_FOLDER_NAME}/plasmid_maps.zip') # downloading a zip file 
    pathname = '/apps/both_map' # redirecting to an unfilled both maps page to mimic reloading the page
    os.system(f"rd /s /q {DATA_FOLDER_NAME}") # deleting the file from the system

    return pathname, final