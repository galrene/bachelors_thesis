import os

import numpy as np

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

def build_correlation_matrix_fast_dot(hamming_weight_matrix: np.ndarray, traces_matrix: np.ndarray) -> np.ndarray:
    """
    Build a correlation matrix for a hamming weight matrix and a traces matrix.
    """
    # Standardize the Hamming weight matrix and traces matrix
    standardized_hamming = (hamming_weight_matrix - np.mean(hamming_weight_matrix, axis=0)) / np.std(hamming_weight_matrix, axis=0)
    standardized_traces = (traces_matrix - np.mean(traces_matrix, axis=0)) / np.std(traces_matrix, axis=0)

    # Calculate the correlation matrix using vectorized operations
    correlation_matrix = np.dot(standardized_hamming.T, standardized_traces) / hamming_weight_matrix.shape[0]
    return correlation_matrix

def build_correlation_matrix_fast_corrcoef(hamming_weight_matrix: np.ndarray, traces_matrix: np.ndarray) -> np.ndarray:
    """
    Build a correlation matrix for a hamming weight matrix and a traces matrix.
    """
    # Standardize the Hamming weight matrix and traces matrix
    standardized_hamming = (hamming_weight_matrix - np.mean(hamming_weight_matrix, axis=0)) / np.std(hamming_weight_matrix, axis=0)
    standardized_traces = (traces_matrix - np.mean(traces_matrix, axis=0)) / np.std(traces_matrix, axis=0)

    # Calculate the correlation matrix using vectorized operations
    correlation_matrix = np.corrcoef(standardized_hamming.T, standardized_traces.T)[:256, 256:]

    return correlation_matrix

def determine_key (correlation_matrix: np.ndarray) -> np.ndarray:
    """
    Returns the key based on the maximum correlation for each byte of the key.
    """
    max_in_flattened = np.argmax(correlation_matrix)
    return np.unravel_index(max_in_flattened, correlation_matrix.shape)[1]

def find_key(measurement: Measurement, key_length_in_bytes ) -> np.ndarray:
    """
    Returns the key based on the maximum correlation for each byte of the key.
    """
    traces_matrix = (np.fromfile(measurement.trace_path, dtype=np.uint8).
                     reshape(-1, measurement.trace_length))
    key = np.ndarray(key_length_in_bytes)
    for i in range(key_length_in_bytes):
        print(f"Calculating key[{i}]")
        hypothesis_matrix = build_hypothesis_matrix_for_byte(measurement, 0)
        hamming_weight_matrix = build_hamming_weight_matrix(hypothesis_matrix)
        correlation_matrix = build_correlation_matrix_fast_dot(hamming_weight_matrix, traces_matrix)
        key_byte = determine_key(correlation_matrix)
        print(f"key[{i}]: {key_byte}")
        key[i] = key_byte
    return key

def main():
    key_length_in_bytes = 16
    # known_key_measurement = Measurement(
    #     plaintext='cpa/plaintext-00112233445566778899aabbccddeeff.txt',
    #     ciphertext='cpa/ciphertext-00112233445566778899aabbccddeeff.txt',
    #     trace='cpa/traces-00112233445566778899aabbccddeeff.bin'
    # )

    unknown_key_measurement = Measurement(
        plaintext='cpa/plaintext-unknown_key.txt',
        ciphertext='cpa/ciphertext-unknown_key.txt',
        trace='cpa/traces-unknown_key.bin'
    )

    key = find_key(unknown_key_measurement, key_length_in_bytes)
    print(f"Key: {key}")


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
