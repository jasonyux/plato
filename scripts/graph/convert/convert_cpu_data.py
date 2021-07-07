import re
import json
import os
import argparse


def read_data(filename):
    ret = []
    with open(filename, 'r') as openfile:
        out = openfile.readlines()
    for line in out:
        if line != '\n' and line[-1] == '\n':
            line = line[:-1]
        ret.append(line)
    return ret

def parse_header(lines):
    algo = ""
    for num, line in enumerate(lines):
        if line == '\n':
            return algo, lines[num+1:]
        algo = line
    return algo, lines[num+1:]

def __parse_data(lines):
    """
    Expects lines in the form of
    ['setup_info=xxx', '31845 0.0 0:00.00 java', '\n', 'setup_info=xxx', '31845 0.0 0:00.00 java', ...]
    """
    out = {}
    curr = {
        'setup':{},
        'data':[]
    }
    is_setup = True
    is_data = False
    
    algo, lines = parse_header(lines)
    out[algo] = []
    for line in lines:
        if is_setup:
            match = re.search("(.*)=(.*)", line)
            try:
                k, v = match.group(1), match.group(2)
            except:
                is_setup = False
                is_data = True
            curr['setup'][k] = int(v)
        if is_data:
            # check if new group data
            if line == '\n':
                out[algo].append(curr)
                is_setup = True
                is_data = False
                curr = {
                    'setup':{},
                    'data':[]
                }
                continue
            curr['data'].append(line)
    return out

def parse_data(filename, out_filename):
    data = read_data(filename)
    data = __parse_data(data)
    write_json(data, out_filename)
    return

def write_json(data, filename):
    json_object = json.dumps(data, indent = 4)
    with open(filename, "w") as outfile:
        outfile.write(json_object)
    return

def main(args):
    infile = args.infile
    outfile = args.outfile
    parse_data(infile, outfile)
    return

def validate_args(args):
    p_dir = os.path.dirname(args.outfile)
    out_ext = os.path.splitext(args.outfile)[-1]
    
    # check input file
    if not os.path.exists(args.infile):
        raise Exception(f"File {args.infile} not found")
    # check output file
    if p_dir and not os.path.exists(p_dir):
        raise Exception(f"Folder {p_dir} does not exist")
    assert(out_ext=='.json')
    return
    
    

if __name__ == "__main__":
    """
    EXPECTS txt file in the format of:
    ---start of txt
    kcore

    machine_num=4
    machine_no=2
    31845 0.0 0:00.00 java
    31847 0.0 0:02.30 java
    31848 0.0 0:00.57 java

    machine_num=4
    machine_no=2
    31845 0.0 0:00.00 java
    31847 0.0 0:02.30 java
    ...
    """
    parser = argparse.ArgumentParser(description="Convert raw experiment cpu data to structured json file for later processing")
    parser.add_argument('infile', type=str, help="input txt file path")
    parser.add_argument('outfile', type=str, help="output json file path")
    args = parser.parse_args()

    validate_args(args)
    main(args)