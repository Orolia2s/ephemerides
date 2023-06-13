"""
Functions and types related to bit manipulation
"""

from enum import Enum
from functools import cache

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

@cache
def lsb(count: int) -> int:
    """
    Creates a mask with the _count_ LSBs on
    """
    if count <= 1:
        return count
    return (lsb(count - 1) << 1) | 1

def keep_lsb(count: int, number: int) -> int:
    """
    Return _number_, only keeping the _count_ LSBs
    """
    return number & lsb(count)

def discard_lsb(count: int, number: int) -> int:
    return number >> count

def append_lsb(count: int, source: int, destination: int) -> int:
    """
    Return _destination_, with the _count_ LSBs of _source_ appended as LSBs
    """
    return (destination << count) | keep_lsb(count, source)

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
