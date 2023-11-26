import os

import numpy as np


class Measurement:
    def __init__(self, plaintext: str, ciphertext: str, trace: str):
        self.plaintext_path = plaintext
        self.ciphertext_path = ciphertext
        self.trace_path = trace
        self.trace_length = self.get_trace_length()

    def get_trace_length(self) -> int:
        """
        Returns length of each trace by dividing the size of the binary file
        by the amount of measurements.
        """
        trace_size = self.get_file_size(self.trace_path)
        with open(self.plaintext_path, 'r') as file:
            pt_line_count = sum(1 for _ in file)
        if trace_size % pt_line_count != 0:
            raise ValueError("Binary data size is not a multiple of PT line count")
        return trace_size // pt_line_count

    def get_file_size(self, file_path: str) -> int:
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


def main():
    knownKeyMeasurement = Measurement(
        plaintext='cpa/plaintext-00112233445566778899aabbccddeeff.txt',
        ciphertext='cpa/ciphertext-00112233445566778899aabbccddeeff.txt',
        trace='cpa/traces-00112233445566778899aabbccddeeff.bin'
    )
    unknownKeyMeasurement = Measurement(
        plaintext='cpa/plaintext-unknown_key.txt',
        ciphertext='cpa/ciphertext-unknown_key.txt',
        trace='cpa/traces-unknown_key.bin'
    )

    # Create a NumPy array
    matrix = np.frombuffer(binary_data, dtype=np.int8).reshape(-1, elements_per_row)

    print(matrix)


if __name__ == "__main__":
    main()
