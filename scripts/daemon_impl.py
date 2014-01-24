import sys
import time

from daemon import Daemon
import lxc_base
# obtained from same place as daemon.py, sample implementation of run method override


class MyDaemon(Daemon):
    def run(self):
        while True:
            time.sleep(1)


def print_usage():
    print "usage: %s start[ container]|stop[ container]|restart|info[ containername]" % sys.argv[0]


if __name__ == "__main__":
    daemon = MyDaemon('/tmp/rvt_daemon.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'info' == sys.argv[1]:
            info = lxc_base.pi_info()
            print "Pi Status"
            print "CPU:", info["cpu_usage"], "\nRAM:", info["ram_used"], "/", info["ram_total"]
        elif 'list' == sys.argv[1]:
            for container in lxc_base.list_containers():
                print container
        else:
            print "Unknown command"
            print_usage()
            sys.exit(2)
        sys.exit(0)
    if len(sys.argv) == 3:
        if 'start' == sys.argv[1]:
            name = sys.argv[2]
            status = lxc_base.start_container(name)
            if status[0]:
                print name, "started"
            else:
                print "error occurred, code", status[1]
        elif 'stop' == sys.argv[1]:
            name = sys.argv[2]
            status = lxc_base.stop_container(name)
            if status[0]:
                print name, "stopped"
            else:
                print "error occurred, code", status[1]
    else:
        print_usage()
        sys.exit(2)


