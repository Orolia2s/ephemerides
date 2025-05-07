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
    def __init__(self, name: str, typename: str, default_value: str | None = None, comment: str | None = None):
        self.name = Zig.identifier(name)
        self.typename = typename
        self.comment = comment
        self.default = default_value

    def argdef(self) -> str:
        return f'{self.name}: {self.typename}'

    def in_struct(self) -> str:
        result = [self.argdef()]
        if self.default:
            result += ['=', self.default]
        result.append(',')
        if self.comment:
            result += ['//', self.comment]
        return ' '.join(result)

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

    def const(self, name: str, value: str, public: bool = False, Type: str = None, end: str = ';'):
        tokens = []
        if public:
            tokens.append('pub')
        tokens += ['const', Zig.identifier(name)]
        if Type:
            tokens += [':', Type]
        tokens += ['=', value, end]
        self.write_line(' '.join(tokens))

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

    def union(self, name: str, tag: str | None = None, public: bool = False):
        return ZigUnion(name, tag, public, self.output)

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
        super().const(self.name, self.keyword, self.public, end='{')
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

class ZigUnion(ZigStruct):
    keyword = 'union'

    def __init__(self, name: str, tag: str | None, public: bool, output: TextIO):
        super().__init__(name, public, output)
        if tag:
            self.keyword = f'union({tag})'

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
    simple_messages = list(sorted(map(simplify, self.messages.keys())))
    constellations = list(sorted(set(message.constellation for message in self.messages.values()), key=lambda c:c.name))
    writer = ZigWriter(output)
    writer.add_imports(['std', 'o2s', 'utils'])
    writer.empty_line()
    writer.const('SkippingBitReader', 'utils.SkippingBitReader')
    for _, message in sorted(self.messages.items()):
        format_to_zig(message, writer)
    writer.empty_line()
    with writer.enum('Constellation', True) as enum:
        enum.add_members(c.name for c in constellations)
        enum.empty_line()
        with enum.function('from_ublox', [ZigVariable('constellation_id', 'o2s.enum_ublox_constellation')], '!@This()', True) as func:
            func.write_line('return switch(constellation_id) {')
            for c in constellations:
                func.write_line(f'\to2s.{c.name} => .{c.name},')
            func.write_line('\telse => error.UnknownConstellation')
            func.write_line('};')
    with writer.enum('GnssMessageType', True) as enum:
        enum.add_members(simple_messages)
        enum.empty_line()
        with enum.function('from_ublox_signal_id', [ZigVariable('constellation_id', 'u8'), ZigVariable('signal_id', 'u8')], '!@This()', True) as func:
            func.write_line('return switch (constellation_id) {')
            for constellation in constellations:
                func.write_line(f"\to2s.{constellation.name} => switch (signal_id) {'{'}")
                for message in sorted(self.per_constellation[constellation], key = lambda m: m.name):
                    if not message.ublox:
                        continue
                    func.write_line(f'\t\t{message.ublox.signal} => .{Zig.identifier(simplify(message.name))},')
                func.write_line('\t\telse => error.MissingMessage')
                func.write_line('\t},')
            func.write_line('\telse => error.MissingConstellation')
            func.write_line('};')
    writer.empty_line()
    for message_name, message in sorted(self.messages.items()):
        simple_name = simplify(message_name)
        with writer.struct(f'{simple_name}Subframe') as struct:
            if message.ublox and message.ublox.subframe_id:
                struct.add_member(ZigVariable('id', 'u8'))
            struct.add_member(ZigVariable('reader', f'{simple_name}.Reader'))
            struct.add_member(ZigVariable('header', f'{simple_name}.Header'))
            if message.page_header:
                struct.add_member(ZigVariable('page_header', f'?{simple_name}.PageHeader'))
    writer.empty_line()
    with writer.union('GnssSubframe', 'GnssMessageType', True) as union:
        for message in simple_messages:
            union.add_member(ZigVariable(message, f'{message}Subframe'))
        union.empty_line()
        union.const('Self', '@This()')
        union.empty_line()
        with union.struct('Key', True) as struct:
            struct.add_member(ZigVariable('subframe', 'u8'))
            struct.add_member(ZigVariable('page', '?u8', 'null'))
        with writer.function('get_key', [ZigVariable('self', 'Self')], 'Key', True) as func:
            func.write_line('return switch (self) {')
            for message_name, message in sorted(self.messages.items()):
                simple_name = simplify(message_name)
                members = []
                if message.ublox and message.ublox.subframe_id:
                    members.append('.subframe = this.id')
                else:
                    members.append('.subframe = this.header.subframe_id')
                if message.page_header:
                    members.append('.page = if (this.page_header) |page_header| page_header.page_id else null')
                func.write_line(f"\t.{simple_name} => |this| .{'{'}{', '.join(members)}{',}'},")
            func.write_line('};')
        union.empty_line()
        with writer.function('from_ublox', [ZigVariable('subframe', '*o2s.struct_ublox_navigation_data')], 'Self', True) as func:
            func.const('multi_ptr', '@ptrCast(subframe)', Type='[*]o2s.struct_ublox_navigation_data')
            func.const('words', '@alignCast(@ptrCast(multi_ptr + 1))', Type=f'[*]u32')
            func.const('signal', '.from_ublox_message(subframe)', Type='GnssMessageType')
            #func.write_line('switch ()')
    with writer.struct('Subframe', True) as struct:
        struct.add_member(ZigVariable('constellation', 'Constellation'))

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
        field_array_to_zig(self.header, 'Header', 'read_header', '*Reader', namespace)
        if self.page_header:
            field_array_to_zig(self.page_header, 'PageHeader', 'read_page_header', '*Reader', namespace)
        for key, value in sorted(self.human_readable.items()):
            namespace.comment(key)
            subframe = key.replace(' ', '')
            if isinstance(value, dict):
                for (start, human_readable), (field_array, description) in sorted(value.items()):
                    name = f'{subframe}Page{start}'
                    namespace.doc(human_readable)
                    if description:
                        namespace.docs(description.strip().split('\n'))
                    field_array_to_zig(field_array, name, f'read_{name}', '*Reader', namespace)
            else:
                field_array, description = value
                if description:
                    namespace.docs(description.strip().split('\n'))
                field_array_to_zig(field_array, subframe, f'read_{subframe}', '*Reader', namespace)
        with namespace.function('is_paged', [ZigVariable('subframe_id', 'u8')], 'bool', True) as func:
            func.write_line('return switch(subframe_id) {')
            if self.paged_subframes:
                func.write_line(f"\t{','.join(map(str, sorted(self.paged_subframes)))} => true,")
            func.write_line('\telse => false')
            func.write_line('};')

        #with namespace.function('get_subframe_id', [ZigVariable('raw_data', '[]u32')], '!u8', True) as func:
        #    if self.ublox and self.ublox.subframe_id:
        #        func.var('reader', f'SkippingBitReader(1, u32, {Zig.array([self.ublox.subframe_id.discard_msb])}, {Zig.array([self.ublox.subframe_id.keep])})', f".init({Zig.array([f'raw_data[{self.ublox.subframe_id.word - 1}]'])})")
        #        func.write_line(f'return try reader.consume({self.ublox.subframe_id.keep}, u8);')
        #    else:
        #        func.write_line(f'std.debug.assert(raw_data.len == {self.ublox.count});');
        #        func.var('reader', 'Reader', f'.init(raw_data[0..{self.ublox.count}].*)')
        #        func.const('header', 'try read_header(&reader)')
        #        func.write_line('return header.subframe_id;')

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
            consume = f'reader.consume({field.bits}, {zigvar.typename})'
            dest = f'result.{zigvar.name}' if field.name else '_'
            if field.value is not None:
                if field.name:
                    func.comment(field.name)
                func.write_line(f'std.debug.assert(try {consume} == {field.value});')
            else:
                func.write_line(f'{dest} = try {consume};')
        func.write_line('return result;' if needs_result else 'return .{};');

def field_type(self) -> str:
    if self.signed and self.half != 'lsb':
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
    return ZigVariable(name, field_type(self), comment = comment)
