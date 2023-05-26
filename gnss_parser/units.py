"""
Custom astropy units
"""

from astropy import units

semicircle = units.def_unit('semicircle', 180 * units.deg)

units.add_enabled_units([semicircle])
