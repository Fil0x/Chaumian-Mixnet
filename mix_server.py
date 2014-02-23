import socket
import threading
import SocketServer
from util import ConfigReader

from simpleflake import simpleflake

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        response = str(simpleflake())
        self.request.sendall(response)
        print 'Voted {}'.format(data)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":  
    try:
        HOST, PORT = ConfigReader.host_info('mix')

        server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print "Server loop running in thread:", server_thread.name
        while 1:
            continue
    except KeyboardInterrupt:
        server.shutdown()