"""
"""

import sys

from astropy.units import Unit

from gnss_parser import ensure_fields, import_fields, Ordering

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
