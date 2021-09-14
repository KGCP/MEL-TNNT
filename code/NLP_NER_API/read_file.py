import os
import json

config = "config.json"
path = os.path.join(os.path.abspath(os.path.dirname(__file__)), config)

with open(path) as cf:
    config = json.load(cf)
