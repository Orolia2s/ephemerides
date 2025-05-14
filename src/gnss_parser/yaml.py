"""
Yaml specific code
"""

import logging


def ensure_fields(location: str, obj: dict[str], fields: list[str]):
    """
    Raise an exception if one of the expected fields is missing
    """
    for field in fields:
        if not field in obj:
            raise Exception(f'Missing the "{field}" from {location}')

def import_fields(destination, source: dict[str], fields: list[str]):
    """
    Creates members to the destination objects, that have the name and values of the desired fields from the source dictionnary.
    Also prints a warning about remaining fields that were not imported
    """
    for field in fields:
        setattr(destination, field, source.get(field, None))
    extras = source.keys() - set(fields)
    if extras:
        logging.warning(f'Ignored extra fields: {extras}')

class RangeList:
    """
    [3, 5, [7, 10]] -> {3, 5, 7, 8, 9, 10}, "3, 5, 7 to 10"
    """

    def __init__(self, iterable):
        if isinstance(iterable, int):
            iterable = [iterable]
        self.as_list = []
        self.human_readable = []
        for element in iterable:
            if isinstance(element, list):
                self.as_list += range(element[0], element[1] + 1)
                self.human_readable.append(f'{element[0]} to {element[1]}')
            else:
                self.as_list.append(element)
                self.human_readable.append(str(element))
        self.as_set = set(self.as_list)

    def __iter__(self):
        return self.as_list.__iter__()

    def __contains__(self, element):
        return self.as_set.__contains__(element)

    def __str__(self):
        return ', '.join(self.human_readable)

    def __len__(self):
        return self.as_list.__len__()
