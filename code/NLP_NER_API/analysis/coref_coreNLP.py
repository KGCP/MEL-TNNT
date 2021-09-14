from stanza.server import CoreNLPClient
import sys,os
import json
sys.path.append(os.path.join(sys.path[0],'..'))
from read_file import config

os.environ["CORENLP_HOME"] = config["package-settings"]["core-nlp"]["home-directory"]
memorysize = config["package-settings"]["core-nlp"]["memory-size"]

# classpath = '"D:\\Comp4550\\stanford-corenlp-4.2.2\\*"'
# ENG_COREFERENCE = {'coref.model' : "D:\\Comp4550\\stanza_model\\stanford-corenlp-4.2.2-models-english.jar"}
class coreNLP:
    
    def __init__(self,string):
        self.string = string
    """
        the coreNLP function is used for coreference resolution tasks in NLP task
    """
    def generate(self,memory = 8):
        with CoreNLPClient(
                properties = "en",
                annotators= 'tokenize,ssplit,pos,lemma,ner,depparse,coref',
                timeout=30000,
                memory= memorysize,
                output_format = 'json',
                be_quiet = True) as client:
            return client.annotate(self.string)

    def formatjson(self):
        """
            if format json does not contain coref then flag gives False
        """
        ann = self.generate()
        return ann
        # return ann
