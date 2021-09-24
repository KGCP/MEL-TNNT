import sys, os
from pathlib import Path
from os import listdir
from os.path import isdir,isfile, join
import json
sys.path.append(join(sys.path[0],'..','interface'))
sys.path.append(join(sys.path[0],'..',))
import path_function as pf 
import json_function as jf
from read_file import config
from copy import deepcopy
import statistics
label_classification = config['label-classification']

allowed_aggregation_function = config['allowed-aggregation-function']
##########################################################################################################################################################################
def find_json_file(l,path):
    for file in listdir(path):
        if (isdir(join(path,file))):
            find_json_file(l,join(path,file))
        elif (join(path,file).endswith(".json")):
            l.append(join(path,file))
    return l
 
# group the file which has the same filename
def group_json_file(path):
    json_group = dict()
    for p in path:
        # omit the MEL+MER_output
        if not 'MEL+NER_output' in p:
            key_dict = '{}--{}--{}'.format(str(p).split('--')[0],str(p).split('--')[1],str(p).split('--')[-1])
            json_group.setdefault(key_dict,[]).append(p)
    return json_group

"""
Unified format to summary file
{
    "model": "spacy_lg_model",
    "category": "ORG",
    "count": 3
},
{
    "model": "spacy_lg_model",
    "category": "GPE",
    "count": 4
}
"""
def normalise_list(lst_of_attr):
    # at first remove the last total set
    lst_of_attr = lst_of_attr[:-1]
    normalise_result = []
    for lst in lst_of_attr:
        if 'model' not in lst.keys():
            normalise_result.append(list(lst.values())[0])
        else:
            return lst_of_attr
    return normalise_result

def maximum(lst_of_attr):
    count = 0
    maximum_result = {}
    for ele in lst_of_attr:
        if count < ele['count']:
            count = ele['count']
            maximum_result = {
                "model": ele['model'],
                "value": count
            }
    return maximum_result

def minimum(lst_of_attr):
    count = float('inf')
    minimum_result = {}
    for ele in lst_of_attr:
        if count > ele['count']:
            count = ele['count']
            minimum_result = {
                "Model": ele['model'],
                "Value": count
            }
    return minimum_result

def frequencies(lst_of_attr):
    return {"Frequencies" : [ele['count'] for ele in lst_of_attr]}

def mean(lst_of_attr):
    avg = sum(frequencies(lst_of_attr)['Frequencies'])/len(lst_of_attr)
    return {"Mean" : avg}

def median(lst_of_attr):
    median = statistics.median(frequencies(lst_of_attr)['Frequencies'])
    return {"Median" : median}

def mode(lst_of_attr):
    mode = statistics.mode(frequencies(lst_of_attr)['Frequencies'])
    return {"Mode": mode}

def multimode(lst_of_attr):
    multi_mode = statistics.multimode(frequencies(lst_of_attr)['Frequencies'])
    return {"Multi-mode": multi_mode}

def std(lst_of_attr):
    lst = frequencies(lst_of_attr)['Frequencies']
    if len(lst) > 2:
        standard_deviation = statistics.stdev(frequencies(lst_of_attr)['Frequencies'])
    else: return None
    return {"Standard Deviation" : standard_deviation}

def var(lst_of_attr):
    lst = frequencies(lst_of_attr)['Frequencies']
    if len(lst) > 2:
        variance = statistics.variance(lst)
    else: return None
    return {"Variance" : variance}

def quartile(lst_of_attr):
    lst = frequencies(lst_of_attr)['Frequencies']
    if len(lst) > 4:
        quartiles = list(map(round, statistics.quantiles(lst,n=4)))
    else: return None
    return {"Quartile" : quartiles}

def geomean(lst_of_attr):
    lst = frequencies(lst)['Frequencies']
    geo_mean = round(statistics.geometric_mean(lst), 1)
    return {"Geometric Mean" : geo_mean}


