import lxc_base
import time

LXC_SYS_DIR = "/sys/fs/cgroup/lxc"
LXC_MEM_USAGE_FILE = "memory.usage_in_bytes"
LXC_CPU_USAGE_FILE = "cpuacct.usage"
PREVIOUS_CPU_USAGES = {}
CPU_USAGES = {}


def memory(container_name):
    global LXC_SYS_DIR, LXC_MEM_USAGE_FILE
    file_dir = "%s/%s/%s" % (LXC_SYS_DIR, container_name, LXC_MEM_USAGE_FILE)
    with open(file_dir, 'r') as f:
        out = int(f.readline())
    return out


def __cpuacct_usage(container_name):
    global LXC_SYS_DIR, LXC_CPU_USAGE_FILE
    file_dir = "%s/%s/%s" % (LXC_SYS_DIR, container_name, LXC_CPU_USAGE_FILE)
    with open(file_dir, 'r') as f:
        out = long(f.readline())
    return out


def __monitor(delay=1):
    global CPU_USAGES, PREVIOUS_CPU_USAGES

    PREVIOUS_CPU_USAGES = CPU_USAGES

    containers = lxc_base.list_containers()
    time.sleep(delay)
    for container in containers:
        CPU_USAGES[container] = __cpuacct_usage(container)
    print CPU_USAGES


def get_usage(container_name):
    global CPU_USAGES, PREVIOUS_CPU_USAGES
    print CPU_USAGES[container_name] - PREVIOUS_CPU_USAGES[container_name]
    return (CPU_USAGES[container_name] - PREVIOUS_CPU_USAGES[container_name]) / float(10**9) / 100
    # int64((float64((cpuUsages[id] - previousCpuUsages[id])) / float64(1e9) / float64(runtime.NumCPU())) * 100)


