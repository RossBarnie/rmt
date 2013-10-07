# Script to start an LXC container, assumes dependencies resolved
# assuming linux platform

import os

# hard-coding test container for now

try:
    os.rename('/etc/foo', '/etc/bar')
except IOError as e:
    if (e[0] == errno.EPERM):
        print >> sys.stderr, "You need root permissions to run this script"
        sys.exit(1)

print "permission granted"
