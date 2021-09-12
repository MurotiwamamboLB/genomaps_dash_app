# REQUIRED LIBRARIES
import os
import pandas as pd
import numpy as np
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
import logging 
import base64
import io
import zipfile
from datetime import datetime
from apps import both_map

now = datetime.now()

# SUMMARY
"""
This document describes a program written to assist in the engineering plasmid design. I intend to heavily lean on the strengths of biopython in describing sequences and writing annotated genbank files.
"""

# setting up logging 

logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s:%(levelname)s:%(message)s')


###################### functions for handing the encoding made by dash ########
def decode_file_content(file: str) -> str:
    """
    Decode file content from base64 to ascii
    Parameters
    ----------
    file: str, required
        A base64 encoded str

    Returns
    -------
    result:
        A decoded str
    """
    return base64.b64decode(file.split(',')[-1].encode('ascii')).decode()

def process_uploads(encoded_text, new_gb_file_name):
    """Converts a base64 to genbank file . 
    
    Parameters:
    argument1 (base64 str): the base64 encoding.
    argument2 (str):name of the resultant genbank file, e.g "example.gb"
    
    Returns:
    None. And places a genabank file in the current directory.
    
    """
    d = decode_file_content(encoded_text)
    
    with open(new_gb_file_name, "w") as f:
        for line in d:
            f.write(line)


######################################################################################################
####################################  HELPER FUNCTIONS  ##############################################
######################################################################################################


# 1. creating the sequence record 
def create_record(sequence, identifier, name = None, description = None):
    """ This function makes a biopython record for a sequence. 
    
    Parameters:
    
    argument1 (str or Biopython Seq object): the sequence you wish to record
    argument2 (str): a unique id for the record or sequence
    argument3 (str): a more user friendly name for the record. If no name is provided, the id will be used instead. 
    argument4 (str): a description of the record. If no description if provided, a note will be included to indicate your choice.
    
    Returns:
    
    object: A Biopython SeqRecord object
    """
    # handling the optional input
    if name == None:
        name = indentifier
    
    if description == None:
        description = "No decription provided"
    
    # writing the record 
    record = SeqRecord(
    Seq(str(sequence)),
    id = identifier,
    name= name,
    description= description,
    annotations={"molecule_type": "DNA"},)
    
    return record


##########################################################################################################################
# 2. checking for a sequence in another sequence 

def sequence_presence_check(record, sequence):
    """ Check the presence of a sequence in a Biopython SeqRecord. 
    
    Parameters:
    argument1 (Biopython SeqRecord object): a SeqRecord object
    argument2 (str): a sequence
    
    Returns:
    Boolean: True if present and False if abscent. 
    """
    if record.seq.find(str(sequence)) < 0:
        return False
    else:
        return True
    
    
###########################################################################################################################
# 3. extract the indeces of a sequence if it matched to another sequence    
def get_sequence_location(record, sequence):
    """ Extracts the indeces of a sequence from a Biopython SeqRecord object, given the provided sequence is present in the sequence of the provided SeqRecord object. 
    
    Parameters:
    argument1 (Biopython SeqRecord object): a SeqRecord object
    
    Returns:
    List of integers: A list with the start and end indeces of the provided sequence in the provided SeqRecord object. 
    """
    
    # check if the sequence is present in the provided record 
    if sequence_presence_check(record, sequence) == True:
        seqence_length = len(sequence) # determining the length of the input sequence for calculating the end index.
        record_sequence = record.seq

        start_index = record_sequence.find(str(sequence)) # find method only returns the start index of a sequence being searched.
        end_index = start_index + seqence_length

        sequence_location = [int(start_index), int(end_index)]
    else:
        return 'Error: The sequence entered was not found.'
    
    return sequence_location


############################################################################################################################
# 4. add the features to a sequence

