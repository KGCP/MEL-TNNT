from gevent.pywsgi import WSGIServer
from app_runner import app, config

if __name__ == '__main__':
    http_server = WSGIServer((config['server-host'], config['tcp-port']), app)
    http_server.serve_forever(stop_timeout=5000)
