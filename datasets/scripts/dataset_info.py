#!/usr/bin/python

# ============================= description ===================================

# This script generates a file containing the given dataset information:
#   number of nodes
#   number of channels
#   duration
#   size
#   ...
#
# The generated file are located here:
#    processed/<site>/<date>_info.json
#
# the format is json:
# {
#   'nb_nodes': <int>,
#   'nb_channels': <int>,
#   'duration': <int>, (in hours)
#   ...
# }

# ============================== imports ======================================

import os
import argparse
import json
import networkx as nx

import DatasetHelper

# ============================== defines ======================================

RAW_PATH = "../raw"
OUT_PATH = "../processed"

# ============================== main =========================================


def main():

    # parsing user arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("testbed", help="The name of the testbed data to process", type=str)
    parser.add_argument("date", help="The date of the dataset", type=str)
    args = parser.parse_args()

    # load the dataset
    raw_file_path = "{0}/{1}/{2}".format(RAW_PATH, args.testbed, args.date)
    df = DatasetHelper.load_dataset(raw_file_path)

    dtsh = DatasetHelper.helper(df)

    # compute degree and radius
    net_degree_list = []
    net_radius_list = []
    for name, df_goup in df.groupby(["transctr"]):
        if df_goup.empty:
            continue

        # create graph
        G = nx.Graph()
        G.add_nodes_from(df_goup.srcmac)
        G.add_edges_from(df_goup.groupby(["srcmac", "mac"]).groups.keys())

        # calculate network degree
        max_edge_count = DatasetHelper.get_max_edge_count(G.number_of_nodes())
        net_degree = G.number_of_edges() / float(max_edge_count)

        # save degree and radius
        net_degree_list.append(net_degree)
        net_radius_list.append(nx.radius(G))

    # calculate average degree and radius
    avg_net_degree = sum(net_degree_list) / float(len(net_degree_list))
    avg_net_radius = sum(net_radius_list) / float(len(net_radius_list))

    # format collected information
    json_data = {
        "start_date": dtsh["start_date"],
        "end_date": dtsh["end_date"],
        "nb_nodes": dtsh["node_count"],
        "nb_channels": dtsh["channel_count"],
        "transaction_count": dtsh["transaction_count"],
        "tx_count": dtsh["tx_count"],
        "tx_ifdur": dtsh["tx_ifdur"],
        "tx_length": dtsh["tx_length"],
        "degree": avg_net_degree,
        "radius": avg_net_radius,
    }
    print(json.dumps(json_data, indent=4))

    # write the information to a file
    path = "{0}/{1}/".format(OUT_PATH, args.testbed)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + "{0}_info.json".format(args.date), 'w') as output_file:
        json.dump(json_data, output_file, indent=4)


if __name__ == '__main__':
    main()
