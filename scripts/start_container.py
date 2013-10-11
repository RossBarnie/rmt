# Script to start an LXC container, assumes dependencies resolved
# assuming linux platform

import os
#import sys
import stat
import subprocess

# hard-coding test container for now

# need root access to start containers

subprocess.call(["lxc-start", "-n", "test"])
print subprocess.call(["lxc-info", "-n", "test"])


