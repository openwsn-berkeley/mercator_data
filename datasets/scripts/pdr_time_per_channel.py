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

import dataset_helper

plt.rcParams.update({'font.size': 14})
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
df, header = dataset_helper.load_dataset(args.dataset)
logging.info("Dataset loaded.")

color_list = ["blue", "red"]
for link, df_link in df.groupby(["src", "dst"]):
    for freq, df_freq in df_link.groupby("channel"):
        plt.plot(df_freq.index, 0.8*df_freq.pdr/100 + freq, '.', zorder=2, markersize=2,
                 color=color_list[freq%len(color_list)])

    for day, df_day in df.groupby(pd.Grouper(freq="1d")):
        if len(df_day) > 5424:
            day_start = day + pd.DateOffset(hours=9)
            day_stop = day + pd.DateOffset(hours=18)
            plt.fill_between([day_start, day_stop], 0, 30, color='#d5dbdb', alpha=0.5, zorder=1)

    plt.xlabel('Time')
    plt.ylabel('PDR (%) per IEEE802.15.4 Channel')
    plt.ylim([10, 27])
    plt.yticks(df.channel.unique())
    plt.grid(True)
    xfmt = md.DateFormatter('%y-%m-%d')
    #xfmt = md.DateFormatter('%H:%M')
    ax = plt.gca()
    ax.xaxis.set_major_formatter(xfmt)
    plt.gcf().autofmt_xdate()

    path = "{0}/{1}".format(OUT_PATH, header['site'])
    if not os.path.exists(path):
        os.makedirs(path)
    plt.savefig("{0}/pdr_time_per_channel_{1}_{2}.png".format(path, header['site'], link),
                format='png', bbox_inches='tight', pad_inches=0)
    plt.clf()
