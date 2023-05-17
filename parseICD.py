import argparse
import yaml
import sys

from enum import Enum
from serial import Serial
from pyubx2 import UBXReader

def ensure_fields(location: str, obj: dict[str], fields: list[str]):
    for field in fields:
        if not field in obj:
            raise Exception(f'Missing the "{field}" from {location}')

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
    (Constellation.GPS, 0): 'LNAV', # L1 C/A (Coarse Acquisition)
}

'''
class Field:
    def __init__(self, field: dict[str]):
        ensure_fields('format list element', field, ['name', 'bits'])
        self.name = field['name']
        self.bits = field['bits']

class Parser:

    def __init__(self, fields: list[dict[str]]):
        self.fields = map(Field, fields)
        self.bit_count = sum(self.fields, key=lambda x: x.bits)

    def parse(self, data: bytes):


    def __call__(self, *args):
        return self.parse(*args)
'''

class GnssFormat:

    def __init__(self, icd: dict[str]):
        ensure_fields('top level', icd, ['header', 'formats', 'metadata', 'order'])
        ensure_fields('metadata', icd['metadata'], ['constellation', 'message'])
        self.message = icd['metadata']['message']
        self.constellation = icd['metadata']['constellation']

    def parse_ublox_sfrbx_words(self, sfrbx: bytes):
        pass

def interpret(obj: dict[str]):
    ensure_fields('top level', obj, ['kind'])
    return {'GNSS_format': GnssFormat}[obj['kind']](obj)

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(description='Parse ICD yaml files')
    group = cli_parser.add_mutually_exclusive_group(required = True)
    group.add_argument('-f', '--file', type = str, help = 'a file to parse as ublox stream')
    group.add_argument('-s', '--serial', type = str, help = 'the serial port to listen to')
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
            print(f'Invalid file "{icd}":', err, file = sys.stderr)

    # Read ublox stream using formats
    if cli_args.serial != None:
        stream = Serial(cli_args.serial, 115200, timeout = 3)
    else:
        stream = open(cli_args.file, 'rb')
    reader = UBXReader(stream, profiler = 3)
    for raw, ublox_message in reader:
        if ublox_message.identity == 'RXM-SFRBX':
            constellation = Constellation(ublox_message.gnssId)
            message = message_from_ublox.get((constellation, ublox_message.reserved0), '(Unsupported)')
            print(constellation, message)
            if message in formats:
                formats[message].parse_ublox_sfrbx_words(raw[14:])
