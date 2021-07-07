import csv
import argparse
import os

from typing import Iterable

node_mapping = {}
lowest = 0

def continous_grouping(row:list) -> Iterable[Iterable]:
    global node_mapping, lowest
    if row is None or len(row) == 0:
        return []
    # sort by the first node
    row.sort(key=lambda elem:int(elem[0]))
    for nodes in row:
        node = nodes[0]
        info = node_mapping.get(node)
        if info is None:
            info = {
                'num': lowest,
                'lst_pos': -1 # does not matter anymore
            }
            lowest += 1
            node_mapping[node] = info
    return row

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
            if len(row) == 0:
                continue
            out.append(row)
    return continous_grouping(out)

def remap_csv(data_rows:Iterable[Iterable]) -> Iterable[Iterable]:
    out = []
    for row in data_rows:
        out.append(continous_mapping(row))
    out.sort(key=lambda elem:tuple(elem))
    return out

def __insert_into_mapping(node):
    global node_mapping, lowest
    if node not in node_mapping.keys():
        node_mapping[node] = lowest
        lowest += 1
    return

def remap_vertices(csvpath):
    with open(csvpath, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if len(row) == 0:
                continue
            n1, _ = row
            __insert_into_mapping(n1)
    return

def __yield_mapped_vertex(node):
    global node_mapping, lowest
    if node not in node_mapping.keys():
        node_mapping[node] = lowest
        lowest += 1
    return node_mapping[node]

def write_to_continous(infile, outfile):
    global node_mapping
    with open(infile, 'r') as inopen, open(outfile, 'w', newline='\n') as outopen:
        csv_reader = csv.reader(inopen)
        csv_writer = csv.writer(outopen)
        for row in csv_reader:
            if len(row) == 0:
                continue
            n1, n2 = row
            n1, n2 = map(__yield_mapped_vertex, (n1, n2))
            csv_writer.writerow((n1, n2))
    return

def write_csv(outpath:str, data_rows:Iterable[Iterable]):
    with open(outpath, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data_rows)
    return

def main(args):
    if args.monotone_increase:
        # 1. scan the file and generate mapping
        remap_vertices(args.file)
        # 2. scan the file again, use the mapping and recreate output
        write_to_continous(args.file, args.outfile)
    else:
        out = regroup_csv(args.file)
        out = remap_csv(out)
        write_csv(args.outfile, out)
    return

def validate_args(args):
    p_dir = os.path.dirname(args.outfile)

    if args.monotone_increase.lower() == "true":
        args.monotone_increase = True
    else:
        args.monotone_increase = False
    # check input file
    if not os.path.exists(args.file):
        raise Exception(f"File {args.file} not found")
    # check output file
    if p_dir and not os.path.exists(p_dir):
        raise Exception(f"Folder {p_dir} does not exist")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts discontinuous csv graph data to continous data')
    parser.add_argument('file',type=str, help='csv file to be converted.')
    parser.add_argument('-o', type=str, default='out.csv', dest='outfile', help='output csv path. Defaults to out.csv')
    parser.add_argument('-monotone_increase', type=str, default="false", dest='monotone_increase', help='Is the node id already monotonously increasing? If yes, this option will SAVE MUCH of the memory/cpu')
    args = parser.parse_args()

    validate_args(args)
    main(args)