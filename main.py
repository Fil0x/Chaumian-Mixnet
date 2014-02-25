from lib.mix_server import MixServer
from lib.verify_server import VerifyServer
from lib.vote_server import VoteServer

if __name__ == "__main__":
    active_servers = []
    try:
        m1 = VoteServer()

        active_servers.append(m1)
        while 1:
            continue
    except KeyboardInterrupt:
        for s in active_servers:
            s.shutdown()