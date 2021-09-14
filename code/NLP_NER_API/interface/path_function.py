import pathlib
from pathlib import PurePath,Path
###############################################################################################
def pathExceptHead(path):
    return Path(*Path(path).parts[1:])
    
def head(path):
    return Path(Path(path).parts[0])

def pathExceptTail(path):
    return Path(*Path(path).parts[:-1])

def tail(path):
    return Path(Path(path).parts[-1])

def get(path,index):
    return Path(Path(path).parts[index])

def depth(pathname): 
    separatepath = Path(pathname).parts[0:]
    return len(separatepath)

################################################################################################
# traverse the path to get the path to file, filename and the information it need about the file 
# filename and the information can be empty.---------------------------------------------------#
def extractPathInfo(base,path,allowed_attribute):
    pathToJson = PurePath()
    filenameandMethods = []
    fileAttribute = PurePath()
    while not path == PurePath():
        headpath = head(path)
        # if the path have suffix then seperate the pathname, the method and its jsonfile
        if (headpath.suffix == ''):
            pathToJson = Path(pathToJson).joinpath(headpath)
        else:
            if depth(path) == 1:
                filenameandMethods = [get(path,0)]
            else:
                filenameandMethods = [get(path,0),str(get(path,1))]
                fileAttribute = Path(*Path(path).parts[2:])
                if depth(path) > 2 and has_attribute(allowed_attribute,str(get(path,2))):
                    filenameandMethods = [get(path,0),str(get(path,1)),str(get(path,2))]
                    fileAttribute = Path(*Path(path).parts[3:])
            break
        path = pathExceptHead(path)
    return pathToJson,filenameandMethods,fileAttribute

def traversePathIfExist(base,path,allowedpath):
    # check if the path exists
    while not path == PurePath():
        headpath = head(path)
        base = Path(base).joinpath(headpath)
        try:
            if list(base.iterdir()):
                path = pathExceptHead(path)
            else:
                return False
        except:
            return False
    # it checks whether the file is allowed to browse.
    return checkIfAllowed(base,allowedpath)

def checkIfAllowed(base,allowedpath):
    #check if the directory is allowed
    for value in allowedpath.values():
        if value in str(base):
            return True
    return False

def has_attribute(allowed_attribute,a):
    for attr in allowed_attribute:
        if (attr in a):
            return True
    return False

    