"""
Ublox-specific
"""

from more_itertools import grouper

from gnss_parser import (Constellation, xor_bits, SingleWordBitReaderMsb,
                         keep_lsb, append_lsb, discard_lsb)

message_from_ublox = {
    (Constellation.GPS, 0): 'LNAV-L',   # L1 C/A (Coarse Acquisition)
    (Constellation.BeiDou, 0): 'D1',    # B1I D1
    #(Constellation.BeiDou, 2): 'D1',    # B2I D1
    (Constellation.Galileo, 3): 'FNAV', # E5aI
    (Constellation.GLONASS, 0): 'L1OF', # L1
    #(Constellation.GLONASS, 2): 'L1OF', # L2
}

def little_endian_32(byte_array: bytes) -> list[int]:
    """
    Converts an array of bytes into an array of 32bits integers,
    considering they were represented as little endian.
    """
    return [int.from_bytes(four, 'little')
            for four in grouper(byte_array, 4, incomplete = 'strict')]

def parity_LNAVL(byte_array: bytes) -> int:
    """
    Hamming Code (32, 26)

    While the parity algorithm is GPS specific, the fact that words are given as
    32-bits little-endian integers with 2 bits of padding is ublox-specific.
    The 2 MSBs are not zero, they are the 2 LSBs of the last word.
    Also, the 24 data bits require no inversion, it has already been done by ublox.
    """
    words = little_endian_32(byte_array)
    total = 0
    previous_29 = 0
    previous_30 = 0
    for word in words:
        b25 = (word & (0b111011000111110011010010 << 6)) | previous_29
        b26 = (word & (0b011101100011111001101001 << 6)) | previous_30
        b27 = (word & (0b101110110001111100110100 << 6)) | previous_29
        b28 = (word & (0b010111011000111110011010 << 6)) | previous_30
        b29 = (word & (0b101011101100011111001101 << 6)) | previous_30
        b30 = (word & (0b001011011110101000100111 << 6)) | previous_29
        parity = sum(xor_bits(t) << p for p, t in enumerate([b30, b29, b28, b27, b26, b25]))
        ublox_parity = keep_lsb(6, word)
        if previous_30:
            ublox_parity = keep_lsb(6, ~ublox_parity)
        if parity != ublox_parity:
            raise Exception(f'Wrong parity: {parity:06b} vs {ublox_parity:06b}')
        previous_30 = keep_lsb(1, parity)
        previous_29 = keep_lsb(1, discard_lsb(1, parity))
        # 24 information bits, 6 parity bits
        total = append_lsb(24, discard_lsb(6, word), total)
    return SingleWordBitReaderMsb(total, 10 * 24)

def extract_data_D1(byte_array: bytes) -> int:
    """
    BeiDou D1
    """
    words = little_endian_32(byte_array)
    # First word: 26 information bits, 4 parity bits
    total = keep_lsb(26, discard_lsb(4, words[0]))
    # words 2-10: 22 information bits, 8 parity bits
    for word in words[1:]:
        total = append_lsb(22, discard_lsb(8, word), total)
    return SingleWordBitReaderMsb(total, 26 + 9 * 22)

def extract_data_FNAV(byte_array: bytes) -> int:
    """
    Galileo F-band message
    """
    words = little_endian_32(byte_array)
    total = 0
    # 6 first words in full
    for word in words[:6]:
        total = append_lsb(32, word, total)
    # 7th word: 22 information bits, 10 parity bits
    total = append_lsb(22, discard_lsb(10, words[6]), total)
    return SingleWordBitReaderMsb(total, 214)

def extract_data_GLONASS(byte_array: bytes) -> int:
    """
    GLONASS L1 or L2 OC
    """
    words = little_endian_32(byte_array)
    total = 0
    # 2 words in full
    for word in words[:2]:
        total = append_lsb(32, word, total)
    # 3rd word: 13 information bits, 8 parity bits and 11 padding bits
    total = append_lsb(13, discard_lsb(8 + 11, words[2]), total)
    return SingleWordBitReaderMsb(total, 77)

reader_from_ublox = {
    'LNAV-L': parity_LNAVL,
    'D1': extract_data_D1,
    'FNAV': extract_data_FNAV,
    'L1OF': extract_data_GLONASS,
}
