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
    comment = f'{self.bit_count} bits mapped as follows:\n'
    heading = '|'.join(['', 'notation', 'name', 'bits', 'factor', 'unit', ''])
    hline   = '|'.join(['', ':------:', ':---', '---:', ':-----', ':--:', ''])
    return '\n'.join([comment, heading, hline] + [field_to_markdown(f) for f in self.fields])

def format_to_markdown(self):
    lines = [f'# {self.constellation.name} {self.name}']
    if self.description:
        lines.append(self.description)
    if self.ublox:
        lines.append(ublox_to_markdown(self.ublox, self))
    lines.append('## Header')
    lines.append(parser_to_markdown(self.header))
    if self.page_header:
        lines.append('## Header extension for paged subframes')
        lines.append(parser_to_markdown(self.page_header))
    current_subframe = None
    for format_data in sorted(self.format_list, key = lambda t: (t.min_subframe, t.min_page)):
        if current_subframe != format_data.min_subframe:
            current_subframe = format_data.min_subframe
            lines.append(f'## Subframe {current_subframe}')
        if format_data.pages is not None:
            lines.append(f"### Page{'s' if len(format_data.pages) > 1 else ''} {format_data.pages}")
        if len(format_data.subframes) > 1:
            lines.append(f'This format applies to subframes {format_data.subframes}')
        if format_data.description:
            lines.append(format_data.description)
        lines.append(parser_to_markdown(format_data.parser))
    return '\n\n'.join(lines)

def ublox_to_markdown(self, parent_format):
    lines = ['## Ublox words layout\n']
    lines.append(f'{parent_format.constellation.name} {parent_format.name} corresponds to gnssId {parent_format.constellation.value}, sigId {self.signal}\n')
    lines += ['|'.join(['Words', 'MSB skipped', 'Data bits', 'LSB skipped']), '|'.join([':-', '-:', '-:', '-:'])]
    for layout in self.layout:
        lines.append('|'.join(map(str, [layout.words, layout.discard_msb, layout.keep, 32 - (layout.discard_msb + layout.keep)])))
    if self.subframe_id:
        lines += ['', f'ublox places the subframe ID in word {self.subframe_id.word}, after {self.subframe_id.discard_msb} MSB, on {self.subframe_id.keep} bits']
    return '\n'.join(lines)
