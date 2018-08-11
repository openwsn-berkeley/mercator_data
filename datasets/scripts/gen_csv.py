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
import pandas as pd
import numpy as np
import json

import dataset_helper

# ============================== defines ======================================

RAW_PATH = "../raw"
OUT_PATH = "../processed"

# ============================== main =========================================

def get_pdr(df_link, dtsh):
    rx_count = len(df_link)
    tx_count = dtsh["tx_count"]

    dbm_values = np.array(df_link["rssi"], dtype=float)
    average_mw = sum(np.power(10, dbm_values / 10)) / len(dbm_values)
    average_dbm = 10 * np.log10(average_mw)

    return pd.Series({
        "datetime": df_link.datetime.iloc[0],
        "transaction_id": df_link['transctr'].iloc[0],
        "pdr": rx_count / float(tx_count),
        "mean_rssi": round(average_dbm, 2),
    })


def main():

    # parsing user arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("testbed", help="The name of the testbed data to process", type=str)
    parser.add_argument("date", help="The date of the dataset", type=str)
    args = parser.parse_args()

    # load the dataset
    raw_file_path = "{0}/{1}/{2}".format(RAW_PATH, args.testbed, args.date)

    transaction_id = 0
    dtsh = None
    header_added = False

    while True:
        df = dataset_helper.load_dataset_by_transaction(raw_file_path, transaction_id)
        if df.empty:
            break

        # extract information
        if dtsh is None:
            dtsh = dataset_helper.helper(df)

        # compute PDR and RSSI average for each link and for each frequency
        df_pdr = df.groupby(["srcmac", "mac", "transctr", "frequency"]).\
            apply(get_pdr, dtsh).reset_index()

        # cleaning
        df_pdr.drop('transctr', axis=1, inplace=True)
        df_pdr.set_index("datetime", inplace=True)
        df_pdr.sort_index(inplace=True)
        df_pdr.rename(columns={'srcmac': 'src', 'mac': 'dst', 'frequency': 'channel'},
                      inplace=True)

        # write dataset to file
        path = "{0}/{1}".format(OUT_PATH, args.testbed)
        if not os.path.exists(path):
            os.makedirs(path)
        if header_added is False:
            df_pdr.to_csv("{0}/{1}.csv".format(path, args.date))
            header_added = True
        else:
            df_pdr.to_csv("{0}/{1}.csv".format(path, args.date), mode='a', header=False)

        transaction_id += 1

    # write dataset header at top of the csv
    dtsh["site"] = args.testbed
    dtsh["transaction_count"] = transaction_id
    header = json.dumps(dtsh)
    path = "{0}/{1}".format(OUT_PATH, args.testbed)
    with open("{0}/{1}.csv".format(path, args.date), 'r+') as f:
        s = f.read()
        f.seek(0, 0)
        f.write(header + "\n" + s)


if __name__ == '__main__':
    main()
