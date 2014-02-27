"""Threaded heartbeat server"""

# Based on http://code.activestate.com/recipes/52302-pyheartbeat-detecting-inactive-computers/
# Which is under PSF license

import socket
import threading
import time
import dblayer
import datetime
from ConfigParser import SafeConfigParser


class config:

    udp_port = 43278  # default 43278
    check_period = 20
    check_timeout = 15
    server_ip = "0.0.0.0"  # must be an IP address

    def refresh_config(self):
        parser = SafeConfigParser()
        parser.read("server.cfg")
        self.udp_port = parser.getint("heartbeat", "udp_port")
        self.check_period = parser.getint("heartbeat", "check_period")
        self.check_timeout = parser.getint("heartbeat", "check_timeout")
        self.server_ip = parser.get("heartbeat", "server_ip")


class Heartbeats(dict):
    """Manage shared heartbeats dictionary with thread locking"""

    def __init__(self):
        super(Heartbeats, self).__init__()
        self._lock = threading.Lock()

    def __setitem__(self, key, value):
        """Create or update the dictionary entry for a client"""
        self._lock.acquire()
        super(Heartbeats, self).__setitem__(key, value)
        self._lock.release()

    def getSilent(self):
        """Return a list of clients with heartbeat older than CHECK_TIMEOUT"""
        cfg = config()
        cfg.refresh_config()
        limit = time.time() - cfg.check_timeout
        self._lock.acquire()
        silent = [ip for (ip, ipTime) in self.items() if ipTime < limit]
        self._lock.release()
        return silent


class Receiver(threading.Thread):
    """Receive UDP packets and log them in the heartbeats dictionary"""

    def __init__(self, goOnEvent, heartbeats):
        super(Receiver, self).__init__()
        self.goOnEvent = goOnEvent
        self.heartbeats = heartbeats
        self.recSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cfg = config()
        cfg.refresh_config()
        self.recSocket.settimeout(cfg.check_timeout)
        self.recSocket.bind((cfg.server_ip, cfg.udp_port))


    def run(self):
        while self.goOnEvent.isSet():
            try:
                data, addr = self.recSocket.recvfrom(5)
                if data == 'PyHB':
                    now = datetime.datetime.utcnow()
                    self.heartbeats[addr[0]] = now.isoformat(" ")
                    dblayer.update_heartbeat(addr[0], now)
            except socket.timeout:
                pass


def main():
    receiverEvent = threading.Event()
    receiverEvent.set()
    heartbeats = Heartbeats()
    receiver = Receiver(goOnEvent = receiverEvent, heartbeats = heartbeats)
    receiver.start()
    cfg = config()
    cfg.refresh_config()
    print ('Threaded heartbeat server listening on port {}\n'
           'press Ctrl-C to stop\n').format(cfg.udp_port)
    try:
        while True:
            cfg.refresh_config()
            time.sleep(cfg.check_period)
    except KeyboardInterrupt:
        print 'Exiting, please wait...'
        receiverEvent.clear()
        receiver.join()
        print 'Finished.'

if __name__ == '__main__':
    main()
