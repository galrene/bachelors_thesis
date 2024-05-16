from time import time
from typing import List, Tuple
import os

import numpy as np
from Crypto.Cipher import AES
from colorama import Fore, Style
from aeskeyschedule import reverse_key_schedule, key_schedule

from measurement import Measurement

def hex_to_int(hex_str: str) -> int:
    return int(hex_str, 16)


SBox = np.array([
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


ShiftRowIndex = np.array([ 0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11 ], dtype=np.uint8)
SBoxInverse = np.array(
            [0x52 ,0x09 ,0x6A ,0xD5 ,0x30 ,0x36 ,0xA5 ,0x38 ,0xBF ,0x40 ,0xA3 ,0x9E ,0x81 ,0xF3 ,0xD7 ,0xFB
            ,0x7C ,0xE3 ,0x39 ,0x82 ,0x9B ,0x2F ,0xFF ,0x87 ,0x34 ,0x8E ,0x43 ,0x44 ,0xC4 ,0xDE ,0xE9 ,0xCB
            ,0x54 ,0x7B ,0x94 ,0x32 ,0xA6 ,0xC2 ,0x23 ,0x3D ,0xEE ,0x4C ,0x95 ,0x0B ,0x42 ,0xFA ,0xC3 ,0x4E
            ,0x08 ,0x2E ,0xA1 ,0x66 ,0x28 ,0xD9 ,0x24 ,0xB2 ,0x76 ,0x5B ,0xA2 ,0x49 ,0x6D ,0x8B ,0xD1 ,0x25
            ,0x72 ,0xF8 ,0xF6 ,0x64 ,0x86 ,0x68 ,0x98 ,0x16 ,0xD4 ,0xA4 ,0x5C ,0xCC ,0x5D ,0x65 ,0xB6 ,0x92
            ,0x6C ,0x70 ,0x48 ,0x50 ,0xFD ,0xED ,0xB9 ,0xDA ,0x5E ,0x15 ,0x46 ,0x57 ,0xA7 ,0x8D ,0x9D ,0x84
            ,0x90 ,0xD8 ,0xAB ,0x00 ,0x8C ,0xBC ,0xD3 ,0x0A ,0xF7 ,0xE4 ,0x58 ,0x05 ,0xB8 ,0xB3 ,0x45 ,0x06
            ,0xD0 ,0x2C ,0x1E ,0x8F ,0xCA ,0x3F ,0x0F ,0x02 ,0xC1 ,0xAF ,0xBD ,0x03 ,0x01 ,0x13 ,0x8A ,0x6B
            ,0x3A ,0x91 ,0x11 ,0x41 ,0x4F ,0x67 ,0xDC ,0xEA ,0x97 ,0xF2 ,0xCF ,0xCE ,0xF0 ,0xB4 ,0xE6 ,0x73
            ,0x96 ,0xAC ,0x74 ,0x22 ,0xE7 ,0xAD ,0x35 ,0x85 ,0xE2 ,0xF9 ,0x37 ,0xE8 ,0x1C ,0x75 ,0xDF ,0x6E
            ,0x47 ,0xF1 ,0x1A ,0x71 ,0x1D ,0x29 ,0xC5 ,0x89 ,0x6F ,0xB7 ,0x62 ,0x0E ,0xAA ,0x18 ,0xBE ,0x1B
            ,0xFC ,0x56 ,0x3E ,0x4B ,0xC6 ,0xD2 ,0x79 ,0x20 ,0x9A ,0xDB ,0xC0 ,0xFE ,0x78 ,0xCD ,0x5A ,0xF4
            ,0x1F ,0xDD ,0xA8 ,0x33 ,0x88 ,0x07 ,0xC7 ,0x31 ,0xB1 ,0x12 ,0x10 ,0x59 ,0x27 ,0x80 ,0xEC ,0x5F
            ,0x60 ,0x51 ,0x7F ,0xA9 ,0x19 ,0xB5 ,0x4A ,0x0D ,0x2D ,0xE5 ,0x7A ,0x9F ,0x93 ,0xC9 ,0x9C ,0xEF
            ,0xA0 ,0xE0 ,0x3B ,0x4D ,0xAE ,0x2A ,0xF5 ,0xB0 ,0xC8 ,0xEB ,0xBB ,0x3C ,0x83 ,0x53 ,0x99 ,0x61
            ,0x17 ,0x2B ,0x04 ,0x7E ,0xBA ,0x77 ,0xD6 ,0x26 ,0xE1 ,0x69 ,0x14 ,0x63 ,0x55 ,0x21 ,0x0C ,0x7D],
            dtype=np.uint8)

def build_hypothesis(measurement: Measurement, byte_idx: int, n_traces: int = 0) -> np.ndarray:
    """
    Build a hypothesis matrix for a single byte of the key by reversing the last round of AES and
    comparing the rounds with the previous one.
    p[i] = i-th measured plaintext
    k[j] = j-th possible key byte
    H[i,j] = sbox[ p[i] xor k[j] ]
    """
    # Load plaintext column
    pt_col = np.loadtxt(measurement.plaintext_path, usecols=byte_idx, converters=hex_to_int, dtype=np.uint8)
    if n_traces != 0:
        pt_col = pt_col[:n_traces]
    # Generate hypothesis matrix
    key_guess = np.arange(256, dtype=np.uint8)
    pt_xor = pt_col[:, np.newaxis] ^ key_guess
    hypothesis_matrix = SBox[pt_xor]

    return hypothesis_matrix

def build_hamming_weight_mtx(hypothesis_matrix: np.ndarray) -> np.ndarray:
    """
    Build a hamming weight matrix for a hypothesis matrix.
    """
    hamming_weight_matrix = np.zeros(hypothesis_matrix.shape, dtype=np.uint8)
    for i in range(hypothesis_matrix.shape[0]):
        for j in range(hypothesis_matrix.shape[1]):
            hamming_weight_matrix[i, j] = bin(hypothesis_matrix[i, j]).count("1")
    return hamming_weight_matrix

def hamm_weight(hex_num : int) -> int:
    """ Calculate the hamming weight of a number """
    return bin(hex_num).count("1")

def hamm_distance(cipher_text_row: np.array, byte_idx: int, keyguess: int):
    """
    Calculate the hamming distance between the AES state register after 9th and after 10th round.
    :param cipher_text_row: 
    :param byte_index: Currently processed byte index within the ciphertext row.
    :param keyguess: Currently guessed key for the given processed byte.
    """
    byte_idx_shifted = ShiftRowIndex[byte_idx]
    state10 = cipher_text_row[byte_idx_shifted]
    
    AddRoundKeyByte = keyguess ^ cipher_text_row[byte_idx]
    state9 = SBoxInverse[ AddRoundKeyByte ]
    
    # hamming_weight of xorred values is their hamming distance
    return hamm_weight ( state9 ^ state10 )

def build_hamm_distance_mtx(ct, n_traces: int, byte_idx: int):
    """
    Kedze budem prehadzovat byty v riadkoch, musim priebezne nacitavat cely riadok ciphertextu,
    kedzto pri utoku na prvy byte mi stacilo prvy element v riadku a teda som to mohol robit rovno
    po stlpcoch.
    """
    mtx = np.zeros((n_traces, 256))
    # ct_row = ct[trace, :] 
    for trace in range(n_traces):
        for keyguess in range(256):
            mtx[trace, keyguess] = hamm_distance(ct[trace, :], byte_idx, keyguess)
    return mtx


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
    print(f"Full traces mtx shape: {standardized_traces.shape}")
    return standardized_traces

def find_idx_in_arr ( arr, key ):
    for i, element in enumerate(arr):
        if element[0] == key:
            return i

def guessing_entropy(correlation_matrix, processed_byte_idx, correct_key):
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
        print(f"Byte guessing entropy: {place_of_correct_key}/{correlation_matrix.shape[0]}")
        return place_of_correct_key
        

def find_key(measurement: Measurement, key_length_in_bytes, n_traces: int = 0,
              attack_mode: str = "lrnd", timer: bool = False ) -> Tuple[np.ndarray, str, int]:
    """
    Return the key and its guessing entropy based on the maximum correlation for each byte of the key.
    """
    if attack_mode not in [ "lrnd", "frnd" ]:
        raise ValueError("Unknown attack mode.")
    
    if timer == True: start_time = time()

    standardized_traces = build_traces_mtx(measurement)
    if n_traces != 0:
        standardized_traces = standardized_traces[:n_traces, :]
    key_arr = np.zeros(key_length_in_bytes, dtype=np.uint8)

    searched_key = measurement.encryption_key
    if attack_mode == "lrnd":
        ct_mtx = np.loadtxt(measurement.ciphertext_path,
                            converters=hex_to_int, dtype=np.uint8)
        if n_traces != 0:
            ct_mtx = ct_mtx[:n_traces, :]
        
        byte_array = key_schedule(bytes(measurement.encryption_key))[10]
        int_list = [int(byte) for byte in byte_array]
        searched_key = np.array(int_list, dtype=np.uint8)                

    # guessing entropies of each subkey byte
    byte_guessing_entropies = []

    for i in range(key_length_in_bytes):
        if attack_mode == "lrnd":
            if n_traces == 0:
                n_traces = measurement.cnt
            hamm_mtx = build_hamm_distance_mtx(ct_mtx, n_traces, i)
        elif attack_mode == "frnd":
            hamm_mtx = build_hamming_weight_mtx(build_hypothesis(measurement, i, n_traces))

        correlation_matrix = correlate(hamm_mtx, standardized_traces)
        key_byte, tracesample_with_max_corr = find_max(correlation_matrix)
        
        # If the real encryption key is known, calculate the guessing entropy
        if measurement.encryption_key is not None:
            byte_guessing_entropies.append(guessing_entropy(correlation_matrix, i, searched_key))
        
        print(f"key[{i}]: 0x{key_byte:02X}, sample: {tracesample_with_max_corr}")
        key_arr[i] = key_byte
    
    if timer == True:
        end_time = time()
        print(f"CPA took: {end_time - start_time:0.0f} seconds")
    
    # If the real encryption key is known, calculate the guessing entropy
    GE = None
    if measurement.encryption_key is not None:
        GE = np.mean(byte_guessing_entropies)
        print(f"Guessing entropy: {GE:.2f}")
    
    key_hex_str = ' '.join([hex(i)[2:].zfill(2).upper() for i in key_arr])
    return key_arr, key_hex_str, GE

def verify_key ( measurement: Measurement, key: np.ndarray ) -> bool:
    key_bytes = bytes(key)
    pt = np.loadtxt(measurement.plaintext_path, converters=hex_to_int, dtype=np.uint8)
    ct = np.loadtxt(measurement.ciphertext_path, converters=hex_to_int, dtype=np.uint8)
    pt_bytes = bytes(pt)
    ct_bytes = bytes(ct)

    cipher = AES.new(key_bytes, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pt_bytes)
    
    return ciphertext == ct_bytes

def red_bg ( text: str ) -> str:
    return Fore.RED + Style.BRIGHT + text + Style.RESET_ALL

def green_bg ( text: str ) -> str:
    return Fore.GREEN + Style.BRIGHT + text + Style.RESET_ALL

def print_key ( found_key: np.ndarray, real_key: np.ndarray = None ) -> bool:
    # the initial encryption key
    print("Found key: ", end='')
    # if real_key is not provided, print only the found key
    if real_key is None:
        print(' '.join([f"0x{byte:02X}" for byte in found_key]))
        return
    for byte in range(len(found_key)):
        keybyte_formatted = f"0x{found_key[byte]:02X}"
        print(
               green_bg(keybyte_formatted) 
               if found_key[byte] == real_key[byte]
                else red_bg(keybyte_formatted), end=' '
        )
    print()

def enc_key_from_last_round_key ( key_arr: np.array ) -> np.array:
    encryption_key = reverse_key_schedule(bytes(key_arr), 10)
    return np.frombuffer(encryption_key, dtype=np.uint8)

def cpa(measurement: Measurement, n_traces: int = 0, attack_mode: str = "lrnd", timer: bool = False) -> bool:
    """
    Perform correlation power analysis on given measurement.
    :param Measurement measurement: Traces, PTs, CTs
    :param str attack_mode: lrnd for last round attack, frnd for first round attack
    """
    if n_traces == 0:
        n_traces = measurement.cnt

    match attack_mode:
        case "lrnd":
            print(f"\nPerforming last round CPA using {n_traces} measurements.")
            last_round_key_arr, key_hex, ge = find_key(measurement, measurement.key_length, n_traces=n_traces, timer=True, attack_mode="lrnd")
            key_arr = enc_key_from_last_round_key(last_round_key_arr)
        case "frnd":
            print(f"\nPerforming first round CPA using {n_traces} measurements.")
            key_arr, key_hex, ge = find_key(measurement, measurement.key_length, n_traces=n_traces, timer=True, attack_mode="frnd")
        case _:
            raise ValueError("Unknown attack mode.")

    print("==========================================================================================")
    print_key(key_arr, measurement.encryption_key)

    success = verify_key(measurement, key_arr)
    if success == False and attack_mode == "lrnd":
        print("Full last round key wasn't found, even its correct subkeys weren't reversed into correct encryption key subkeys.")
        print("Found last round key: ", " ".join([hex(byte)[2:].upper() for byte in last_round_key_arr]))
    print(f"Attack success: { Fore.GREEN + str(success) if success == True else Fore.RED + str(success) }")
    print(Style.RESET_ALL, end='')
    
    return success, ge

def plot_ge_vs_ntraces ( results: List[Tuple[int, float]], trace_cnt, trace_increment_step ):
    import matplotlib.pyplot as plt
    n_traces, ge = zip(*results)
    plt.plot(n_traces, ge, color='red', linewidth=1)
    plt.xlabel("Number of traces")
    plt.ylabel("Guessing entropy")
    plt.title("Guessing entropy vs number of traces")
    plt.xticks(np.arange(0, trace_cnt+trace_increment_step, trace_increment_step))
    plt.grid(True)
    plt.show()


def main():
    WORKING_DIR = "../traces"

    known_key_measurement = Measurement(
        plaintext=f'{WORKING_DIR}/cpa_srcs/plaintext-00112233445566778899aabbccddeeff.txt',
        ciphertext=f'{WORKING_DIR}/cpa_srcs/ciphertext-00112233445566778899aabbccddeeff.txt',
        trace=f'{WORKING_DIR}/cpa_srcs/traces-00112233445566778899aabbccddeeff.bin',
        encryption_key=[0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 
                        0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff]
    )

    unknown_key_measurement = Measurement(
        plaintext=f'{WORKING_DIR}/cpa_srcs/plaintext-unknown_key.txt',
        ciphertext=f'{WORKING_DIR}/cpa_srcs/ciphertext-unknown_key.txt',
        trace=f'{WORKING_DIR}/cpa_srcs/traces-unknown_key.bin'
    )

    # rds_70k = Measurement(
    #     plaintext=f'{WORKING_DIR}/test70k_128w/plaintexts.txt',
    #     ciphertext=f'{WORKING_DIR}/test70k_128w/ciphertexts.txt',
    #     trace=f'{WORKING_DIR}/test70k_128w/traces.bin',
    #     encryption_key=[0x7D, 0x26, 0x6a, 0xec, 0xb1, 0x53, 0xb4,
    #                     0xd5, 0xd6, 0xb1, 0x71, 0xa5, 0x81, 0x36, 0x60, 0x5b]
    # )
    # rds_20k = Measurement(
    #     plaintext=f'{WORKING_DIR}/test20k_from40k/plaintexts.txt',
    #     ciphertext=f'{WORKING_DIR}/test20k_from40k/ciphertexts.txt',
    #     trace=f'{WORKING_DIR}/test20k_from40k/traces.bin',
    #     encryption_key=[0x7D, 0x26, 0x6a, 0xec, 0xb1, 0x53, 0xb4,
    #                     0xd5, 0xd6, 0xb1, 0x71, 0xa5, 0x81, 0x36, 0x60, 0x5b]
    # )
    #================================================================================================
    # last round attack
    # trace_cnt_and_ge_2500 = [(1000, 81.625), (3500, 50.5), (6000, 19.625), (8500, 8.75),
    #         (11000, 2.3125), (13500, 0.3125), (15000, 0)]

    # trace_cnt_and_ge_500 = [(500, 99.6875), (1000, 81.625), (1500, 76.4375), (2000, 67.875), (2500, 58.625),
    # (3000, 53.5), (3500, 50.5), (4000, 35.9375), (4500, 31.5625), (5000, 22.75), (5500, 18.1875),
    # (6000, 19.625), (6500, 18.6875), (7000, 15.8125), (7500, 14.375), (8000, 7.25), (8500, 8.75),
    # (9000, 6.4375), (9500, 4.0625), (10000, 3.3125), (10500, 3.375), (11000, 2.3125),
    # (11500, 1.1875), (12000, 0.625), (12500, 0.6875), (13000, 0.375), (13500, 0.3125),
    # (14000, 0.25), (14500, 0.0625), (15000, 0.0)]
    #================================================================================================
    # first round attack
    # trace_cnt_and_ge_500frnd = [(500, 133.9375), (1000, 113.9375), (1500, 153.1875), (2000, 134.25),
    #  (2500, 139.5), (3000, 143.375), (3500, 155.75), (4000, 149.1875), (4500, 143.1875),
    #  (5000, 144.3125), (5500, 134.125), (6000, 134.25), (6500, 131.75), (7000, 125.4375), 
    #  (7500, 119.9375), (8000, 119.625), (8500, 124.625), (9000, 123.625), (9500, 116.625), 
    #  (10000, 113.25), (10500, 120.25), (11000, 113.1875), (11500, 105.1875), (12000, 103.6875),
    #  (12500, 90.125), (13000, 97.25), (13500, 100.375), (14000, 97.6875), (14500, 96.3125),
    #  (15000, 98.9375), (15500, 98.0625), (16000, 102.5625), (16500, 105.125), (17000, 107.8125),
    #  (17500, 109.9375), (18000, 104.3125), (18500, 97.875), (19000, 98.4375), (19500, 90.9375), 
    #  (20000, 90.4375), (20500, 86.125), (21000, 86.625), (21500, 87.9375), (22000, 85.8125), 
    #  (22500, 85.5625), (23000, 85.6875), (23500, 80.1875), (24000, 80.75), (24500, 76.6875), 
    #  (25000, 75.6875), (25500, 76.25), (26000, 85.25), (26500, 84.875), (27000, 83.8125),
    #  (27500, 89.5625), (28000, 90.6875), (28500, 95.6875), (29000, 92.875), (29500, 91.3125), 
    #  (30000, 101.3125), (30500, 101.8125), (31000, 97.0625), (31500, 94.4375), (32000, 98.1875), 
    #  (32500, 101.4375), (33000, 102.5), (33500, 105.625), (34000, 105.875), (34500, 96.875), 
    #  (35000, 97.5625), (35500, 97.4375), (36000, 90.3125), (36500, 88.625), (37000, 84.375), 
    #  (37500, 83.6875), (38000, 80.8125), (38500, 86.0), (39000, 86.3125), (39500, 89.75), 
    #  (40000, 82.5)]
    # rds_40k = Measurement(
    #     plaintext=f'{WORKING_DIR}/test40k/plaintexts.txt',
    #     ciphertext=f'{WORKING_DIR}/test40k/ciphertexts.txt',
    #     trace=f'{WORKING_DIR}/test40k/traces.bin',
    #     encryption_key=[0x7D, 0x26, 0x6a, 0xec, 0xb1, 0x53, 0xb4,
    #                     0xd5, 0xd6, 0xb1, 0x71, 0xa5, 0x81, 0x36, 0x60, 0x5b]
    # )
    #================================================================================================
    #trace_cnt_and_ge_100kfrnd= [(5000, 130.25), (10000, 125.0625), (15000, 118.1875), (20000, 116.0625), (25000, 82.9375), (30000, 99.125), (35000, 104.625), (40000, 99.25), (45000, 95.25), (50000, 95.6875), (55000, 86.9375), (60000, 72.125), (65000, 76.375), (70000, 74.0), (75000, 63.75), (80000, 53.75), (85000, 65.8125), (90000, 67.25), (95000, 68.5), (100000, 78.375)]
    #trace_cnt_and_ge_150kfrnd[(10000, 125.0625), (20000, 116.0625), (30000, 99.125), (40000, 99.25), (50000, 95.6875), (60000, 72.125), (70000, 74.0), (80000, 53.75), (90000, 67.25), (100000, 78.375), (110000, 66.25), (120000, 66.625), (130000, 62.6875), (140000, 58.0), (150000, 56.0)]
    rds_150k = Measurement(
        plaintext=f'{WORKING_DIR}/test150k_pt02_01/plaintexts.txt',
        ciphertext=f'{WORKING_DIR}/test150k_pt02_01/ciphertexts.txt',
        trace=f'{WORKING_DIR}/test150k_pt02_01/traces.bin',
        encryption_key=[0x7D, 0x26, 0x6a, 0xec, 0xb1, 0x53, 0xb4,
                        0xd5, 0xd6, 0xb1, 0x71, 0xa5, 0x81, 0x36, 0x60, 0x5b]
    )
    
    trace_cnt_and_ge = []
    trace_increment_step = 10000
    measurement = rds_150k
    trace_cnt = 150000
    attack_mode = "frnd"

    for i in range(trace_increment_step, trace_cnt+trace_increment_step, trace_increment_step):
        _, ge = cpa(measurement, n_traces=i, timer=True, attack_mode=attack_mode)
        trace_cnt_and_ge.append( (i, ge) )
        print(trace_cnt_and_ge)
    
    print("Array of results with n_traces and guessing entropy:")
    plot_ge_vs_ntraces(trace_cnt_and_ge, trace_cnt, trace_increment_step)

if __name__ == "__main__":
    main()
