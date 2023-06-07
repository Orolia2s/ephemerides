"""
Code related to parsing binary and interpreting it as a sequence of fields of varying widths
"""

import sys
import logging

from types import SimpleNamespace
from collections import defaultdict
from more_itertools import grouper

from astropy.units import Unit

from gnss_parser import ensure_fields, import_fields, Ordering, SingleWordBitReaderMsb, complementary_half

class Field:
    """
    Represents a single field.
    No name would represent padding of reserved
    """
    def __init__(self, field: dict[str]):
        ensure_fields('format list element', field, ['bits'])
        import_fields(self, field, ['name', 'bits', 'value', 'latex', 'shift', 'unit', 'half', 'signed', 'factor'])
        if self.unit:
            self.unit = Unit(self.unit)
        if self.factor and self.shift:
            raise Exception("Can't have both factor and shift !")
        if self.half:
            assert self.half in complementary_half, 'Half can only be ' + ' or '.join(complementary_half)
            if not self.name:
                raise Exception('Split field without name !')

    def parse(self, reader, destination):
        value = reader.read(self.bits)
        if self.half:
            logging.debug(f'Found the {self.half} half of {self.name} : {value:0{self.bits}b}')
            destination.halves[self.name][self.half] = (value, self)
            return
        if self.value != None and self.value != value:
            logging.warning(f'Field "{self.name}" didn\'t have expected value of {self.value}, instead: {value}')
        if self.shift:
            value *= 2 ** self.shift
        if self.factor:
            value *= self.factor
        if self.unit:
            value *= self.unit
        if self.name:
            # print(f'\t{self.name}: {value}')
            setattr(destination, self.name, value)

class Parser:
    """
    Represent a continuous sequence of fields
    """

    def __init__(self, fields: list[dict[str]]):
        self.fields = list(map(Field, fields))
        self.bit_count = sum(f.bits for f in self.fields)

    def parse(self, reader):
        result = SimpleNamespace()
        result.halves = defaultdict(dict)
        for field in self.fields:
            field.parse(reader, result)
        return result

class GnssFormat:
    """
    """

    def __init__(self, icd: dict[str]):
        ensure_fields('top level', icd, ['header', 'formats', 'metadata', 'order'])
        ensure_fields('metadata', icd['metadata'], ['constellation', 'message'])
        import_fields(self, icd['metadata'], ['constellation', 'message', 'description'])

        self.header = Parser(icd['header'])
        if 'page_header' in icd:
            self.page_header = Parser(icd['page_header'])

        self.order = Ordering[icd['order']]

        self.formats = {}
        self.readable_formats = defaultdict(dict)
        for format in icd['formats']:
            ensure_fields('format', format, ['subframe', 'fields'])
            subframe = format['subframe']
            parser = Parser(format['fields'])
            description = format['description'] if 'description' in format else None
            if 'pages' in format:
                pages = set()
                human_readable = []
                for p in format['pages']:
                    if isinstance(p, list):
                        for page in range(p[0], p[1] + 1):
                            pages.add(page)
                        human_readable += [f'{p[0]} to {p[1]}']
                    else:
                        pages.add(p)
                        human_readable += [str(p)]
                logging.info(f'Found format of subframe {subframe} for pages {pages}')
                self.readable_formats[f'Subframe {subframe}'][min(pages), f"Page{('s' if len(pages) > 1 else '')} {', '.join(human_readable)}"] = (parser, description)
            else:
                pages = [None]
                logging.info(f'Found format of subframe {subframe}, not paged')
                self.readable_formats[f'Subframe {subframe}'] = (parser, description)
            for page in pages:
                self.formats[subframe, page] = parser

    def parse_ublox_subframe(self, reader):
        header = self.header.parse(reader)
        len_header = reader.count
        logging.debug(f'Parsed the header and consumed {len_header} bits ({self.header.bit_count})')
        logging.debug(f'{header}')
        logging.debug(f'The header indicates this is subframe {header.subframe_id}')
        if (header.subframe_id, None) in self.formats:
            logging.debug(f'Parsed a total of {reader.count} bits')
            return header, None, self.formats[header.subframe_id, None].parse(reader)
        elif hasattr(self, 'page_header'):
            page_header = self.page_header.parse(reader)
            logging.debug(f'Parsed an additional {reader.count - len_header} bits to find out this is page {page_header.page_id} ({self.page_header.bit_count})')
            if (header.subframe_id, page_header.page_id) in self.formats:
                result = self.formats[header.subframe_id, page_header.page_id].parse(reader)
                logging.debug(f'Parsed a total of {reader.count} bits')
                return header, page_header, result
            else:
                raise Exception(f'Invalid subframe ID and page combination: {header.subframe_id}, {page_header.page_id}')
        else:
            raise Exception(f'Invalid subframe ID with no page: {header.subframe_id}')
