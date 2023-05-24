import argparse
import yaml
import sys

from serial import Serial
from pyubx2 import UBXReader

from gnss_parser import GnssFormat, Constellation, ensure_fields

message_from_ublox = {
    (Constellation.GPS, 0): 'LNAV-L', # L1 C/A (Coarse Acquisition)
}

def interpret(obj: dict[str]):
    ensure_fields('top level', obj, ['kind'])
    return {'GNSS_format': GnssFormat}[obj['kind']](obj)

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(description='Parse ICD yaml files')
    group = cli_parser.add_mutually_exclusive_group(required = True)
    group.add_argument('-f', '--file', type = str, help = 'a file to parse as ublox stream')
    group.add_argument('-s', '--serial', type = str, help = 'the serial port to listen to')
    group.add_argument('-o', '--output', choices = ['md'], help = 'Instead of parsing, generate to sdtin in the language provided')
    cli_parser.add_argument('files', metavar = 'FILE', type = str, nargs = '+', help = 'a yaml file to process')
    cli_args = cli_parser.parse_args()

    # Parse ICDs to define formats
    formats = {}
    for file_name in cli_args.files:
        try:
            with open(file_name) as f:
                format_parser = interpret(yaml.safe_load(f))
                formats[format_parser.message] = format_parser
        except Exception as err:
            print(f'Invalid file "{file_name}":', err, file = sys.stderr)

    # Read ublox stream using formats
    if cli_args.output:
        for name, format in formats.items():
            print(format.to_markdown())
        exit(0)
    if cli_args.serial:
        stream = Serial(cli_args.serial, 115200, timeout = 3)
    else:
        stream = open(cli_args.file, 'rb')
    reader = UBXReader(stream, protfilter = 2)
    for _, ublox_message in reader:
        #if not hasattr(ublox_message, 'identity'):
        #    continue
        if ublox_message.identity == 'RXM-SFRBX':
            constellation = Constellation(ublox_message.gnssId)
            message = message_from_ublox.get((constellation, ublox_message.sigId), '(Unsupported)')
            print(constellation, message)
            if message in formats:
                words = [getattr(ublox_message, f'dwrd_{i+1:02}') for i in range(ublox_message.numWords)]
                total = 0
                if message == 'LNAV-L':
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
                        parity = sum((t.bit_count() & 1) << p for p, t in enumerate([b30 | P29,
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
                #try:
                #formats[message].parse_ublox_subframe(ublox_message.payload[8:])
                #except Exception as err:
                #    print(f'Error when parsing message {message} ({constellation}):', err, file = sys.stderr)
