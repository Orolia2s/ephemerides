"""
Functions and types related to bit manipulation
"""

from enum import Enum

def twos_complement(integer: int, bits: int) -> int:
    """
    Apply 2s complement with the specified amount of bits
    """
    sign_bit = 1 << (bits - 1)
    if integer & sign_bit:
        return integer - (1 << bits)
    return integer

def xor_bits(integer: int):
    """
    Apply an exclusive or on all bits of the number.
    The result is 1 if the number of 'on' bits is odd, else it is 0
    """
    return integer.bit_count() & 1

class Ordering(Enum):
    """
    The order of the fields listed in the yaml
    """
    msb_first = 0
    lsb_first = 1

complementary_half = {'msb': 'lsb', 'lsb': 'msb'}

class BitReader:
    """
    Abstract class
    """

    iter = None

    def read(self, count: int) -> int:
        """
        Read a field of the specified width
        """
        result = 0
        for _, bit in zip(range(count), self.iter):
            result <<= 1
            result += bit
        return result

class SingleWordBitReaderMsb(BitReader):
    """
    A single integer containing all the bits
    """

    def __init__(self, word: int, size: int):
        self.data = word
        self.count = 0
        self.size = size
        self.iter = iter(self)

    def __iter__(self):
        for mask in (1 << i for i in range(self.size - 1, -1, -1)):
            self.count += 1
            yield bool(self.data & mask)

'''
class WordArrayBitReaderMsbFirst(BitReader):

    def __init__(self, words: bytes, data_bits: range):
        self.data = words
        self.range = range(data_bits[0], data_bits[1])
        self.count = 0
        self.iter = iter(self)

    def __iter__(self):
        for word in self.data:
            for mask in (1 << shift for shift in range(29 - self.range.start, 29 - self.range.stop, -1)):
                self.count += 1
                yield bool(word & mask)
'''
