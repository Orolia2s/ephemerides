"""
Custom astropy units
"""

from astropy import units

semicircle = units.def_unit('semicircle', 180 * units.deg)
solar_flux = units.def_unit('sfu', 1e-22 * units.W / (units.Hz * units.m ** 2))

units.add_enabled_units([semicircle, solar_flux])
