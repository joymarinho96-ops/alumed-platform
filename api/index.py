import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from alumed.wsgi import app
except Exception as e:
    # If the app fails to load, create a dummy WSGI app that returns the traceback
    error_msg = traceback.format_exc()
    def app(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [error_msg.encode('utf-8')]
