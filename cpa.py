import os

import numpy as np


def get_file_size(file_path):
    try:
        size = os.path.getsize(file_path)
        return size
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def load_binary_file(file_path):
    with open(file_path, 'rb') as binary_file:
        data = binary_file.read()
    return data


def load_trace_length_file(file_path):
    with open(file_path, 'r') as trace_length_file:
        return int(trace_length_file.readline()[1:])  # skip the + character


def get_trace_length(bin_file, pt_file):
    """
    bin_file: path to measurement.bin file
    pt_file: path to plaintext file
    Returns length of each trace by dividing the size of the binary file
    by the amount of measurements.
    """
    bin_size = get_file_size(bin_file)
    with open(pt_file, 'r') as file:
        pt_line_count = sum(1 for _ in file)
    if bin_size % pt_line_count != 0:
        raise ValueError("Binary data size is not a multiple of PT line count")
    return bin_size // pt_line_count


def main():
    binary_file_path = 'cpa/traces-00112233445566778899aabbccddeeff.bin'
    pt_file_path = 'cpa/plaintext-00112233445566778899aabbccddeeff.txt'

    trace_length = get_trace_length(binary_file_path, pt_file_path)
    binary_data = load_binary_file(binary_file_path)
    elements_per_row = len(binary_data) // trace_length

    if len(binary_data) % trace_length != 0:
        raise ValueError("Binary data size is not a multiple of trace length")

    # Create a NumPy array
    matrix = np.frombuffer(binary_data, dtype=np.int8).reshape(-1, elements_per_row)

    print(matrix)


if __name__ == "__main__":
    main()
