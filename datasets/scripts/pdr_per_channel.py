"""
This script plots the PDR per channel.

Usage example:
  $ python pdr_per_channel.py grenoble 2017.06.20-16.22.14
"""

import argparse
import DatasetHelper
import matplotlib.pyplot as plt
import logging

# ============================== logging ======================================

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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

    df_grouped = df.groupby(df.channel).pdr.mean()
    print df_grouped
    plt.bar(df_grouped.index, df_grouped*100)

    # plot
    plt.xlabel('IEEE802.15.4 Channels')
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
