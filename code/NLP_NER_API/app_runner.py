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
from path_function import traversePathIfExist,extractPathInfo
from json_function import Json_dump, Json_dict, recursive, findEntityValueWithKey, searchKeyWord
import filter_summary

# for Restful API
from flask import Flask,request,make_response,render_template,redirect
from flask_restful import Resource, Api

# To deal with path
import pathlib
from pathlib import PurePath,Path
#============================================================================================================#

app = Flask(__name__)
api = Api(app)

path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.json")
with open(path) as cf:
    config = json.load(cf)

basedir = config['base-directory']
MEL_NER_METHODS = "MEL+NER"
EMPTY_SEARCH   = config["outputs"]['EMPTY_SEARCH']
EMPTY_RESULTS  = config["outputs"]['EMPTY_RESULTS']
ERROR_ACCEPT   = config["outputs"]['ERROR_ACCEPT']
ERROR_AGGR     = config["outputs"]['ERROR_AGGR']
SUCCESS_AGGR   = config["outputs"]['SUCCESS_AGGR']
ERROR_AGGR_ALERT = config["outputs"]['ERROR_AGGR_ALERT']
ERROR_ARGS = config["outputs"]["ERROR_ARGS"]
ERROR_FILTER = config["outputs"]["ERROR_FILTER"]
ERROR_SEARCH = config["outputs"]["ERROR_SEARCH"]
Abbr_Word_dict = config['abbreviation-of-word-dict']
allowed_directory = config['allowed-directories']
find_entity = config['request-args']['entity']

def isAcceptJSON():
    return (request.headers['Accept'] == 'application/json')

def isAcceptHTMLorDefault():
    return ('text/html' in request.headers['Accept']) or\
         ('*/*' in request.headers['Accept']) or\
         ('*' in request.headers['Accept']) or\
         ('' in request.headers['Accept'])

# To get the name of file from MEL+NER file
def extractMELNERFilename(json):
    length_before_extended_name = len(json.split('.')[0])
    string_before_extended_name = json.split('.')[0]
    # iterate to see a '-' symbol then stops
    for char in range(length_before_extended_name,len(json)):
        string_before_extended_name += str(json[char])
        if str(json[char]) == '-':
            break
    return string_before_extended_name[:-1]

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

