# to copy the dictionary
import copy
import os
import json
#get the punctuation
from string import punctuation

import re
import functionforfile as f 

path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../config.json")
with open(path) as cf:
    config = json.load(cf)

base = config['base-directory']

# extract the jsonfile summary

# filtering
# extract the string contains number
def filternum(summaryfilename):
    with open(summaryfilename) as f:
        jsonfile = json.load(f)['NLP-NER-Aggregated-Summary']
        jsonresults = copy.deepcopy(jsonfile)
        for doc_key in jsonfile.keys():
            for entity in jsonfile[doc_key].keys():
                flag = True
                for m in entity:
                    if m.isdigit():
                        flag = False
                        break
                if flag:
                    jsonresults[doc_key].pop(entity,None)    
    return jsonresults

# filtering
#extract the string only contain number
def filterOnlyNum(summaryfilename):
    with open(summaryfilename) as f:
        jsonfile = json.load(f)['NLP-NER-Aggregated-Summary']
        jsonresults = copy.deepcopy(jsonfile)
        for doc_key in jsonfile.keys():
            for entity in jsonfile[doc_key].keys():
                judgemodel = [m.isdigit() for m in entity if m not in punctuation and m not in ' ']
                if not all(judgemodel):
                    jsonresults[doc_key].pop(entity,None)
    return jsonresults

# filtering
#extract the string only contain alphbetical string
def filterOnlyString(summaryfilename):
    with open(summaryfilename) as f:
        jsonfile = json.load(f)['NLP-NER-Aggregated-Summary']
        jsonresults = copy.deepcopy(jsonfile)
        for doc_key in jsonfile.keys():
            for entity in jsonfile[doc_key].keys():
                judgemodel = [m.isalpha() for m in entity if m not in punctuation and m not in ' ']
                if not all(judgemodel):
                    jsonresults[doc_key].pop(entity,None)
    return jsonresults

# filtering
#extract the string with website
def filterwebsite(summaryfilename):
    with open(summaryfilename) as f:
        jsonfile = json.load(f)['NLP-NER-Aggregated-Summary']
        jsonresults = copy.deepcopy(jsonfile)
        for doc_key in jsonfile.keys():
            for entity in jsonfile[doc_key].keys():
                regexp = re.compile('((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')
                if (not regexp.search(entity)):
                    jsonresults[doc_key].pop(entity,None)
    return jsonresults
