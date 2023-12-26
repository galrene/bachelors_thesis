import os
import numpy as np
from time import time
"""
TODO:
"""

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
        Returns the amount of non-blank lines in a file.
        """
        with open(file_path, 'r') as file:
            line_count = sum(1 for line in file if line.strip())
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


sbox = np.array([
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
    ], dtype='uint8')

def hypothesis(measurement: Measurement, byte_idx: int) -> np.ndarray:
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
            hypothesis_matrix[i, j] = sbox[pt_col[i] ^ j]
    return hypothesis_matrix

def hamming(hypothesis_matrix: np.ndarray) -> np.ndarray:
    """
    Build a hamming weight matrix for a hypothesis matrix.
    """
    hamming_weight_matrix = np.zeros(hypothesis_matrix.shape, dtype=np.uint8)
    for i in range(hypothesis_matrix.shape[0]):
        for j in range(hypothesis_matrix.shape[1]):
            hamming_weight_matrix[i, j] = bin(hypothesis_matrix[i, j]).count("1")
    return hamming_weight_matrix

def correlate(x, y):
    """
    Correlate all columns from matrix x of shape (a,b)
    with all columns from matrix y of shape (a,c),
    creating correlation matrix C of shape (b,c).

    Originally matlab script by Jiri Bucek in NI-HWB.
    """
    x = x - np.average(x, 0)  # remove vertical averages
    y = y - np.average(y, 0)  # remove vertical averages
    C = x.T @ y  # (n-1) Cov(x,y)
    C = C / (np.sum(x ** 2, 0) ** (1 / 2))[:, np.newaxis]  # divide by (n-1) Var(x)
    C = C / (np.sum(y ** 2, 0) ** (1 / 2))  # divide by (n-1) Var(y)
    return C


def determine_key(correlation_matrix: np.ndarray):
    """
    Returns the key based on the maximum correlation for each byte of the key.
    """
    max_in_flattened = np.argmax(correlation_matrix)
    max_indices = np.unravel_index(max_in_flattened, correlation_matrix.shape)
    # max_indices[0] is the row index, which is the key byte
    return max_indices[0]

def find_key(measurement: Measurement, key_length_in_bytes ) -> (np.ndarray, str):
    """
    Returns the key based on the maximum correlation for each byte of the key.
    """
    traces_matrix = (np.fromfile(measurement.trace_path, dtype=np.uint8).
                     reshape(-1, measurement.trace_length))
    # standardized_traces = ((traces_matrix - np.mean(traces_matrix, axis=0))
    #                        / np.std(traces_matrix, axis=0))
    key = np.zeros(key_length_in_bytes, dtype=np.uint16)
    for i in range(key_length_in_bytes):
        print(f"Calculating key[{i}]")
        hypothesis_matrix = hypothesis(measurement, i)
        hamming_weight_matrix = hamming(hypothesis_matrix)
        # standardized_hamming = ((hamming_weight_matrix - np.mean(hamming_weight_matrix, axis=0))
        #                          / np.std(hamming_weight_matrix, axis=0))
        # correlation_matrix = correlate(standardized_hamming, standardized_traces)
        correlation_matrix = correlate(hamming_weight_matrix, traces_matrix)
        key_byte = determine_key(correlation_matrix)
        print(f"key[{i}]: {hex(key_byte)}")
        key[i] = key_byte
    key_hex = ''.join([hex(i)[2:] for i in key])
    return key, key_hex

def main():
    key_length_in_bytes = 16
    known_key_measurement = Measurement(
        plaintext='cpa/plaintext-00112233445566778899aabbccddeeff.txt',
        ciphertext='cpa/ciphertext-00112233445566778899aabbccddeeff.txt',
        trace='cpa/traces-00112233445566778899aabbccddeeff.bin'
    )

    unknown_key_measurement = Measurement(
        plaintext='cpa/plaintext-unknown_key.txt',
        ciphertext='cpa/ciphertext-unknown_key.txt',
        trace='cpa/traces-unknown_key.bin'
    )
    start_time = time()
    key, key_hex = find_key(known_key_measurement, key_length_in_bytes)
    end_time = time()
    print(f"Key: {key_hex}")
    print(f"CPA took: {end_time - start_time:0.0f} seconds")


if __name__ == "__main__":
    # matrix = np.array([[20,2,13], [4,15,6], [7,28,9]])
    # print(matrix)
    # print(matrix.flatten())
    # max_index = np.argmax(matrix)
    # print("max:\n", matrix.flatten()[max_index])
    # max_index_2d = np.unravel_index(max_index, matrix.shape)
    # print("max 2d:\n", max_index_2d)
    # print("col max:\n", max_index_2d[1])
    main()
