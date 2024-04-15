from time import time
from typing import List, Tuple
import os

import numpy as np
from Crypto.Cipher import AES
from colorama import Fore, Style

from measurement import Measurement

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

def build_hypothesis(measurement: Measurement, byte_idx: int) -> np.ndarray:
    """
    Build a hypothesis matrix for a single byte of the key. Using a single byte of all measured plaintexts.
    p[i] = i-th measured plaintext
    k[j] = j-th possible key byte
    H[i,j] = sbpx[ p[i] xor k[j] ]
    """
    # Load plaintext column
    pt_col = np.loadtxt(measurement.plaintext_path, usecols=byte_idx, converters=hex_to_int, dtype=np.uint8)

    # pt_length = 16  # Bytes
    # bin_file_path = os.path.join(os.path.split(measurement.plaintext_path)[0], "plaintexts.bin")
    # # check if conversion script text output matches sensor binary output
    # if os.path.exists(bin_file_path):
    #     pt_col_from_bin = np.fromfile(bin_file_path, dtype=np.uint8).reshape(-1, pt_length)[:, byte_idx]
    #     assert (pt_col_from_bin == pt_col).all()
    
    # Generate hypothesis matrix
    key_guess = np.arange(256, dtype=np.uint8)
    pt_xor = pt_col[:, np.newaxis] ^ key_guess
    hypothesis_matrix = sbox[pt_xor]

    return hypothesis_matrix

def build_hamming(hypothesis_matrix: np.ndarray) -> np.ndarray:
    """
    Build a hamming weight matrix for a hypothesis matrix.
    """
    hamming_weight_matrix = np.zeros(hypothesis_matrix.shape, dtype=np.uint8)
    for i in range(hypothesis_matrix.shape[0]):
        for j in range(hypothesis_matrix.shape[1]):
            hamming_weight_matrix[i, j] = bin(hypothesis_matrix[i, j]).count("1")
    return hamming_weight_matrix

def correlate(hamming_mtx: np.ndarray, std_traces_mtx: np.ndarray) -> np.ndarray:
    """
    Build a correlation matrix from a hamming weight matrix (a,b) and a standardized traces matrix.
    
    Sizes:
    Hamming     : ( measurement_cnt, 256 )
    Traces      : ( measurement_cnt, trace_len )
    Correlation : ( 256, trace_len )

    Note:
    Standardization partially calculates the correlation matrix ( subtracts the mean and divides by the standard deviation ),
    so speeds up the calculation.
    The second matrix is the traces matrix, which is going to be reused for all key bytes, therefore it is standardized beforehand.
    """
    hamming = ((hamming_mtx - np.mean(hamming_mtx, axis=0)) # standardize hamming matrix
                            / np.std(hamming_mtx, axis=0))
    correlation_matrix = ( hamming.T @ std_traces_mtx ) / hamming.shape[0] # complete the correlation calculation
    correlation_matrix = np.abs(correlation_matrix)
    return correlation_matrix


def find_max(correlation_matrix: np.ndarray):
    """ Returns key byte and trace sample (time of leakage) with the maximum correlation."""
    max_in_flattened = np.argmax(correlation_matrix)
    max_indices = np.unravel_index(max_in_flattened, correlation_matrix.shape)
    return max_indices


def build_traces_mtx(measurement: Measurement) -> np.ndarray:
    # numpy matrix of traces from a binary file
    traces_matrix = (np.fromfile(measurement.trace_path, dtype=np.uint8). # load traces
                     reshape(-1, measurement.trace_length))
    # slice traces matrix to the relevant part
    # traces_matrix = traces_matrix[:, 64:110]
    standardized_traces = ((traces_matrix - np.mean(traces_matrix, axis=0)) # standardize traces to save time
                           / np.std(traces_matrix, axis=0))
    print(f"Traces mtx shape: {standardized_traces.shape}")
    return standardized_traces

def find_idx_in_arr ( arr, key ):
    for i, element in enumerate(arr):
        if element[0] == key:
            return i

def entropy_guess(correlation_matrix, processed_byte_idx, correct_key):
        """
        V korelacnej matici v kazdom riadku (kazdom z odhadov kluca) najdem maximum a index
        riadku na ktorom sa dane maximum nachadza (odhad kluca).
        Tieto maximalne korelacie zoradim zostupne a zistim, kolkaty v poradi je realny kluc, co
        sa tyka vypocitanej korelacie.

        Riadok korelacnej matice je odhad kluca, index maximalnej hodnoty v riadku (index
        stlpca v matici) je moment (cislo traceu) v ktorom sa vyskytla najvyssia korelacia.
        """
        # array containing key guess and its correlation
        key_corr_arr = []
        # for each row of correlation matrix find the maximum value and its index
        for (key_guess, row) in enumerate(correlation_matrix):
            # whole row index is a key guess, index of max value
            # within the row is the moment of the leakage
            max_corr_of_guess = np.max(row)
            key_corr_arr.append([key_guess, max_corr_of_guess])
        # sort by correlations, descending
        key_corr_arr.sort(key=lambda x: x[1], reverse=True)
        place_of_correct_key = find_idx_in_arr(key_corr_arr, correct_key[processed_byte_idx])
        print(f"Correct key place: {place_of_correct_key}/{correlation_matrix.shape[0]}")
        return place_of_correct_key
        

