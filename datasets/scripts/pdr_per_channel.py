"""
This script plots the PDR per channel.

Usage example:
  $ python pdr_per_channel.py grenoble 2017.06.20-16.22.14
"""

import argparse
import DatasetHelper
import matplotlib.pyplot as plt
import logging
import os

# ============================== logging ======================================

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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
print df.head()

df_grouped = df.groupby(df.channel).pdr.mean()
plt.bar([int(i) for i in df_grouped.index], df_grouped.values)

# plot
plt.xlabel('IEEE802.15.4 Channels')
plt.ylabel('PDR %')
plt.xlim([10, 27])
plt.ylim([40, 102])
plt.tight_layout()
plt.grid(True)

path = "{0}/{1}".format(OUT_PATH, header['site'])
if not os.path.exists(path):
    os.makedirs(path)
plt.savefig("{0}/pdr_per_channel_{1}.png".format(path, header['site']),
            format='png', bbox_inches='tight', pad_inches=0)
plt.show()
