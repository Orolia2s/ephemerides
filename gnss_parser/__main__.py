"""
Executed when using this module as a program.

To do so :
python -m gnss_parser

"""

import argparse
import logging
import sys
import yaml

from serial import Serial
from pyubx2 import UBXReader

from gnss_parser import Constellation
from gnss_parser.formats import GnssFormatHandler

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(prog = 'Ephemerides',
        description = 'Parse yaml ICD files, to generate code or parse ublox stream',
        epilog = 'Orolia 2S')
    group = cli_parser.add_mutually_exclusive_group(required = True)
    group.add_argument('-f', '--file', type = str,
                       help = 'a file to parse as ublox stream')
    group.add_argument('-s', '--serial', type = str,
                       help = 'the serial port to listen to')
    group.add_argument('-o', '--output', choices = ['md'],
                       help = 'Instead of parsing, generate to sdtin in the language provided')
    cli_parser.add_argument('files', metavar = 'FILE', type = str, nargs = '+',
                            help = 'a yaml file to process')
    cli_parser.add_argument('-v', '--verbose', action='store_true')
    cli_args = cli_parser.parse_args()

    logging.basicConfig(level = logging.DEBUG if cli_args.verbose else logging.INFO)
    logging.info('Starting Ephemerides Generator with arguments: %s', str(cli_args))

    handler = GnssFormatHandler()

    # Parse ICDs to define formats
    for file_name in cli_args.files:
        try:
            with open(file_name, encoding='utf8') as f:
                handler.parse_icd(yaml.safe_load(f))
        except Exception as err:
            logging.exception(err)

    # Generate documentation / code from ICDs
    if cli_args.output:
        generate = {'md': format_to_markdown}[cli_args.output]
        for name, format in formats.items():
            print(generate(format))
        sys.exit(0)

    # Read ublox stream using formats
    if cli_args.serial:
        stream = Serial(cli_args.serial, 115200, timeout = 3)
    else:
        stream = open(cli_args.file, 'rb', encoding='utf8')
    reader = UBXReader(stream, protfilter = 2)
    for _, ublox_message in reader:
        if ublox_message.identity != 'RXM-SFRBX':
            continue
        print(ublox_message)
