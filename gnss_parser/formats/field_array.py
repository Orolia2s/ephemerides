from gnss_format.formats import Field

class FieldArray:
    """
    Represent a continuous sequence of fields
    """

    def __init__(self, fields: list[Field]):
        self.fields = fields
        self.bit_count = sum(f.bits for f in self.fields)

    @classmethod
    def from_icd(cls, icd: list[dict[str]]):
        return cls(list(map(Field.from_icd, icd)))
