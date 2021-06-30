''''
@script: MEL with NLP-NER Toolkit (Sampling).
@author: Sergio.
@summary: runs the NLP-NER toolkit over a random sample of various docs. datasets stored on CouchDB.
@project: AGRIF.
# History Update:
#    2021-01-05: creation.
'''


# ==================================================================================================
import builtins
builtins.MEL_config_filename = "config-NER-Sampling" # default configuration file
import MEL


# ==================================================================================================
MEL.header()

# runs the main execution process:
#MEL.Test.NER_process("BP4 2001-02.pdf") # for a specific file

MEL.NER.processSamplingSet()

MEL.footer()
# ==================================================================================================
