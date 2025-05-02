from typing import TextIO
import re

class Zig:

    @staticmethod
    def array(array: list) -> str:
        return '.{' + ','.join(map(str, array)) + '}'

    @staticmethod
    def identifier(identifier: str) -> str:
        if re.fullmatch(r'[a-zA-Z]\w*', identifier):
            return identifier
        return f'@"{identifier}"'

class ZigVariable:
    def __init__(self, name: str, typename: str, comment: str | None = None):
        self.name = Zig.identifier(name)
        self.typename = Zig.identifier(typename)
        self.comment = comment

    def argdef(self) -> str:
        return f'{self.name}: {self.typename}'

    def in_struct(self) -> str:
        result = self.argdef() + ','
        if self.comment:
            result += f' // {self.comment}'
        return result

    def __str__(self) -> str:
        return self.name

class ZigWriter:
    def __init__(self, output: TextIO):
        self.output = output

    def empty_line(self):
        self.output.write('\n')

    def write_line(self, line: str):
        self.output.write(line + '\n')

    def const(self, name: str, value: str):
        self.write_line(f'const {Zig.identifier(name)} = {value};')

    def var(self, name: str, Type: str, value: str):
        self.write_line(f'var {Zig.identifier(name)}: {Type} = {value};')

    def add_import(self, name: str, module: str = None):
        if not module:
            module = name
        self.const(name, f'@import("{module}")')

    def add_imports(self, imports: list[str]):
        for imp in imports:
            self.add_import(imp)

    def comment(self, comment: str):
        self.write_line(f'// {comment}')

    def function(self, name: str, arguments: list[ZigVariable], return_type: str, public: bool = False):
        return ZigFunction(name, arguments, return_type, public, self.output)

    def enum(self, name: str, elements: list[str]):
        self.write_line(f"const {Zig.identifier(name)} = enum {'{'}{', '.join(map(Zig.identifier, elements))}{'}'};");

    def struct(self, name: str, members: list[ZigVariable]):
        self.write_line(f"const {Zig.identifier(name)} = struct {'{'}")
        for member in members:
            self.write_line('\t' + member.in_struct())
        self.write_line('};')

class ZigFunction(ZigWriter):
    def __init__(self, name: str, arguments: list[ZigVariable], return_type: str, public: bool, output: TextIO):
        self.name = name
        self.public = public
        self.arguments = arguments
        self.return_type = return_type
        super().__init__(output)

    def write_line(self, line: str):
        super().write_line('\t' + line)

    def __enter__(self):
        tokens = []
        if self.public:
            tokens.append('pub')
        tokens += ['fn', Zig.identifier(self.name), '(', ', '.join(map(ZigVariable.argdef, self.arguments)), ')', self.return_type, '{']
        super().write_line(' '.join(tokens))
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        super().write_line('}')

def handler_to_zig(self, output: TextIO):
    writer = ZigWriter(output)
    writer.add_imports(['std', 'o2s', 'utils'])
    writer.empty_line()
    writer.const('SkippingBitReader', 'utilz.SkippingBitReader')
    for _, message in sorted(self.messages.items()):
        format_to_zig(message, writer)
    writer.enum('GnssMessage', sorted(self.messages.keys()))
    with writer.function('main', [], '!void', True) as main:
        pass

def format_to_zig(self, writer: ZigWriter):
    simple_name = ''.join(filter(str.isalnum, self.name))
    header_name = simple_name + 'Header'
    reader_name = simple_name + 'Reader'
    writer.empty_line()
    writer.comment(f"Code about {self.constellation.name} {self.name}")
    if self.ublox:
        ublox_to_zig(self.ublox, reader_name, writer)
    field_array_to_zig(self.header, header_name, f'read_{simple_name}_header', reader_name, writer)
    #with writer.function('read_' + simple_name, [ZigVariable('reader', reader_name)], '!void', True):
    #    pass

def ublox_to_zig(self, reader_name: str, writer: ZigWriter):
    to_skip = [self.per_word[i].discard_msb for i in range(1, self.count + 1)]
    to_keep = [self.per_word[i].keep for i in range(1, self.count + 1)]
    writer.const(Zig.identifier(reader_name), f'SkippingBitReader({self.count}, u32, {Zig.array(to_skip)}, {Zig.array(to_keep)})')

def field_array_to_zig(self, struct_name: str, function_name: str, reader_name: str, writer: ZigWriter):
    writer.struct(struct_name, [field_to_zigvar(field)
                                for field in self.fields
                                if field.name and not field.value])
    with writer.function(function_name, [ZigVariable('reader', reader_name)], f'!{struct_name}', False) as func:
        func.var('result', struct_name, 'undefined');
        for field in self.fields:
            typename = '{}{}'.format('i' if field.signed else 'u', field.bits)
            consume = f'reader.consume({typename}, {field.bits})'
            dest = f'result.{field.name}' if field.name else '_'
            if field.value is not None:
                func.write_line(f'std.debug.assert(try {consume} == {field.value});')
            else:
                func.write_line(f'{dest} = try {consume};')
        func.write_line('return result;');

def field_to_zigvar(self):
    comment = None
    if self.half:
        comment = f'{self.half}'
    elif self.factor or self.shift or self.unit:
        factor = f'2^{self.shift}' if self.shift else self.factor
        comment = ' '.join(str(t) for t in (factor, self.unit) if t)
    return ZigVariable(self.name,
                       '{}{}'.format('i' if self.signed else 'u', self.bits),
                       comment)
