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
import os
from pathlib import Path
from dagl_msg import Dagl_Message

def MakeHandlerClassFromArgs(message, display_sleeping):
    
    class S(BaseHTTPRequestHandler):

        def __init__(self, *args, **kwargs):
            if display_sleeping == None:
                self.dagl_msg = message
                self.display_sleeping = display_sleeping
            super(S, self).__init__(*args, **kwargs)

        # def __init__(self, message: Dagl_Message, display_sleeping):
        #     pass
        #     self.dagl_msg = message
        #     self.display_sleeping = display_sleeping
        #     super().__init__()

        def _set_response(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
            self._set_response()
            sleeping_file = Path("sleeping.txt")
            if self.path == "/togglesleep":
                #if self.display_sleeping:
                #    self.sleeping_file = False
                if os.path.isfile(sleeping_file):
                    os.remove(sleeping_file)
                    print("waking up")
                    self.wfile.write("awaking".encode("utf-8"))
                else:
                    self.display_sleeping = True
                    with open(sleeping_file, "w"):
                        pass
                    print("going to sleep")
                    self.wfile.write("sleeping".encode("utf-8"))
                #with open("index.html") as main_page:
                #    self.wfile.write((main_page.read()).encode('utf-8'))
            elif self.path == "/apple-touch-icon.png":
                self.headers = "image/png"
                with open("data/whats_ingo_icon.png") as icon:
                    self.wfile.write(icon.read())
            else: 
                with open("index.html") as main_page:
                    self.wfile.write((main_page.read()).encode('utf-8'))

        def do_POST(self):
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            post_data = urllib.parse.unquote_plus(str(post_data))
            logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                    str(self.path), str(self.headers), post_data)
            name_of_field = "message"
            with open("data/message.txt", mode="w") as message_file:
                message_file.write(post_data[post_data.find(name_of_field)+len(name_of_field)+1:])
            self.dagl_msg.message = post_data[post_data.find(name_of_field)+len(name_of_field)+1:]
            self._set_response()
            with open("index.html") as main_page:
                self.wfile.write((main_page.read()).encode('utf-8'))
    
    return S

def run(message=None, display_sleeping=False, server_class=HTTPServer,  port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    #httpd = server_class(server_address, handler_class, message)
    handler_class = MakeHandlerClassFromArgs(message, None)
    httpd = server_class(server_address, handler_class)
    #handler_class = S(message, display_sleeping)
    #httpd = server_class(server_address, handler_class)
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