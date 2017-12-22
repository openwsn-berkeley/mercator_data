"""
This script plots the PDR over time per channel.

Usage example:
  $ python pdr_time_per_channel.py grenoble 2017.06.20-16.22.15
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
               dtsh_link["transaction_count"]

    return pd.Series({
        "datetime": df_link.datetime.iloc[0],
        "pdr": 0.8*rx_count / float(tx_count)
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
    print df.head()

    # compute PDR and RSSI average for each link and for each frequency
    df_pdr = df.groupby(["srcmac", "mac", "transctr", "frequency"]).apply(get_pdr).reset_index()
    print df_pdr.head()

    for link, df_link in df_pdr.groupby(["srcmac", "mac"]):
        for freq, df_freq in df_link.groupby("frequency"):
            plt.plot(df_freq.datetime, df_freq.pdr + freq, '+', zorder=0)
        break

    plt.xlabel('Time')
    plt.ylabel('IEEE802.15.4 Channels')
    plt.ylim([10, 27])
    plt.yticks(df.frequency.unique())
    plt.grid(True)
    plt.gcf().autofmt_xdate()

    plt.savefig("{0}/{1}/{2}_pdr_time_per_freq.png".format(OUT_PATH, args.testbed, args.date),
                format='png', bbox_inches='tight', pad_inches=0)
    plt.show()


if __name__ == '__main__':
    main()
