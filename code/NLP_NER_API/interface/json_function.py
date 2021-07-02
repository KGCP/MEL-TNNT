from pathlib import PurePath, Path
from path_function import head,pathExceptHead

# dump the json results
def Json_dump(name, string_list):
    if len(string_list) == 1:
        js_output = {name : string_list[0]}
    else:
        js_output = {name : string_list}
    return js_output

def Json_dict(name,d):
    return {name:d}

# extract the Jsonfile
def recursive(jsonfile, path):
    if path == PurePath():
        return readJson(jsonfile,'_stats')
    # iterate the path
    content = jsonfile
    while not path == PurePath():
        headpath = head(path)
        content = readJson(content,headpath)
        path = pathExceptHead(path)
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

# if start is not none, then it gives string starts with particular substring
# if end is not none, then it gives string ends with particular substring
def searchKeyWord(sections, keyword, start=None, end=None, l =[]):
    # if part is list
    def checkIfcontainSubword(keyword,targetword,start,end):
        if start and end is None:      
            return str(targetword).startswith(str(keyword))
        elif start is None and end:
            return str(targetword).endswith(str(keyword))
        elif start and end:
            return str(keyword) in str(targetword)
        return False
    # these breaks are used to avoid duplicates
    if isinstance(sections,list):
        for section in sections:
            searchKeyWord(section,keyword,start, end, l)
    elif isinstance(sections,dict):
        for entities in sections.values():
            for entity in entities:
                for attribute in entity.values():
                    if not isinstance(attribute,str):
                        if checkIfcontainSubword(keyword,attribute,start,end):
                            l.append(entity)
                            break
                    else:
                        for word in attribute.split(' '):
                            if checkIfcontainSubword(keyword,word,start,end):
                                l.append(entity)
                                break
                        break
    return l
