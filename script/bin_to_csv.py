import os



def bin_to_txt(input_file: str, n_traces: int, n_samples: int, separator: str = ' '):
    output_file = os.path.splitext(input_file)[0]+".txt" 
    print(f"Converting {input_file} to {output_file}...")
    bin_file = open(input_file, 'rb')
    text_file = open(output_file, 'w')
    for i in range(0, n_traces):
        for j in range(0, n_samples):
            text_file.write(str(int.from_bytes(bin_file.read(1), 'little')))
            if j != n_samples-1:
                text_file.write(separator)
        text_file.write('\n')
    text_file.close()
    bin_file.close()

bin_to_txt("../traces/test150k_pt02/traces_cpy.bin", 1000, 256, separator=',')


"""
Binarka traces skonvertovana naspat na csv nedala rovnake hodnoty.
"""
