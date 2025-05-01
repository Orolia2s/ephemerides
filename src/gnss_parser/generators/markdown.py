"""
Generate a markdown document describing the GNSS message
"""

def handler_to_markdown(self):
    lines = []
    for _, message in sorted(self.messages.items()):
        lines.append(format_to_markdown(message))
    return '\n'.join(lines)

def field_to_markdown(self):
    cells = ['']
    cells.append(f'${self.latex}$' if self.latex else f'`{self.value:0{self.bits}b}`' if self.value != None else '')
    cells.append(self.name if self.name else '_ignored_')
    if self.half:
        cells[-1] += f' ({self.half})'
    cells.append(f'$^*{self.bits}$' if self.signed else str(self.bits))
    cells.append(str(self.factor) if self.factor else f'$2^{{{self.shift}}}$' if self.shift else '')
    cells.append(f'{self.unit:latex}' if self.unit else '')
    return '|'.join(cells + [''])

def parser_to_markdown(self):
    comment = f'\n{self.bit_count} bits mapped as follows:\n'
    heading = '|'.join(['', 'notation', 'name', 'bits', 'factor', 'unit', ''])
    hline   = '|'.join(['', ':------:', ':---', '---:', ':-----', ':--:', ''])
    return '\n'.join([comment, heading, hline] + [field_to_markdown(f) for f in self.fields])

def format_to_markdown(self):
    lines = [f'# {self.constellation.name} {self.name}\n']
    if self.description:
        lines.append(self.description)
    if self.ublox:
        lines.append(ublox_to_markdown(self.ublox, self))
    lines.append('## Header')
    lines.append(parser_to_markdown(self.header))
    if self.page_header:
        lines.append('\n## Header extension for paged subframes')
        lines.append(parser_to_markdown(self.page_header))
    for key, value in sorted(self.human_readable.items()):
        lines.append(f'\n## {key}')
        if isinstance(value, dict):
            for subkey, subvalue in sorted(value.items()):
                lines.append(f'\n### {subkey[1]}')
                if subvalue[1]:
                    lines.append(f'\n{subvalue[1]}')
                lines.append(parser_to_markdown(subvalue[0]))
        else:
            lines.append(f'\n{value[1]}')
            lines.append(parser_to_markdown(value[0]))
    return '\n'.join(lines)

def ublox_to_markdown(self, parent_format):
    lines = ['## Ublox words layout\n']
    lines.append(f'{parent_format.constellation.name} {parent_format.name} corresponds to gnssId {parent_format.constellation.value}, sigId {self.signal}\n')
    lines += ['|'.join(['Words', 'MSB skipped', 'Data bits', 'LSB skipped']), '|'.join([':-', '-:', '-:', '-:'])]
    for layout in self.layout:
        lines.append('|'.join(map(str, [layout.words, layout.discard_msb, layout.keep, 32 - (layout.discard_msb + layout.keep)])))
    return '\n'.join(lines + [''])
