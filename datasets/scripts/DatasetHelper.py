from scipy.spatial import distance
import urllib
import json
import datetime
import pandas as pd


def load_dataset(raw_file_path):
    df_list = {}
    df = pd.read_csv(raw_file_path)

    group_trans = df.groupby("transctr")
    for transctr, df_trans in group_trans:

        # remove wrong values
        df_trans = df_trans.drop_duplicates()
        df_trans = df_trans[(df_trans.crc == 1) & (df_trans.expected == 1)]

        if transctr in df_list:
            df_list[transctr].append(df_trans)
        else:
            df_list[transctr] = df_trans

    return df_list


def helper(df, testbed):
    helper = {
        "node_count": -1,
        "tx_count": None,
        "channel_count": None,
        "testbed": testbed,
        "data":  None,
    }

    # extract dataset properties

    helper["node_count"] = len(df.groupby("mac"))
    helper["channel_count"] = len(df.groupby("frequency"))
    if "nbpackets" in df.keys():
        helper["tx_count"] = df["nbpackets"].iloc[0]
    else:
        helper["tx_count"] = df["txnumpk"].iloc[0]
    helper["tx_ifdur"] = df["txifdur"].iloc[0]
    if "txpksize" in df.keys():
        helper["tx_length"] = df["txpksize"].iloc[0]
    else:
        helper["tx_length"] = df["txlength"].iloc[0]
    helper["transaction_count"] = len(df.groupby(["transctr", "srcmac"]))/helper["node_count"]
    start_date = datetime.datetime.strptime(df["timestamp"].iloc[0], "%Y-%m-%d_%H.%M.%S")
    end_date = datetime.datetime.strptime(df["timestamp"].iloc[-1], "%Y-%m-%d_%H.%M.%S")
    helper["start_date"] = start_date.strftime("%Y-%m-%d %H:%M:%S")
    helper["end_date"] = end_date.strftime("%Y-%m-%d %H:%M:%S")
    helper["duration"] = round((end_date - start_date).seconds/3600.0, 2)

    return helper


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


def get_dist(node_list, mac1, mac2):
    mac1_coords = get_coords(node_list, mac1)
    mac2_coords = get_coords(node_list, mac2)
    dist = round(distance.euclidean(mac1_coords, mac2_coords), 1)
    return dist
