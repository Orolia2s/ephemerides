import logging

from collections import defaultdict
from types import SimpleNamespace

from gnss_parser import Constellation, ephemerides

storage = {}

subscribers = {
    'LNAV': {
        (2, 3): ephemerides,
    },
    'D1': {
        (2, 3): ephemerides
    },
}

def merge(messages: list[SimpleNamespace]) -> SimpleNamespace:
    halves = defaultdict(dict)
    for message in messages:
        for field, parts in message.halves.items():
            for part, value in parts:
                if part in halves[field]:
                    raise Exception(f'Found multiple {part} of {field} !?')
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

    result = {}
    for message in messages:
        result.update(message)
    return SimpleNamespace(**result)

def accumulate(message_type: str, satellite: int, subframe: int, page: int | None, time: int, message):
    if message_type not in storage:
        print(f'New message type: {message_type}')
        storage[message_type] = {}
    if satellite not in storage[message_type]:
        print(f'First {message_type} of satellite {satellite}')
        storage[message_type][satellite] = {}

    key = (subframe, page) if page else subframe
    storage[message_type][satellite][key] = message

    for message_type, subscriber in subscribers.items():
        if message_type not in storage:
            continue
        for subframes, callback in subscriber:
            for satellite in storage[message_type]:
                if set(subframes).is_subset(set(satellite.keys())):
                    callback(merge(satellite[k] for k in subframes))
