"""
This script plots the PDR over time per channel.

Usage example:
  $ python pdr_time_per_channel.py grenoble 2017.06.20-16.22.15
"""

import argparse
import logging
import matplotlib.pyplot as plt
import matplotlib.dates as md
import os
import pandas as pd

import DatasetHelper

# ============================== defines ======================================

RAW_PATH = "../processed"
OUT_PATH = "../results"

# ============================== main =========================================

# parsing user arguments
parser = argparse.ArgumentParser()
parser.add_argument("dataset", help="The path to the dataset", type=str)
args = parser.parse_args()

# load the dataset
file_name = os.path.basename(args.dataset)
df, header = DatasetHelper.load_dataset(args.dataset)
logging.info("Dataset loaded.")

color_list = ["blue", "red"]
for link, df_link in df.groupby(["src", "dst"]):
    for freq, df_freq in df_link.groupby("channel"):
        df_grouped = df_freq.groupby(pd.Grouper(freq="15min")).first()
        print df_grouped.pdr.fillna(0)
        plt.plot(df_grouped.index, 0.8*df_grouped.pdr/100 + freq, '.', zorder=0, markersize=2,
                 color=color_list[freq%len(color_list)])

    plt.xlabel('Time')
    plt.ylabel('IEEE802.15.4 Channels')
    plt.ylim([10, 27])
    plt.xlim(["2017-12-19 21:34:57", "2017-12-22 21:34:57"])
    plt.yticks(df.channel.unique())
    plt.grid(True)
    xfmt = md.DateFormatter('%H:%M:%S')
    ax = plt.gca()
    ax.xaxis.set_major_formatter(xfmt)
    plt.gcf().autofmt_xdate()

    path = "{0}/{1}".format(OUT_PATH, header['site'])
    if not os.path.exists(path):
        os.makedirs(path)
    plt.savefig("{0}/pdr_time_per_channel_{1}_{2}.png".format(path, header['site'], link),
                format='png', bbox_inches='tight', pad_inches=0)
    plt.show()
    plt.clf()
