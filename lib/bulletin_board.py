import sys
if ".." not in sys.path:
    sys.path.append("..")

import socket
import threading
import SocketServer

from util import Settings
from util.BaseClasses import ThreadedTCPServer

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        if 'vote-count' in data:
            self.server.vote_count = int(data.split('-')[2])
            print '{} expecting {} votes'.format(self.server.name, self.server.vote_count)
            #self.request.sendall(response)
        elif self.server.received_votes < self.server.vote_count:
            self.server.actual_votes.append(data)
            self.server.received_votes += 1
            print '{}: {} votes received'.format(self.server.name, self.server.received_votes)
            if self.server.vote_count == self.server.received_votes:
                print '{} received {} votes'.format(self.server.name, self.server.received_votes)
                print 'Notifying the next mixserver'

class BulletinBoard(object):
    def __init__(self, name='BulletinBoard'):
        self.name = name

        HOST, PORT = Settings.host_info(self.name)

        self.server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        self.server.name = self.name
        self.server.vote_count = 0
        self.server.actual_votes = []
        self.server.received_votes = 0
        ip, port = self.server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True
        self.server_thread.start()
        print "Server loop running in thread({}) & name({})".format(self.server_thread.name, self.name)
        
    def shutdown(self):
        self.server.shutdown()