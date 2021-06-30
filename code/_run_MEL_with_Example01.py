''''
@script: MEL with NLP-NER Toolkit (run for a specific configuration file).
@author: Sergio.
@summary: runs MEL and NLP-NER toolkit over a specific document input without any interaction with CouchDB.
@project: AGRIF.
# History Update:
#    2021-01-06: creation.
'''


# ==================================================================================================
import builtins
builtins.MEL_config_filename = "config-Example01" # default configuration file; "Only-UseCase" param. is required!
import MEL


# ==================================================================================================
MEL.header()
MEL.Test.File(_input_file="test.txt") # file to process
MEL.footer()
# ==================================================================================================
