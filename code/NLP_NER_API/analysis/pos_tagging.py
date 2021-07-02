import json
import nltk 
from nltk import word_tokenize
from nltk.tokenize import TreebankWordTokenizer
from nltk.tokenize import PunktSentenceTokenizer
from string import punctuation

with open("C:\\Users\\horat\\Downloads\\_examples\\Use_case_1\\Dataset\\66459_0.pdf-layout.txt-MEL+NER_output.json") as f:
    jsonfile = json.load(f)
    text = jsonfile["Specific-Metadata"]["text-analysis"]['clean-text']

class nltk_pos_tagging:
    def __init__(self, pathname):
        self.pathname = pathname

    def tokenize(self,text):
        # tokenize the sentence
        tokenized_sent = PunktSentenceTokenizer().tokenize(text)

        #Word tokenizer
        word_tokenize = [TreebankWordTokenizer().tokenize(token) for token in tokenized_sent]

        pos_tag = [nltk.pos_tag(word) for word in word_tokenize]

        return tokenized_sent,pos_tag

    # remove punctuncation after the result
    def removePunctunation(self, tokenized_result):
        result = [[] for _ in range(len(tokenized_result))]
        for index in range(len(tokenized_result)):
            for voc_pos in tokenized_result[index]:
                if voc_pos[0] not in punctuation:
                    result[index].append(voc_pos)

        return result      

test = nltk_pos_tagging("C:\\Users\\horat\\Downloads\\_examples\\Use_case_1\\Dataset\\66459_0.pdf-layout.txt-MEL+NER_output.json")

segment,pos_tag = test.tokenize(text)
result = test.removePunctunation(pos_tag)