def add_features(record, feature_dict):
    """ Adds features to a SeqRecord object. 
    
    Parameters:
    
    argument1 (Biopython SeqRecord object): a SeqRecord object
    argument2 (dictionary): a dictionary with features where a key is the name of a feature and the values is a sequence of the feature. 
    
    Returns:
    object: A Biopython SeqRecord object with features attached. 
    """
    
    # iterating through each annotation from the list
    for k,v in feature_dict.items():
        # first check if the sequence is present in the record
        name = k
        sequence = v

        if sequence_presence_check(record, sequence) == True:
            # appending the annotations to the SeqRecord object; key = type, value = turple with start and end indeces
            sequence_indeces = get_sequence_location(record, sequence)

            record.features.append(SeqFeature(FeatureLocation(sequence_indeces[0], sequence_indeces[1]), type = str(name)))

    annotated_record = record
    
    return annotated_record

############################################################################################################################
# 5. extract the sequence of a feature 

def get_feature_seq(record, feature):
    """ Extracts the sequence of a feature in a Biopython SeqRecord object. 
    
    Parameters:
    argument1 (Biopython SeqRecord object): a SeqRecord object
    argument2 (str): the feature name
    
    Returns:
    A biopython Seq object: the sequence of the named feature. 
    """
    start_index = int(feature.location.start)
    end_index = int(feature.location.end)
    sequence = record.seq[start_index:end_index]
    
    return sequence

############################################################################################################################
# 6. extract the features form a record
def extract_features(record):
    """ Extracts features from a biopython SeqRecord while preserving all aspects of the feature including qualifiers. 
    
    Parameters:
    
    argument1 (Biopython SeqRecord object): a SeqRecord object with features.
    
    Returns:
    dictionary: A dictionary with names of features as keys and sequences of the features as values. 
    """
    
    # initializating the dictionary of features
    feature_dict = {}
    
    # iterating through features 
    for feature in record.features:
        name = str(feature.location.start) +"_"+str(feature.location.end)
        #sequence = get_feature_seq(record, name)
        feature_dict[name] = feature
        
    return feature_dict


###########################################################################################################################
# 7. check if the HAs are compatible between foundation and insert

def HA_compatibility_check(record1, record2):
    """ Compares the compatibility between an insert and a foundation/backbone sequence through comparing their HAs. 
    
    Parameters:
    argument1 (Biopython SeqRecord object): a SeqRecord object - can be an insert or a foundation
    argument2 (Biopython SeqRecord object): a SeqRecord object - can be an insert or a foundation
    
    Returns:
    Boolean: True if they are compatible and False otherwise
    """
    # comparing if they are equal
    if get_feature_seq(record1, "LHA") == get_feature_seq(record2, "LHA") and get_feature_seq(record1, "RHA") == get_feature_seq(record2, "RHA"):
        return True
    
    else:
        return False


###########################################################################################################################
# 8. Write the results to a genbank file  
def write_genbank_file(annotated_record, out_file_name):
    """ Writes a Biopython SeqRecord into a genbank file with all feature preserved.  
    
    Parameters:
    argument1 (Biopython SeqRecord object): an annotated Biopython SeqRecord object
    argument2 (str): a name the user prefers to use for the output file name, e.g "example.gb"
    
    Returns:
    A genbank file is added to the current working directory. 
    """
    SeqIO.write(annotated_record, out_file_name, "genbank")
    
    return None

############################################################################################################################
#9. reads a genbank file into a SeqRecord

def read_genbank(name_of_file):
    """Converts a genbank file to a Biopython SeqRecord. 
    
    Parameters:
    argument1 (str): the name of a genbank file with a record the user wishes to convert into a record, e.g "example.gb"
    
    Returns:
    A biopython SeqRecord Object. 
    
    """
    record = SeqIO.read(name_of_file, "genbank")
    
    return record


############################################################################################################################
#10. transfers annotations from one record to another 
def transfer_features(original_record, new_record):
    """Transfers features from one Biopythn SeqRecord to another, preserving all components of the features. 
    
    Parameters:
    argument1 (Biopython SeqRecord object): a SeqRecord object that has the features you want to transfer to a new sequence
    argument1 (Biopython SeqRecord object): a SeqRecord object that you would like to transfer the features to
    
    Returns:
    An annotated Biopython SeqRecord object
    """
    
    # extract the features from a record
    features_dict = extract_features(original_record)
    
    for k,v in features_dict.items():
        # get the sequence from the original record 
        sequence = get_feature_seq(original_record, v)
        
        #proceed only if a sequence is found in the new record:
        if sequence_presence_check(new_record, sequence) == True:
            # find new indeces in the new record 
            indeces = get_sequence_location(new_record, sequence)
            strand = v.strand
            f_type = v.type # type is protected word
            qualifiers = v.qualifiers

            # new feature for the new record
            new_feature = SeqFeature(FeatureLocation(indeces[0],indeces[1], strand = strand)
                                              , type = str(f_type),
                                             qualifiers = qualifiers)
            
            # add the feature if it is not already there in the new record
            if new_feature not in new_record.features:
                new_record.features.append(new_feature)

    return new_record


