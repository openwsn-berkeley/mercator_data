"""
This script converst a mercator dataset into a generic dataset

Usage example:
  $ python gen_csv.py grenoble 2017.06.20-16.22.15

Input CSV format:
timestamp,mac,frequency,length,rssi,crc,expected,srcmac,transctr,pkctr,nbpackets,txpower,txifdur,txpksize,txfillbyte

Ouput CSV format:
datetime,src,dst,channel,mean_rssi,pdr

"""

import os
import argparse
import logging
import pandas as pd
from scipy.special import logsumexp

import DatasetHelper

# ============================== defines ======================================

RAW_PATH = "../raw"
OUT_PATH = "../processed"

# ============================== main =========================================

def get_pdr(df_link, dtsh):
    rx_count = len(df_link)
    tx_count = dtsh["tx_count"]

    return pd.Series({
        "datetime": df_link.datetime.iloc[0],
        "pdr": rx_count / float(tx_count),
        "mean_rssi": round(logsumexp(df_link["rssi"]) * 2) / 2,
    })


def main():

    # parsing user arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("testbed", help="The name of the testbed data to process", type=str)
    parser.add_argument("date", help="The date of the dataset", type=str)
    args = parser.parse_args()

    # load the dataset
    raw_file_path = "{0}/{1}/{2}".format(RAW_PATH, args.testbed, args.date)
    df = DatasetHelper.load_raw_dataset(raw_file_path)
    logging.info("Dataset loaded.")

    # extract information
    dtsh = DatasetHelper.helper(df)

    # compute PDR and RSSI average for each link and for each frequency
    df_pdr = df.groupby(["srcmac", "mac", "transctr", "frequency"]).apply(get_pdr, dtsh).reset_index()

    # free space (ugly you said?)
    del df

    # cleaning
    df_pdr.drop('transctr', axis=1, inplace=True)
    df_pdr.set_index("datetime", inplace=True)
    df_pdr.sort_index(inplace=True)
    df_pdr.rename(columns={'srcmac': 'src', 'mac': 'dst', 'frequency': 'channel'}, inplace=True)

    # write dataset to file
    path = "{0}/{1}/{2}.csv".format(OUT_PATH, args.testbed, args.date)
    if not os.path.exists(path):
        os.makedirs(path)
    df_pdr.to_csv(path)


if __name__ == '__main__':
    main()
