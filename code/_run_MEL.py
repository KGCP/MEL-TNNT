''''
@script: Metadata Extraction & Loader (MEL).
@author: Sergio.
@summary: MEL module execution script.
@project: AGRIF.
# History Update:
#    2020-04-08: creation.
#    2020-11-09: main()
'''


# ==================================================================================================
import MEL # default configuration file: *config.json*
MEL.process() # <-- MEL task

# ==================================================================================================
#MEL.header()


# runs the main execution process:
#MEL.main()
'''
MEL.NER.processFromAndToCouchDB_forDocSet(
    {
        "General-Metadata": { "FILENAME": "2002-2003_DPRS_PBS_01_pref.htm" }
    }
)
'''
#MEL.Test.File() # uses the default values from config.json
#MEL.Test.CouchDB() # NHMRC prunning
#MEL.Test.NER_process()
#MEL.Test.NER_process("BP4 2008-09.pdf")
#MEL.Test.NER_sampling()


#MEL.footer()
# ==================================================================================================