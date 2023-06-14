from gnss_format import ensure_fields


class GnssFormatHandler:

    def __init__(self):
        self.formats = {}

    def parse_icd(self, obj: dict[str]):
        ensure_fields('top level', obj, ['kind'])
        if obj['kind'] != 'GNSS_format':
            raise Exception('Provided yaml file is not a GNSS format')
        ensure_fields('top level of GNSS format', obj, ['header', 'formats', 'metadata', 'order', 'ublox'])
        ensure_fields('GNSS format metadata', obj, ['constellation', 'message'])
