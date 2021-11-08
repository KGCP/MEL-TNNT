from stanza.server import CoreNLPClient
import sys,os
import json
sys.path.append(os.path.join(sys.path[0],'..'))
from read_file import config

core_nlp_settings = config['package-settings']['core-nlp']
os.environ["CORENLP_HOME"] = core_nlp_settings['home-directory']
memorysize = core_nlp_settings['memory-size']
timeout = core_nlp_settings['timeout']
maxcharlength =  core_nlp_settings['maxcharlength']
suppress_output = bool(core_nlp_settings['suppress_output'])
file_boundary = core_nlp_settings['thread-settings']['file-size-boundary(in byte)']
large_thread = core_nlp_settings['thread-settings']['large-thread']
regular_thread = core_nlp_settings['thread-settings']['regular-thread']
# os.environ["CORENLP_HOME"] = '"D:\\Comp4550\\stanford-corenlp-4.2.2\\*"'
# ENG_COREFERENCE = {'coref.model' : "D:\\Comp4550\\stanza_model\\stanford-corenlp-4.2.2-models-english.jar"}
class coreNLP:
    
    def __init__(self,string,size):
        self.string = string
        self.size = size
    """
        the coreNLP function is used for coreference resolution tasks in NLP task
    """
    def generate(self):
        thread =  regular_thread if self.size < file_boundary else large_thread
        with CoreNLPClient(
                properties = "en",
                annotators= 'tokenize,ssplit,pos,lemma,ner,depparse,coref',
                timeout=timeout,
                memory= memorysize,
                max_char_length = maxcharlength,
                threads = thread,
                output_format = 'json',
                be_quiet = suppress_output) as client:
            return client.annotate(self.string)

    def formatjson(self):
        """
            if format json does not contain coref then flag gives False
        """
        ann = self.generate()
        return ann
        # return ann
