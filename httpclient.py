#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    # updated
    def get_code(self, data):
        # return code from request eg. GET 200 ...
        return int(data.split()[1])

    # updated
    def get_url(self,data):
        # get object of parsed header
        # https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse
        obj = urllib.parse.urlparse(data)

        # ensure non-empty port
        port = obj.port
        if not port:
            if obj.scheme == "http":
                port = 80

            elif obj.scheme == "https":
                port = 443

        # ensure non-empty path
        path = obj.path
        if not obj.path:
            path = "/"

        # handle case of query
        if obj.query:
            path += ("?"+obj.query)

        return obj, port, path

    # updated
    def get_body(self, data):
        # print GET
        print(data)

        # split by getting the request end sequence and return
        body = data.split("\r\n\r\n")
        return body[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
    # added function
    def sendRequest(self, obj, port, request):
        # connect and send request
        self.connect(obj.hostname, port)
        self.sendall(request)

        # receive, print and parse response
        response = self.recvall(self.socket)
        print(response)
        if not response:
            return HTTPResponse(404, "")
            
        code = self.get_code(response)
        body = self.get_body(response)

        # close connection and return response
        self.socket.close()
        return HTTPResponse(code, body)

    # updated
    def GET(self, url, args=None):
        # get required info
        obj, port, path = self.get_url(url)

        # define GET request
        request = f"GET {path} HTTP/1.1\r\nHost: {obj.hostname}\r\nAccept: */*\r\nConnection: Closed\r\n\r\n"

        # send request
        return self.sendRequest(obj, port, request)

    # updated
    def POST(self, url, args=None):
        # get required info
        obj, port, path = self.get_url(url)

        # define POST request
        # if empty argument parameters, otherwise determine requestBody + length
        requestBody = ""
        contentLength = "0"
        if args:
            requestBody = urllib.parse.urlencode(args, doseq=True)
            contentLength = str(len(requestBody))

        request = f"POST {path} HTTP/1.1\r\nHost: {obj.hostname}\r\nAccept: */*\r\n \
                        Connection: Closed\r\nContent-Length: {contentLength}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n{requestBody}"
    
        # send request
        return self.sendRequest(obj, port, request)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
