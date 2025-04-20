"""
GNSS specific code
"""

from enum import IntEnum


class Constellation(IntEnum):
    """
    GNSS system list, that conveniently corresponds to ublox representation
    """
    GPS     = 0
    SBAS    = 1
    Galileo = 2
    BeiDou  = 3
    IMES    = 4
    QZSS    = 5
    GLONASS = 6
    NavIC   = 7
