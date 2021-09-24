import os
import json

config_test   = "config.json"
config_dev    = "config (@dev).json"
config_server = "config (@server).json"

def tryWithConfiFile(f):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), f) if os.path.isfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), f)) else None

path = tryWithConfiFile(config_test)                               # default file: initial try
path = tryWithConfiFile(config_dev)    if (path is None) else path # for development: overrides test file
path = tryWithConfiFile(config_server) if (path is None) else path # for server deployment: overrides dev file

if (path is None):
    print(f"No configuration file was found!")

try:
    print(f"Loading configuration file in [{path}]")
    with open(path) as cf:
        config = json.load(cf)
    # print(f"Configuration file:\n{config}")
except:
    print(f"The system was not able to open the configuration file.  Check its path: [{path}]")
