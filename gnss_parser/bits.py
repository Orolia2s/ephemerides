from enum import Enum

class Ordering(Enum):
    msb_first = 0
    lsb_first = 1

class BitReaderMsbFirst:

    def __init__(self, words: bytes, data_bits: range):
        self.data = words
        self.range = range(data_bits[0], data_bits[1])

    def __iter__(self):
        for word in self.data:
            for mask in (1 << shift for shift in range(30 - self.range.start, 30 - self.range.stop, -1)):
                yield bool(word & mask)