class path(Resource):
    jsonfile = []
    # from the fileset with given filename and method to find the exact file
    # And return the whole json filename and the list of path to that file
    def findJsonFile(self, pathname,fileSet, filename, method, search):
        pathToFileDict = dict()
        for file in list(fileSet):
            # if the file contain MEL_NER
            if (MEL_NER_METHODS in file):
                if (str(method) == MEL_NER_METHODS and extractMELNERFilename(file) == str(filename) and str(filename) in file and method) or\
                    (extractMELNERFilename(file) == str(filename)and method is None and search is None) or\
                    (extractMELNERFilename(file) == str(filename) and method is None and str(search) in file and search):
                    pathToFileDict.setdefault(file,str(Path(pathname).joinpath(file)))
            # if the file does not contain MEL_NER and has suffix
            elif (Path(file).suffix != ''):
                if (str(method) == file.split('--')[-2].replace('(','').replace(')','') and (str(filename) == file.split('--')[0] or\
                      str(filename) == file.split('--')[-1] ) and str(filename) in str(file)) or\
                ((str(filename) == file.split('--')[0] or str(filename) == file.split('--')[-1] ) and method is None and search is None) or\
                ((str(filename) == file.split('--')[0] or str(filename) == file.split('--')[-1] )  and method is None and str(search) in file and search):
                    pathToFileDict.setdefault(file,str(Path(pathname).joinpath(file)))
        return pathToFileDict

    def get(self, pathname): 
        # catch the search key words
        search = request.args.get(config['request-args']['search'])
        aggr = request.args.get(config['request-args']['aggr'])
        pathToJson,filenameandMethod,fileAttribute = extractPathInfo(basedir,pathname)
        # if pathToJson is null do nothing
        if pathToJson == PurePath(): return 
        if not (isAcceptJSON() or isAcceptHTMLorDefault()): return ERROR_ACCEPT
        # return back to a normal url
        if (http_normalize_slashes(request.url)!=request.url):
            return redirect(http_normalize_slashes(request.url),code=302)
        # if path is valid then let user for visited
        if (traversePathIfExist(basedir,pathToJson,allowed_directory)):
            compPathtoJson = Path(basedir).joinpath(pathToJson)
            # if the path depth is not long which means that it only gives the path to json
            # When dealing with the path _examples/_____/==================================================#
            if filenameandMethod == [] and fileAttribute == PurePath():
                fileSet = set()
                directorySet = set()
                for file in compPathtoJson.iterdir():
                    if ((Path(file).suffix == '.json' and search is None)\
                        or (Path(file).suffix == '.json' and search and str(search) in str(file.parts[-1]))):
                        if MEL_NER_METHODS in str(file.parts[-1]):
                            fileSet.add(extractMELNERFilename(str(file.parts[-1])))
                        else:
                            fileSet.add(str(file.parts[-1]).split('--')[0])
                    elif ((Path(file).suffix == '' and search is None)\
                        or (Path(file).suffix == '' and search and str(search) in str(file.parts[-1]))):
                        directorySet.add(str(file.parts[-1]))
                # this generate unique filename
                listofFilename = list(fileSet|directorySet)
                if isAcceptJSON(): 
                    response = make_response(Json_dump('Filename',listofFilename))
                    response.headers = config['json-header']
                elif isAcceptHTMLorDefault():
                    for k in allowed_directory.keys():
                        if allowed_directory[k] == str(compPathtoJson):
                            title = k
                        elif allowed_directory[k] in str(compPathtoJson):
                            title = ''
                    response = make_response(render_template('pathpages.html',
                                                    file = listofFilename, 
                                                    len = len(listofFilename),
                                                    pathname = pathname,
                                                    title = title,
                                                    datelist = None,
                                                    sizelist = None,
                    ))
                    response.headers = config['html-header']
                return response
            #==========================================================================================================#
            else:
                filename = filenameandMethod[0]
                method = []
                fileSet = [str(file.parts[-1]) for file in compPathtoJson.iterdir() if file.suffix == '.json']
                # When only given the filename but without method When dealing _examples/____/____.json=================#
                if len(filenameandMethod) == 1:
                    pathToFileDict = self.findJsonFile(compPathtoJson,fileSet, filename, None, search)
                    if pathToFileDict == dict(): return EMPTY_RESULTS
                    # during aggregation=======================================================================#
                    if aggr in request.args:
                        l = dict()
                        for file in list(pathToFileDict.values()):
                            if not MEL_NER_METHODS in file: 
                                l.setdefault(file.replace(Path(file).parts[-1].split('--')[-2],''),[]).append(file)
                        if (aggregate_jsonfile_summary(l) == dict()):
                            return ERROR_AGGR
                        else:
                            return SUCCESS_AGGR
                        return ERROR_AGGR_ALERT
                    #==========================================================================================#
                    for i in list(pathToFileDict.keys()):
                        if MEL_NER_METHODS in i:
                            method.append('{}--{}'.format(extractMELNERFilename(i),MEL_NER_METHODS))
                        else:
                            method.append('{}--{}'.format(i.split('--')[0],i.split('--')[-2].replace('(','').replace(')','')))
                    if isAcceptJSON(): 
                        response = make_response(Json_dump('Filename', method))
                        response.headers = config['json-header']
                    elif isAcceptHTMLorDefault():
                        datelist = [fileinfo.createDate(i) for i in list(pathToFileDict.values())]
                        sizelist = [fileinfo.size(i) for i in list(pathToFileDict.values())]
                        response = make_response(render_template('pathpages.html',
                                                        file = method, 
                                                        len = len(method),
                                                        pathname = pathname,
                                                        title = '',
                                                        datelist = datelist,
                                                        sizelist = sizelist,
                        ))
                        response.headers = config['html-header']
                    return response
                #========================================================================================================#
                #When dealing with the jsonFile ========================================================================#
                pathToFileDict = self.findJsonFile(compPathtoJson,fileSet, filename, filenameandMethod[1], search)
                try:
                    with open (list(pathToFileDict.values())[0]) as f:
                        jsonfile = json.load(f)
                except:
                    return EMPTY_RESULTS
                content = jsonfile if str(filenameandMethod[1]) == 'summary' and fileAttribute == PurePath() else recursive(jsonfile,fileAttribute)
                #When dealing with the args ====================================#
                if request.args:
                    for req in request.args:
                        if req in find_entity.keys():
                            try:
                                # findEntityValueWithKey(obj,entityKey,entityValue,key)
                                response =  make_response(findEntityValueWithKey(content,req,find_entity[req],str(fileAttribute.parts[-1])))
                                response.headers = config['json-header']
                                return response
                            except:
                                return ERROR_ARGS
                        elif req == config['request-args']['search']:
                            return ERROR_SEARCH
                        # to search the substring
                        elif (req[0] == '*' and req[-1] == '*'):
                            response =  make_response(Json_dict("search: " + str(req),searchKeyWord(content, req[1:-1],start=1,end=1,l=[])))
                            response.headers = config['json-header']
                            return response
                        elif req[0] == '*' and req[-1] != '*': 
                            response =  make_response(Json_dict("search: " + str(req),searchKeyWord(content, req[1:],start=1,l=[])))
                            response.headers = config['json-header']
                            return response
                        elif req[0] != '*' and req[-1] == '*': 
                            response =  make_response(Json_dict("search: " + str(req),searchKeyWord(content, req[:-1],end=1,l=[])))
                            response.headers = config['json-header']
                            return response
                        #if the method is summary then can do filtering function or return error=================================#
                        elif req in config['request-args']['filterfunction']:
                            if str(filenameandMethod[1]) == 'summary':
                                response = make_response(getattr(filter_summary,config['request-args']['filterfunction'][req])(jsonfile))
                                response.headers = config['json-header']
                                return response
                            else: 
                                return ERROR_FILTER 
                        #========================================================================================================#
                    return ERROR_ARGS
                #===============================================================#
                if fileAttribute != PurePath():
                    response = make_response(Json_dict(str(fileAttribute.parts[-1]), content))
                else:
                    # if the method is summary demonstrates the whole thing
                    if (str(filenameandMethod[1]) == 'summary'):
                        response = make_response(jsonfile)
                    else:
                        response = make_response(Json_dump('_stats', content))
                response.headers = config['json-header']
                return response
        else:   return EMPTY_RESULTS
        return ERROR_ACCEPT
            

class index(Resource):
    # get the file
    def get(self):
        # if request header is application/json
        file = dict()
        for k,v in allowed_directory.items():
            file.setdefault(str(k),str(v).replace(basedir,''))
        if isAcceptJSON():
            response = make_response(Json_dump('Filename',list(file.values())))
            response.headers = config['json-header']
            return response
        # if request header is text/html or could be ran on google chrome
        elif isAcceptHTMLorDefault():
            # set the headers to text/html
            response = make_response(render_template('pathpages.html',
                                                    file = file, 
                                                    len = 1,
                                                    pathname = '/',
                                                    datelist = None,
                                                    sizelist = None,
            ))
            response.headers = config['html-header']
            return response
        else:
            return ERROR_ACCEPT


api.add_resource(index, '/')
api.add_resource(path,'/<path:pathname>')

if __name__ == '__main__':
    # app.run(debug=True, port=config['tcp-port'])
    app.config['DEBUG'] = bool(config['debug-flag'])
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True 
    app.config['SERVER_NAME'] = f"{config['server-host']}:{config['tcp-port']}"
    app.run()
