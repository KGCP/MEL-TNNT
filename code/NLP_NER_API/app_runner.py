'''
@component: NLP/NER Toolkit RESTful API.
@author: Xuecheng & Sergio.
@summary: RESTful API for the NLP/NER Toolkit results and functions.
@project: KG Tooling.
# History Update:
#    2021-03-27: Initial release on the server (production environment).
'''

#============================================================================================================#
# To read the json file
import json
import re
# To link with other python file
import sys,os
sys.path.append(os.path.join(sys.path[0],'interface'))
sys.path.append(os.path.join(sys.path[0],'analysis'))
import fileinfo
from aggregation import aggregate_jsonfile_summary
from path_function import traversePathIfExist,extractPathInfo,get,has_attribute,tail
from json_function import Json_dump, Json_dict, recursive, readJson,findEntityValueWithKey, searchKeyWord
import filter_summary
from stanza_PT_DP_task import PT_DP_tasks_stanza
from spacy_PT_DP_task import PT_DP_tasks_spacy
from coref_coreNLP import coreNLP
from pagination import partionlist,partiondict
# for Restful API
from flask import Flask,request,make_response,render_template,redirect
from flask_restful import Resource, Api
from read_file import config
# To deal with path
import pathlib
from pathlib import PurePath,Path

# add numpy to predict execution time
import numpy as np 
from sklearn.linear_model import LinearRegression

# To normalise the filename
from urllib.parse import quote

# To store logs
import logging

