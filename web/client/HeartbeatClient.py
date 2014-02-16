"""Heartbeat client, sends out an UDP packet periodically"""

# Taken from http://code.activestate.com/recipes/52302-pyheartbeat-detecting-inactive-computers/
# Under PSF license

import socket
import time
from ConfigParser import SafeConfigParser

SERVER_IP = "localhost"  # these are placeholders, actually retrieves these values from config
SERVER_PORT = 8080
BEAT_PERIOD = 5


def get_config():
    global SERVER_IP
    global SERVER_PORT
    global BEAT_PERIOD
    parser = SafeConfigParser()
    parser.read("hbclient.cfg")
    SERVER_IP = parser.get("server", "ip")
    SERVER_PORT = parser.getint("server", "port")
    BEAT_PERIOD = parser.getint("client", "beat_period")


def main():
    get_config()
    print ('Sending heartbeat to IP %s , port %d\n'
           'press Ctrl-C to stop\n') % (SERVER_IP, SERVER_PORT)
    while True:
        hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hbSocket.sendto('PyHB', (SERVER_IP, SERVER_PORT))
        if __debug__: print 'Time: %s' % time.ctime()
        time.sleep(BEAT_PERIOD)


if __name__ == "__main__":
    main()
