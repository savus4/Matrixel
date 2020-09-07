#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import logging
import base64

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.headers = "image/png"
        if self.path != "/apple-touch-icon.png":
            with open("index.html") as main_page:
                self.wfile.write((main_page.read()).encode('utf-8'))
        else: 
            with open("data/whats_ingo_icon.png") as icon:
                self.wfile.write(icon.read())

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        post_data = urllib.parse.unquote_plus(str(post_data))
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data)
        name_of_field = "message"
        
        with open("data/message.txt", mode="w") as message_file:
            message_file.write(post_data[post_data.find(name_of_field)+len(name_of_field)+1:])
        self._set_response()
        with open("index.html") as main_page:
            self.wfile.write((main_page.read()).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()