"""
This script plots the PDR over average RSSI.
The PDR is calculated over all the channel for each link.
This plot is better known as the Waterfall plot.

Usage example:
  $ python pdr_rssi.py grenoble 2017.06.20-16.22.15
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
    tx_count = dtsh_link["tx_count"] *\
               dtsh_link["transaction_count"] *\
               dtsh_link["channel_count"]

    return pd.Series({
        "mean_rssi": round(df_link["rssi"].mean() * 2) / 2,
        "pdr": rx_count * 100 / float(tx_count)
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
    df_pdr = df.groupby(["srcmac", "mac", "transctr"]).apply(get_pdr)

    # compute error bar
    df_grouped = df_pdr.groupby(["mean_rssi"])
    mean_index = [name for name, group in df_grouped]
    mean_pdr = [group.pdr.mean() for name, group in df_grouped]
    std_pdr = [group.pdr.std() for name, group in df_grouped]

    # plot
    plt.plot(df_pdr.mean_rssi, df_pdr.pdr, '+', zorder=0)
    plt.errorbar(mean_index, mean_pdr, std_pdr)

    plt.xlabel('RSSI average (dBm)')
    plt.ylabel('PDR %')
    plt.xlim([-95, -15])
    plt.ylim([0, 110])
    plt.tight_layout()

    plt.grid(True)

    plt.savefig("{0}/{1}/{2}_pdr_rssi.png".format(OUT_PATH, args.testbed, args.date),
                format='png', bbox_inches='tight', pad_inches=0)
    plt.show()


if __name__ == '__main__':
    main()
