import subprocess
import re

class Task(object):
    def __init__(self, script_path) -> None:
        super().__init__()
        self._script_path = script_path

    def run(self):
        p = subprocess.Popen(self._script_path, stdout=subprocess.PIPE)
        output = p.stdout.read()
        return output.decode('utf-8')

    @staticmethod
    def extract_perf(stdout):
        pass

def find_exp_groups(logs:list):
    ret = []
    start = -1
    for idx, log in enumerate(logs):
        found = re.search("(.*)\.log", log)
        if found is not None:
            # init
            if start == -1:
                start = idx
            # new range
            if idx > start:
                ret.append((start, idx))
                start = idx
    ret.append((start, -1))
    assert(len(ret) == 4)
    return ret