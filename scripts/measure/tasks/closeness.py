import os
import re
from typing import Iterable

from os.path import dirname, abspath
from task import Task, find_exp_groups

SCRIPT_DIR=dirname(dirname(abspath(__file__)))

class ClosenessTask(Task):
    def __init__(self) -> None:
        super().__init__(os.path.join(SCRIPT_DIR, "measure_closeness.sh"))

    @staticmethod
    def process_setup_info(line:str):
        filename = os.path.basename(line)
        parts = filename.split(".")
        info = []
        for part in parts:
            if part.isnumeric():
                info.append(part)
        assert(len(info) == 2)
        return {
            "machine_num": int(info[0].strip()),
            "num_samples": int(info[1].strip()),
            "filename": filename
        }

    @staticmethod
    def process_performance_info(performance_data:Iterable):
        ret = {
            "time (s)": 0.0,
            "vps": 0.0
        }
        for row in performance_data:
            time = re.search("cnc done const: (\d+\.\d+)s", row)
            vps = re.search("performance: (\d+\.\d+) vps", row)
            if time is not None:
                ret["time (s)"] = float(time.group(1).strip())
            if vps is not None:
                ret["vps"] = float(vps.group(1).strip())
        return ret

    @staticmethod
    def process_log_group(grouped_data:Iterable):
        if grouped_data is None or len(grouped_data) == 0:
            print("[Warning] no grouped_data provided")
        setup_info = ClosenessTask.process_setup_info(grouped_data[0])
        performance_info = ClosenessTask.process_performance_info(grouped_data[1:])
        return {
            "setup": setup_info,
            "performance": performance_info
        }

    @staticmethod
    def extract_perf(stdout:str):
        out = []
        all_data = stdout.split("\n")
        exp_groups = find_exp_groups(all_data)
        for group in exp_groups:
            start, end = group
            out.append(ClosenessTask.process_log_group(all_data[start:end]))
        return out