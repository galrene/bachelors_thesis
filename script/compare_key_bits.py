

real_key = "7D 26 6A EC B1 53 B4 D5 D6 B1 71 A5 81 36 60 5B"
found_key_hwb = "7B F2 9A 9D 91 E9 44 D5 26 AA A5 9B 82 31 CE 45"
found_key_150k = "7B 03 A3 EC 91 6B DF D5 9D AA DA 36 82 31 CE 45"
found_key_110k = "6E 4B 54 18 5B 61 B4 DA 95 80 7A E3 C4 39 74 C8"

bin_real = ''.join(format(int(byte, 16), '08b') for byte in real_key.split())
bin_found = ''.join(format(int(byte, 16), '08b') for byte in found_key_hwb.split())

print(bin_real)
print(bin_found)

match_cnt = 0

for i in range(len(bin_real)):
    if bin_real[i] == bin_found[i]:
        match_cnt += 1

print(f"Matched bits: {match_cnt}")