############################################################################################################################
#11. extrats the homology arms
def extract_HAs(genbank_file_with_HAs):
    """Extracts the homology arms from a genbank file consisting of many HAs
    
    Parameters:
    argument1 (genbank file): a genbank file containing LHAs and RHAs
    
    Returns:
    A list with two dictionaries, the first is a dictionary of LHAs and the second is a dictionary of RHAs
    """
    
    LHAs_dict = {}
    RHAs_dict = {}
    
    # parsing the genbank file with HAs
    for record in SeqIO.parse(genbank_file_with_HAs, "genbank"):
        current_HA = {}
        
        # find THE HA feature
        if str(record.features[0].type).lower() == "homology_arm" or str(record.features[0].type).lower() == "ha":
            HA_name = record.features[0].qualifiers['label'][0]
            spitted_HA_name = HA_name.split('_')
            HA_type = spitted_HA_name[-1]
            
            # add the HA to the appropriete list
            if HA_type.upper() == "LHA":
                LHAs_dict[HA_name] = record
                
            if  HA_type.upper() == "RHA":
                    RHAs_dict[HA_name] = record
                    
    return (LHAs_dict, RHAs_dict)

############################################################################################################################
# 12. reads a genbank file 

def genbank_to_record(name_of_file):
    """Converts a genbank file to a Biopython SeqRecord. 
    
    Parameters:
    argument1 (str): the name of a genbank file with a record the user wishes to convert into a record, e.g "example.gb"
    
    Returns:
    A biopython SeqRecord Object. 
    
    """
    record = SeqIO.read(name_of_file, "genbank")
    
    return record

#############################################################################################################################
#13. find correct pairs given a genbak with many HAs

def find_HA_pairs(genbank_file_with_HAs):
    """Identifies and pairs the LHA to its rightful RHA based on naming. 
    
    Parameters:
    argument1 (genbank file): a genbank file containing LHAs and RHAs
    
    Returns:
    A dictionary of dictionaries. The phage_site_name is the key and a dictionary with the LHA:SeqRecord object and the RHA:SeqRecord object is the value.
    """
    
    # initialising the dictionary to hold paires
    pairs_dict = {}
    
    # make a list of LHAs and RHAs dictionaries with their labels as keys and SeqRecord object as values
    HAs_list = extract_HAs(genbank_file_with_HAs) # returns a turple with 2 dictionaries, LHAs at index 0 and RHAs at index 1
    
    LHAs_list = list(HAs_list[0])
    RHAs_list = list(HAs_list[1])
    
    LHAs_dict = HAs_list[0]
    RHAs_dict = HAs_list[1]

    logging.info("**************************************** Identified Matching Homology Arms Pairs ****************************************")

    
    # make a dummy RHA list using the LHA to compare with the real RHA_list above to find LHA with a pairing RHA.
    dummy_RHA_list = []
    
    for LHA in LHAs_list:
        dummy_RHA_name = LHA.replace("LHA", "RHA")
        
        # the RHA has matched to a LHA
        if dummy_RHA_name in RHAs_list:
            phage_name = dummy_RHA_name.split("_")[0]
            insert_name = dummy_RHA_name.split("_")[1]
            site_name = "_".join((phage_name,insert_name))
            
            # populate the original pairs dict with site name as key and a dictionary with LHA:record and RHA:record as a value 
            current_pair_dict = {}            
            
            current_pair_dict[LHA] = LHAs_dict[LHA]
            current_pair_dict[dummy_RHA_name] = RHAs_dict[dummy_RHA_name]
            
            pairs_dict[site_name] = current_pair_dict
            
            logging.info(f"Site: {site_name}, LHA:{LHA}, RHA: {dummy_RHA_name}")

        #else:
            # may need this for better logging 


    return pairs_dict


