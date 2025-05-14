import logging
import sys
from collections import defaultdict, namedtuple
from types import SimpleNamespace

from more_itertools import grouper

from gnss_parser.bits import SingleWordBitReaderMsb, complementary_half, twos_complement
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

FormatData = namedtuple('FormatData', ['min_subframe', 'min_page', 'subframes', 'pages', 'parser', 'description'])

class GnssFormat(SimpleNamespace):

    def __init__(self, name: str, constellation: Constellation, header: FieldArray, **kwargs):
        super().__init__(name=name, constellation=constellation, header=header, **kwargs)

    @classmethod
    def from_icd(cls, icd: dict[str]):
        ensure_fields('top level of GNSS format', icd, ['header', 'formats', 'metadata'])
        ensure_fields('GNSS format metadata', icd['metadata'], ['constellation', 'message'])
        constellation = icd['metadata']['constellation']
        messageName = icd['metadata']['message']
        result = SimpleNamespace()
        result.page_header = FieldArray.from_icd(icd['page_header']) if 'page_header' in icd else None
        result.ublox = Ublox.from_icd(icd['ublox']) if 'ublox' in icd else None
        result.description = icd['metadata']['description'].strip() if 'description' in icd['metadata'] else None
        result.paged_subframes = set()
        result.per_subframe = defaultdict(dict)
        result.switch = defaultdict(dict)
        result.format_list = []
        for fmt in icd['formats']:
            ensure_fields('format', fmt, ['subframe', 'fields'])
            subframes = RangeList(fmt['subframe']) if isinstance(fmt['subframe'], list) else [fmt['subframe']]
            parser = FieldArray.from_icd(fmt['fields'])
            description = fmt['description'] if 'description' in fmt else None
            if 'pages' in fmt:
                pages = RangeList(fmt['pages'])
                result.format_list.append(FormatData(min(subframes), min(pages), subframes, pages, parser, description))
                for subframe in subframes:
                    result.paged_subframes.add(subframe)
                    result.switch[subframe][min(pages)] = (min(subframes), pages)
                    for page in pages:
                        result.per_subframe[subframe][page] = parser
                logging.debug(f"Added format message {constellation} {messageName} > Subframe(s) {subframes} > page(s) {pages}")
            else:
                for subframe in subframes:
                    result.switch[subframe] = min(subframes)
                    result.per_subframe[subframe] = parser
                result.format_list.append(FormatData(min(subframes), 0, subframes, None, parser, description))
                logging.debug(f"Added format message {constellation} {messageName} > Subframe(s) {subframes}")
        return cls(messageName, Constellation[constellation], FieldArray.from_icd(icd['header']), **result.__dict__)

    def parse_subframe(self, reader):
        header = self.header.parse(reader)
        len_header = reader.count
        if not hasattr(header, 'subframe_id'):
            raise Exception('No subframe ID in header')
        if header.subframe_id not in self.per_subframe:
            raise Exception(f'No such subframe ID: {header.subframe_id}')
        if header.subframe_id not in self.paged_subframes:
            return header, None, self.per_subframe[header.subframe_id].parse(reader)
        if self.page_header is None:
            raise Exception(f'Invalid subframe ID with no page: {header.subframe_id}')
        page_header = self.page_header.parse(reader)
        if page_header.page_id not in self.per_subframe[header.subframe_id]:
            raise Exception(f'Invalid subframe ID and page combination: {header.subframe_id}, {page_header.page_id}')
        return header, page_header, self.per_subframe[header.subframe_id][page_header.page_id].parse(reader)
