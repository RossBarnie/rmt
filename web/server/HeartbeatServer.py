"""Threaded heartbeat server"""

# Based on http://code.activestate.com/recipes/52302-pyheartbeat-detecting-inactive-computers/
# Which is under PSF license

UDP_PORT = 43278
CHECK_PERIOD = 20
CHECK_TIMEOUT = 15
SERVER_IP = "0.0.0.0"

import socket, threading, time, dblayer, datetime
from ConfigParser import SafeConfigParser


def get_config():
    global UDP_PORT
    global CHECK_PERIOD
    global CHECK_TIMEOUT
    global SERVER_IP
    parser = SafeConfigParser()
    parser.read("server.cfg")
    UDP_PORT = parser.getint("heartbeat", "udp_port")
    CHECK_PERIOD = parser.getint("heartbeat", "check_period")
    CHECK_TIMEOUT = parser.getint("heartbeat", "check_timeout")
    SERVER_IP = parser.get("heartbeat", "server_ip")


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
        limit = time.time() - CHECK_TIMEOUT
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
        self.recSocket.settimeout(CHECK_TIMEOUT)
        self.recSocket.bind((SERVER_IP, UDP_PORT))


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
    print ('Threaded heartbeat server listening on port %d\n'
        'press Ctrl-C to stop\n') % UDP_PORT
    try:
        while True:
            silent = heartbeats.getSilent()
            print 'Silent clients: %s' % silent
            time.sleep(CHECK_PERIOD)
    except KeyboardInterrupt:
        print 'Exiting, please wait...'
        receiverEvent.clear()
        receiver.join()
        print 'Finished.'

if __name__ == '__main__':
    get_config()
    main()
