import psutil


class Usage:

    def __init__(self, pid, name):
        self.pid = pid
        self.name = name

    def cpu(self):
        try:
            p = psutil.Process(self.pid)
        except psutil.NoSuchProcess:
            return -1
        return p.get_cpu_percent(interval=1)

    def memory(self):
        try:
            p = psutil.Process(self.pid)
        except psutil.NoSuchProcess:
            return -1
        return p.get_memory_percent()
