import sys
if ".." not in sys.path:
    sys.path.append("..")

import socket
import threading
import SocketServer

from util import Settings
from util.BaseClasses import ThreadedTCPServer

from Crypto import Random
from Crypto.PublicKey import RSA

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        if data == 'get-pk': #Client asked for the public key e.g. ( modulus n, public exponent e )
            n = self.server.key.publickey().n
            e = self.server.key.publickey().e
            response = '{},{},{}'.format(self.server.name, str(n), str(e))
            self.request.sendall(response)
        elif 'vote-count' in data:
            self.server.vote_count = int(data.split('-')[2])
            print '{} expecting {} votes'.format(self.server.name, self.server.vote_count)
        else:
            response = 'NOPKFORU'

class MixServer(object):
    def __init__(self, name, isFirst=False, isLast=False):
        self.name = name
        self.isFirst = isFirst
        self.isLast = isLast
        
        #Generate a unique key per mix server
        print '{}: Creating key...'.format(self.name)
        rng = Random.new().read
        RSAkey = RSA.generate(1024, rng)
        print '{}: Generation completed.'.format(self.name)

        HOST, PORT = Settings.host_info(self.name)

        self.server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        self.server.key = RSAkey
        self.server.name = self.name
        self.server.vote_count = 0
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