def find_key(measurement: Measurement, key_length_in_bytes,
              timer: bool = False ) -> Tuple[np.ndarray, str]:
    """
    Return the key based on the maximum correlation for each byte of the key.
    """
    
    if timer == True:
        start_time = time()

    standardized_traces = build_traces_mtx(measurement)
    key_arr = np.zeros(key_length_in_bytes, dtype=np.uint8)

    # place of correct key within a sorted array of max correlations
    # for each key guess for given byte. used for entropy calculation
    correct_key_places = []

    for i in range(key_length_in_bytes):
        hamming_weight_matrix = build_hamming(build_hypothesis(measurement, i))
        correlation_matrix = correlate(hamming_weight_matrix, standardized_traces)
        key_byte, tracesample_with_max_corr = find_max(correlation_matrix)
        if measurement.correct_key is not None:
            correct_key_places.append(entropy_guess(correlation_matrix, i, measurement.correct_key))
        print(f"key[{i}]: 0x{key_byte:02X}, sample: {tracesample_with_max_corr}")
        key_arr[i] = key_byte
    
    if timer == True:
        end_time = time()
        print(f"CPA took: {end_time - start_time:0.0f} seconds")
    
    if measurement.correct_key is not None:
        avg = np.mean(correct_key_places)
        print(f"Average place of correct key correlation value within an array of key guesses: {avg:.2f}")

    key_hex_str = ' '.join([hex(i)[2:].zfill(2).upper() for i in key_arr])
    return key_arr, key_hex_str

def verify_key ( measurement: Measurement, key: np.ndarray ) -> bool:
    key_bytes = bytes(key)
    pt = np.loadtxt(measurement.plaintext_path, converters=hex_to_int, dtype=np.uint8)
    ct = np.loadtxt(measurement.ciphertext_path, converters=hex_to_int, dtype=np.uint8)
    pt_bytes = bytes(pt)
    ct_bytes = bytes(ct)

    cipher = AES.new(key_bytes, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pt_bytes)
    
    return ciphertext == ct_bytes

def print_key ( found_key: np.ndarray, real_key: np.ndarray ) -> bool:
    print("Found key: ", end='')
    for byte in range(len(found_key)):
        keybyte_formatted = f"0x{found_key[byte]:02X}"
        if found_key[byte] != real_key[byte]:
            keybyte_formatted = Fore.RED + Style.BRIGHT + f"{keybyte_formatted}" + Style.RESET_ALL
        else:
            keybyte_formatted = Fore.GREEN + Style.BRIGHT + f"{keybyte_formatted}" + Style.RESET_ALL
        print(keybyte_formatted, end=' ')
    print()

def cpa(measurement: Measurement, key_length_in_bytes: int = 16, timer: bool = False) -> bool:
    print(f"\nPerforming CPA using {measurement.cnt} measurements.")
    key_arr, key_hex = find_key(measurement, key_length_in_bytes, timer=True)
    print("========================================================================")
    print_key(key_arr, measurement.correct_key)
    success = verify_key(measurement, key_arr)
    print(f"Encryption success: { Fore.GREEN + str(success) if success == True else Fore.RED + str(success) }")
    print(Style.RESET_ALL)
    
    return success


def main():
    known_key_measurement = Measurement(
        plaintext='../cpa_srcs/plaintext-00112233445566778899aabbccddeeff.txt',
        ciphertext='../cpa_srcs/ciphertext-00112233445566778899aabbccddeeff.txt',
        trace='../cpa_srcs/traces-00112233445566778899aabbccddeeff.bin',
        correct_key=[0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 
                        0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff]
    )

    unknown_key_measurement = Measurement(
        plaintext='../cpa_srcs/plaintext-unknown_key.txt',
        ciphertext='../cpa_srcs/ciphertext-unknown_key.txt',
        trace='../cpa_srcs/traces-unknown_key.bin'
    )
    WORKING_DIR = "../traces"

    rds_150k110k = Measurement(
        plaintext=f'{WORKING_DIR}/test150k110k/plaintexts.txt',
        ciphertext=f'{WORKING_DIR}/test150k110k/ciphertexts.txt',
        trace=f'{WORKING_DIR}/test150k110k/traces.bin',
        correct_key=[0x7D, 0x26, 0x6a, 0xec, 0xb1, 0x53, 0xb4,
                        0xd5, 0xd6, 0xb1, 0x71, 0xa5, 0x81, 0x36, 0x60, 0x5b]
    )


    rds_200k = Measurement(
        plaintext=f'{WORKING_DIR}/test200k_pt03/plaintexts.txt',
        ciphertext=f'{WORKING_DIR}/test200k_pt03/ciphertexts.txt',
        trace=f'{WORKING_DIR}/test200k_pt03/traces.bin',
        correct_key=[0x7D, 0x26, 0x6a, 0xec, 0xb1, 0x53, 0xb4,
                        0xd5, 0xd6, 0xb1, 0x71, 0xa5, 0x81, 0x36, 0x60, 0x5b]
    )

    rds_70k = Measurement(
        plaintext=f'{WORKING_DIR}/test70k_128w/plaintexts.txt',
        ciphertext=f'{WORKING_DIR}/test70k_128w/ciphertexts.txt',
        trace=f'{WORKING_DIR}/test70k_128w/traces.bin',
        correct_key=[0x7D, 0x26, 0x6a, 0xec, 0xb1, 0x53, 0xb4,
                        0xd5, 0xd6, 0xb1, 0x71, 0xa5, 0x81, 0x36, 0x60, 0x5b]
    )


    cpa(rds_200k, timer=True)
 

if __name__ == "__main__":
    main()
