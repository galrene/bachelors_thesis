import numpy as np

def load_binary_file(file_path):
    with open(file_path, 'rb') as binary_file:
        data = binary_file.read()
    return data

def load_trace_length_file(file_path):
    with open(file_path, 'r') as trace_length_file:
        return int(trace_length_file.readline()[1:])  # skip the + character

def main():
    binary_file_path = 'traces-00112233445566778899aabbccddeeff.bin'
    trace_length_file_path = 'traceLength-unknown_key.txt'

    trace_length = load_trace_length_file(trace_length_file_path)
    binary_data = load_binary_file(binary_file_path)
    elements_per_row = len(binary_data) // trace_length

    if len(binary_data) % trace_length != 0:
        raise ValueError("Binary data size is not a multiple of trace length")

    # Create a NumPy array
    matrix = np.frombuffer(binary_data, dtype=np.int8).reshape(-1, elements_per_row)

    print(matrix)


if __name__ == "__main__":
    main()
