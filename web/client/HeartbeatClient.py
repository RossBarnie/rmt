"""Heartbeat client, sends out an UDP packet periodically"""

# Taken from http://code.activestate.com/recipes/52302-pyheartbeat-detecting-inactive-computers/
# Under PSF license

import socket
import time
from ConfigParser import SafeConfigParser


class config:

    def __init__(self):
        self.server_ip = "0.0.0.0"
        self.server_port = 8080
        self.beat_period = 5
        self.refresh_config()

    def refresh_config(self):
        parser = SafeConfigParser()
        parser.read("hbclient.cfg")
        self.server_ip = parser.get("server", "ip")
        self.server_port = parser.getint("server", "port")
        self.beat_period = parser.getint("client", "beat_period")


def main():
    cfg = config()
    print ('Sending heartbeat to IP %s , port %d\n'
           'press Ctrl-C to stop\n') % (cfg.server_ip, cfg.server_port)
    while True:
        cfg.refresh_config()
        hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hbSocket.sendto('PyHB', (cfg.server_ip, cfg.server_port))
        if __debug__: print 'Time: %s' % time.ctime()
        time.sleep(cfg.beat_period)


if __name__ == "__main__":
    main()
