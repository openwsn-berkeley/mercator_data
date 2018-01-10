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

RAW_PATH = "../raw"
OUT_PATH = "../processed"

# ============================== main =========================================

def get_pdr(df_link, dtsh):
    rx_count = len(df_link)
    tx_count = dtsh["tx_count"] * \
               dtsh["channel_count"]

    return pd.Series({
        "datetime": df_link.datetime.iloc[0],
        "pdr": 100*rx_count / float(tx_count)
    })

def main():

    # parsing user arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("testbed", help="The name of the testbed data to process", type=str)
    parser.add_argument("date", help="The date of the dataset", type=str)
    args = parser.parse_args()

    # load the dataset
    raw_file_path = "{0}/{1}/{2}".format(RAW_PATH, args.testbed, args.date)
    df = DatasetHelper.load_dataset(raw_file_path)
    logging.info("Dataset loaded.")

    dtsh = DatasetHelper.helper(df)

    # compute degree and radius
    avg_degree_list = []
    for name, df_goup in df.groupby(["transctr"]):
        logging.info("Transaction: {0}".format(name))
        if df_goup.empty:
            continue

        # calculate pdr
        df_pdr = df_goup.groupby(["srcmac", "mac"]).apply(get_pdr, dtsh).reset_index()

        # removing links with PDR <= 50
        df_pdr = df_pdr[df_pdr.pdr > 50]

        # create graph
        G = nx.Graph()
        G.add_nodes_from(df_goup.srcmac)
        G.add_edges_from(df_pdr.groupby(["srcmac", "mac"]).groups.keys())

        # calculate average degree
        avg_degree = sum([d[1] for d in G.degree()]) / float(G.number_of_nodes())

        # save degree and radius
        avg_degree_list.append(avg_degree)

        del df_pdr

    # calculate average degree and radius
    avg_net_degree = sum(avg_degree_list) / float(len(avg_degree_list))

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
        "avg_degree": avg_net_degree,
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
