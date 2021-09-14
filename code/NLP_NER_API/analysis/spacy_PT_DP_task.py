import spacy
from spacy.tokens import Token
from spacy.tokenizer import Tokenizer
from spacy.language import Language
import json
import re
def excluded(token):
    # Getter function to determine the value of token._.is_excluded
    return token.pos_ in ['SPACE'] or token.is_stop or token.dep_ in ['punct']

Token.set_extension('is_excluded', getter=excluded)

class spacy_PT_DP_task:
    def __init__(self):
        self.sentence = []
    
    def remove_blank_at_front(self,text):
        return text if text[0] != ' ' else text[1:]
    """
    tokenize the text
    return the list of dictionary with Text, Lemma, POS, TAG, isalpha, isstop
    """
    def pt_dp(self,text,flag):
        text = self.remove_blank_at_front(text)
        # tokenize the sentence
        nlp = spacy.load("en_core_web_sm")
        if flag == 1:
            # add sentencizer to the last pipeline of spacy
            nlp.add_pipe("sentencizer", last=True)
            doc = nlp(text)
            for sent in doc.sents:
                self.sentence.append(sent)
            pos_tag = [[] for _ in range(len(self.sentence))]
            dependency_parser = [[] for _ in range(len(self.sentence))]
            for sent in range(len(self.sentence)):
                for token in self.sentence[sent]:
                    if not token._.is_excluded:
                        pos_tag[sent].append({
                            token.text:{
                            "lemma":token.lemma_, 
                            "pos":token.pos_, 
                            "tag":token.tag_, 
                            "alpha":token.is_alpha,
                            "starts" : token.idx,
                            "ends" : token.idx + len(token.text),
                        }})
                        dependency_parser[sent].append({
                            token.text :{"dep" : token.dep_,
                        }})
            if len(pos_tag) == 1:
                pos_tag = pos_tag[0]
                dependency_parser = dependency_parser[0]
            return pos_tag, dependency_parser
        else:
            doc = nlp(text)
            pos_tag=[]; dependency_parser = []
            for token in doc:
                if not token._.is_excluded:
                    pos_tag.append({
                        token.text:{
                        "lemma":token.lemma_, 
                        "pos":token.pos_, 
                        "tag":token.tag_, 
                        "alpha":token.is_alpha,
                        "starts" : token.idx,
                        "ends" : token.idx + len(token.text),
                    }})
                    dependency_parser.append({
                        token.text :{"dep" : token.dep_,
                    }})
            if len(pos_tag) == 1:
                pos_tag = pos_tag[0]
                dependency_parser = dependency_parser[0]
            return pos_tag, dependency_parser
PT_DP_tasks_spacy = spacy_PT_DP_task()

