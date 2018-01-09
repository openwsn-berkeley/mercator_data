"""
This script plots the PDR per channel.

Usage example:
  $ python pdr_per_channel.py grenoble 2017.06.20-16.22.14
"""

import argparse
import pandas as pd
import DatasetHelper
import matplotlib.pyplot as plt

# ============================== defines ======================================

RAW_PATH = "../raw"
OUT_PATH = "../processed"

# ============================== main =========================================

def get_pdr(df_link):
    dtsh_link = DatasetHelper.helper(df_link)
    rx_count = len(df_link)
    tx_expected = dtsh_link["tx_count"] *\
                  dtsh_link["transaction_count"] *\
                  dtsh_link["node_count"] * (dtsh_link["node_count"] - 1)

    return pd.Series({
        "pdr": rx_count * 100 / float(tx_expected)
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

    # compute PDR and RSSI average for each link
    df_pdr = df.groupby(["frequency"]).apply(get_pdr)

    plt.bar(df_pdr.index, df_pdr.pdr)

    # plot
    plt.xlabel('Channels')
    plt.ylabel('PDR %')
    plt.xlim([10, 27])
    plt.ylim([40, 102])
    plt.tight_layout()

    plt.grid(True)

    plt.savefig("{0}/{1}/{2}_pdr_per_channel.png".format(OUT_PATH, args.testbed, args.date),
                format='png', bbox_inches='tight', pad_inches=0)
    plt.show()


if __name__ == '__main__':
    main()
