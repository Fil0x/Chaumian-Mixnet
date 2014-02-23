import socket

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
    HOST = "127.0.0.1"
    VERIFY_PORT = 20000
    VOTE_PORT = 20001
    MIX_PORT = 20002

    client(HOST, MIX_PORT, "Vote 1")
    client(HOST, MIX_PORT, "Vote 2")
    client(HOST, MIX_PORT, "Vote 1")
    
    print 'Client done sending!'