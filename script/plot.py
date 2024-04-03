#!/usr/bin/env python3
"""
Script for plotting traces from a csv file.
"""
import csv
import sys
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

if (len(sys.argv) < 2):
    print("Not enough arguments: python3 plot.py /path/to/traces.csv [n_traces_to_plot]")
    exit()
if not path.exists(sys.argv[1]):
    print(f"File {sys.argv[1]} does not exist")
    exit()
n_traces = 5
if len(sys.argv) == 3:
    n_traces = int(sys.argv[2])
trace_csv_path = sys.argv[1]

title = path.split(path.split(trace_csv_path)[0])[1]

plot(csv_to_ham(trace_csv_path), title, n_rows=n_traces, cols_from=60, cols_to=200)