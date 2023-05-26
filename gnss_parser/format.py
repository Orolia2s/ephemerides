"""
Code related to parsing binary and interpreting it as a sequence of fields of varying widths
"""

import sys
import logging

from types import SimpleNamespace
from collections import defaultdict
from more_itertools import grouper

from astropy.units import Unit

from gnss_parser import ensure_fields, import_fields, Ordering, SingleWordBitReaderMsb

class Field:
    """
    Represents a single field.
    No name would represent padding of reserved
    """
    def __init__(self, field: dict[str]):
        ensure_fields('format list element', field, ['bits'])
        import_fields(self, field, ['name', 'bits', 'value', 'latex', 'shift', 'unit'])
        if self.unit:
            self.unit = Unit(self.unit)

    def parse(self, reader, destination):
        value = reader.read(self.bits)
        if self.value and self.value != value:
            logging.warning(f'Field "{self.name}" didn\'t have expected value of {self.value}, instead: {value}')
        if self.shift:
            value *= 2 ** self.shift
        if self.unit:
            value *= self.unit
        print(f'\t{self.name}: {value}')
        setattr(destination, self.name, value)

    def to_markdown(self):
        cells = ['']
        cells.append(f'${self.latex}$' if self.latex else '')
        cells.append(self.name if self.name else '_ignored_')
        cells.append(str(self.bits))
        cells.append(f'$2^{{{self.shift}}}$' if self.shift else '')
        cells.append(f'{self.unit:latex}' if self.unit else '')
        return '|'.join(cells + [''])

class Parser:
    """
    Represent a continuous sequence of fields
    """

    def __init__(self, fields: list[dict[str]]):
        self.fields = list(map(Field, fields))
        self.bit_count = sum(f.bits for f in self.fields)

    def parse(self, reader):
        result = SimpleNamespace()
        for field in self.fields:
            field.parse(reader, result)
        return result

    def to_markdown(self):
        comment = f'\n{self.bit_count} bits mapped as follows:\n'
        heading = '|'.join(['', 'notation', 'name', 'bits', 'factor', 'unit', ''])
        hline   = '|'.join(['', ':------:', ':---', '---:', ':-----', ':--:', ''])
        return '\n'.join([comment, heading, hline] + [f.to_markdown() for f in self.fields])

    def __call__(self, *args):
        return self.parse(*args)

class GnssFormat:
    """
    """

    def __init__(self, icd: dict[str]):
        ensure_fields('top level', icd, ['header', 'formats', 'metadata', 'order'])
        ensure_fields('metadata', icd['metadata'], ['constellation', 'message'])
        import_fields(self, icd['metadata'], ['constellation', 'message', 'description'])

        self.header = Parser(icd['header'])
        self.order = Ordering[icd['order']]

        frame_count = icd['frame_count']
        self.formats = {}
        self.readable_formats = defaultdict(dict)
        for format in icd['formats']:
            ensure_fields('format', format, ['subframe', 'fields'])
            subframe = format['subframe']
            parser = Parser(format['fields'])
            if 'pages' in format:
                pages = set()
                for p in format['pages']:
                    if isinstance(p, list):
                        for page in range(p[0], p[1]):
                            pages.add(page)
                    else:
                        pages.add(p)
                logging.info(f'Found format of subframe {subframe} for pages {pages}')
                self.readable_formats[f'Subframe {subframe}'][f"Page{('s' if len(pages) > 1 else '')} {', '.join(map(str, pages))}"] = parser
            else:
                pages = range(frame_count)
                logging.info(f'Found format of subframe {subframe} for all {frame_count} pages')
                self.readable_formats[f'Subframe {subframe}'] = parser
            for page in pages:
                self.formats[subframe, page] = parser

    def parse_ublox_subframe(self, reader):
        self.header.parse(reader)

    def to_markdown(self):
        lines = [f'# {self.constellation} {self.message}\n']
        lines.append(self.description)
        lines.append('## Header')
        lines.append(self.header.to_markdown())
        for key, value in sorted(self.readable_formats.items()):
            lines.append(f'\n## {key}')
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    lines.append(f'\n### {subkey}')
                    lines.append(subvalue.to_markdown())
            else:
                lines.append(value.to_markdown())
        return '\n'.join(lines)
