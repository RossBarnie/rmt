# Script to start an LXC container, assumes dependencies resolved
# assuming linux platform

import os
#import sys
import stat

# hard-coding test container for now

# need root access to start containers
st = os.stat("./start_container.py")  # possibly heavy?
if not bool(st.st_mode & stat.S_IXUSR):
    print "permission denied, run as root"
    exit(1)




