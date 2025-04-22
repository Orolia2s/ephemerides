import re

def handler_to_zig(self):
    lines = [
        'const std = @import("std");',
        'const utils = @import("utilz");',
        ''
    ]
    lines += [
        'const SkippingBitReader = utils.SkippingBitReader;',
    ]
    for _, message in sorted(self.messages.items()):
        lines += format_to_zig(message)
    return '\n'.join(lines)

def format_to_zig(self):
    lines = ['', f'// Code for {self.name}']
    if self.ublox:
        lines += ublox_to_zig(self.ublox, self.name)
    return lines

def zig_array(array):
    return '.{' + ','.join(map(str, array)) + '}'

def zig_identifier(identifier):
    if re.fullmatch(r'[a-zA-Z]\w*', identifier):
        return identifier
    return f'@"{identifier}"'

def ublox_to_zig(self, message_name):
    lines = []
    to_skip = [self.per_word[i].discard_msb for i in range(1, self.count + 1)]
    to_keep = [self.per_word[i].keep for i in range(1, self.count + 1)]
    lines.append(f"const {zig_identifier(message_name + '_reader')} = SkippingBitReader({self.count}, u32, {zig_array(to_skip)}, {zig_array(to_keep)});")
    return lines
