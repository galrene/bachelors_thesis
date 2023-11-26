import os

import numpy as np


class Measurement:
    """
    Class encapsulating an oscilloscope measurement, it's corresponding plaintext and ciphertext
    for a power analysis attack.
    """

    def __init__(self, plaintext: str, ciphertext: str, trace: str):
        if (not os.path.isfile(plaintext)
                or not os.path.isfile(ciphertext)
                or not os.path.isfile(trace)):
            raise FileNotFoundError(f"The file '{plaintext}' was not found.")
        self.plaintext_path = plaintext
        self.ciphertext_path = ciphertext
        self.trace_path = trace
        self.trace_length = self.get_trace_length()
        self.cnt = self.get_line_count(self.plaintext_path) # number of total measurements

    def get_trace_length(self) -> int:
        """
        Returns length of each trace by dividing the size of the binary file
        by the amount of measurements.
        """
        trace_size = self.get_file_size(self.trace_path)
        pt_line_count = self.get_line_count(self.plaintext_path)
        if trace_size % pt_line_count != 0:
            print(f"Trace size: {trace_size}\nPT line count: {pt_line_count}")
            raise ValueError("Binary data size is not a multiple of PT line count")
        return trace_size // pt_line_count

    def get_line_count(self, file_path: str) -> int:
        """
        Returns the amount of lines in a file.
        """
        with open(file_path, 'r') as file:
            line_count = sum(1 for _ in file)
        return line_count

    def get_file_size(self, file_path: str) -> int:
        try:
            size = os.path.getsize(file_path)
            return size
        except FileNotFoundError:
            print(f"The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

def hex_to_int(hex_str: str) -> int:
    return int(hex_str, 16)

def build_hypothesis_matrix_for_byte(measurement: Measurement, byte_idx: int) -> np.ndarray:
    """
    Build a hypothesis matrix for a single byte of the key. Using a single byte of all measured plaintexts.
    p[i] = i-th measured plaintext
    k[j] = j-th possible key byte
    H[i,j] = p[i] xor k[j]
    """
    # noinspection PyTypeChecker
    pt_col = np.loadtxt(measurement.plaintext_path, usecols=byte_idx, converters=hex_to_int, dtype=np.uint8)
    hypothesis_matrix = np.zeros((measurement.cnt, 256), dtype=np.uint8)
    assert pt_col.size == measurement.cnt  # check if the pt[byte_idx] column is as long as the number of measurements

    for i in range(measurement.cnt):
        for j in range(256):
            hypothesis_matrix[i, j] = pt_col[i] ^ j
    return hypothesis_matrix

def build_hamming_weight_matrix(hypothesis_matrix: np.ndarray) -> np.ndarray:
    """
    Build a hamming weight matrix for a hypothesis matrix.
    """
    hamming_weight_matrix = np.zeros(hypothesis_matrix.shape, dtype=np.uint8)
    for i in range(hypothesis_matrix.shape[0]):
        for j in range(hypothesis_matrix.shape[1]):
            hamming_weight_matrix[i, j] = bin(hypothesis_matrix[i, j]).count("1")
    return hamming_weight_matrix

def main():
    unknown_key_measurement = Measurement(
        plaintext='cpa/plaintext-unknown_key.txt',
        ciphertext='cpa/ciphertext-unknown_key.txt',
        trace='cpa/traces-unknown_key.bin'
    )

    traces_matrix = (np.fromfile(unknown_key_measurement.trace_path, dtype=np.uint8).
                     reshape(-1, unknown_key_measurement.trace_length))

    hypothesis_matrix = build_hypothesis_matrix_for_byte(unknown_key_measurement, 0)
    hamming_weight_matrix = build_hamming_weight_matrix(hypothesis_matrix)

    print(hypothesis_matrix)
    print(hamming_weight_matrix)


if __name__ == "__main__":
    main()
