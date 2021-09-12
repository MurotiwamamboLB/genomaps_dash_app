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
        id='upload-data-HAs-plasmid_map',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The HOMOLOGY ARMS GenBank File",
          
        ]),
        multiple = False,
        className = "upload"),

        
        # upload Insert

        dcc.Upload(
        id='upload-data-insert-plasmid_map',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The INSERT GenBank File"
        ]),
        multiple = False,
        className = "upload"),

        # upload plasmid backbone

        dcc.Upload(
        id='upload-data-plasmid_backbone-plasmid_map',
        children=html.Div([html.A('SELECT'),' or Drag and Drop :', " The PLASMID BACKBONE GenBank File"
        ]),
        multiple = False,
        className = "upload"),

        
        # updates - simple hidden elements to help when i need functions that dont neccessarily have required output
        html.Div(id = "updates-plasmid_map", className = "updates",hidden ='HIDDEN'),
        html.Div(id = "reset-plasmid_map", className = "updates", hidden ='HIDDEN'),


        #html.Button([dcc.Download(id="download-component")],id = "download-button", className = "submit-button", n_clicks = 0),
        
        ]),
      

  ], className = "upload-block"),

  #upload and down load block  starts

  html.Div([
      # the download button 

      dcc.Loading(id="spinner-phage-plasmid_map",type="dot", color="rgb(43,75,111)",className = "spinner",
          children=html.Div(
            html.Button([dcc.Download(id="download-component-plasmid_map"), "Download Maps"], id = "download-button-plasmid_map", n_clicks = 0),
          )),



      ], className = "submit-download-block")

]) 




@app.callback(
    [Output("updates-plasmid_map", "children"),
    Output("download-button-plasmid_map", "className"),
    Output('upload-data-HAs-plasmid_map', 'style'),
    Output('upload-data-insert-plasmid_map', 'style'),
    Output('upload-data-plasmid_backbone-plasmid_map', 'style')],
    [Input('upload-data-HAs-plasmid_map', 'contents'),Input('upload-data-HAs-plasmid_map', 'filename'),
    Input('upload-data-insert-plasmid_map', 'contents'),Input('upload-data-insert-plasmid_map', 'filename'),
    Input('upload-data-plasmid_backbone-plasmid_map', 'contents'),Input('upload-data-plasmid_backbone-plasmid_map', 'filename'),
    ], prevent_initial_call=False)
def process_input(HA_content, HA_fname, INSERT_content, INSERT_fname, BB_content, BB_fname):
  input_ids = ['upload-data-HAs-plasmid_map', 'upload-data-insert-plasmid_map', 'upload-data-plasmid_backbone-plasmid_map']

  inputs= {'upload-data-HAs-plasmid_map': (HA_fname,HA_content), 'upload-data-insert-plasmid_map': (INSERT_fname,INSERT_content), 'upload-data-plasmid_backbone-plasmid_map':(BB_fname,BB_content)}
  valid_inputs_dict = {}
  output_dict = {}
  download_button_class_name = "hidden-download-button"
  #generate_button_class_name = "hidden-generate-button"
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
    #generate_button_class_name = "generate-button"
    download_button_class_name = "download-button"

    
    updates_message = json.dumps(valid_inputs_dict)


  return updates_message, download_button_class_name, output_dict['upload-data-HAs-plasmid_map'], output_dict['upload-data-insert-plasmid_map'], output_dict['upload-data-plasmid_backbone-plasmid_map']




@app.callback(
  [Output('url-plasmid_map', 'pathname'),
  Output("download-component-plasmid_map", "data")],
  Input("download-button-plasmid_map", "n_clicks"),
  State("updates-plasmid_map", "children"),
  prevent_initial_call=True)
def download_maps(n, DATA_FOLDER_NAME):

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
    functions.create_plasmid_map(f'./{DATA_FOLDER_NAME}/upload-data-HAs-plasmid_map.gb', f'./{DATA_FOLDER_NAME}/upload-data-insert-plasmid_map.gb', f'./{DATA_FOLDER_NAME}/upload-data-plasmid_backbone-plasmid_map.gb', DATA_FOLDER_NAME)

    # generate a zip file 
    functions.write_zip_file(["_plasmid_map.gb", ".log"],f'./{DATA_FOLDER_NAME}', f'./{DATA_FOLDER_NAME}/plasmid_maps.zip')


    final = dcc.send_file(f'./{DATA_FOLDER_NAME}/plasmid_maps.zip') # downloading a zip file 
    pathname = '/apps/both_map' # redirecting to an unfilled both maps page to mimic reloading the page
    os.system(f"rd /s /q {DATA_FOLDER_NAME}") # deleting the file from the system

    return pathname, final