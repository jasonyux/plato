import os
import re
from typing import Iterable

from os.path import dirname, abspath
from task import Task, find_exp_groups

SCRIPT_DIR=dirname(dirname(abspath(__file__)))

class PageRankTask(Task):
    def __init__(self) -> None:
        super().__init__(os.path.join(SCRIPT_DIR, "measure_pagerank.sh"))

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
            "iterations": int(info[1].strip()),
            "filename": filename
        }

    @staticmethod
    def process_performance_info(performance_data:Iterable):
        ret = {
            "time (s)":0,
            "memory_usage (mb)":0.0
        }
        for row in performance_data:
            time = re.search("whole cost: (\d+\.\d+)s", row)
            mem = re.search("memory usage: (\d+\.\d+) MBytes", row)
            if time is not None:
                ret["time (s)"] = float(time.group(1).strip())
            if mem is not None:
                ret["memory_usage (mb)"] += float(mem.group(1).strip())
        return ret

    @staticmethod
    def process_log_group(grouped_data:Iterable):
        if grouped_data is None or len(grouped_data) == 0:
            print("[Warning] no grouped_data provided")
        setup_info = PageRankTask.process_setup_info(grouped_data[0])
        performance_info = PageRankTask.process_performance_info(grouped_data[1:])
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
            out.append(PageRankTask.process_log_group(all_data[start:end]))
        return out