import time
#============================================================================================================#
app = Flask(__name__)
api = Api(app)
# base directory of file
codebasedir = os.path.dirname(__file__)
basedir = config['directories']['data']['base-directory']
MEL_NER_METHODS = "MEL+NER"
SUCCESS_AGGR   = config["outputs"]['SUCCESS_AGGR']
SUCCESS_POS_TAG = config["outputs"]['SUCCESS_POS_TAG']
SUCCESS_COREF = config['outputs']["SUCCESS_COREF"]
EMPTY_SEARCH   = config["outputs"]['EMPTY_SEARCH']
EMPTY_RESULTS  = config["outputs"]['EMPTY_RESULTS']
ERROR_ACCEPT   = config["outputs"]['ERROR_ACCEPT']
ERROR_AGGR     = config["outputs"]['ERROR_AGGR']
ERROR_AGGR_ALERT = config["outputs"]['ERROR_AGGR_ALERT']
ERROR_ARGS = config["outputs"]["ERROR_ARGS"]
ERROR_FILTER = config["outputs"]["ERROR_FILTER"]
ERROR_SEARCH = config["outputs"]["ERROR_SEARCH"]
ERROR_POS_TAG_NO_TOOL = config["outputs"]["ERROR_POS_TAG_NO_TOOL"]
ERROR_POS_TAG_NO_REPLACE = config["outputs"]["ERROR_POS_TAG_NO_REPLACE"]
ERROR_POS_TAG_NOT_EXIST_TOOL = config["outputs"]["ERROR_POS_TAG_NOT_EXIST_TOOL"]
ERROR_POS_TAG_FILE_EXIST = config['outputs']["ERROR_POS_TAG_FILE_EXIST"]
ERROR_COREF_NON_EXIST = config['outputs']["ERROR_COREF_NON_EXIST"]
ERROR_COREF_IS_EXIST = config['outputs']['ERROR_COREF_IS_EXIST']
ERROR_COREF = config['outputs']['ERROR_COREF']
FAIL_POS_TAG = config['outputs']["FAIL_POS_TAG"]
Abbr_Word_dict = config['abbreviation-of-word-dict']
allowed_directory = config['directories']['data']['allowed-directories']
find_entity = config['request-args']['entity']
pt_dp = config['request-args']['pt-dp-args']
aggr =  config['request-args']['aggr']  
allowed_attribute = config['allowed-attribute']
special_NEL_NER = config['special-NEL-NER']
# it contains the helpinfo in config.json
help_info = config['help']
help_request = config['request-args']['help']
max_elements_in_page = config['html-templates']['max-elements-in-page']
pt_dp_name = config['allowed-attribute'][0]
max_pages_in_row = config['html-templates']['max-pages-in-row']
coref_args = config['request-args']['CoRef_task']
path_to_stats= config['directories']['system']['stats']
path_to_logs = config['directories']['system']['logs']
retrieve_args = config['request-args']['CoRef_task']['retrieve']
directories_system = config['directories']['system']
file_size = config['package-settings']['core-nlp']['thread-settings']['file-size-boundary(in byte)']
def logger():
    log = logging.getLogger()
    log.setLevel(level=logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(f"{path_to_logs}/app.log",
                            mode = 'w',
                            encoding = 'utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)

def isAcceptJSON():
    return (request.headers['Accept'] == 'application/json')

def isAcceptHTMLorDefault():
    return ('text/html' in request.headers['Accept']) or\
         ('*/*' in request.headers['Accept']) or\
         ('*' in request.headers['Accept']) or\
         ('' in request.headers['Accept'])

""" 
To get the name of file from MEL+NER file
"""
def extractMELNERFilename(jsonfilename):
    length_before_extended_name = len(jsonfilename.split('.')[0])
    string_before_extended_name = jsonfilename.split('.')[0]
    # iterate to see a '-' symbol then stops
    for char in range(length_before_extended_name,len(jsonfilename)):
        string_before_extended_name += str(jsonfilename[char])
        if str(jsonfilename[char]) == '-':
            break
    return string_before_extended_name[:-1]

"""
If the url is not correctly spelled, then it will redirect to normalized url.
"""
def http_normalize_slashes(url):
    url = str(url)
    segments = url.split('/')
    correct_segments = []
    for segment in segments:
        if segment != '':
            correct_segments.append(segment)
    first_segment = str(correct_segments[0])
    if first_segment.find('http') == -1:
        correct_segments = ['http:'] + correct_segments
    correct_segments[0] = correct_segments[0] + '/'
    normalized_url = '/'.join(correct_segments)
    return normalized_url

def is_MEL_NER_File(jsonfilename):
    return MEL_NER_METHODS in jsonfilename

def is_PT_DP_File(jsonfilename):
    return "PT_DP" in jsonfilename

def get_file_name(jsonfilename):
    filename = extractMELNERFilename(jsonfilename) if is_MEL_NER_File(jsonfilename) else jsonfilename.split("--")[0]
    return filename

def get_file_name_except_hash(jsonfilename):
    return jsonfilename.replace(f"--{jsonfilename.split('--')[-1]}",'')

"""
    extract the MEL+NER name from JSON file
"""
def extract_file(MEL_NER_FILE):
    MEL_idx = MEL_NER_FILE.find(MEL_NER_METHODS)
    for idx in range(MEL_idx,len(MEL_NER_FILE)):
        if MEL_NER_FILE[idx] == '.' or MEL_NER_FILE[idx] == '-':
            return MEL_NER_FILE[MEL_idx:idx]
            
def getModel(jsonfilename):
    
    model = extract_file(jsonfilename) if is_MEL_NER_File(jsonfilename) else find_element_in_bracket(jsonfilename,0) # the first element in the bracket
    return model

def getHash(jsonfilename):
    if not is_MEL_NER_File(jsonfilename):
        return jsonfilename.split('--')[-1]

"""
    Get the content in the brackets. By using regular expression
"""
def find_element_in_bracket(string,group_num):
    try:
        result = re.findall(r'\(.*?\)', string)[group_num]
    except:
        return
    return result.replace('(','').replace(')','')

# the method in PT_DP method
def get_PT_DP_method(jsonfilename):
    PT_DP_method = find_element_in_bracket(jsonfilename,0) if is_MEL_NER_File(jsonfilename) else jsonfilename.split("--")[-2]
    return PT_DP_method.replace('(','').replace(')','')

"""
    To check if it contains ['_stats','_outputs']
"""
def is_in_keyword(method):
    return method == PurePath() or str(get(method,0)) in special_NEL_NER 
        
def pos_tag_sentence(model,jsonfile,methods):
    if not is_MEL_NER_File(model):
        output = jsonfile['NLP-NER'][model]['_output']
        for ks,vs in output.items():
            for v in vs:
                if 'sentence' in v.keys():
                    v["POS-tagging"] = dict()
                    v["dependency-parsing"] = dict()
                    for method in methods:
                        pos,dep = getattr(eval(method), 'pt_dp')(v['sentence'],0)
                        v["POS-tagging"].setdefault(method,pos)
                        v["dependency-parsing"].setdefault(method,dep)
                else:
                    return 
        return jsonfile
    else:
        if "Specific-Metadata" in  jsonfile.keys():
            clean_text = jsonfile['Specific-Metadata']['text-analysis']['clean-text']
            jsonfile['Specific-Metadata']['text-analysis']['POS-tagging'] = dict()
            jsonfile['Specific-Metadata']['text-analysis']['dependency-parsing'] = dict()
            for method in methods:  
                pos,dep = getattr(eval(method), 'pt_dp')(clean_text,1)
                jsonfile['Specific-Metadata']['text-analysis']['POS-tagging'].setdefault(method,pos)
                jsonfile['Specific-Metadata']['text-analysis']['dependency-parsing'].setdefault(method,pos)
        return jsonfile

"""
Giving help instructions.
id = 0, providing search instructions
id = 1, providing search and aggr instructions
id = 2, providing search entity and pos-tag instructions
id = 3, providing search entity instructions
id = 4, providing filter function in summary
"""
def help(id):
    return {"Allowed-request" : help_info[id]}

def getpageno(page):
    page = page-1 if page else 0
    return page 
    
def contain_sentence(path):
    def open_file(path):
        with open(path) as f:
            jsonfile = json.load(f)
        return jsonfile

    # if the file is 
    if is_MEL_NER_File(path) or\
        is_PT_DP_File(path):
        return "YES"
    elif "summary" in path:
        return "NO"
    else:
        try:
            nlp_ner = open_file(path)["NLP-NER"]
            first_element = list(list(list(nlp_ner.values())[0].values())[0].values())[0][0] 
            if 'sentence' in first_element.keys():
                return "YES"
            else:
                return "NO"
        except:
            return "NO"

"""
flag = "all",
flag = "spacy",
flag = "stanza"
"""
def store(size_of_file,time,flag):
    with open(os.path.join(codebasedir,f"{path_to_stats}/{flag}.txt"),"a") as f:
        f.write(str(size_of_file) + " " + str(time) + "\n")
    return 

def ReadandPredict(flag, size_of_file):
    times = []; size_of_files = [];
    with open(os.path.join(codebasedir,f"{path_to_stats}/{flag}.txt"),"r")  as f:
        line = f.readline()
        while line:
            size_of_files.append(line.split(" ")[0])
            times.append(line.split(" ")[1])
            line = f.readline()
            
    times = np.array(times,dtype=np.float32); size_of_files = np.array(size_of_files,dtype=np.float32).reshape(-1,1)
    reg = LinearRegression().fit(size_of_files, times)
    coef_ = reg.coef_[0]
    intercept_ = reg.intercept_
    y = round((coef_ * size_of_file + intercept_)/60) if (coef_ * size_of_file + intercept_) > 0 else "< 1"
    return y
    
def is_all_json(model):
    return "summary" in str(model) 

def is_special_attribute(filename):
    for attr in allowed_attribute:
        if attr in filename:
            return True
    return False

def isSystem(pathname):
    for d in directories_system.keys():
        if '_' + d == pathname:
            return True
    return False
 
# sys for "stats" or "logs"
# It is able to generate several files with outputs.
def readText(sys):
    # head to system files (e.g. stats or logs)
    pathtosys = eval(f"path_to{sys}")
    # initialise the dictionary
    sysresult = {
        sys : {}
    }
    for path in Path(pathtosys).iterdir():
        filename = tail(path)
        # set every path to a dictionary
        sysresult[sys][str(filename)] = {}

        with open(path,'r') as f: 
            lines = f.readlines()
        
        count = 0
        for line in lines:
            count += 1
            sysresult[sys][str(filename)][f"line {count}"] = line

    return sysresult

class path(Resource):
    jsonfile = []
    # from the fileset with given filename and method to find the exact file
    # And return the whole json filename and the list of path to that file
    def findJsonFile(self, pathname,fileSet, filename, method, search):
        def method_in_file(method, file):
            for i,ele in enumerate(method.split('|')):
                if ele not in file:
                    return False
            return True
        
        pathToFileDict = dict()
        uniqueFileDict = dict()
        for file in list(fileSet):
            full_path_to_file = str(Path(pathname).joinpath(file))
            if is_MEL_NER_File(file):
                if (method and (len(method.split('|'))==1 and pt_dp_name not in file or len(method.split('|'))>1 and method_in_file(method,file)) and\
                     get_file_name(file) == str(filename) and str(filename) in file and is_MEL_NER_File(method) and method == getModel(file)) or\
                    (get_file_name(file) == str(filename) and method is None and search is None) or\
                    (search and get_file_name(file) == str(filename) and method is None and str(search) in file ) or\
                    (method and len(method.split('|'))==2 and get_file_name(file) == str(filename) and str(filename) in file and method.split('|')[0] == getModel(file) and method.split('|')[1] in file):
                    # coreference
                    pathToFileDict[file] = full_path_to_file
            # if the file has suffixes
            elif (Path(file).suffix != ""): 
                if method and (len(method.split('|'))==1 and len(file.split('--')) == 4 and pt_dp_name not in file or len(method.split('|'))>1 and method_in_file(method,file)) and method.split('|')[0] == getModel(file) and (str(filename) == get_file_name(file) or\
                      str(filename) == getHash(file) ) and str(filename) in str(file) or\
                (method is None and search is None and (str(filename) == get_file_name(file) or str(filename) == getHash(file))) or\
                (method is None and search and (str(filename) == get_file_name(file) or str(filename) == getHash(file))  and str(search) in file) or\
                (method and len(method.split('|'))==2 and get_file_name(file) == str(filename) and str(filename) in file and method.split('|')[0] == getModel(file) and method.split('|')[1] in file):
                    if (get_file_name_except_hash(file) not in uniqueFileDict.keys()):
                        pathToFileDict[file] = full_path_to_file
                        # set key as the filename without hashes and value as the full directory path to file
                        uniqueFileDict.setdefault(get_file_name_except_hash(file),full_path_to_file)
                    else:
                        latest_file_path = fileinfo.compare_file_date(uniqueFileDict[get_file_name_except_hash(file)],full_path_to_file)
                        # if the latest_file_path is larger then the original file.
                        if latest_file_path == full_path_to_file:
                            pathToFileDict.pop(str(Path(uniqueFileDict[get_file_name_except_hash(file)]).parts[-1]))
                        uniqueFileDict[get_file_name_except_hash(file)] = latest_file_path
                        pathToFileDict[file] = latest_file_path         
        return pathToFileDict

    def get(self, pathname): 
        # catch the search key words
        search = request.args.get(config['request-args']['search'])
        page_no = getpageno(request.args.get('page',type=int))
        pathToJson,filenameandModel,fileAttribute = extractPathInfo(basedir,pathname,allowed_attribute)
        # if pathToJson is null do nothing
        if pathToJson == PurePath(): return 
        if not (isAcceptJSON() or isAcceptHTMLorDefault()): return ERROR_ACCEPT
        # return back to a normal url
        if (http_normalize_slashes(request.url)!=request.url):
            return redirect(http_normalize_slashes(request.url),code=302)

        # when the path is in system set-up (e.g. stats/logs)
        if isSystem(pathname):
            return readText(pathname)

        # if path is valid then let user for visited
        if (traversePathIfExist(basedir,pathToJson,allowed_directory)):
            cpltPathtoJson = Path(basedir).joinpath(pathToJson)
            # if the path depth is not long which means that it only gives the path to json
            # When dealing with the path _examples/_____/==================================================#
            if filenameandModel == [] and fileAttribute == PurePath():
                # dealing with the helping argument
                if help_request in request.args:
                    response = make_response(help(0))
                    response.headers = config['json-header']
                    return response

                fileSet = set()
                directorySet = set()
                for file in cpltPathtoJson.iterdir():
                    if ((Path(file).suffix == '.json' and search is None)\
                        or (Path(file).suffix == '.json' and search and str(search) in str(file.parts[-1]))):
                        if is_MEL_NER_File(str(file.parts[-1])):
                            fileSet.add(extractMELNERFilename(str(file.parts[-1])))
                        else:
                            fileSet.add(str(file.parts[-1]).split('--')[0])
                    elif ((Path(file).suffix == '' and search is None)\
                        or (Path(file).suffix == '' and search and str(search) in str(file.parts[-1]))):
                        directorySet.add(str(file.parts[-1]))
                # this generate unique filename
                listofFilename = list(fileSet|directorySet)
                page_split_list = partionlist(listofFilename,max_elements_in_page)
                # if the page_split_list is less than page_no then return wrong results
                if len(page_split_list) <= page_no: return EMPTY_RESULTS
                if len(listofFilename) <1: return EMPTY_RESULTS
                if isAcceptJSON(): 
                    response = make_response({
                        "Filenames" : fileSet,
                        "Folders" : directorySet
                        })
                    response.headers = config['http-headers']['json-header']
                elif isAcceptHTMLorDefault():
                    for k in allowed_directory.keys():
                        if allowed_directory[k] == str(cpltPathtoJson):
                            title = k
                        elif allowed_directory[k] in str(cpltPathtoJson):
                            title = ''

                    response = make_response(render_template('pathpages.html',
                                                    file = page_split_list[page_no], 
                                                    len = len(page_split_list[page_no]),
                                                    pathname = pathname,
                                                    page_no = page_no+1,
                                                    pagenum = len(page_split_list),
                                                    title = title,
                                                    containsentencelist = None,
                                                    max_pages_in_row = max_pages_in_row,
                                                    datelist = None,
                                                    sizelist = None,
                    ))
                    response.headers = config['http-headers']['html-header']
                return response
            #==========================================================================================================#
            else:
                filename = filenameandModel[0]
                method = []
                fileSet = [str(file.parts[-1]) for file in cpltPathtoJson.iterdir() if file.suffix == '.json']
                def coref_generated():
                    flag = False
                    for f in fileSet:
                        if str(filename) in f and '(coref)' in f:
                            flag = True
                    return flag

                def is_retrieve_full():
                    return request.args.get('retrieve') == 'full'
           
                def is_retrieve_corefs():
                    return request.args.get('retrieve') == 'corefs'

                def is_retrieve_sentences():
                    return request.args.get('retrieve') == 'sentences'

                # When only given the filename but without method When dealing _examples/filename/====================#
                if len(filenameandModel) == 1:
                    pathToFileDict = self.findJsonFile(cpltPathtoJson,fileSet, filename, None, search)
                    if pathToFileDict == dict(): return EMPTY_RESULTS
                    # during help==============================================================================#
                    if help_request in request.args:
                        response = make_response(help(1))
                        response.headers = config['http-headers']['json-header']
                        return response
                    # coref task =============================================================================#
                    if 'CoRef_task' in request.args and 'retrieve' in request.args:
                        if request.args.get(coref_args['repl']) in ['0','1'] and \
                            request.args.get('retrieve') in retrieve_args:
                            # Since the file with the same name but with different models have the same "CLEANTEXT" to generate
                            fileTocoref = list(pathToFileDict.values())[0]
                            if 'MEL' in fileTocoref:
                                if coref_generated() and request.args.get(coref_args['repl']) == '0':
                                    return ERROR_COREF_IS_EXIST
                                else:
                                    with open(fileTocoref,'r') as f:
                                        data = json.load(f)
                                        # if the file is mel_ner file
                                        if "Specific-Metadata" in data.keys():
                                            clean_text = data['Specific-Metadata']['text-analysis']['clean-text']
                                            # When coreference resolution task is performed on specific metadata,
                                            # the thread is directly setting to max_thread.
                                            cNLP = coreNLP(clean_text,file_size)
                                            cNLP = cNLP.formatjson()
                                            outputfilename = f"{filename}-MEL+NER_output-(coref).json"
                                            #normalise the filename
                                            outputfilepath = str(os.path.join(cpltPathtoJson,outputfilename))
                                            with open(outputfilepath,'w') as f:
                                                json.dump(cNLP,f)
                                            # full retrieve
                                            if request.args.get('retrieve') == 'full':
                                                return cNLP
                                            # sentence retrieve
                                            else:
                                                return cNLP[request.args.get('retrieve')]
                                        else:
                                            return ERROR_COREF_NON_EXIST
                        return ERROR_COREF
                    # during aggregation=======================================================================#
                    if aggr in request.args:
                        # deal with the situation in MEL+NER situation
                        l = dict()
                        try:
                            for file in list(pathToFileDict.values()):
                                if not (is_MEL_NER_File(file) or is_special_attribute(file)): 
                                    l.setdefault(file.replace(Path(file).parts[-1].split('--')[2],''),[]).append(file)
                        except:
                            return ERROR_AGGR
                    # wait to change summary
                    # if the aggregated file is null then shows the error message.
                        if (aggregate_jsonfile_summary(l) == [dict() for _ in range(4)] ):
                            return ERROR_AGGR
                        else:
                            return SUCCESS_AGGR
                        return ERROR_AGGR_ALERT
                    #==========================================================================================#
                    for i in list(pathToFileDict.keys()):
                        if not is_MEL_NER_File(i):
                            # if the file contains coreference resolution
                            if 'coref' not in i:
                                i = i.replace('--NER','').replace(i.split('--')[-1],'')[:-2]
                        else:
                            attr = "" if not has_attribute(allowed_attribute,i) else f"--{find_element_in_bracket(i,-1)}"
                            i = f"{extractMELNERFilename(i)}--{extract_file(i)}{attr}"
                        method.append(i.replace('(','').replace(')','').replace(".json",""))
                    if isAcceptJSON(): 
                        response = make_response(Json_dump('Models', method))
                        response.headers = config['http-headers']['json-header']
                    elif isAcceptHTMLorDefault():
                        page_split_list = partionlist(method,max_elements_in_page)
                        if len(page_split_list) <= page_no: return EMPTY_RESULTS
                        datelist = [fileinfo.createDate(i) for i in list(pathToFileDict.values())]
                        date_split_list = partionlist(datelist,max_elements_in_page)
                        sizelist = [fileinfo.size(i) for i in list(pathToFileDict.values())]
                        size_split_list = partionlist(sizelist,max_elements_in_page) 
                        sentence_list = [contain_sentence(i) for i in list(pathToFileDict.values())]
                        sentence_split_list = partionlist(sentence_list,max_elements_in_page) 
                       
                        response = make_response(render_template('pathpages.html',
                                                        file = page_split_list[page_no], 
                                                        len = len(page_split_list[page_no]),
                                                        page_no = page_no+1,
                                                        pathname = pathname,
                                                        containsentencelist = sentence_split_list[page_no],
                                                        max_pages_in_row = max_pages_in_row,
                                                        pagenum = len(page_split_list),
                                                        title = '',
                                                        datelist = date_split_list[page_no],
                                                        sizelist = size_split_list[page_no],
                        ))
                        
                        response.headers = config['http-headers']['html-header']
                    return response
                #========================================================================================================#
                #When opening derivative file like coref file ===========================================================#
                #When dealing with the jsonFile ========================================================================#
                #under this pathToFileDict should contain only one file 
                model = "|".join(filenameandModel[1:])
                pathToFileDict = self.findJsonFile(cpltPathtoJson,fileSet, filename, model, search)
                # if url name contains coref then go through that file:
                if 'coref' in Path(pathname).parts:
                    with open (list(pathToFileDict.values())[0]) as jf:
                        jsonfile = json.load(jf)
                        return jsonfile
                    return EMPTY_RESULTS
                try:
                    completejsonfilepath = list(pathToFileDict.values())[0]
                    with open (completejsonfilepath) as f:
                        jsonfile = json.load(f)
                except:
                    return EMPTY_RESULTS
                # summary is demonstrating the whole summary file
                content = jsonfile if is_all_json(model) and fileAttribute == PurePath() else recursive(jsonfile,fileAttribute,is_MEL_NER_File(completejsonfilepath),is_in_keyword(fileAttribute))
                #When dealing with the args ====================================#   
                if request.args:
                    for req in request.args:
                        if req in find_entity.keys():
                            try:
                                response =  make_response(findEntityValueWithKey(content,req,find_entity[req],str(fileAttribute.parts[-1])))
                                response.headers = config['http-headers']['json-header']
                                return response
                            except:
                                return ERROR_ARGS
                        elif req == config['request-args']['search']:
                            return ERROR_SEARCH
                        # to search the substring
                        elif (req[0] == '*' and req[-1] == '*'):
                            response =  make_response(Json_dict("search: " + str(req),searchKeyWord(content, req[1:-1],start=1,end=1,l={})))
                            response.headers = config['http-headers']['json-header']
                            return response
                        elif req[0] == '*' and req[-1] != '*': 
                            response =  make_response(Json_dict("search: " + str(req),searchKeyWord(content, req[1:],end=1,l={})))
                            response.headers = config['http-headers']['json-header']
                            return response
                        elif req[0] != '*' and req[-1] == '*': 
                            response =  make_response(Json_dict("search: " + str(req),searchKeyWord(content, req[:-1],start=1,l={})))
                            response.headers = config['http-headers']['json-header']
                            return response
                        #if the method is summary then can do filtering function or return error=================================#
                        elif req in config['request-args']['filterfunction']:
                            if str(model) == 'summary':
                                response = make_response(getattr(filter_summary,config['request-args']['filterfunction'][req])(jsonfile))
                                response.headers = config['http-headers']['json-header']
                                return response
                            else: 
                                return ERROR_FILTER
                            
                        # predict the execution time
                        elif req == "predict":
                            # if predict the tool
                            if 'tool' in request.args:
                                tool = request.args.get(pt_dp['tool'])
                                if tool in pt_dp['pt-dp-tool'].keys():
                                    predict_time = ReadandPredict(tool,fileinfo.size(completejsonfilepath)) 
                                    return make_response(Json_dict(f"predicted elapsed time (minutes) in {tool} tool", predict_time))
                        # if is requested to do pos-tagging and dependency parsing=====================#    
                        elif req == pt_dp['PT-DP']:
                            if 'tool' in request.args:
                                start = time.process_time()
                                tool = request.args.get(pt_dp['tool'])
                                if tool in pt_dp['pt-dp-tool'].keys():
                                    methods = pt_dp['pt-dp-tool'][tool].split('|')
                                    toolname = f"{pt_dp_name}_all" if tool == '' or tool == 'all' else f'{pt_dp_name}_{tool}' 
                                    if request.args.get(pt_dp['replace']) == "0":
                                        for file in fileSet:
                                            if (get_file_name(file) == str(filenameandModel[0]) and str(filenameandModel[1]) == getModel(file)):
                                                if (MEL_NER_METHODS not in file and find_element_in_bracket(file,1)) == toolname or\
                                                    (MEL_NER_METHODS in file and find_element_in_bracket(file,0)) == toolname: 
                                                    return ERROR_POS_TAG_FILE_EXIST   
                                    if request.args.get(pt_dp['replace']) in ["0","1"] :               
                                        if MEL_NER_METHODS in str(completejsonfilepath):
                                            postagfilepath = str(completejsonfilepath)[:-5] + f"-({toolname})" + str(completejsonfilepath)[-5:] 
                                        else:
                                            postagfilepath = f'{"--".join(str(completejsonfilepath).split("--")[0:3])}--({toolname})--{str(completejsonfilepath).split("--")[-1]}'
                                        if pos_tag_sentence(str(model),jsonfile,methods):
                                            with open(postagfilepath, "w") as outfile:
                                                json.dump(pos_tag_sentence(str(model),jsonfile,methods),outfile)
                                            elapsed_time = time.process_time() - start
                                            # store the time after execution
                                            store(fileinfo.size(completejsonfilepath),elapsed_time,tool)
                                            return SUCCESS_POS_TAG
                                        else:
                                            return FAIL_POS_TAG
                                else:
                                    return ERROR_POS_TAG_NOT_EXIST_TOOL
                            else:
                                return ERROR_POS_TAG_NO_TOOL
                        
                        elif req in "CoRef_task" and request.args.get(coref_args['repl']) in ['0','1']:
                            # if file has been generated:
                            if coref_generated() and request.args.get(coref_args['repl']) == '0':
                                return ERROR_COREF_IS_EXIST
                            else:
                                # if the file is mel_ner file
                                if not is_MEL_NER_File(str(filename)):
                                    output = jsonfile['NLP-NER'][model]['_output']
                                    outputfilename = f"{filename}--{model}--(coref).json"
                                    coref_output = {}
                                    filesize = fileinfo.size(completejsonfilepath)
                                    for catg, ents in output.items():
                                        for ent in ents:
                                            if 'sentence' in ent.keys():
                                                entity = ent['entity']
                                                start_index = ent['start_index']
                                                sentence = ent['sentence']
                                                cNLP = coreNLP(sentence,filesize)
                                                cNLP = cNLP.formatjson()
                                                
                                                # normalise entity name
                                                outputfilepath = str(os.path.join(cpltPathtoJson,outputfilename))
                                                if request.args.get('retrieve') == 'full':
                                                    cNLP = cNLP
                                                elif request.args.get('retrieve') in ['corefs', 'sentences']:
                                                    cNLP = cNLP[request.args.get('retrieve')]
                                                else:
                                                    return ERROR_COREF_NON_EXIST

                                                coref_result = {
                                                    "sentence" : sentence,
                                                    "results" : cNLP
                                                }
                                                coref_output.setdefault("co-reference-resolution-results",[]).append(coref_result)

                                    with open(outputfilepath,'w') as f:
                                        json.dump(coref_output,f)

                                    return coref_output
                                return ERROR_COREF_NON_EXIST
                        #===============================================================================#
                            # jump out of the loop
                            break

                        elif req == help_request:
                            # during help==============================================================================#
                            response = make_response(help(3)) if fileAttribute != PurePath() else make_response(help(2))
                            if str(model) == 'summary':
                                response = make_response(help(4))
                            response.headers = config['http-headers']['json-header']
                            return response
                        #========================================================================================================
                    return ERROR_ARGS
                #===============================================================#
                if fileAttribute != PurePath():
                    response = make_response(Json_dict(f"search-keyword: {str(fileAttribute.parts[-1])}| displaying exact matches", content))
                else:
                    # if the method is summary demonstrates the whole thing
                    if (is_all_json(model)):
                        response = make_response(jsonfile)
                    else:
                        response = make_response(Json_dump('_stats', content))
                response.headers = config['http-headers']['json-header']
                return response
        else:   return EMPTY_RESULTS
        return ERROR_ACCEPT
            

class index(Resource):
    # get the file
    def get(self):
        # if request header is application/json
        file = dict()
        page_no = getpageno(request.args.get('page',type=int))
        for k,v in allowed_directory.items():
            file.setdefault(str(k),str(v).replace(basedir,''))
        page_split_list = partiondict(file,max_elements_in_page)
        # if the page_split_list is less than page_no then return wrong results
        if len(page_split_list) <= page_no: return EMPTY_RESULTS
        if isAcceptJSON():
            response = make_response(Json_dump('Folders',list(file.values())))
            response.headers = config['http-headers']['json-header']
            return response
        # if request header is text/html or could be ran on google chrome
        elif isAcceptHTMLorDefault():
            # set the headers to text/html
            response = make_response(render_template('pathpages.html',
                                                    file = page_split_list[page_no], 
                                                    len = 1,
                                                    pathname = '/',
                                                    containsentencelist = None,
                                                    page_no = page_no+1,
                                                    max_pages_in_row = max_pages_in_row,
                                                    pagenum = len(page_split_list),
                                                    datelist = None,
                                                    sizelist = None,
            ))
            response.headers = config['http-headers']['html-header']
            return response
        else:
            return ERROR_ACCEPT


api.add_resource(index, '/')
api.add_resource(path,'/<path:pathname>')

if __name__ == '__main__':
    # app.run(debug=True, port=config['tcp-port'])
    app.config['DEBUG'] = bool(config['WSGI-server']['debug-flag'])
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True 
    app.config['SERVER_NAME'] = f"{config['WSGI-server']['server-host']}:{config['WSGI-server']['tcp-port']}"
    # run and store the log
    logger()
    app.run()
