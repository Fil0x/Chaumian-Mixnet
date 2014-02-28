from lib.mix_server import MixServer
from lib.bulletin_board import BulletinBoard

if __name__ == "__main__":
    active_servers = []
    try:
        b = BulletinBoard()
        m1 = MixServer('Mix1', isFirst=True)
        m2 = MixServer('Mix2')
        m3 = MixServer('Mix3', isLast=True)
        
        active_servers.append(b)
        active_servers.append(m1)
        active_servers.append(m2)
        active_servers.append(m3)
        while 1:
            continue
    except KeyboardInterrupt:
        for s in active_servers:
            s.shutdown()