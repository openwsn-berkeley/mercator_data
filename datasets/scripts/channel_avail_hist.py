"""
This script plots histogram of the number of available channels per link.

Usage example:
  $ python channel_avail_hist.py grenoble 2017.06.20-16.22.14
"""

import argparse
import dataset_helper
import matplotlib.pyplot as plt
import logging
import pandas as pd
import os

plt.rcParams.update({'font.size': 14})
# ============================== logging ======================================

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# ============================== defines ======================================

RAW_PATH = "../raw"
OUT_PATH = "../results"

# ============================== main =========================================

def get_pdr(df_link):
    dtsh_link = dataset_helper.helper(df_link)
    rx_count = len(df_link)
    tx_expected = dtsh_link["tx_count"]

    return pd.Series({
        "pdr": rx_count * 100 / float(tx_expected)
    })

def main():
    # parsing user arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", help="The path to the dataset", type=str)
    args = parser.parse_args()

    # load the dataset
    file_name = os.path.basename(args.dataset)
    df, header = dataset_helper.load_dataset(args.dataset)
    logging.info("Dataset loaded.")

    # filter bad links
    df_filtered = df[df.pdr > 50]

    # count number of channels available per links over time
    avail_count = []
    for link, df_link in df_filtered.groupby(["src", "dst"]):
        chan_list = df_link.groupby("transaction_id").channel.unique().str.len().tolist()
        avail_count += chan_list

    plt.hist(avail_count, bins=[i for i in range(0, 18)])

    plt.xlabel('number of frequencies with PDR>50%')
    plt.ylabel('number of PDR measurements')
    plt.xlim([0, 17])
    plt.xticks([t for t in range(0, 17)])
    plt.grid(True)

    path = "{0}/{1}".format(OUT_PATH, header['site'])
    if not os.path.exists(path):
        os.makedirs(path)
    plt.savefig("{0}/channel_avail_hist_{1}.png".format(path, header['site']),
                format='png', bbox_inches='tight', pad_inches=0)
    plt.show()


if __name__ == '__main__':
    main()
