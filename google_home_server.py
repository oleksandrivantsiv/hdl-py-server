#!/usr/bin/python

import ssl
from base64 import b64encode
import argparse
import BaseHTTPServer
from threading import Thread

from hdlclient import HDLClient


# server config
SERVER_IP = '0.0.0.0'
SERVER_PORT = 9999
USER=b"supersecureuser:supersecurepassword"
SSL_CERTFILE = 'cert/server.pem'


def authenticate(func):
    def wrapper(inst, *args, **kwargs):
        auth = 'Basic %s' % b64encode(USER).decode("ascii")
        if auth != inst.headers.get('authorization'):
            inst._make_response('"Unauthorized"', 401)
            return

        return func(inst, *args, **kwargs)
    return wrapper


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    hdl_client = HDLClient()

    def _make_response(self, response_body, code):
         self.protocol_version = self.request_version
         self.send_response(code)

         self.send_header('Content-Length', len(str(response_body)))
         self.send_header('Content-Type', 'application/json')
         self.send_header('Connection', 'close')
         self.end_headers()

         self.wfile.write(response_body)

    @authenticate
    def do_POST(self):
        try:
            # Execute IFTTT action
            self.hdl_client.process_ifttt(self.path)
            response = '{"status": "ok"}'
            self._make_response(response, 202)
        except Exception as e:
            print("Failed to process IFTTT request: %s" % e)
            response = '{"status": "failure"}'
            self._make_response(response, 400)


class HdlServer(object):

    def __init__(self, server_ip=SERVER_IP, port=SERVER_PORT):
        self.server_ip = server_ip
        self.port = port
        self.httpd = None
        self.handler = RequestHandler

    def start(self):
        server_address = (self.server_ip, self.port)
        self.httpd = BaseHTTPServer.HTTPServer(server_address, self.handler)
        self.httpd.socket = ssl.wrap_socket(self.httpd.socket, certfile=SSL_CERTFILE, server_side=True)
        self.server_thread = Thread(target=self.httpd.serve_forever)
        self.server_thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.server_thread.join()


def parse_cmd_arguments():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-i", "--server_ip", type=str, default=SERVER_IP, help="IP on which HdlServer server will listen")
    arg_parser.add_argument("-p", "--port", type=int, default=SERVER_PORT, help="Port on which HdlServer server will listen")
    arguments = arg_parser.parse_args()

    return arguments


if __name__ == '__main__':
     args = parse_cmd_arguments()

     es = HdlServer(args.server_ip, args.port)
     es.start()

     try:
         raw_input()
     finally:
         es.stop()