from typing import TextIO
import re

class Zig:

    @staticmethod
    def array(array: list) -> str:
        return '.{' + ','.join(map(str, array)) + '}'

    @staticmethod
    def identifier(identifier: str) -> str:
        if re.fullmatch(r'[a-zA-Z_]\w*', identifier):
            return identifier
        return f'@"{identifier}"'

class ZigVariable:
    def __init__(self, name: str, typename: str, comment: str | None = None):
        self.name = Zig.identifier(name)
        self.typename = typename
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

    def write(self, string: str):
        self.output.write(string)

    def empty_line(self):
        self.write('\n')

    def write_line(self, line: str):
        self.write(line + '\n')

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

    def doc(self, comment: str):
        self.write_line(f'/// {comment}')

    def docs(self, comments: list[str]):
        for comment in comments:
            self.doc(comment)

    def function(self, name: str, arguments: list[ZigVariable], return_type: str, public: bool = False):
        return ZigFunction(name, arguments, return_type, public, self.output)

    def enum(self, name: str, public: bool = False):
        return ZigEnum(name, public, self.output)

    def struct(self, name: str, public: bool = False):
        return ZigStruct(name, public, self.output)

class ZigStruct(ZigWriter):
    keyword = 'struct'

    def __init__(self, name: str, public: bool, output: TextIO):
        self.name = name
        self.public = public
        super().__init__(output)

    def write_line(self, line: str):
        super().write_line('\t' + line)

    def __enter__(self):
        tokens = []
        if self.public:
            tokens.append('pub')
        tokens += ['const', Zig.identifier(self.name), '=', self.keyword, '{']
        super().write_line(' '.join(tokens))
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        super().write_line('};')

    def add_member(self, member: ZigVariable):
        self.write_line(member.in_struct())

    def add_members(self, members: list[ZigVariable]):
        for member in members:
            self.add_member(member)

class ZigEnum(ZigStruct):
    keyword = 'enum'

    def add_member(self, member: str):
        self.write_line(f'{Zig.identifier(member)},')

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
    writer.const('SkippingBitReader', 'utils.SkippingBitReader')
    for _, message in sorted(self.messages.items()):
        format_to_zig(message, writer)
    writer.empty_line()
    with writer.enum('GnssMessage', True) as enum:
        enum.add_members(sorted(map(simplify, self.messages.keys())))
        enum.empty_line()
        with enum.function('from_ublox_message', [ZigVariable('message', '*o2s.ublox_message_t')], '!@This()') as func:
            constellations = sorted(self.per_constellation.keys(), key = lambda c: c.value)
            for constellation in constellations:
                func.write_line(f'comptime std.debug.assert({constellation.value} == o2s.{constellation.name});')
            func.write_line('return switch (message.constellation) {')
            for constellation in constellations:
                func.write_line(f"\to2s.{constellation.name} => switch (message.signal) {'{'}")
                for message in sorted(self.per_constellation[constellation], key = lambda m: m.name):
                    if not message.ublox:
                        continue
                    func.write_line(f'\t\t{message.ublox.signal} => .{Zig.identifier(simplify(message.name))},')
                func.write_line('\t\telse => error.MissingMessage')
                func.write_line('\t},')
            func.write_line('\telse => error.MissingConstellation')
            func.write_line('};')
    writer.empty_line()

def simplify(name: str) -> str:
    return ''.join(filter(str.isalnum, name))

def format_to_zig(self, writer: ZigWriter):
    simple_name = simplify(self.name)
    writer.empty_line()
    writer.doc(f"{self.constellation.name} {self.name}")
    if self.description:
        writer.docs(self.description.strip().split('\n'))
    with writer.struct(simple_name) as namespace:
        if self.ublox:
            ublox_to_zig(self.ublox, 'Reader', namespace)
        field_array_to_zig(self.header, 'Header', 'read_header', 'Reader', namespace)
        if self.page_header:
            field_array_to_zig(self.page_header, 'PageHeader', 'read_page_header', 'Reader', namespace)
        for key, value in sorted(self.human_readable.items()):
            namespace.comment(key)
            subframe = key.replace(' ', '')
            if isinstance(value, dict):
                for (start, human_readable), (field_array, description) in sorted(value.items()):
                    name = f'{subframe}Page{start}'
                    namespace.doc(human_readable)
                    if description:
                        namespace.docs(description.strip().split('\n'))
                    field_array_to_zig(field_array, name, f'read_{name}', 'Reader', namespace)
            else:
                field_array, description = value
                if description:
                    namespace.docs(description.strip().split('\n'))
                field_array_to_zig(field_array, subframe, f'read_{subframe}', 'Reader', namespace)


    #with writer.function('read_' + simple_name, [ZigVariable('reader', reader_name)], '!void', True):
    #    pass

def ublox_to_zig(self, reader_name: str, writer: ZigWriter):
    to_skip = [self.per_word[i].discard_msb for i in range(1, self.count + 1)]
    to_keep = [self.per_word[i].keep for i in range(1, self.count + 1)]
    writer.const(Zig.identifier(reader_name), f'SkippingBitReader({self.count}, u32, {Zig.array(to_skip)}, {Zig.array(to_keep)})')

def field_array_to_zig(self, struct_name: str, function_name: str, reader_name: str, writer: ZigWriter):
    with writer.struct(struct_name) as struct:
        for field in self.fields:
            if field.name and field.value is None:
                struct.add_member(field_to_zigvar(field))
    with writer.function(function_name, [ZigVariable('reader', reader_name)], f'!{struct_name}', False) as func:
        needs_result = any(map(lambda f: f.name and field.value is None, self.fields))
        if needs_result:
            func.var('result', struct_name, 'undefined');
        for field in self.fields:
            zigvar = field_to_zigvar(field)
            consume = f'reader.consume({zigvar.typename}, {field.bits})'
            dest = f'result.{zigvar.name}' if field.name else '_'
            if field.value is not None:
                if field.name:
                    func.comment(field.name)
                func.write_line(f'std.debug.assert(try {consume} == {field.value});')
            else:
                func.write_line(f'{dest} = try {consume};')
        func.write_line('return result;' if needs_result else 'return .{};');

def field_type(self) -> str:
    if self.signed and self.half == 'msb':
        return f'i{self.bits}'
    return f'u{self.bits}'

def field_to_zigvar(self):
    comment = None
    name = self.name if self.name else '_'
    if self.half:
        name += f'_{self.half}'
        comment = f'{self.half}'
    elif self.factor or self.shift or self.unit:
        factor = f'2^{self.shift}' if self.shift else self.factor
        comment = ' '.join(str(t) for t in (factor, self.unit) if t)
    return ZigVariable(name, field_type(self), comment)
