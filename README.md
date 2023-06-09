# Ephemerides Generator

## Generate markdown ICDs

```bash
make
```

## Parse GNSS signals

```bash
make run
```

## Ordering

Regardless of the order bits are transmitted from the satellite to the receiver, ublox gives us the subframes as an array of 4-bytes little-endian unsigned integers