# group
# l is a dictionary which is like ------------------------------------------------------------------------# 
# {'basedir\\Use_case_1\\Dataset\\2017-18 PBS - Finance.pdf--NER--8e8cca60facbdf.json': ------------------#
# ['basedir\\Use_case_1\\Dataset\\2017-18 PBS - Finance.pdf--NER--(spacy_lg_model)--8e8cca60facbdf.json',-#
#  'basedir\\Use_case_1\\Dataset\\2017-18 PBS - Finance.pdf--NER--(spacy_md_model)--8e8cca60facbdf.json',-#
# 'basedir\\Use_case_1\\Dataset\\2017-18 PBS - Finance.pdf--NER--(spacy_sm_model)--8e8cca60facbdf.json']}-#
# the key is path to json without model and the value is existing model-----------------------------------#
# it merges every model and provide the results ----------------------------------------------------------#
def aggregate_jsonfile_summary(l):
    def getAggregatedNER_JSONobj(_json):
        if ('NLP-NER-Aggregated-Summary' in _json.keys()):
            return _json['NLP-NER-Aggregated-Summary']
        elif ('NLP-NER-Aggregated-Summary-By-Category' in _json.keys()):
            return _json['NLP-NER-Aggregated-Summary-By-Category']
        return None

    def isAggregatedNER_JSONobj(_json):
        if ('NLP-NER-Aggregated-Summary' in _json.keys()):
            return True
        elif ('NLP-NER-Aggregated-Summary-By-Category' in _json.keys()):
            return False
        return None

    # @sergio(2021-03-15): Handling different versions of the JSON structure for the "Summary" object.
    def getSummaryNER_JSONobj(_json):
        if ('NLP-NER-Summary' in _json):
            return _json['NLP-NER-Summary']
        elif ('NLP-NER-Summary-(From-Last-Run)' in _json):
            return _json['NLP-NER-Summary-(From-Last-Run)']
        return None

    def insert_general_metadata(file,file_summary):
        _gm = file['General-Metadata']
        file_summary = jf.Json_dict('NLP-NER-Aggregated-Summary',file_summary)
        file_summary.update({'General-Metadata':_gm})
        file_summary['NLP-NER-Aggregated-Summary'] = file_summary.pop('NLP-NER-Aggregated-Summary')
        return file_summary

    def summary_stats(_json):
        _json_ = deepcopy(_json)
        cate_name = 'NLP-NER-Aggregated-Summary' if isAggregatedNER_JSONobj(_json) else 'NLP-NER-Aggregated-Summary-By-Category'
        for doc,values in getAggregatedNER_JSONobj(_json).items():
            for entity,models in values.items():
                _json_[cate_name][doc][entity] = {}
                for func in allowed_aggregation_function:
                    # use different function
                    key = func
                    try:
                        value = eval(key)(normalise_list(models))
                        _json_[cate_name][doc][entity][key] = value
                    except:
                        print(f"Your function request {key} does not exist")
        return _json_
                    

    def aggregated_Summary_By_Category(summarised_file):
        summarised_file = deepcopy(summarised_file)
        nnas = summarised_file['NLP-NER-Aggregated-Summary']
        gm_file = summarised_file['General-Metadata']
        gm_file['NLP-NER-Aggregated-Summary-By-Category'] = {}
        gm_dict = {}
        gm_count = {}
        # get the label classification
        for doc_num, entities in nnas.items():
            gm_file['NLP-NER-Aggregated-Summary-By-Category'].setdefault(doc_num,{})
            for cat, entity_list in entities.items():
                for ent in entity_list:
                    # if the model is in TNNT
                    for tnnt, model in label_classification.items():
                        for key,val in model.items():
                            if 'model' in ent.keys() and  ent['category'] == val and ent['model'] == key:
                                gm_file['NLP-NER-Aggregated-Summary-By-Category'][doc_num].setdefault(tnnt,[])
                                # calculate the total number of 
                                gm_count[tnnt] = gm_count.setdefault(tnnt, 0) + ent['count']
                                gm_file['NLP-NER-Aggregated-Summary-By-Category'][doc_num][tnnt].append({cat: {
                                    "model": ent['model'],
                                    "count": ent['count']
                                }})
       
        for doc_num, entities in nnas.items():
            for tnnt, model in label_classification.items():
                if tnnt in gm_count.keys():
                    gm_file['NLP-NER-Aggregated-Summary-By-Category'][doc_num][tnnt].append({ 'total' : gm_count[tnnt]})

        return gm_file

    file_summaries = [ dict() for _ in range(4)]
    """
    file_summaries[0] is summary by entity
    file_summaries[1] is summary by category
    file_summaries[2] is summary by entity with stats
    file_summaries[3] is summary by category with stats 
    """
    key = list(l.keys())[0]
    tailpath = str(Path(key).parts[-1])
    jsonpath = pf.pathExceptTail(key)
    # generate the summary json file
    summary_names = [ '{}--{}--(summary)--{}'.format(tailpath.split('--')[0],tailpath.split('--')[1],tailpath.split('--')[-1]), \
    '{}--{}--(summary-by-category)--{}'.format(tailpath.split('--')[0],tailpath.split('--')[1],tailpath.split('--')[-1]), \
    '{}--{}--(summary)--(stats)--{}'.format(tailpath.split('--')[0],tailpath.split('--')[1],tailpath.split('--')[-1]), \
    '{}--{}--(summary-by-category)--(stats)--{}'.format(tailpath.split('--')[0],tailpath.split('--')[1],tailpath.split('--')[-1])]
    summary_paths = []
    for i in range(4):
        summary_paths.append(Path(jsonpath).joinpath(summary_names[i]))

    # if file exists then do nothing
    if summary_paths[0].exists() or summary_paths[1].exists() \
        or summary_paths[2].exists() or summary_paths[3].exists():
        # return two empty dictionaries
        return [dict() for _ in range(4)]

    for value in l[key]:
        with open(value) as file:
            jsonfile = json.load(file)
            # jsonfilepath => summary_paths[0], filename_summary => file_summaries[0] 
            if str(summary_paths[0]) not in file_summaries[0] :
                file_summaries[0].update({str(summary_paths[0]) : getSummaryNER_JSONobj(jsonfile)})
            else:
                file_summaries[0][str(summary_paths[0])] = update_aggregation(file_summaries[0][str(summary_paths[0])] , getSummaryNER_JSONobj(jsonfile))
    # calculate each file summaries
    file_summaries[0] = file_summaries[0][str(summary_paths[0])] 
    file_summaries[0] = insert_general_metadata(jsonfile,file_summaries[0])
    file_summaries[1] = aggregated_Summary_By_Category(file_summaries[0])
    file_summaries[2] = summary_stats(file_summaries[0])
    file_summaries[3] = summary_stats(file_summaries[1])
    # generate summary file and summary_by_category_file
    for i in range(4):
        with open(summary_paths[i],'w') as output:
            json.dump(file_summaries[i],output)
    # generate stats summary file and summary_by_category_file
    return file_summaries


def update_aggregation(summary, data):
    # no need to update
    def updatedict(model,category,count):
        return {
            "model" : model,
            "category" : category,
            "count" : count
        }

    if summary == data:
        return summary

    for data_key in data.keys():
        for entity in data[data_key].keys():
            # if the model does not exist in current summary
            if entity not in summary[data_key].keys():
                summary[data_key].update({entity:data[data_key][entity]})
            else:
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

