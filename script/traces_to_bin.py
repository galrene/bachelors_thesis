#!/usr/bin/env python3
import csv

def csv_to_bin(outfile: str, infile: str):
    """
    Read a csv file with numbers, write them in binary.
    """
    with open(infile, "r") as ifile:
        reader = csv.reader(ifile, lineterminator="\n")
        with open(outfile, "wb") as ofile:
            for row in reader:
                # write each item in row as a byte
                for item in row:
                    ofile.write(bytes(item))

