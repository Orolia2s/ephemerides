import argparse
import yaml
import sys
import logging
import traceback

from serial import Serial
from pyubx2 import UBXReader

from gnss_parser import GnssFormat, ensure_fields

def interpret(obj: dict[str]):
    ensure_fields('top level', obj, ['kind'])
    return {'GNSS_format': GnssFormat}[obj['kind']](obj)

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(prog = 'Ephemerides',
                                         description = 'Parse yaml ICD files, to generate code or parse ublox stream',
                                         epilog = 'Orolia 2S')
    group = cli_parser.add_mutually_exclusive_group(required = True)
    group.add_argument('-f', '--file', type = str, help = 'a file to parse as ublox stream')
    group.add_argument('-s', '--serial', type = str, help = 'the serial port to listen to')
    group.add_argument('-o', '--output', choices = ['md'], help = 'Instead of parsing, generate to sdtin in the language provided')
    cli_parser.add_argument('files', metavar = 'FILE', type = str, nargs = '+', help = 'a yaml file to process')
    cli_parser.add_argument('-v', '--verbose', action='store_true')
    cli_args = cli_parser.parse_args()

    logging.basicConfig(level = logging.DEBUG if cli_args.verbose else logging.INFO)
    logging.info(f'Starting Ephemerides Generator with arguments: {cli_args}')

    # Parse ICDs to define formats
    formats = {}
    for file_name in cli_args.files:
        try:
            with open(file_name) as f:
                format_parser = interpret(yaml.safe_load(f))
                formats[format_parser.message] = format_parser
        except Exception as err:
            logging.exception(err)

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
        try:
            formats[message].parse_ublox_subframe()
        except Exception as err:
            logging.exception(err)
            #print(f'Error when parsing message {message} ({constellation}):', err, file = sys.stderr)
