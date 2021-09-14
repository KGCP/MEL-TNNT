import stanza
from string import punctuation
import json
import sys,os

sys.path.append(os.path.join(sys.path[0],'..'))
from read_file import config
class stanza_PT_DP_task:
    """
    the config file represents the installation location of stanza 'en' package
    """
    def create_pipeline(self,sentences):
        nlp = stanza.Pipeline(lang='en', dir = config['package-settings']['stanza']['resources-directory'], processors='tokenize,pos,lemma,depparse',verbose=False)
        doc = nlp(sentences)
        return doc

    def is_alpha(self,word):
        return word.isalpha()

    def is_stop(self,word):
        return (word in punctuation)

    # if flag = 0 indicates that the length of sentence is 1
    def pt_dp(self,sentences,flag):
        doc = self.create_pipeline(sentences)
        if flag == 1:
            pos_tag = [[] for _ in range(len(doc.sentences))]
            dependency_parser = [[] for _ in range(len(doc.sentences))]
            for i, sentence in enumerate(doc.sentences):
                for word in sentence.words:
                    if not self.is_stop(word.text):
                        pos_tag[i].append({
                            word.text: {
                                "lemma":word.lemma, 
                                "pos":word.upos, 
                                "tag":word.xpos, 
                                "alpha":self.is_alpha(word.text),
                                "starts" : int(word.misc.split("|")[0].split("=")[-1]),
                                "ends" : int(word.misc.split("|")[1].split("=")[-1]),
                            }
                        })
                        dependency_parser[i].append({word.text : {"dep" : word.deprel}})
            if len(pos_tag) == 1:
                pos_tag = pos_tag[0]
                dependency_parser = dependency_parser[0]
            return pos_tag,dependency_parser
        else:
            pos_tag = []
            dependency_parser = []
            for i, sentence in enumerate(doc.sentences):
                for word in sentence.words:
                    if not self.is_stop(word.text):
                        pos_tag.append({
                            word.text: {
                                "lemma":word.lemma, 
                                "pos":word.upos, 
                                "tag":word.xpos, 
                                "alpha":self.is_alpha(word.text),
                                "starts" : int(word.start_char),
                                # or int(word.misc.split("|")[0].split("=")[-1])
                                "ends" : word.end_char,
                                # or int(word.misc.split("|")[1].split("=")[-1])
                            }
                        })
                        dependency_parser.append({word.text : {"dep" : word.deprel}})
            if len(pos_tag) == 1:
                pos_tag = pos_tag[0]
                dependency_parser = dependency_parser[0]
            return pos_tag,dependency_parser

PT_DP_tasks_stanza = stanza_PT_DP_task()
