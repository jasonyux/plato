import argparse
import os
import random
import csv
import igraph

MILLION=10**6

# used for storing depulicate edges for undirected graph
edge_map = {}
# generated data
generated_info = {}

def __generate_edges(node_id, density, is_directed, node_min_id, node_max_id):
    ret = []
    for edge in range(node_min_id, node_max_id+1):
        if edge == node_id:
            continue
        if not is_directed:
            # duplicate if (edge, node_id) existed
            if edge in edge_map.keys() and node_id in edge_map[edge].keys():
                continue
        if random.random() <= density:
            ret.append((node_id, edge))
            if not is_directed:
                # initialize if new
                if node_id not in edge_map.keys():
                    edge_map[node_id] = {}
                # add
                edge_map[node_id][edge] = edge
    return ret

def __filenames_init(v_num, densities, output_dir):
    for density in densities:
        filename = "v{}_d{}.csv".format(v_num, density)
        path = os.path.join(output_dir, filename)
        if os.path.exists(path):
            raise Exception(f"File {path} already exists!")
    return

def __generate_other_graphs(v_num, densities, is_directed, max_density, first_graph, output_dir):
    max_density = max(densities)
    max_edge_num = v_num * (v_num - 1)
    if not is_directed:
        max_edge_num /= 2
    # compute other densities
    for density in densities:
        if density == max_density:
            continue
        cut_probability = float(max_density - density)/max_density
        filename = "v{}_d{}.csv".format(v_num, density)
        save_to_csv_w_info(density, os.path.join(output_dir, filename), first_graph, cut_probability)
    return

def __generate_graphs(v_num, densities, is_directed, output_dir, flush_batch) -> "list[tuple]":
    ret = []

    __filenames_init(v_num, densities, output_dir)
    # compute one graph
    max_density = max(densities)
    filename = "v{}_d{}.csv".format(v_num, max_density)
    for i in range(v_num):
        ret += __generate_edges(i, max_density, is_directed, 0, v_num-1)
        # batch related optimization
        if len(ret) >= flush_batch:
            save_to_csv_w_info(max_density, os.path.join(output_dir, filename), ret, 0.0)
            # generate other lower density graph by cutting some edges out
            __generate_other_graphs(v_num, densities, is_directed, max_density, ret, output_dir)
            ret = []
    # flush last batch
    if len(ret) != 0:
        save_to_csv_w_info(max_density, os.path.join(output_dir, filename), ret, 0.0)
        __generate_other_graphs(v_num, densities, is_directed, max_density, ret, output_dir)
        ret = []
    return

def show_all_info(v_num, is_directed):
    for k, v in generated_info.items():
        show_info(v_num, v['edges'], is_directed, k)
    return

def show_info(v_num, e_num, is_directed, input_density):
    max_edge_num = v_num * (v_num - 1)
    if not is_directed:
        max_edge_num /= 2
    info = """
    Target is_directed={}, input density={}
    Generated vertices={}, edges={}, density={}
    """.format(is_directed, input_density, v_num, e_num, e_num/float(max_edge_num))
    print(info)
    return v_num, e_num, e_num/float(max_edge_num)

def save_to_csv_w_info(density, path, data, cut_probability):
    if density not in generated_info.keys():
        generated_info[density] = {'edges': 0}
    num_written = save_to_csv(path, data, cut_probability)
    generated_info[density]['edges'] += num_written
    return

def save_to_csv(path, data, cut_probability):
    count = 0
    with open(path, 'a', newline='\n') as openfile:
        # creating a csv writer object 
        csvwriter = csv.writer(openfile)
        for row in data:
            # cut the edge
            if random.random() < cut_probability:
                continue
            csvwriter.writerow(row)
            count += 1
    return count

def __save_igraph_to_csv(edgelist, path):
    with open(path, 'w', newline='\n') as openfile:
        # creating a csv writer object 
        csvwriter = csv.writer(openfile)
        csvwriter.writerows(edgelist)
    return

def save_igraph_to_file(g, filename):
    __save_igraph_to_csv(g.get_edgelist(), filename)
    #igraph.write(g, filename, format = "edgelist")
    return

def __record_generated(density, g_e_num):
    if density not in generated_info.keys():
        generated_info[density] = {'edges': g_e_num}
    generated_info[density]['edges'] = g_e_num
    return

def generate_graphs(v_num, densities, is_directed, output_dir):
    """old. This is quite slow but seems to work better with memory
    # compute graph with highest density
    __generate_graphs(v_num, densities, is_directed, output_dir, flush_batch=1000)
    """
    # generate max density first
    max_density = max(densities)
    max_edge_num = v_num * (v_num - 1)
    if not is_directed:
        max_edge_num /= 2
    e_num = int(max_density*max_edge_num)
    g = igraph.Graph.Erdos_Renyi(n=v_num, m=e_num, directed=is_directed)
    filename = f"v{v_num}_e{e_num}.csv"
    save_igraph_to_file(g, os.path.join(output_dir, filename))
    # record info
    __record_generated(max_density, e_num)
    for density in densities:
        if density == max_density:
            continue
        e_num = int(density*max_edge_num)
        edge_list = random.sample(g.get_edgelist(), e_num)
        filename = f"v{v_num}_e{e_num}.csv"
        __save_igraph_to_csv(edge_list, os.path.join(output_dir, filename))
        # record info
        __record_generated(density, e_num)
    return

def main(args):
    v_num = round(args.v_num * MILLION)
    densities = args.density
    is_directed = args.is_directed
    output_dir = args.output
    generate_graphs(v_num, densities, is_directed, output_dir)
    show_all_info(v_num, is_directed)
    return

def check_input(args):
    # warning
    if args.v_num >= 10:
        print("[Warning] This might go OOM and gets killed.")
    # parse boolean value
    if args.is_directed.lower() == "true":
        args.is_directed = True
    else:
        args.is_directed = False
    # check density
    for density in args.density:
        assert(density >= 0.0 and density <= 1.0)
    assert(args.v_num >= 0)
    if not os.path.exists(args.output):
        raise(f"Path {args.output} does not exist!")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Undirected/Directed Graph Data")
    parser.add_argument('v_num', type=float, help="Number of vertices in the graph. Unit in Million")
    parser.add_argument('is_directed', type=str, help="Whether if graphs should be directed")
    parser.add_argument('density', type=float, nargs="+", help="List of graph with specified edge densities to generate. This will be useful for comparision since they will have the SAME num vertices and a similar topology. Value takes the range of [0,1].")
    parser.add_argument('--output', type=str, dest='output', default="./output", help="Output directory to save generated graphs.")
    args = parser.parse_args()
    
    check_input(args)
    main(args)