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
import pandas as pd
import logging

import DatasetHelper

# ============================== logging ======================================

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# ============================== defines ======================================

RAW_PATH = "../processed"
OUT_PATH = "../results"

# ============================== main =========================================

def main():

    # parsing user arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", help="The path to the dataset", type=str)
    args = parser.parse_args()

    # load the dataset
    file_name = os.path.basename(args.dataset)
    df, header = DatasetHelper.load_dataset(args.dataset)
    logging.info("Dataset loaded.")

    # compute degree and radius
    avg_degree_list = []
    for name, df_trans in df.groupby(pd.Grouper(freq="1H")):
        if df_trans.empty:
            continue

        #df_link = df_trans.groupby(["src", "dst"]).mean().reset_index().dropna()

        # removing links with PDR <= 50
        df_filtered = df_trans[df_trans.mean_rssi > -85]

        # create graph
        G = nx.Graph()
        G.add_nodes_from(df_trans.src.unique())
        G.add_edges_from(df_filtered.groupby(["src", "dst"]).groups.keys())

        # calculate average degree
        avg_degree = sum([d[1] for d in G.degree()]) / float(G.number_of_nodes())

        # save degree and radius
        avg_degree_list.append(avg_degree)

        #del df_pdr

    # calculate average degree and radius
    avg_net_degree = sum(avg_degree_list) / float(len(avg_degree_list))

    # format collected information
    json_data = {
        # "start_date": header["start_date"],
        # "end_date": header["end_date"],
        # "nb_nodes": header["node_count"],
        # "nb_channels": header["channel_count"],
        # "transaction_count": header["transaction_count"],
        # "tx_count": header["tx_count"],
        # "tx_ifdur": header["tx_ifdur"],
        # "tx_length": header["tx_length"],
        "avg_degree": avg_net_degree,
    }
    print(json.dumps(json_data, indent=4))

    # write the information to a file
    path = "{0}/{1}/".format(OUT_PATH, header['site'])
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + "{0}_info.json".format(header["start_date"]), 'w') as output_file:
        json.dump(json_data, output_file, indent=4)


if __name__ == '__main__':
    main()
