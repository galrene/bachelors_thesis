import os

import numpy as np
from scipy.signal import correlate2d
"""
TODO:
- verify whether the fast cpa is correct
- finding key is incorrect pretty sure
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

def build_correlation_matrix(hamming_weight_matrix: np.ndarray, traces_matrix: np.ndarray) -> np.ndarray:
    """
    Build a correlation matrix for a hamming weight matrix and a traces matrix.
    """
    correlation_matrix = np.zeros((hamming_weight_matrix.shape[1], traces_matrix.shape[1]), dtype=np.float64)
    for i in range(hamming_weight_matrix.shape[1]):
        for j in range(traces_matrix.shape[1]):
            print(f"Calculating correlation for byte {i} and trace {j}")
            correlation_matrix[i, j] = np.corrcoef(hamming_weight_matrix[:, i], traces_matrix[:, j])[0, 1]
    return correlation_matrix

def build_correlation_matrix_fast_dot(standardized_hamming_weight_matrix: np.ndarray, standardized_traces_matrix: np.ndarray) -> np.ndarray:
    """
    Build a correlation matrix for a hamming weight matrix and a traces matrix.
    Dot je maticove nasobenie.
    """
    correlation_matrix = (np.dot(standardized_hamming_weight_matrix.T, standardized_traces_matrix)
                          / standardized_hamming_weight_matrix.shape[0])
    return correlation_matrix

def build_correlation_matrix_corrcoef_memissue(standardized_hamming_weight_matrix: np.ndarray, standardized_traces_matrix: np.ndarray) -> np.ndarray:
    """
    Build a correlation matrix for a hamming weight matrix and a traces matrix.
    """
    # c_mtx = 256 x trace_length
    correlation_matrix = np.zeros((standardized_hamming_weight_matrix.shape[1], standardized_traces_matrix.shape[1]), dtype=np.float64)
    print("standardized_hamming_weight_matrix.shape: ", standardized_hamming_weight_matrix.shape)
    print("standardized_traces_matrix.shape: ", standardized_traces_matrix.shape)
    correlation_matrix = np.corrcoef(standardized_hamming_weight_matrix, standardized_traces_matrix, rowvar=False)[:256, ::]
    return correlation_matrix

def build_correlation_matrix_corrcoef(standardized_hamming_weight_matrix: np.ndarray, standardized_traces_matrix: np.ndarray, chunk_size: int = 100) -> np.ndarray:
    """
    Build a correlation matrix for a hamming weight matrix and a traces matrix.
    """
    key_len = standardized_hamming_weight_matrix.shape[1]
    trace_len = standardized_traces_matrix.shape[1]

    # Initialize an empty correlation matrix
    correlation_matrix = np.zeros((key_len, trace_len))

    # Calculate correlations column-wise for each chunk
    for i in range(0, trace_len, chunk_size):
        end_idx = min(i + chunk_size, trace_len)
        correlation_matrix[:, i:end_idx] = np.corrcoef(standardized_hamming_weight_matrix, standardized_traces_matrix[:, i:end_idx], rowvar=False)[:key_len, :]

    return correlation_matrix

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
    standardized_traces = ((traces_matrix - np.mean(traces_matrix, axis=0))
                           / np.std(traces_matrix, axis=0))
    key = np.zeros(key_length_in_bytes, dtype=np.uint16)
    for i in range(key_length_in_bytes):
        print(f"Calculating key[{i}]")
        hypothesis_matrix = build_hypothesis_matrix_for_byte(measurement, i)
        hamming_weight_matrix = build_hamming_weight_matrix(hypothesis_matrix)
        standardized_hamming = ((hamming_weight_matrix - np.mean(hamming_weight_matrix, axis=0))
                                 / np.std(hamming_weight_matrix, axis=0))
        correlation_matrix = build_correlation_matrix_corrcoef(standardized_hamming, standardized_traces)
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

    key, key_hex = find_key(known_key_measurement, key_length_in_bytes)
    print(f"Key: {key_hex}")


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
