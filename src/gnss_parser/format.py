import logging
import sys
from collections import defaultdict
from types import SimpleNamespace

from more_itertools import grouper

from gnss_parser.bits import (Ordering, SingleWordBitReaderMsb,
                              complementary_half, twos_complement)
from gnss_parser.constellations import Constellation
from gnss_parser.field import FieldArray
from gnss_parser.ublox import Ublox, reader_from_ublox
from gnss_parser.yaml import RangeList, ensure_fields, import_fields


class GnssFormatHandler:

    def __init__(self):
        self.messages = {}
        self.ublox_mapping = {}
        self.per_constellation = defaultdict(list)

    def parse_icd(self, obj: dict):
        ensure_fields('top level', obj, ['kind'])
        if obj['kind'] != 'GNSS_format':
            raise Exception('Provided yaml file is not a GNSS format')
        message = GnssFormat.from_icd(obj)
        self.messages[message.name] = message
        if message.ublox:
            self.ublox_mapping[message.constellation.value, message.ublox.signal] = message.name
        self.per_constellation[message.constellation].append(message)

    def parse_subframe(self, message_name: str, reader):
        return self.messages[message_name].parse_subframe(reader)

    def parse_ublox_subframe(self, gnssId: int, sigId: int, words: bytes):
        if (gnssId, sigId) not in self.ublox_mapping:
            raise Exception(f'Unknown ublox (consellation, signal) combination ({gnssId}, {sigId})')
        message = self.ublox_mapping[gnssId, sigId]
        return message, *self.parse_subframe(message, reader_from_ublox[message](words))

class GnssFormat(SimpleNamespace):

    def __init__(self, name: str, constellation: Constellation, order: Ordering, header: FieldArray, **kwargs):
        super().__init__(name=name, constellation=constellation, order=order, header=header, **kwargs)

    @classmethod
    def from_icd(cls, icd: dict[str]):
        ensure_fields('top level of GNSS format', icd, ['header', 'formats', 'metadata', 'order'])
        ensure_fields('GNSS format metadata', icd['metadata'], ['constellation', 'message'])
        result = SimpleNamespace()
        result.page_header = FieldArray.from_icd(icd['page_header']) if 'page_header' in icd else None
        result.ublox = Ublox.from_icd(icd['ublox']) if 'ublox' in icd else None
        result.description = icd['metadata']['description'] if 'description' in icd['metadata'] else None
        result.formats = {}
        result.human_readable = defaultdict(dict)
        for fmt in icd['formats']:
            ensure_fields('format', fmt, ['subframe', 'fields'])
            subframe = fmt['subframe']
            parser = FieldArray.from_icd(fmt['fields'])
            description = fmt['description'] if 'description' in fmt else None
            if 'pages' in fmt:
                pages = RangeList(fmt['pages'])
                for page in pages:
                    result.formats[subframe, page] = parser
                result.human_readable[f'Subframe {subframe}'][min(pages), f"Page{'s' if len(pages.as_list) > 1 else ''} {pages}"] = (parser, description)
                logging.debug(f"Added format message {icd['metadata']['constellation']} {icd['metadata']['message']} > Subframe {subframe} > page(s) {pages}")
            else:
                result.formats[subframe, None] = parser
                result.human_readable[f'Subframe {subframe}'] = (parser, description)
                logging.debug(f"Added format message {icd['metadata']['constellation']} {icd['metadata']['message']} > Subframe {subframe}")
        return cls(icd['metadata']['message'], Constellation[icd['metadata']['constellation']], Ordering[icd['order']], FieldArray.from_icd(icd['header']), **result.__dict__)

    def parse_subframe(self, reader):
        header = self.header.parse(reader)
        len_header = reader.count
        if not hasattr(header, 'subframe_id'):
            raise Exception('No subframe ID in header')
        logging.debug(f'Parsed the header and consumed {len_header} bits ({self.header.bit_count}). It indicated the subframe is {header.subframe_id}')
        if (header.subframe_id, None) in self.formats:
            logging.debug(f'Parsed a total of {reader.count} bits')
            return header, None, self.formats[header.subframe_id, None].parse(reader)
        elif self.page_header is not None:
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
