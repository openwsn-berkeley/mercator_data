"""
This script plots the PDR over time per channel.

Usage example:
  $ python pdr_time_per_channel.py grenoble 2017.06.20-16.22.15
"""

import argparse
import logging
import pandas as pd
import matplotlib.pyplot as plt

import DatasetHelper

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
    logging.info("Dataset loaded.")
    print df.head()

    # fill missing values when PDR = 0
    # empty_array = []
    # for transaction_id in range(0, dtsh["transaction_count"]):
    #     for channel in range(11,27):
    #         for link, df_link in df_pdr.groupby(["srcmac", "mac"]):
    #             empty_array.append([link[0], link[1], transaction_id, channel])
    # df_filled = pd.DataFrame(empty_array, columns=["srcmac", "mac", "transctr", "frequency"])
    # print df_filled
    # df_merged = pd.merge(df_filled, df_pdr, how='outer', on=["srcmac", "mac", "transctr", "frequency"])
    # df_merged.datetime.interpolate(method='linear', inplace=True)
    # df_merged.pdr.fillna(0, inplace=True)
    # df_merged.datetime.dropna(inplace=True)
    # print df_merged.head()

    color_list = ["blue", "red"]
    for link, df_link in df.groupby(["src", "dst"]):
        for freq, df_freq in df_link.groupby("channel"):
            plt.plot(df_freq.index, 0.8*df_freq.pdr + freq, '.', zorder=0, markersize=2,
                     color=color_list[freq%len(color_list)])

        plt.xlabel('Time')
        plt.ylabel('IEEE802.15.4 Channels')
        plt.ylim([10, 27])
        plt.yticks(df.channel.unique())
        plt.grid(True)
        plt.gcf().autofmt_xdate()

        plt.savefig("{0}/{1}/{2}_{3}_pdr_time_per_channel.png".format(OUT_PATH, args.testbed, args.date, link),
                    format='png', bbox_inches='tight', pad_inches=0)
        plt.show()
        plt.clf()


if __name__ == '__main__':
    main()
