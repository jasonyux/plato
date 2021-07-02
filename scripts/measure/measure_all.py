from task import Task
from tasks.pagerank import PageRankTask

def numeric_average(infos:list):
    """
    Expecting [{'setup': {}, 'performance': {}}, {'setup': {}, 'performance': {}}, ...]
    """
    if infos is None or len(infos) == 0:
        print("[Warning] numeric_average got no info")
        return {}
    out = infos[0]
    for info in infos[1:]:
        for key, values in info.items():
            for __key, __value in values.items():
                if isinstance(__value, (int, float)):
                    out[key][__key] += __value
    for key, values in out.items():
        for __key, __value in values.items():
            if isinstance(__value, (int, float)):
                out[key][__key] /= len(infos)
                out[key][__key] = round(out[key][__key], 2)
    return out

def measure_single(task:Task, tries=3):
    tmp = []
    out = []
    group_len = 0
    for i in range(tries):
        ret = task.run()
        performances = task.extract_perf(ret)
        group_len = len(performances)
        tmp += performances
        print(performances)
    for i in range(group_len):
        out.append(numeric_average(tmp[i::group_len]))
    print(out)
    return out

if __name__ == "__main__":
    Tasks = [
        PageRankTask()
    ]
    measure_single(Tasks[0])
