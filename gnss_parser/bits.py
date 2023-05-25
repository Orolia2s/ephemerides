from enum import Enum

def xor_bits(n: int):
    """
    Apply an exclusive or on all bits of the number.
    The result is 1 if the number of 'on' bits is odd, else it is 0
    """
    return n.bit_count() & 1

class Ordering(Enum):
    msb_first = 0
    lsb_first = 1

class BitReaderMsbFirst:

    def __init__(self, words: bytes, data_bits: range):
        self.data = words
        self.range = range(data_bits[0], data_bits[1])
        self.count = 0
        self.iter = iter(self)

    def __iter__(self):
        for word in self.data:
            for mask in (1 << shift for shift in range(30 - self.range.start, 30 - self.range.stop, -1)):
                self.count += 1
                yield bool(word & mask)

    def read(self, count: int) -> int:
        result = 0
        for _, b in zip(range(count), self.iter):
            result <<= 1
            result += b
        return result
