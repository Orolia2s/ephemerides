import logging
from types import SimpleNamespace

from astropy.units import Unit

from gnss_parser.bits import complementary_half
from gnss_parser.yaml import ensure_fields, import_fields


class Field(SimpleNamespace):
    """
    Represents a single field.
    Name can be None to mean padding or reserved
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.unit:
            self.unit = Unit(self.unit)
        if self.factor and self.shift:
            raise Exception("Field can't have both factor and shift !")
        if self.half:
            assert self.half in complementary_half, 'Half can only be ' + ' or '.join(complementary_half)
            if not self.name:
                raise Exception('Split field without name !')

    @classmethod
    def from_icd(cls, icd: dict[str]):
        result = SimpleNamespace()
        ensure_fields('format array element', icd, ['bits'])
        import_fields(result, icd, ['name', 'bits', 'value', 'latex', 'shift', 'unit', 'half', 'signed', 'factor'])
        return cls(**result.__dict__)

    def parse(self, reader, destination):
        value = reader.read(self.bits)
        if self.half:
            logging.debug(f'Found the {self.half} half of {self.name} : {value:0{self.bits}b}')
            destination.halves[self.name][self.half] = (value, self)
            return
        if self.value is not None and self.value != value:
            logging.warning(f'Field "{self.name}" didn\'t have expected value of {self.value}, instead: {value}')
        if self.signed:
            value = twos_complement(value, self.bits)
        if self.shift:
            value *= 2 ** self.shift
        if self.factor:
            value *= self.factor
        if self.unit:
            value *= self.unit
        if self.name:
            setattr(destination, self.name, value)

class FieldArray:
    """
    Represent a contiguous sequence of fields
    """

    def __init__(self, fields: list[Field]):
        self.fields = fields
        self.bit_count = sum(f.bits for f in self.fields)

    @classmethod
    def from_icd(cls, icd: list[dict[str]]):
        return cls(list(map(Field.from_icd, icd)))
