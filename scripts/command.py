import subprocess


class Command:
    """ Class to represent an OS-level command """

    def __init__(self, comm):
        self.comm = comm

    def execute(self, return_output):
        if return_output:
            return subprocess.check_output(self.comm)
        return subprocess.call(self.comm)


print Command(["ls", "-l"]).execute(True)
