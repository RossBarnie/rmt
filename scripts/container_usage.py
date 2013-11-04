__author__ = 'ross'

LXC_SYS_DIR = "/sys/fs/cgroup/lxc"
LXC_MEM_USAGE_FILE = "memory.usage_in_bytes"
LXC_CPU_USAGE_FILE = "cpuacct.usage"


def memory(container_name):
    global LXC_SYS_DIR, LXC_MEM_USAGE_FILE
    file_dir = "%s/%s/%s" % (LXC_SYS_DIR, container_name, LXC_MEM_USAGE_FILE)
    with open(file_dir, 'r') as f:
        out = int(f.readline())
    return out


# Need to do more calculation in the cpu function because the file uses clock ticks
#
#def cpu(container_name):
#    global LXC_SYS_DIR, LXC_CPU_USAGE_FILE
#    with open(LXC_SYS_DIR.join([container_name, "/", LXC_CPU_USAGE_FILE]), 'r') as f:
#        out = int(f.readline())
#    return out



