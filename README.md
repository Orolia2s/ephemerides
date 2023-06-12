# Ephemerides Generator

## Generate markdown ICDs

```bash
make
```

## Parse GNSS signals

```bash
make run
```

## Navigation Data

The navigation data contain all the parameters required for the user to compute a complete position, velocity and time (PVT) solution.
They are stored on board each satellite with a validity duration and broadcast world-wide by all the satellites.
The 4 types of data needed to perform positioning are:
 - Ephemeris parameters, which are needed to indicate the position of the satellite to the user receiver
 - Time and clock correction parameters which are needed to compute pseudo-range
 - Service parameters which are needed to identify the set of navigation data, satellites, and indicators of the signal health
 - Almanac parameters, which are needed to indicate the position of all the satellites in the constellation with a reduced accuracy

### Ephemeris

Given an inertial frame of reference and an arbitrary epoch (a specified point in time),
exactly six parameters are necessary to unambiguously define an arbitrary and unperturbed orbit,
as the problem contains six degrees of freedom.

These correspond to the three spatial dimensions which define position
(x, y, z in a Cartesian coordinate system),
plus the velocity in each of these dimensions.
These can be described as orbital state vectors,
but this is often an inconvenient way to represent an orbit,
which is why Keplerian elements are commonly used instead.
(source: [Orbital elements](https://en.wikipedia.org/wiki/Orbital_elements))

Here are the 6 traditional Keplerian elements, along with a reference time:

| Notation | Name | Description |
|:--------:|:-----|:------------|
| $t_{0e}$ | Ephemeris reference time | |
| $e$ | Eccentricity | shape of the ellipse, describing how much it is elongated compared to a circle |
| $A$ | Semimajor axis | the sum of the periapsis and apoapsis distances divided by two |
| $i$ | Inclination | vertical tilt of the ellipse with respect to the reference plane, measured at the ascending node |
| $\Omega$ | Longitude of the ascending node | horizontally orients the ascending node of the ellipse |
| $\omega$ | Argument of periapsis | defines the orientation of the ellipse in the orbital plane, as an angle measured from the ascending node to the periapsis |
| $v$ | True anomaly | defines the position of the orbiting body along the ellipse at the epoch |

However, in practice the orbit is perturbed, so more than 6 parameters are transmitted.

Here are the parameters actually transmitted:
- $t_{0e}$
- $e$
- $\sqrt{A}$
- $i$
- $\dot{i}$ the derivatove of $i$
- $\Omega$
- $\dot{\Omega}$ the derivative of $\Omega$
- $\omega$
- $M$ Mean anomaly
- $\Delta_n$ the mean motion difference

The mean anomaly M is a mathematically convenient fictitious "angle" which varies linearly with time, but which does not correspond to a real geometric angle.
The mean motion can be seen as the derivative of the mean motion.

To find the mean motion:

$$ n_0 = \sqrt{\frac{\mu}{A^3}} $$

$$ n   = n_0 + \Delta_n $$

## Ordering

Regardless of the order bits are transmitted from the satellite to the receiver, ublox gives us the subframes as an array of 4-bytes little-endian unsigned integers
