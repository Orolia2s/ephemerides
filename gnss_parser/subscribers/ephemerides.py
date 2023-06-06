from types import SimpleNamespace

'''
SqrtA
Eccentricity
LittleOmega
M0
I0
BigOmega
DeltaN
Idot
BigOmegaDot

Adot
DeltaN0dot

Cuc
Cus
Cic
Cis
Crc
Crs

ClockBias
ClockDrift
ClockDriftRate
Tgd
'''

translate_to_skydel =
{
    'square_root_of_semi_major_axis': 'SqrtA',
    'eccentricity': 'Eccentricity',
    'argument_of_perigee': 'LittleOmega',
    'mean_anomaly': 'M0',
    'inclination_angle', 'I0',
    'ascending_node_longitude': 'BigOmega',
    'mean_motion_difference': 'DeltaN',
    'rate_of_inclination_angle': 'Idot',
    'rate_of_right_ascension': 'BigOmegaDot',

    'argument_of_latitude_cosine_correction': 'Cuc',
    'argument_of_latitude_sine_correction': 'Cus',
    'inclination_angle_cosine_correction': 'Cic',
    'inclination_angle_sine_correction': 'Cis',
    'orbit_radius_cosine_correction': 'Crc',
    'orbit_radius_sine_correction': 'Crs',

    'clock_bias_correction': 'ClockBias',
    'clock_drift_correction': 'ClockDrift',
    'clock_drift_rate_correction': 'ClockDriftRate',
    'group_delay_differential': 'Tgd'
}

def ephemeris(data: SimpleNamespace):
    print('Could create a Rinex:')
    for key, value in data.__dict__.items():
        print(f'{key:40}:', value)
