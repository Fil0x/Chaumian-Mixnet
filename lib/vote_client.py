import sys
if ".." not in sys.path:
    sys.path.append("..")
import socket

from util import ConfigReader

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = ConfigReader.host_info('Vote')

    client(HOST, PORT, "Vote 1")
    client(HOST, PORT, "Vote 2")
    client(HOST, PORT, "Vote 1")
    
    print 'Client done sending!'