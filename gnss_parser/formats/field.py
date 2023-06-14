from types import SimpleNamespace
from astropy.units import Unit
from gnss_format import ensure_fields, import_fields

class Field(SimpleNamespace):

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
