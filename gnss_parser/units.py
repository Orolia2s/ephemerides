from astropy import units

semicirle = units.def_unit('semicircle', 180 * deg)

units.set_enabled_aliases({'semicircle': semicircle})
