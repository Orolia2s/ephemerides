from types import SimpleNamespace

from gnss_format.yaml import ensure_fields, import_fields

class GnssFormat(SimpleNamespace):

    def __init__(self, header: FieldArray, page_header: FieldArray | None, metadata):
        self.header = header
        self.page_header = page_header
        super().__init__(metadata)

    @classmethod
    def from_icd(cls, icd: dict[str]):
        ensure_fields('top level of GNSS format', icd, ['header', 'formats', 'metadata', 'order', 'ublox'])
        ensure_fields('GNSS format metadata', icd, ['constellation', 'message'])
        metadata = SimpleNamespace()
        import_fields(metadata, icd['metadata'], ['constellation', 'message', 'description'])
        return cls(FieldArray.from_icd(icd['header']), )
