"""
"""

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
    lines = [f'# {self.constellation} {self.message}\n']
    lines.append(self.description)
    lines.append('## Header')
    lines.append(parser_to_markdown(self.header))
    if hasattr(self, 'page_header'):
        lines.append('\n## Header extension for paged subframes')
        lines.append(parser_to_markdown(self.page_header))
    for key, value in sorted(self.readable_formats.items()):
        lines.append(f'\n## {key}')
        if isinstance(value, dict):
            for subkey, subvalue in sorted(value.items()):
                lines.append(f'\n### {subkey[1]}')
                lines.append(f'\n{subvalue[1]}')
                lines.append(parser_to_markdown(subvalue[0]))
        else:
            lines.append(f'\n{value[1]}')
            lines.append(parser_to_markdown(value[0]))
    return '\n'.join(lines)
