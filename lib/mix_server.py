import sys
if ".." not in sys.path:
    sys.path.append("..")

import socket
import threading
import SocketServer

from util import ConfigReader
from util.BaseClasses import ThreadedTCPServer

from simpleflake import simpleflake

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        response = str(simpleflake())
        self.request.sendall(response)
        print 'Voted {}'.format(data)

class MixServer(object):
    def __init__(self, name, isFirst=False, isLast=False):
        self.name = name
        self.isFirst = isFirst
        self.isLast = isLast

        HOST, PORT = ConfigReader.host_info(self.name)

        self.server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        ip, port = self.server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True
        self.server_thread.start()
        print "Server loop running in thread:", self.server_thread.name
        
    def shutdown(self):
        self.server.shutdown()