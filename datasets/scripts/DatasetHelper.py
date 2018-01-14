from scipy.spatial import distance
import json
import pandas as pd
import numpy as np
import os

def load_raw_dataset(raw_file_path):
    if os.path.isfile(raw_file_path + ".csv"):
        raw_file_path += ".csv"
    elif os.path.isfile(raw_file_path + ".csv.gz"):
        raw_file_path += ".csv.gz"
    else:
        print "Files supported: .csv and .csv.gz"
        quit()

    df = pd.read_csv(raw_file_path,
                     dtype={"timestamp": np.str,
                           "mac": np.str,
                           "frequency": np.uint8,
                           "length":np.uint32,
                           "rssi": np.int32,
                           "crc": np.bool,
                           "expected": np.bool,
                           "srcmac": np.str,
                           "transctr": np.uint32,
                           "pkctr": np.uint32,
                           "nbpackets": np.uint32,
                           "txpower": np.uint16,
                           "txifdur": np.uint32,
                           "txpksize": np.uint32,
                           "txfillbyte": np.str
                           },
                     date_parser = lambda timestamp: pd.datetime.strptime(timestamp, "%Y-%m-%d_%H.%M.%S"),
                     parse_dates = {'datetime': ['timestamp']},
                     #index_col = [0],  # make datetime column as index
                     )

    # clean dataset
    print "Length: {0}".format(len(df))
    df = df.drop_duplicates()
    print "Length without duplicates: {0}".format(len(df))
    df = df[(df.crc == 1) & (df.expected == 1)]
    df.drop('crc', axis=1, inplace=True)
    df.drop('expected', axis=1, inplace=True)

    return df

def load_dataset(raw_file_path):
    with open(raw_file_path, 'r') as f:
        header = json.loads(f.readline())

    df = pd.read_csv(raw_file_path,
                     parse_dates = ['datetime'],
                     index_col = [0],  # make datetime column as index
                     skiprows=1,
                     )
    return df, header

def helper(df):
    if "nbpackets" in df.keys():
        tx_count = df["nbpackets"].iloc[0]
    else:
        tx_count = df["txnumpk"].iloc[0]

    if "txpksize" in df.keys():
        tx_length = df["txpksize"].iloc[0]
    else:
        tx_length = df["txlength"].iloc[0]

    return {
        "node_count": len(df.mac.unique()),
        "channel_count": len(df.frequency.unique()),
        "tx_count": int(tx_count),
        "tx_ifdur": int(df["txifdur"].iloc[0]),
        "tx_length": int(tx_length),
        "transaction_count": len(df.transctr.unique()),
        "start_date": df.datetime.iloc[0].strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": df.datetime.iloc[-1].strftime("%Y-%m-%d %H:%M:%S"),
    }

def get_nodes_info(testbed):
    target_url = "../../metas/{0}.json".format(testbed)
    with open(target_url) as meta_file:
        node_list = json.load(meta_file)["nodes"]
    return node_list


def get_coords(node_list, mac):
    for node in node_list:
        if "mac" in node and node["mac"] == mac:
            return float(node["x"]), float(node["y"]), float(node["z"])
    return 0, 0, 0

def get_max_edge_count(node_count):
    max_link_count = 0
    node_count = node_count -1
    for i in range(node_count):
        max_link_count += node_count - i
    return max_link_count


def get_dist(node_list, mac1, mac2):
    mac1_coords = get_coords(node_list, mac1)
    mac2_coords = get_coords(node_list, mac2)
    dist = round(distance.euclidean(mac1_coords, mac2_coords), 1)
    return dist
