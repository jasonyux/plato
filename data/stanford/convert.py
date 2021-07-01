import csv
import argparse

from typing import Callable, Iterable

node_mapping = {}
lowest = 0

def continous_grouping(row, ret) -> list[str]:
    global node_mapping, lowest
    if row is None or len(row) == 0:
        return []
    # first iteration
    node = row[0]
    info = node_mapping.get(node)
    if info is None:
        info = {
            'num': lowest,
            'lst_pos': len(ret)
        }
        lowest += 1
        node_mapping[node] = info
    else:
        info['lst_pos'] += 1
    lst_pos = info['lst_pos']
    ret.insert(lst_pos, row)
    return ret

def continous_mapping(row) -> list[str]:
    global node_mapping, lowest
    ret = []
    for node in row:
        info = node_mapping.get(node)
        if info is None:
            info = {
                'num': lowest,
                'lst_pos': -1 # does not matter anymore
            }
            lowest += 1
            node_mapping[node] = info
        ret.append(info['num'])
    return ret


def regroup_csv(csvpath:str) -> Iterable[Iterable]:
    out = []
    # first scan, group rows into the correct position
    with open(csvpath, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            out = continous_grouping(row, out)
    return out

def remap_csv(data_rows:Iterable[Iterable]) -> Iterable[Iterable]:
    out = []
    for row in data_rows:
        out.append(continous_mapping(row))
    return out

def write_csv(outpath:str, data_rows:Iterable[Iterable]):
    with open(outpath, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data_rows)
    return

def main(args):
    out = regroup_csv(args.file)
    out = remap_csv(out)
    write_csv(args.outfile, out)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts discontinuous csv graph data to continous data')
    parser.add_argument('file',type=str, help='csv file to be converted.')
    parser.add_argument('-o', type=str, default='out.csv', dest='outfile', help='output csv path. Defaults to out.csv')
    args = parser.parse_args()

    main(args)