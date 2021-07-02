import sys, os
from pathlib import Path
from os import listdir
from os.path import isdir,isfile, join
import json

sys.path.append(join(sys.path[0],'..','interface'))
sys.path.append(join(sys.path[0],'..'))

import fileinfo
import datetime
import path_function as pf 
import json_function as jf
path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../config.json")
with open(path) as cf:
    config = json.load(cf)

base = config['base-directory']


def find_json_file(l,path):
    for file in listdir(path):
        if (isdir(join(path,file))):
            find_json_file(l,join(path,file))
        elif (join(path,file).endswith(".json")):
            l.append(join(path,file))
    return l
 
def group_json_file(path):
    json_group = dict()
    for p in path:
        # omit the MEL+MER_output
        if not 'MEL+NER_output' in p:
            key_dict = '{}--{}--{}'.format(str(p).split('--')[0],str(p).split('--')[1],str(p).split('--')[-1])
            json_group.setdefault(key_dict,[]).append(p)
    return json_group

# l is a dictionary which is form like 
# {'basedir\\Use_case_1\\Dataset\\2017-18 PBS - Finance.pdf--NER--8e8cca60facbdf.json': 
# ['basedir\\Use_case_1\\Dataset\\2017-18 PBS - Finance.pdf--NER--(spacy_lg_model)--8e8cca60facbdf.json',
#  'basedir\\Use_case_1\\Dataset\\2017-18 PBS - Finance.pdf--NER--(spacy_md_model)--8e8cca60facbdf.json', 
# 'basedir\\Use_case_1\\Dataset\\2017-18 PBS - Finance.pdf--NER--(spacy_sm_model)--8e8cca60facbdf.json']}
# the key is path to json without model and the key is existing model
# it merges every model and provide the results
def aggregate_jsonfile_summary(l):
    
    # @sergio(2021-03-15): Handling different versions of the JSON structure for the "Summary" object.
    def getSummaryNER_JSONobj(_json):
        if ('NLP-NER-Summary' in jsonfile):
            return jsonfile['NLP-NER-Summary']
        elif ('NLP-NER-Summary-(From-Last-Run)' in jsonfile):
            return jsonfile['NLP-NER-Summary-(From-Last-Run)']
        return None
    
    filename_summary = dict()

    for key in l.keys():

        # if file exists then do nothing
        tailpath = str(Path(key).parts[-1])
        jsonpath = pf.removeTailPath(key)
        jsonfilename = '{}--{}--summary--{}'.format(tailpath.split('--')[0],tailpath.split('--')[1],tailpath.split('--')[-1])
        jsonfilepath = Path(jsonpath).joinpath(jsonfilename)

        if (jsonfilepath).exists():
            continue
        
        for value in l[key]:

            with open(value) as file:
                jsonfile = json.load(file)
            
            if str(jsonfilepath) not in filename_summary:
                filename_summary.update( { str(jsonfilepath) : getSummaryNER_JSONobj(jsonfile) } )
            else:
                filename_summary[str(jsonfilepath)] = update(filename_summary[str(jsonfilepath)], getSummaryNER_JSONobj(jsonfile))

        _gm = jsonfile['General-Metadata']
        filename_summary[str(jsonfilepath)] = jf.Json_dict('NLP-NER-Aggregated-Summary',filename_summary[str(jsonfilepath)])
        filename_summary[str(jsonfilepath)].update({'General-Metadata':_gm})
        filename_summary[str(jsonfilepath)]['NLP-NER-Aggregated-Summary'] = filename_summary[str(jsonfilepath)].pop('NLP-NER-Aggregated-Summary')
        # filename_summary[str(jsonfilepath)]['NLP-NER-Summary-(From-Last-Run)'] = filename_summary[str(jsonfilepath)].pop('NLP-NER-Summary-(From-Last-Run)')
    for filepath in filename_summary.keys():
        with open(filepath,'w') as outfile:
            json.dump(filename_summary[filepath],outfile)
            
    return filename_summary


def update(summary, data):
    # no need to update

    if summary == data:
        return summary
    
    for data_key in data.keys():
        for entity in data[data_key].keys():
            # if the model does not exist in current summary
            if entity not in summary[data_key].keys():
                summary[data_key].update({entity:data[data_key][entity]})
            else:
                # 
                for index in range(len(data[data_key][entity][:-1])):
                    if data[data_key][entity][index]['model'] not in summary[data_key][entity][index].values():
                        # append the model
                        summary[data_key][entity].insert(-2,updatedict(
                            data[data_key][entity][index]['model'],
                            data[data_key][entity][index]['category'],
                            data[data_key][entity][index]['count'],
                        ))
                        
                        summary[data_key][entity][-1]['total'] += data[data_key][entity][index]['count']

        return summary


def updatedict(model,category,count):
    return {
        "model" : model,
        "category" : category,
        "count" : count
    }
