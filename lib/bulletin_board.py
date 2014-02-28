import sys
if ".." not in sys.path:
    sys.path.append("..")

import socket
import threading
import SocketServer

from util import logger
from util import Settings
from util.BaseClasses import ThreadedTCPServer


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def  setup(self):
        self.logger = logger.logger_factory('BBH')

    def send_vote(self, ip, port, vote):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        try:
            sock.sendall(vote)
        finally:
            sock.close()

    def handle(self):
        data = self.request.recv(1024)
        if 'vote-count' in data:
            self.server.vote_count = int(data.split('-')[2])
            self.logger.debug('{} expecting {} votes'.format(self.server.name, self.server.vote_count))
        elif self.server.received_votes < self.server.vote_count:
            self.server.actual_votes.append(data)
            self.server.received_votes += 1
            self.logger.debug('{}: {} votes received'.format(self.server.name, self.server.received_votes))
            if self.server.vote_count == self.server.received_votes:
                self.logger.debug('{}: Votes completed'.format(self.server.name))
                if self.server.current_mix <= self.server.mix_count:
                    #Send the received votes to the next mixserver
                    self.logger.debug('Notifying the next mixserver: Mix{}'.format(self.server.current_mix))
                    HOST, PORT = Settings.host_info('Mix{}'.format(self.server.current_mix))
                    for v in self.server.actual_votes:
                        self.send_vote(HOST, PORT, v)
                    #Get ready for the results of the mixnet
                    self.server.current_mix += 1
                    self.server.actual_votes = []
                    self.server.received_votes = 0
                else:
                    #Voting is completed
                    self.logger.debug(self.server.received_votes)
                    self.server.current_mix = 1
                    self.server.actual_votes = []
                    self.server.received_votes = 0


class BulletinBoard(object):
    def __init__(self, name='BulletinBoard'):
        self.logger = logger.logger_factory('BB')
        self.name = name
        
        HOST, PORT = Settings.host_info(self.name)

        self.server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        self.server.name = self.name
        self.server.vote_count = 0
        self.server.actual_votes = []
        self.server.received_votes = 0
        self.server.mix_count = Settings.mix_count()
        self.server.current_mix = 1
        ip, port = self.server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True
        self.server_thread.start()
        self.logger.debug("Server loop running in thread({}) & name({})".format(self.server_thread.name, self.name))

    def shutdown(self):
        self.server.shutdown()