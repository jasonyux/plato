import matplotlib.pyplot as plt
import re
import json

from textwrap import wrap
from typing import Iterable

def group_by_algo(data, group_num):
    grouped_data = {}
    for i in range(0, len(data), group_num):
        name = data[i]['setup']['filename']
        found = re.search("^(\w+_*\w+)\.(\w+_*\w+)", name.replace("-","_"))
        dataset = found.group(1)
        algorithm = found.group(2)
        grouped_data[algorithm] = data[i:i+group_num]
    return dataset, grouped_data


class GraphInfo(object):
    def __init__(self, algo:str, info_group:Iterable[dict]):
        self.__info_group = info_group
        self.__algo = algo
    
    def extract_y(self):
        out = {}
        for info in self.__info_group:
            perf = info['performance']
            for k, v in perf.items():
                if k not in out.keys():
                    out[k] = [v]
                else:
                    out[k].append(v)
        return out
    
    def extract_x(self):
        out = {}
        for info in self.__info_group:
            perf = info['setup']
            for k, v in perf.items():
                if k == 'filename':
                    continue
                if k not in out.keys():
                    out[k] = [v]
                else:
                    out[k].append(v)
        return out

    def graphable_perf(self):
        return self.extract_x(), self.extract_y()

    def get_algorithm(self):
        return self.__algo


def addlabels(x,y, offset=0):
    for i in range(len(x)):
        plt.text(i+1+offset, y[i], y[i], ha = 'center')
    return

def plot_single_bar(plt, x, y, width, offset=0, color='blue'):
    plt.bar([i + offset for i in x], y, width = width, color=color)
    # configure y
    addlabels(x, y, offset)
    return plt

def dict_to_str(input:dict):
    ret = ""
    for k, v in input.items():
        ret+="{}={}, ".format(k,v[0])
    return ret[:-2]

def graph_single_algo(graph_info:GraphInfo, width=0.5):
    plt.clf()
    # data
    colors = ['blue', 'green','red','cyan', 'magenta']
    x_label = 'machine_num'
    x, y = graph_info.graphable_perf()
    x_copy = x.copy()
    x_copy.pop(x_label)
    num_plots = len(y.keys())
    x = x[x_label]

    title = "Performance of Plato {} algorithm with {}".format(graph_info.get_algorithm(), dict_to_str(x_copy))
    title="\n".join(wrap(title, 50))
    # plots
    plt.suptitle(title, fontsize=17, y=1.1)
    count = 0
    for k, v in y.items():
        ax = plt.subplot(1, num_plots, count+1)
        plt.ylabel(k, fontsize=16)
        plt.xlabel(x_label, fontsize=16)
        plot_single_bar(plt, x, v, width, color=colors[count])
        plt.setp(ax.get_xticklabels(), fontsize=14)
        plt.setp(ax.get_yticklabels(), fontsize=14)
        count += 1
    # overall
    plt.tight_layout()
    return plt

def save_fig(path):
    print(f"Saving to {path}")
    plt.savefig(path, bbox_inches='tight')

"""
Plot and saves
"""
def plot_all(dataset, grouped_data:dict):
    for k, v in grouped_data.items():
        info = GraphInfo(k, v)
        graph_single_algo(info)
        save_fig(f'{dataset}/{k}_performance.png')
    return

if __name__ == "__main__":
    # this data comes from the 'measure_all.py' from the Plaot project 
    group_num = 4 # number of data in each group
    with open("data.json") as openfile:
        exp_data = json.load(openfile)
        print("Avaiable Keys {}".format(exp_data.keys()))
        for key in exp_data.keys():
            print("Plotting {}".format(key))
            data = exp_data[key]
            dataset, grouped_data = group_by_algo(data, group_num)
            plot_all(dataset, grouped_data)


