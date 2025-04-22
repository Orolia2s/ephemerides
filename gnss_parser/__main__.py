"""
Executed when using this module as a program.

To do so :
python -m gnss_parser

"""

import argparse
import logging
import sys

import yaml
from pyubx2 import UBXReader
from serial import Serial

from gnss_parser import GnssFormatHandler, accumulate
from gnss_parser.constellations import Constellation
from gnss_parser.generators.markdown import handler_to_markdown
from gnss_parser.generators.zig import handler_to_zig
from gnss_parser.yaml import ensure_fields
from gnss_parser.to_json import format_as_json

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(prog = 'Ephemerides',
        description = 'Read yaml ICD files, to generate code or parse ublox stream',
        epilog = 'Orolia 2S')
    cli_parser.add_argument('-v', '--verbose', action='store_true', help = 'Display debug logs')
    cli_parser.add_argument('-I', '--icd', dest = 'icds', metavar = 'FILE', type = str, action = 'append', required = True, help = 'Provide an input YAML ICD. This option can be specified multiple times')
    subparsers = cli_parser.add_subparsers(required = True, dest = 'subcommand')
    translate = subparsers.add_parser('translate', help = 'Translate the ICDs to a desired format and exit')
    translate.add_argument('format', choices = ('md', 'zig'), help = 'Generate ICDs to stdout in the language provided')
    parse_ubx = subparsers.add_parser('parse', help = 'Parse a stream of ublox messages')
    parse_ubx.add_argument('path', type = str, help = 'The path of a file to parse as ublox stream')
    parse_ubx.add_argument('-s', '--serial', action = 'store_true', help = 'The file to parse is a serial port and must be configured')
    parse_ubx.add_argument('-b', '--baudrate', metavar = 'INT', type = int, default = 115200, help = 'Specify the baudrate to use when configuring the serial port. Defaults to 115200')
    parse_ubx.add_argument('-d', '--dump', action = 'store_true', help = 'In addition to parsing, output a yaml stream of parsed messages to stdout')
    cli_args = cli_parser.parse_args()

    logging.basicConfig(level = logging.DEBUG if cli_args.verbose else logging.INFO)
    logging.info('Starting Ephemerides Generator with arguments: %s', str(cli_args))

    handler = GnssFormatHandler()

    # Parse ICDs to define formats
    for file_name in cli_args.icds:
        try:
            with open(file_name, encoding='utf8') as f:
                handler.parse_icd(yaml.safe_load(f))
        except Exception as err:
            logging.exception(err)

    # Generate documentation / code from ICDs
    if cli_args.subcommand == 'translate':
        generate = {'md': handler_to_markdown, 'zig': handler_to_zig}[cli_args.format]
        print(generate(handler))
        sys.exit(0)

    # Read ublox stream using formats
    if cli_args.serial:
        stream = Serial(cli_args.path, cli_args.baudrate, timeout = 3)
    else:
        stream = open(cli_args.path, 'rb')
    reader = UBXReader(stream, protfilter = 2)
    for _, ublox_message in reader:
        if ublox_message.identity != 'RXM-SFRBX':
            continue
        try:
            message, header, page_header, parsed = handler.parse_ublox_subframe(ublox_message.gnssId, ublox_message.sigId, ublox_message.payload[8:])
            if cli_args.dump:
                print(format_as_json(message, ublox_message.svId, header, page_header, parsed), end='\n---\n')
            accumulate(message, ublox_message.svId, header.subframe_id, page_header.page_id if page_header else None, header.time_of_week if hasattr(header, 'time_of_week') else None, parsed)
        except Exception as err:
            logging.exception(err)
