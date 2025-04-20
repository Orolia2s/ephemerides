import logging
import sys
from collections import defaultdict

from more_itertools import grouper

from gnss_parser.bits import (Ordering, SingleWordBitReaderMsb,
                              complementary_half, twos_complement)
from gnss_parser.constellations import Constellation
from gnss_parser.field import FieldArray
from gnss_parser.ublox import Ublox
from gnss_parser.yaml import ensure_fields, import_fields


class GnssFormat:

    def __init__(self, icd: dict[str]):
        ensure_fields('top level', icd, ['header', 'formats', 'metadata', 'order'])
        ensure_fields('metadata', icd['metadata'], ['constellation', 'message'])
        import_fields(self, icd['metadata'], ['constellation', 'message', 'description'])

        self.constellation = Constellation[self.constellation]
        self.ublox = Ublox.from_icd(icd['ublox']) if 'ublox' in icd else None
        self.header = FieldArray.from_icd(icd['header'])
        if 'page_header' in icd:
            self.page_header = FieldArray.from_icd(icd['page_header'])

        self.order = Ordering[icd['order']]

        self.formats = {}
        self.readable_formats = defaultdict(dict)
        for format in icd['formats']:
            ensure_fields('format', format, ['subframe', 'fields'])
            subframe = format['subframe']
            parser = FieldArray.from_icd(format['fields'])
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
