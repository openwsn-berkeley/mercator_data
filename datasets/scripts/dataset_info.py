#!/usr/bin/python

# ============================= description ===================================

# This script generates a file containing the given dataset information:
#   number of nodes
#   number of channels
#   duration
#   size
#
# The generated file are located here:
#    processed/<site>/<data>/info.json
#
# the format is json:
# {
#   'nb_nodes': <int>,
#   'nb_channels': <int>,
#   'duration': <int> (in hours)
# }

# ============================== imports ======================================

import os
import argparse
import pandas as pd
import json

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
    if os.path.isfile(raw_file_path + ".csv"):
        raw_file_path += ".csv"
    elif os.path.isfile(raw_file_path + ".csv.gz"):
        raw_file_path += ".csv.gz"
    else:
        print "Files supported: .csv and .csv.gz"
        quit()

    df = pd.read_csv(raw_file_path)

    # clean dataset
    df = df.drop_duplicates()
    df = df[(df.crc == 1) & (df.expected == 1)]

    dtsh = DatasetHelper.helper(df, args.testbed)

    # get nodes info

    node_list = DatasetHelper.get_nodes_info(args.testbed)

    # compute paths list
    path_list = []
    df["hash"] = df.apply(lambda row: (get_hash(row["mac"], row["srcmac"])), axis=1)
    for hash, link in df.groupby(["hash"]):
        AtoB = {}
        BtoA = {}

        # compute PDR for each link and separate A->B and B->A links
        for m, gr in link.groupby(["mac"]):
            rx_count = len(gr)
            rx_expected = dtsh["transaction_count"] * dtsh["tx_count"] * dtsh["channel_count"]
            avg_pdr = rx_count * 100 / rx_expected

            # compute PDR for each frequency
            pdr_list = []
            for channel, df_freq in gr.groupby(["frequency"]):
                rx_count = len(df_freq)
                rx_expected = dtsh["transaction_count"] * dtsh["tx_count"]
                pdr = rx_count * 100 / rx_expected
                pdr_list.append((channel, pdr))

            res = { "src": gr["srcmac"].iloc[0],
                    "dst": m,
                    "distance": DatasetHelper.get_dist(node_list, gr["srcmac"].iloc[0], m),
                    "PDR": {
                        "average": avg_pdr,
                        "channel": {channel: pdr for (channel, pdr) in pdr_list}
                    }
            }
            if check_hash(m, gr["srcmac"].iloc[0], hash):
                AtoB = res
            else:
                BtoA = res
            print res

        # add path
        path_list.append([AtoB, BtoA])

    # format collected information

    json_data = {
        "global": {
            "start_date": dtsh["start_date"],
            "end_date": dtsh["end_date"],
            "duration": dtsh["duration"],
            "nb_nodes": dtsh["node_count"],
            "nb_channels": dtsh["channel_count"],
            "transaction_count": dtsh["transaction_count"],
            "tx_count": dtsh["tx_count"],
            "tx_ifdur": dtsh["tx_ifdur"],
            "tx_length": dtsh["tx_length"],
            },
        "paths": path_list
    }

    # write the information to a file

    path = "{0}/{1}/{2}/".format(OUT_PATH, args.testbed, args.date)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + "info.json", 'w') as output_file:
        json.dump(json_data, output_file)


def get_hash(A, B):
    return ''.join(sorted([A, B]))


def check_hash(A, B, hash):
    if ''.join([A, B]) == hash:
        return True
    else:
        return False

if __name__ == '__main__':
    main()