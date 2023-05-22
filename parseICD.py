import argparse
import yaml
import sys

from enum import Enum
from serial import Serial
from pyubx2 import UBXReader
from astropy.units import Unit
from more_itertools import grouper

def ensure_fields(location: str, obj: dict[str], fields: list[str]):
    for field in fields:
        if not field in obj:
            raise Exception(f'Missing the "{field}" from {location}')

def import_fields(destination, source: dict[str], fields: list[str]):
    for field in fields:
        setattr(destination, field, source.get(field, None))
    extras = source.keys() - set(fields)
    if extras:
        print('Ignored extra fields:', extras, file=sys.stderr)

class Constellation(Enum):
    GPS     = 0
    SBAS    = 1
    Galileo = 2
    BeiDou  = 3
    IMES    = 4
    QZSS    = 5
    GLONASS = 6
    NavIC   = 7

message_from_ublox = {
    (Constellation.GPS, 0): 'LNAV-L', # L1 C/A (Coarse Acquisition)
}

class Ordering(Enum):
    msb_first = 0
    lsb_first = 1

class Field:
    def __init__(self, field: dict[str]):
        ensure_fields('format list element', field, ['bits'])
        import_fields(self, field, ['name', 'bits', 'value', 'latex', 'shift', 'unit'])
        if self.unit:
            self.unit = Unit(self.unit)

    def parse(self, reader, destination):
        value = reader.read(self.bits)
        if self.value and self.value != value:
            print(f'Field "{self.name}" didn\'t have expected value of {self.value}, instead:',
                  value, file=sys.stderr)
        if self.shift:
            value *= 2 ** self.shift
        if self.unit:
            value *= self.unit
        print(f'\t{self.name}: {value}')
        setattr(destination, self.name, value)

    def to_markdown(self):
        cells = ['']
        cells.append(self.name if self.name else '_ignored_')
        cells.append(f'${self.latex}$' if self.latex else '')
        cells.append(str(self.bits))
        cells.append(f'$2^{{{self.shift}}}$' if self.shift else '')
        cells.append(f'${self.unit:latex}$' if self.unit else '')
        return '|'.join(cells + [''])

class Parser:

    def __init__(self, fields: list[dict[str]]):
        self.fields = list(map(Field, fields))
        self.bit_count = sum(f.bits for f in self.fields)

    def parse(self, reader, destination):
        pass

    def to_markdown(self):
        heading = '|'.join(['', 'name', 'notation', 'bits', 'factor', 'unit', ''])
        hline   = '|'.join(['', ':---', ':------:', '---:', ':-----', ':--:', ''])
        return '\n'.join([heading, hline] + [f.to_markdown() for f in self.fields])

    def __call__(self, *args):
        return self.parse(*args)

class BitReaderMsbFirst:

    def __init__(self, words: bytes, data_bits: range):
        self.data = words
        self.range = range(data_bits[0], data_bits[1])

    def __iter__(self):
        for word in self.data:
            for mask in (1 << shift for shift in range(30 - self.range.start, 30 - self.range.stop, -1)):
                yield bool(word & mask)

class GnssFormat:

    def __init__(self, icd: dict[str]):
        ensure_fields('top level', icd, ['header', 'formats', 'metadata', 'order'])
        ensure_fields('metadata', icd['metadata'], ['constellation', 'message'])
        import_fields(self, icd['metadata'], ['constellation', 'message', 'description'])

        self.header = Parser(icd['header'])
        self.order = Ordering[icd['order']]

        frame_count = icd['frame_count']
        self.formats = {}
        for format in icd['formats']:
            ensure_fields('format', format, ['subframe', 'fields'])
            subframe = format['subframe']
            if 'pages' in format:
                pages = set()
                for p in format['pages']:
                    if isinstance(p, list):
                        for page in range(p[0], p[1]):
                            pages.add(page)
                    else:
                        pages.add(p)
                print(f'Found format of subframe {subframe} for pages {pages}', file=sys.stderr)
            else:
                pages = range(frame_count)
                print(f'Found format of subframe {subframe} for all {frame_count} pages', file=sys.stderr)
            parser = Parser(format['fields'])
            for page in pages:
                self.formats[subframe, page] = parser

    def parse_ublox_subframe(self, subframe: bytes):
        words = [int.from_bytes(word, 'little') for word in grouper(subframe, 4)]
        self.reader = {Order.msb_first: BitReaderMsbFirst}[self.order](words)

    def to_markdown(self):
        lines = [f'## {self.constellation} {self.message}\n']
        lines.append(self.description)
        lines.append('\n### Header\n')
        lines.append(f'{self.header.bit_count} bits mapped as follows:\n')
        lines.append(self.header.to_markdown())
        for key, format in self.formats.items():
            lines.append(f'\n### Subframe {key[0]}, pages {key[1]}\n')
            lines.append(format.to_markdown())
        return '\n'.join(lines)

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
    reader = UBXReader(stream, profiler = 3)
    for _, ublox_message in reader:
        if ublox_message.identity == 'RXM-SFRBX':
            constellation = Constellation(ublox_message.gnssId)
            message = message_from_ublox.get((constellation, ublox_message.reserved0), '(Unsupported)')
            print(constellation, message)
            if message in formats:
                try:
                    formats[message].parse_ublox_subframe(ublox_message.payload[8:])
                except Exception as err:
                    print(f'Error when parsing message {message} ({constellation}):', err, file = sys.stderr)
