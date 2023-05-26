"""
Ublox-specific
"""

import logging

from more_itertools import grouper

from gnss_parser import Constellation, xor_bits, SingleWordBitReaderMsb

message_from_ublox = {
    (Constellation.GPS, 0): 'LNAV-L', # L1 C/A (Coarse Acquisition)
}

def parity_LNAVL(byte_array: bytes) -> int:
    """
    Hamming Code (32, 26)
    """
    words = [int.from_bytes(four, 'little') for four in grouper(byte_array, 4, incomplete = 'strict')]
    total = 0
    p29 = 0
    p30 = 0
    for word in words:
        if p30:
            word = ~word & 0xffffffff
        b25 = word & (0b111011000111110011010010 << 6)
        b26 = word & (0b011101100011111001101001 << 6)
        b27 = word & (0b101110110001111100110100 << 6)
        b28 = word & (0b010111011000111110011010 << 6)
        b29 = word & (0b101011101100011111001101 << 6)
        b30 = word & (0b001011011110101000100111 << 6)
        if p29:
            b25 |= 1
            b27 |= 1
            b30 |= 1
        if p30:
            b26 |= 1
            b28 |= 1
            b29 |= 1
        parity = sum(xor_bits(t) << p for p, t in enumerate([b30, b29, b28, b27, b26, b25]))
        if parity != word & 0x3F:
            logging.warning(f'Wrong parity: {parity:06b} vs {word & 0x3f:06b}')
        p30 = word & 1
        p29 = (word & 2) >> 1
        total <<= 24
        total += (word >> 6) & 0xFFFFFF
    return SingleWordBitReaderMsb(total, 240)

reader_from_ublox = {
    'LNAV-L': parity_LNAVL
}