#############################################################################################################################
#14. write files into a zip folder
def write_zip_file(list_ending_patterns,input_folder, out_file_name):
    """
    Generates a zip file.
    
    Parameters:
    argument1 (list of str): a list of strings that match the ending partttens of the desired files for compression. 
    argument2 (str):the path to the dir holding the files to be compressed.
    argument2 (str):the desired name for the eventual zip file. Must have a .zip at the end. 
    
    
    Returns:
    None. And places a zip file in the current directory.
    
    """
    
    #for ending in list_ending_patterns:
    with zipfile.ZipFile(out_file_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                for ending in list_ending_patterns:
                    if file.endswith(ending):
                        zf.write(f'{input_folder}/{file}')

    return None

######################################################################################################
#########################################  MAIN MAPPING FUNCTIONS  ###################################
######################################################################################################

def create_plasmid_map(HAs_genbank_file,INSERT_genbank_file, BACKBONE_genbank_file, OUT_FOLDER_NAME):
    """ Creates a plasmid map. 
    
    Parameters:
    argument1 (genbank file): a genbank file containing LHAs and RHAs.
    argument1 (genbank file): a genbank file containing INSERT including all features and fragments.
    argument1 (genbank file): a genbank file containing the PLASMID BACKBONE.

    
    Returns:
    An annotated SeqRecord object with an insert integrated into the backbone SeqRecord objects. 
    """


    # the logger is global, thus here we are setting up a local handler that will be made each run, it will have the root's configs set above
    plasmid_mapping_log_handler = logging.FileHandler(f'./{OUT_FOLDER_NAME}/Plasmid_Mapping_Log.log', 'a')

    # adding some formatting preferences 
    formatter = logging.Formatter('%(asctime)s:%(message)s')
    plasmid_mapping_log_handler.setFormatter(formatter)

    # removing all other handlers just in case 
    log = logging.getLogger()  # root logger
    for hdlr in log.handlers[:]:  # remove all old handlers
        log.removeHandler(hdlr)

    # adding the current logger configured to put data in the suggested log file
    log.addHandler(plasmid_mapping_log_handler) 


    logging.info("#########################################################################################################################")
    logging.info("################################################# PLASMID MAPPING STARTING ##############################################")

    logging.info("\n\n")

    # a list of all maps created 
    maps_generated = []

    for backbone_record in SeqIO.parse(INSERT_genbank_file, "genbank"):
            for insert_record in SeqIO.parse(BACKBONE_genbank_file, "genbank"):
                # setting variables 
                INSERT = backbone_record
                BACKBONE = insert_record
                
                
                # reading in the HAs
                HAs_dict = find_HA_pairs(HAs_genbank_file)

                logging.info("\n")
                logging.info("************************************************** Mapping Attempts *****************************************************")

                
                # logging the HAs present
                # logging.info("Engineering sites with both Homology Arms present and properly named: \n\n".format(HAs_dict))
                
                # iterating through the sites provided to produce several plasmid maps
                for site_name, HAs in HAs_dict.items():
                
                    # initializing the LHA and RHA
                    LHA_record = HAs[site_name+"_LHA"]
                    RHA_record = HAs[site_name+"_RHA"]

                    # making the plasmid map
                    plasmid_map = LHA_record + INSERT + RHA_record + BACKBONE

                    # make a new record to accommodate including a name, id and description
                    sequence = plasmid_map.seq
                    identifier = site_name+"_plasmid_map"
                    name = site_name +"_"+INSERT.name+ "_plamid_map"
                    description = "A plasmid map for engineering phage: {}, on site: {}, insert_name: {}".format(site_name.split("_")[0],
                                                                                                               site_name, INSERT.name)

                    new_plasmid_map = create_record(sequence=sequence, identifier=identifier, name = name, description = description)

                    # adding features
                    annotated_plasmid_map = transfer_features(original_record=plasmid_map, new_record=new_plasmid_map)

                    # wring a plasmid map into a genbank file
                    OUT_FILE_NAME = f"./{OUT_FOLDER_NAME}/{site_name}_{INSERT.name}_plasmid_map.gb"
                    #"./data/"+site_name + "_" +INSERT.id+ "_plamid_map.gb"
                    maps_generated.append(OUT_FILE_NAME)

                    write_genbank_file(annotated_record = annotated_plasmid_map, out_file_name=OUT_FILE_NAME)
                    
                    # logging the creating of a plasmid map for each site
                    logging.info("****** Successful: Backbone name: {}, Insert name: {}, Site name: {}, Plasmid Map Name: {}".format(BACKBONE.name, 
                                                                                                  INSERT.name,
                                                                                                  site_name,
                                                                                                  site_name + "_" +INSERT.name+ "_plamid_map"))
    logging.info("\n\n")
    logging.info("############################################## PLASMID MAPPING RUN COMPLETED ############################################")
    logging.info("#########################################################################################################################")

    plasmid_mapping_log_handler.close() # clossing the handler to avoid problems with trying to delete open files. 
    
    return None

#####################################################################################################################################
def create_phage_map(HAs_genbank_file,INSERT_genbank_file, PHAGE_genbank_file, OUT_FOLDER_NAME):
    #create_phage_map(HAs_genbank_file, INSERT_genbank_file, PHAGE_genbank_file, OUT_FOLDER_NAME):
    """ Creates a plasmid map. 
    
    Parameters:
    argument1 (genbank file): a genbank file containing LHAs and RHAs.
    argument1 (genbank file): a genbank file containing INSERT including all features and fragments.
    argument1 (genbank file): a genbank file containing the PHAGE BACKBONE.

    
    Returns:
    An annotated SeqRecord object with an insert integrated into the backbone SeqRecord objects. 
    """
    # the logger is global, thus here we are setting up a local handler that will be made each run, it will have the root's configs set above
    phage_mapping_log_handler = logging.FileHandler(f'./{OUT_FOLDER_NAME}/Phage_Mapping_Log.log', 'a')

    # adding some formatting preferences 
    formatter = logging.Formatter('%(asctime)s:%(message)s')
    phage_mapping_log_handler.setFormatter(formatter)

    # removing all other handlers just in case 
    log = logging.getLogger()  # root logger
    for hdlr in log.handlers[:]:  # remove all old handlers
        log.removeHandler(hdlr)

    # adding the current logger configured to put data in the suggested log file
    log.addHandler(phage_mapping_log_handler)
    logging.info("#########################################################################################################################")
    logging.info("################################################# PHAGE MAPPING STARTING ################################################")
    logging.info("\n\n")


    # a list of all maps created 
    maps_generated = []

    for backbone_record in SeqIO.parse(INSERT_genbank_file, "genbank"):
        for insert_record in SeqIO.parse(PHAGE_genbank_file, "genbank"):
            # setting variables 
            INSERT = backbone_record
            BACKBONE = insert_record
    
            # making a fully annotated reverse backbone record just incase the HAs are provided the other way round
            BACKBONE_REVERSE = BACKBONE.reverse_complement(id=True, 
                                                           name=True, 
                                                           description=True,
                                                           features=True,
                                                           annotations=True, 
                                                           letter_annotations=True, 
                                                           dbxrefs=True)

            # reading in the HAs
            HAs_dict = find_HA_pairs(HAs_genbank_file)

            logging.info("\n")
            logging.info("************************************************** Mapping Attempts *****************************************************")


            # iterating through the sites provided to produce several plasmid maps
            for site_name, HAs in HAs_dict.items():
            
                # initializing the LHA and RHA
                LHA_record = HAs[site_name+"_LHA"]
                RHA_record = HAs[site_name+"_RHA"]

                # making the INSERT + HAs
                COMBINED_INSERT = LHA_record + INSERT + RHA_record

                # checking if the foundation and the insert sequences have comparable homology arm sequences
                if sequence_presence_check(BACKBONE, LHA_record.seq) == True and sequence_presence_check(BACKBONE, RHA_record.seq) == True:
                    
                    # find the start of the LHA and the end of the RHA on the foundation sequence
                    LHA_sequence = LHA_record.seq
                    RHA_sequence = RHA_record.seq

                    LHA_start_index = get_sequence_location(BACKBONE, LHA_sequence)[0]
                    RHA_end_index = get_sequence_location(BACKBONE, RHA_sequence)[1]
                    
                    # separate the phage into a left fragment and right fragment seqrecord
                    PHAGE_LEFT_FRAGMENT = BACKBONE[0:LHA_start_index]
                    PHAGE_RIGHT_FRAGMENT = BACKBONE[RHA_end_index:]
                    
                    # creating the phage map
                    PHAGE_MAP = PHAGE_LEFT_FRAGMENT + LHA_record + INSERT + RHA_record + PHAGE_RIGHT_FRAGMENT
                    PHAGE_MAP.annotations["molecule_type"] = "DNA" # this annotation is requied to write a genbank file
                    
                    # writing out a genbank file 
                    # OUT_FILE_NAME = site_name+"_"+ INSERT.id + "_phage_map.gb"
                    OUT_FILE_NAME = f"./{OUT_FOLDER_NAME}/{site_name}_{INSERT.name}_phage_map.gb"
                    write_genbank_file(annotated_record = PHAGE_MAP, out_file_name=OUT_FILE_NAME)

                    maps_generated.append(OUT_FILE_NAME)
                    
                # checking if the foundation_reverse_complement and the insert sequences have comparable homology arm sequences 
                elif sequence_presence_check(BACKBONE_REVERSE, LHA_record.seq) and sequence_presence_check(BACKBONE_REVERSE, RHA_record.seq):
                    
                    # find the start of the LHA and the end of the RHA on the foundation sequence
                    LHA_sequence = LHA_record.seq
                    RHA_sequence = RHA_record.seq

                    LHA_start_index = get_sequence_location(BACKBONE_REVERSE, LHA_sequence)[0]
                    RHA_end_index = get_sequence_location(BACKBONE_REVERSE, RHA_sequence)[1]
                    
                    # separate the phage into a left fragment and right fragment seqrecord
                    PHAGE_LEFT_FRAGMENT = BACKBONE_REVERSE[0:LHA_start_index]
                    PHAGE_RIGHT_FRAGMENT = BACKBONE_REVERSE[RHA_end_index:]
                    
                    # creating the phage map
                    PHAGE_MAP_REVERSE = PHAGE_LEFT_FRAGMENT + LHA_record + INSERT + RHA_record + PHAGE_RIGHT_FRAGMENT
                    
                    # turning back to the reverse compliment
                    PHAGE_MAP = PHAGE_MAP_REVERSE.reverse_complement(id=site_name +"_"+ INSERT.name + "_phage_map.gb", 
                                                                     name=site_name +"_"+ INSERT.name + "_phage_map.gb", 
                                                                     description="A phage map for phage: {}, site: {}, insert: {}".format(BACKBONE.name,
                                                                                                                                          site_name, 
                                                                                                                                          INSERT.name),
                                                                     features=True, annotations={"molecule_type":"DNA"}, 
                                                                     letter_annotations=True, dbxrefs=True)
                    
                
                    # writing out a genbank file 
                    OUT_FILE_NAME = f"./{OUT_FOLDER_NAME}/{site_name}_{INSERT.name}_phage_map.gb"
                    write_genbank_file(annotated_record = PHAGE_MAP, out_file_name=OUT_FILE_NAME)
                    # logging the creating of a plasmid map for each site
                    

                    logging.info("****** Successful: Phage name: {}, Insert name: {}, Site name: {}, Phage Map Name: {}".format(BACKBONE.name, 
                                                                                              INSERT.name,
                                                                                              site_name,
                                                                                              site_name + "_" +INSERT.name+ "_phage_map"))

                    maps_generated.append(OUT_FILE_NAME)
                    
                else:
                    # logging the HAs that did no match to the phage 
                    logging.info("****** Failed: Homology Arms Pair Not Found in Phage: LHA: {}, RHA: {}, Phage: {}".format(LHA_record.name, RHA_record.name, BACKBONE.name))

                #maps_generated.append(OUT_FILE_NAME)
        

    logging.info("\n\n")
    logging.info("############################################## PHAGE MAPPING RUN COMPLETED ##############################################")
    logging.info("#########################################################################################################################")
    logging.info("\n\n")
    
    phage_mapping_log_handler.close()
    
    return None
##################################################################################################################################################