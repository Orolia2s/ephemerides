# Ephemerides Generator

## Ordering

Regardless of the order bits are transmitted from the satellite to the receiver, ublox gives us the subframes as an array of 4-bytes little-endian unsigned integers
(using the 30 lsb of the uint32_t)
