import os

class Measurement:
    """
    Class encapsulating an oscilloscope measurement, it's corresponding plaintext and ciphertext
    for a power analysis attack.
    """
    def __init__(self, plaintext: str, ciphertext: str, trace: str, correct_key: str = None):
        if (not os.path.isfile(plaintext)
                or not os.path.isfile(ciphertext)
                or not os.path.isfile(trace)):
            raise FileNotFoundError(f"The file '{plaintext}' was not found.")
        self.plaintext_path = plaintext
        self.ciphertext_path = ciphertext
        self.trace_path = trace
        self.trace_length = self.get_trace_length()
        self.cnt = self.get_line_count(self.plaintext_path) # number of total measurements
        self.correct_key = correct_key

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
