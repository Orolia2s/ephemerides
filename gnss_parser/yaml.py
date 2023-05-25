"""
"""

import sys
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
        logging.warning('Ignored extra fields: {extras}')
