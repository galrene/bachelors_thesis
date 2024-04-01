#!/usr/bin/env python3
import csv
from os import path
import pandas as pd
import matplotlib.pyplot as plt

def hamm_weight(hex_num : str) -> int:
    """ Calculate the hamming weight of a hexadecimal number """
    return bin(int(hex_num, 16)).count("1")

def csv_to_ham(infile: str):
    """
    Read a csv file with hexadecimal numbers, calculate the hamming weight
    for each number and write the result to a new csv file
    """
    outfile = path.split(infile)[0] + "/hamm_weights.csv"

    if path.exists(outfile):
        print("Hamming weight csv already exists, not converting...")
        return outfile

    with open(infile, "r") as ifile:
        reader = csv.reader(ifile, lineterminator="\n")
        with open(outfile, "w") as ofile:
            writer = csv.writer(ofile, lineterminator="\n")
            for row in reader:
                writer.writerow ( [ hamm_weight(item) for item in row ] )
    return outfile

def plot ( csv_path, title, n_rows : int = 5, cols_from : int = 0, cols_to : int = 256):
    df = pd.read_csv(csv_path, header=None, nrows=n_rows)
    # Slice the DataFrame to select only the first n columns
    df_slice = df.iloc[:, cols_from:cols_to]
    # Iterate over each row in the sliced DataFrame and plot
    for index, row in df_slice.iterrows():
        plt.plot(row)
    plt.title(title)
    plt.xlabel('trace sample')
    plt.ylabel('measured value')
    plt.grid(True)
    plt.show()


YELLOW_BASYS_TRACE = "/home/galrene/school/bakalarka/RDS_git/basys3/sw/debug/traces/test100_yellowbasys/hamm_weights.csv"
OG_BASYS_TRACE = "/home/galrene/school/bakalarka/RDS_git/basys3/sw/debug/traces/test100_128tracewidth/sensor_traces_0k.csv"
NEWEST_TRACE_128W = "/home/galrene/school/bakalarka/RDS_git/basys3/sw/debug/traces/test70k_128w/sensor_traces_70k.csv"

plot(csv_to_ham(NEWEST_TRACE_128W), "70k Basys_128", n_rows=6, cols_from=60, cols_to=200)