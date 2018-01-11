"""
This script plots the PDR over time.
The PDR is calculated over all the channel for each link.

Usage example:
  $ python pdr_time.py grenoble 2017.06.20-16.22.15
"""

import argparse
import pandas as pd
import DatasetHelper
import matplotlib.pyplot as plt

# ============================== defines ======================================

RAW_PATH = "../processed"
OUT_PATH = "../results"

# ============================== main =========================================

def main():

    # parsing user arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("testbed", help="The name of the testbed data to process", type=str)
    parser.add_argument("date", help="The date of the dataset", type=str)
    args = parser.parse_args()

    # load the dataset
    raw_file_path = "{0}/{1}/{2}".format(RAW_PATH, args.testbed, args.date)
    df = DatasetHelper.load_dataset(raw_file_path)

    pdr_grouped = df.pdr.groupby(pd.TimeGrouper('25Min')).mean().dropna()

    # plot
    plt.plot(df.index, df.pdr, '+')
    plt.plot(pdr_grouped.index, pdr_grouped)

    plt.xlabel('Time')
    plt.ylabel('PDR (%)')
    plt.ylim([0, 1.1])
    plt.grid(True)
    plt.gcf().autofmt_xdate()

    plt.savefig("{0}/{1}/{2}_pdr_time.png".format(OUT_PATH, args.testbed, args.date),
                format='png', bbox_inches='tight', pad_inches=0)

    plt.show()

    # plot per link
    # plt.yticks(df_pdr.frequency.unique())
    # for link, df_link in df_pdr.groupby(["srcmac", "mac"]):
    #     for freq, df_freq in df_link.groupby("frequency"):
    #         plt.plot(df_freq.datetime, df_freq.pdr + freq, '.', markersize=2)
    #     #break
    #
    #     plt.xlabel('Time')
    #     plt.ylabel('IEEE802.15.4 Channels')
    #     plt.ylim([10, 27])
    #     plt.grid(True)
    #     plt.gcf().autofmt_xdate()
    #
    #     plt.show()


if __name__ == '__main__':
    main()