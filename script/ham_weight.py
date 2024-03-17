import csv
import numpy as np

WORKING_DIR = "/home/galrene/school/bakalarka/cpa_srcs/test_40k"

def hamm_weight(hex_num : str) -> int:
    """ Calculate the hamming weight of a hexadecimal number """
    return bin(int(hex_num, 16)).count("1")

def csv_to_ham(outfile: str, infile: str):
    """
    Read a csv file with hexadecimal numbers, calculate the hamming weight
    for each number and write the result to a new csv file
    """
    with open(infile, "r") as ifile:
        reader = csv.reader(ifile, lineterminator="\n")
        with open(outfile, "w") as ofile:
            writer = csv.writer(ofile, lineterminator="\n")
            for row in reader:
                writer.writerow ( [ hamm_weight(item) for item in row ] )

def csv_to_bin(outfile: str, infile: str):
    """
    Read a csv file with hexadecimal numbers, get their hamming weight, 
    convert the hamming weight to binary and write result to a binary file
    """
    with open(infile, "r") as ifile:
        reader = csv.reader(ifile, lineterminator="\n")
        with open(outfile, "wb") as ofile:
            for row in reader:
                # calculate hamming weight of each number in row and convert it to binary, then write is as a byte
                for item in row:
                    ofile.write(bytes([hamm_weight(item)]))
                

# hexnum = "09d4e8d5fffd3fb73fab97dfd863b9fd"
# print(hamm_weight(hexnum))

csv_to_ham(f"{WORKING_DIR}/hamm_weights.csv", f"{WORKING_DIR}/sensor_traces_40k.csv")
# csv_to_bin(f"{WORKING_DIR}/hamm_weights.bin", f"{WORKING_DIR}/sensor_traces_40k.csv")