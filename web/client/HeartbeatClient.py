"""Heartbeat client, sends out an UDP packet periodically"""

# Taken from http://code.activestate.com/recipes/52302-pyheartbeat-detecting-inactive-computers/
# Under PSF license

import socket
import time
from ConfigParser import SafeConfigParser


class config:

    server_ip = "0.0.0.0"
    server_port = 8080
    beat_period = 5

    def refresh_config(self):
        parser = SafeConfigParser()
        parser.read("hbclient.cfg")
        self.server_ip = parser.get("server", "ip")
        self.server_port = parser.getint("server", "port")
        self.beat_period = parser.getint("client", "beat_period")


def main():
    config.refresh_config()
    print ('Sending heartbeat to IP %s , port %d\n'
           'press Ctrl-C to stop\n') % (config.server_ip, config.server_port)
    while True:
        config.refresh_config()
        hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hbSocket.sendto('PyHB', (config.server_ip, config.server_port))
        if __debug__: print 'Time: %s' % time.ctime()
        time.sleep(config.beat_period)


if __name__ == "__main__":
    main()
