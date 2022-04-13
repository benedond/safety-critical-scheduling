#! /usr/bin/python3

# Add measured data to the results
# - open the results file
#   - for each instance, find the measurement file in given folder
#   - get the measured average power consumption
#   - add it to the new_column

import argparse
import os
import pandas as pd
import utils


parser = argparse.ArgumentParser()
parser.add_argument("-r", "--results_file", type=str, help="Path to the results file to be modified.")
parser.add_argument("-m", "--measurements_folder", type=str, help="Path to the folder containing the measurements.")
parser.add_argument("-c", "--new_column_name", type=str, help="Name of the column to be added.")
parser.add_argument("-s", "--measurement_suffix", default=".json.yaml.csv", type=str, help="Suffix to be added to the instance name to find the measurement file.")


if __name__ == "__main__":
    args = parser.parse_args()

    # read the results
    df = utils.read_csv(args.results_file)      
    # arr new column with power measurements
    df[args.new_column_name] = df.apply(lambda row: utils.get_power_from_measurement_file(os.path.join(args.measurements_folder, row.instance + args.measurement_suffix)), axis=1)
    # write back
    df.to_csv(args.results_file, index=False)
