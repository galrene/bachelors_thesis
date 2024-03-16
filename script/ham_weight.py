import csv
import numpy as np

WORKING_DIR = "/home/galrene/school/bakalarka/RDS_git/basys3/sw/debug/traces/test100"
HEX_CSV_PATH = f"{WORKING_DIR}/sensor_traces_0k.csv"
HAMM_CSV_PATH = f"{WORKING_DIR}/hamm_weights.csv"

# calculate the hamming weight of a hexadecimal number
def hamm_weight(hex_num : str) -> int:
    return bin(int(hex_num, 16)).count("1")

# read a csv file with hexadecimal numbers, calculate the hamming weight for each number and write the result to a new csv file
def csv_to_ham(outfile: str, infile: str):
    with open(infile, "r") as ifile:
        reader = csv.reader(ifile, lineterminator="\n")
        with open(outfile, "w") as ofile:
            writer = csv.writer(ofile, lineterminator="\n")
            for row in reader:
                writer.writerow ( [ hamm_weight(item) for item in row ] )

# hexnum = "09d4e8d5fffd3fb73fab97dfd863b9fd"
# print(hamm_weight(hexnum))

csv_to_ham(HAMM_CSV_PATH, HEX_CSV_PATH)