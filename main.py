from lib.mix_server import MixServer
from lib.verify_server import VerifyServer
from lib.vote_server import VoteServer

if __name__ == "__main__":
    try:
        m1 = VoteServer()

        while 1:
            continue
    except KeyboardInterrupt:
        m1.stop()