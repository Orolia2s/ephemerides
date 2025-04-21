"""
Handle subframes accross time, calling subscribers when sufficient data has been collected
"""

import logging
from collections import defaultdict
from types import SimpleNamespace

from gnss_parser.constellations import Constellation
from gnss_parser.subscribers.ephemerides import ephemeris

storage = {}

subscribers = {
    'LNAV-L': {
        (2, 3): ephemeris,
    },
    'D1': {
        (2, 3): ephemeris
    },
}

def merge(messages: list[SimpleNamespace]) -> SimpleNamespace:
    """
    Create a single object from multiple subframes, also reconstructing split fields
    """
    print(f'Merging {len(messages)} subframes')
    result = {}

    halves = defaultdict(dict)
    for message in messages:
        for field, parts in message.halves.items():
            for part, value in parts.items():
                if part in halves[field]:
                    logging.warning(f'Found multiple {part} of {field} !?')
                halves[field][part] = value
    for field, parts in halves.items():
        if parts.keys() != {'msb', 'lsb'}:
            logging.error(f'Unable to reconstruct {field}: {parts}')
            continue
        msb, _ = parts['msb']
        value, data = parts['lsb']
        value += msb << data.bits
        if data.shift:
            value *= 2 ** data.shift
        elif data.factor:
            value *= data.factor
        if data.unit:
            value *= data.unit
        logging.info(f'Reconstructed field "{field}": {value}')
        result[field] = value

    for message in messages:
        message.__dict__.pop('halves')
        duplicates = message.__dict__.keys() & result.keys()
        if duplicates:
            logging.error(f'Duplicate fields: {duplicates}')
        result.update(message.__dict__)
    return SimpleNamespace(**result)

def accumulate(message_type: str, satellite: int, subframe: int, page: int | None, time: int, message):
    """
    Store a single subframe
    """
    if message_type not in storage:
        logging.debug(f'New message type: {message_type}')
        storage[message_type] = {}
    if satellite not in storage[message_type]:
        logging.debug(f'First {message_type} of satellite {satellite}')
        storage[message_type][satellite] = {}

    key = (subframe, page) if page else subframe
    storage[message_type][satellite][key] = message

    for sought_subframes, callback in subscribers[message_type].items():
        sought_subframes = set(sought_subframes)
        if key not in sought_subframes:
            continue
        stored_subframes = storage[message_type][satellite]
        logging.debug(f'In {message_type}, we are looking for {sought_subframes} for satellite {satellite} : {set(stored_subframes.keys())}')
        if sought_subframes <= stored_subframes.keys():
            callback(merge(list(stored_subframes[key] for key in sought_subframes)))
