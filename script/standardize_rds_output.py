"""
Script that converts RDS sensor output to a standard format

Outputs:
- ciphertext, plaintext, key as a .txt file with hex values separated by spaces
- traces as a .bin file with 8-bit unsigned integers
"""

import csv
import sys
import os

DEFAULT_CIPHERTEXT_NAME = "ciphertexts.bin"
DEFAULT_PLAINTEXT_NAME = "plaintexts.bin"
DEFAULT_KEY_NAME = "keys.bin"
DEFAULT_TRACES_PART_OF_NAME = "sensor_traces"

def hamm_weight(hex_num : str) -> int:
    """ Calculate the hamming weight of a hexadecimal number """
    return bin(int(hex_num, 16)).count("1")

def csv_to_bin(infile: str):
    """
    Read a csv file with hexadecimal numbers, get their hamming weight, 
    convert the hamming weight to binary and write result to a binary file
    """
    outfile = os.path.split(infile)[0]+"/traces.bin"
    print(f"Converting {infile} to {outfile}...")
    with open(infile, "r") as ifile:
        reader = csv.reader(ifile, lineterminator="\n")
        with open(outfile, "wb") as ofile:
            for row in reader:
                # calculate hamming weight of each number in row and convert it to binary, then write is as a byte
                for item in row:
                    ofile.write(bytes([hamm_weight(item)]))

def bin_to_txt(input_file: str, n_traces: int):
    output_file = os.path.splitext(input_file)[0]+".txt" 
    print(f"Converting {input_file} to {output_file}...")
    bin_file = open(input_file, 'rb')
    text_file = open(output_file, 'w')
    for i in range(0, n_traces):
        for j in range(0, 16):
            text_file.write(str(bin_file.read(1).hex().upper()))
            text_file.write(' ')
        text_file.write('\n')
    text_file.close()
    bin_file.close()


def find_trace_file ( traces_dir: str ):
    for file in os.listdir(traces_dir):
        if DEFAULT_TRACES_PART_OF_NAME in file and file.endswith(".csv"):
            return file
    return None

# todo: automatically derive the number of traces from the traces file

def check_files_exist ( traces_dir: str ):
    """
    Check if the necessary files exist in the traces directory
    return the trace file name if it exists, None otherwise.
    """
    if not os.path.isfile(f"{traces_dir}/{DEFAULT_CIPHERTEXT_NAME}"):
        print(f"No {DEFAULT_CIPHERTEXT_NAME} file found in {traces_dir}")
        return None
    if not os.path.isfile(f"{traces_dir}/{DEFAULT_PLAINTEXT_NAME}"):
        print(f"No {DEFAULT_PLAINTEXT_NAME} file found in {traces_dir}")
        return None
    if not os.path.isfile(f"{traces_dir}/{DEFAULT_KEY_NAME}"):
        print(f"No {DEFAULT_KEY_NAME} file found in {traces_dir}")
        return None
    trace_file_name = find_trace_file(traces_dir)
    if trace_file_name is None:
        print(f"No trace file found in {traces_dir}")
        return None
    return trace_file_name

def main():
    if len(sys.argv) != 3:
        print("Not enough arguments: python3 standardize_rds_output.py /path/to/traces_dir n_traces")
        exit()
    traces_dir = sys.argv[1]
    n_traces = int(sys.argv[2])
    if not os.path.exists(traces_dir):
        print(f"Directory {traces_dir} does not exist")
        exit()
    if not os.path.isdir(traces_dir):
        print(f"{traces_dir} is not a directory")
        exit()
    
    trace_file = check_files_exist(traces_dir)
    if trace_file is None:
        print(f"Could not find all necessary files in {traces_dir}")
        exit()

    bin_to_txt(f"{traces_dir}/{DEFAULT_CIPHERTEXT_NAME}", n_traces)
    bin_to_txt(f"{traces_dir}/{DEFAULT_PLAINTEXT_NAME}", n_traces)
    bin_to_txt(f"{traces_dir}/{DEFAULT_KEY_NAME}", n_traces)
    csv_to_bin(f"{traces_dir}/{trace_file}")
    print("Conversion complete.")
    

if __name__ == "__main__":
    main()