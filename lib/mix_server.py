import sys
if ".." not in sys.path:
    sys.path.append("..")

import time
import socket
import random
import threading
import SocketServer

from util import logger
from util import Settings
from util.BaseClasses import ThreadedTCPServer

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def setup(self):
        self.logger = logger.logger_factory('{}H'.format(self.server.name))

    def send_vote(self, ip, port, vote):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        try:
            sock.sendall(vote)
        finally:
            sock.close()

    def handle(self):
        data = self.request.recv(1024)
        if data == 'get-pk': #Client asked for the public key e.g. ( modulus n, public exponent e )
            n = self.server.key.publickey().n
            e = self.server.key.publickey().e
            response = '{},{},{}'.format(self.server.name, str(n), str(e))
            self.request.sendall(response)
        elif 'vote-count' in data:
            self.server.vote_count = int(data.split('-')[2])
            self.logger.debug('Expecting {} votes'.format(self.server.vote_count))
            #Generate a permutation
            self.logger.debug('generating permutation')
            self.server.perm = range(self.server.vote_count)
            random.shuffle(self.server.perm)
        elif self.server.received_votes < self.server.vote_count:
            self.server.actual_votes.append(data)
            self.server.received_votes += 1
            self.logger.debug('{} votes received'.format(self.server.received_votes))
            if self.server.vote_count == self.server.received_votes:
                if not self.server.isLast:
                    self.logger.debug('Votes completed.Decryption & shuffling time...')
                    #Have to remove an RSA layer
                    decrypted_votes = []
                    for v in self.server.actual_votes:
                        decrypted_votes.append(self.server.key.decrypt(v))
                    #Shuffle them
                    decrypted_votes = [decrypted_votes[i] for i in self.server.perm]
                    #Send them back
                    self.logger.debug('Sending back....')
                    HOST, PORT = Settings.host_info('BulletinBoard')
                    for v in decrypted_votes:
                        time.sleep(0.5)
                        self.logger.debug('Sending next...')
                        self.send_vote(HOST, PORT, v)
                    #self.request.sendall(response)
                else:
                    self.logger.debug('Votes completed.Decryption & shuffling time...')
                    #Have to remove an RSA layer
                    decrypted_votes = []
                    cipher = PKCS1_OAEP.new(self.server.key)
                    for v in self.server.actual_votes:
                        decrypted_votes.append(cipher.decrypt(v))
                    #Shuffle them
                    decrypted_votes = [decrypted_votes[i] for i in self.server.perm]
                    #Send them back
                    self.logger.debug('Sending back....')
                    HOST, PORT = Settings.host_info('BulletinBoard')
                    for v in decrypted_votes:
                        time.sleep(0.5)
                        self.logger.debug('Sending next...')
                        self.send_vote(HOST, PORT, v)
                self.server.received_votes = 0
                self.server.actual_votes = []

class MixServer(object):
    def __init__(self, name, isFirst=False, isLast=False):
        log = logger.logger_factory(name)
    
        #Generate a unique key per mix server
        log.debug('Creating key...')
        rng = Random.new().read
        RSAkey = RSA.generate(1024, rng)
        log.debug('Generation completed.')

        HOST, PORT = Settings.host_info(name)

        self.server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        self.server.key = RSAkey
        self.server.name = name
        self.server.vote_count = 0
        self.server.received_votes = 0
        self.server.actual_votes = []
        self.server.isFirst = isFirst
        self.server.isLast = isLast        
        ip, port = self.server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True
        self.server_thread.start()
        log.debug('Server loop running in thread({})'.format(self.server_thread.name))

    def shutdown(self):
        self.server.shutdown()
