#from collections import defaultdict

from gnss_parser import Constellation

storage = {} #defaultdict(dict)

def accumulate(message_type: str, satellite: int, subframe: int, page: int | None, time: int, message):
    if message_type not in storage:
        print(f'New message type: {message_type}')
        storage[message_type] = {}
    if satellite not in storage[message_type]:
        print(f'First {message_type} of satellite {satellite}')
        storage[message_type][satellite] = {}

    key = (subframe, page) if page else subframe
    storage[message_type][satellite][key] = message
