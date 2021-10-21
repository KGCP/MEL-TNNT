from pathlib import PurePath, Path
from path_function import head,pathExceptHead

"""
If the string_list is a list containing one elements then remove the square brackets.
Otherwise donothing but add the key of dictionary.
"""
def Json_dump(name, string_list):
    if len(string_list) == 1 and isinstance(string_list,list):
        js_output = {name : string_list[0]}
    else:
        js_output = {name : string_list}
    return js_output

def Json_dict(name,d):
    return {name:d}

# extract the Jsonfile
def recursive(jsonfile, path, is_MEL_NER, is_in_keyword):
    if not (is_MEL_NER and is_in_keyword):
        if path == PurePath():
            return readJson(jsonfile,'_stats')
        # iterate the path
        content = jsonfile
        while not path == PurePath():
            headpath = head(path)
            content = readJson(content,headpath)
            path = pathExceptHead(path)
    else:
        if path == PurePath():
            path = '_stats'
        content = dict()
        for doc in jsonfile['NLP-NER']:
            for d_k, d_v in doc.items():
                content[d_k] = dict()
                for m_k,m_v in d_v.items():
                    if isinstance(m_v,dict) and str(path) in m_v.keys():
                        content[d_k][m_k] = m_v[str(path)]
    return content

def readJson(obj, key):
    value_arr = []
    key_arr = []
    def extract(obj,arr,key):
        if (isinstance(obj,dict)):
            for k,v in obj.items():
                if str(k) == str(key):
                    key_arr.append(v)
                if str(v) == str(key):
                    value_arr.append(obj)
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
        elif isinstance(obj, list):
            for item in obj:
                extract(item,arr,key)
        return key_arr,value_arr
    key_arr,value_arr = extract(obj, key_arr, key)
    # avoid of two square bracket
    if value_arr == []:
        if len(key_arr) == 1:
            key_arr = key_arr[0]
        return key_arr
    else:
        if len(value_arr) == 1:
            value_arr = value_arr[0]
        return value_arr

# the obj may contain list type or dict type
# the entity represents the wanted entity
def findEntityValue(obj,entityKey,entityValue):
    entityValue = entityValue.split('|')
    if len(entityValue) == 1:
        if isinstance(obj,list):
            result = [ele[entityValue[0]] for ele in obj]
        elif isinstance(obj,dict):
            result = obj[entityValue[0]]
    else:
        if isinstance(obj,list):
            result = []
            for ele in obj:
                dictInResult = dict()
                for index in range(len(entityValue)):
                    dictInResult.setdefault(entityValue[index],ele[entityValue[index]])
                result.append(dictInResult)
        elif isinstance(obj,dict):
            result = dict()
            for index in range(len(entityValue)):
                result.setdefault(entityValue[index],obj[entityValue[index]])
    return Json_dict(entityKey,result)

#the findEntityValueWithKey will return key as key and calling the findEntityValue function as the value
#it generates the value of entity.
def findEntityValueWithKey(obj,entityKey,entityValue,key):
    return Json_dict(key,findEntityValue(obj,entityKey,entityValue))

"""
We need the capability to search for the NER entity results, including substrings (startsWith, endsWith , substring) and exactMatch, in the following way:
/DoF/.../spacy_md_model/_output/PERSON/Car*: all entities that start with Car
/DoF/.../spacy_md_model/_output/PERSON/Carter: exact match for entity Carter
/DoF/.../spacy_md_model/_output/PERSON/*ter: all entities that finish with ter
/DoF/.../spacy_md_model/_output/PERSON/*arte*: all entities that have the substring arte
"""
def searchKeyWord(sections, keyword, start=None, end=None, l = {}):
    # split every word in the list with the space
    def checkIfcontainSubword(keyword,targetword,start,end):
        if (start and end is None) and str(targetword).startswith(str(keyword)): 
            return True
        elif (start is None and end) and str(targetword).endswith(str(keyword)):
            return True
        elif (start and end) and str(keyword) in str(targetword):
            return True
        return False
    
    # these breaks are used to avoid duplicates
    if isinstance(sections,list):
        for section in sections:
            searchKeyWord(section,keyword,start, end, l)
    elif isinstance(sections,dict):
        for key,entities in sections.items():
            if isinstance(entities,list): 
                for ent in entities:
                    if 'entity' in ent:
                        if checkIfcontainSubword(keyword,ent['entity'],start,end):
                            l.setdefault(key,[]).append(ent)
                        break
                
    return l



