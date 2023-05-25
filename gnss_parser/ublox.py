from gnss_parser import GnssFormat, Constellation, ensure_fields

message_from_ublox = {
    (Constellation.GPS, 0): 'LNAV-L', # L1 C/A (Coarse Acquisition)
}

def parity_LNAVL(words: bytes) -> int:
    P29 = 0
    P30 = 0
    for word in words:
        print(f'{word:032b}')
        if P30:
            word = ~word & 0xffffffff
        print(f'{word:032b}')
        b25 = word & (0b111011000111110011010010 << 6)
        b26 = word & (0b011101100011111001101001 << 6)
        b27 = word & (0b101110110001111100110100 << 6)
        b28 = word & (0b010111011000111110011010 << 6)
        b29 = word & (0b101011101100011111001101 << 6)
        b30 = word & (0b001011011110101000100111 << 6)
        parity = sum((xor_bits(t) << p for p, t in enumerate([b30 | P29,
                                                              b29 | P30,
                                                              b28 | P30,
                                                              b27 | P29,
                                                              b26 | P30,
                                                              b25 | P29]))
        print(f'{parity: 32b}')
        P30 = parity & 1
        P29 = (parity & 2) >> 1
        total <<= 24
        total += (word >> 6) & 0xFFFFFF
    print(f'{total:060x}')


reader_from_ublox = {
}
