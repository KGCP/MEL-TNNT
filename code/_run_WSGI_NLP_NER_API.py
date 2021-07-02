''''
@script: NLP NER RESTful API WSGI.
@author: Sergio.
@summary: NLP NER RESTful API Web Server Gateway Interface.
# History Update:
#    2021-03-18: creation.
'''


# ==================================================================================================
from gevent.pywsgi import WSGIServer
from NLP_NER_API import app_runner

http_server = WSGIServer(('', 5000), app_runner)
http_server.serve_forever()

# ==================================================================================================
