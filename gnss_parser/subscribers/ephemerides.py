from types import SimpleNamespace

def ephemeris(data: SimpleNamespace):
    print('Could create a Rinex:')
    for key, value in data.__dict__.items():
        print(f'{key:40}:', value)
