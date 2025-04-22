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
    def __init__(self, name: str, typename: str, const: bool = True):
        self.name = name
        self.typename = typename
        self.const = const

    def argdef(self) -> str:
        return f'{self.name}: {self.typename}'

    def declaration(self, value: str = 'undefined') -> str:
        return f"{'const' if self.const else 'var'} {self.argdef()} = {value};"

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
        self.write_line(f'const {name} = {value};')

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
        tokens += ['fn', Zig.identifier(self.name), '(', ', '.join(map(ZigVariable.argdef, self.arguments)), ')', '->', self.return_type, '{']
        self.empty_line()
        super().write_line(' '.join(tokens))

    def __exit__(self, exception_type, exception_value, traceback):
        super().write_line('}')

def handler_to_zig(self, output: TextIO):
    writer = ZigWriter(output)
    writer.add_imports(['std', 'utilz'])
    writer.empty_line()
    writer.const('SkippingBitReader', 'utilz.SkippingBitReader')
    for _, message in sorted(self.messages.items()):
        writer.empty_line()
        format_to_zig(message, writer)
    with writer.function('main', [], 'void', True) as main:
        pass

def format_to_zig(self, writer: ZigWriter):
    writer.comment(f'Code for {self.name}')
    if self.ublox:
        ublox_to_zig(self.ublox, self.name, writer)

def ublox_to_zig(self, message_name: str, writer: ZigWriter):
    to_skip = [self.per_word[i].discard_msb for i in range(1, self.count + 1)]
    to_keep = [self.per_word[i].keep for i in range(1, self.count + 1)]
    writer.const(Zig.identifier(message_name + '_reader'), f'SkippingBitReader({self.count}, u32, {Zig.array(to_skip)}, {Zig.array(to_keep)})')
