"""
This script calculate the lifetime of a link

Usage example:
      $ python link_lifetime.py grenoble 2017.06.20-16.22.15
"""

import argparse
import logging
import datetime
import os
import json

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
    #print df.head()

    json_data = {}
    for link, df_link in df.groupby(["srcmac", "mac"]):
        link_lifetimes = []
        prev_state = 0
        start_date = df_link.datetime.iloc[0]

        for i, row in df_link.iterrows():
            current_state = 1 if row["pdr"] > 50 else 0
            if prev_state == 0 and current_state == 1:  # link going up
                start_date = row["datetime"]
            elif prev_state == 1 and current_state == 0:  # link going down
                lifetime = row["datetime"] - start_date
                link_lifetimes.append(lifetime)
                if lifetime == 0:
                    print row

            # save values
            prev_state = current_state

        # save lifetime if link was up
        if prev_state == 1:
            lifetime = df_link.iloc[-1]["datetime"] - start_date
            link_lifetimes.append(lifetime)

        if len(link_lifetimes):
            print link
            print link_lifetimes
            avg = sum(link_lifetimes, datetime.timedelta())/len(link_lifetimes)
            print "avg: {1}".format(link, avg)
            json_data[link] = avg

    # write the information to a file
    path = "{0}/{1}/".format(OUT_PATH, args.testbed)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + "{0}_link_lifetime.json".format(args.date), 'w') as output_file:
        json.dump(json_data, output_file, indent=4)


if __name__ == '__main__':
    main()
