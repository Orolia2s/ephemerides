# Ephemerides Generator

This repo is a proof of concept to show it is possible to represent GNSS messages in language-agnostic YAMLs, in order to generate code that parses such messages in any language.

## Requirements

- Building binaries requires [zig](https://ziglang.org/download/)
- The python package requires [uv](https://docs.astral.sh/uv/getting-started/installation)
- A pdf detailing GNSS ICDs can be generated with [typst](https://github.com/typst/typst/releases)

## Usage

```
uv run icd-manager --help
uv run icd-manager translate --help
uv run icd-manager parse --help
```

### Read the YAML ICDs

Each YAML can be translated to markdown for human verification:
```bash
make markdown
```

All YAMLs can be aggregated in a single PDF with extra information:
```bash
make pdf
open ephemerides.pdf
```

### Generate and compile a parser

```bash
make zig
./zig/zig-out/bin/ephemerides --help

#Parse from USB
./zig/zig-out/bin/ephemerides /dev/ttyACM0 --baudrate 115200
```

### Parse ublox stream from python

All subframes can be dumped as a YAML stream:
```bash
make parse PORT=test/two.ubx ARGS=--dump
```

You can pipe it in [yq](https://github.com/mikefarah/yq):
```bash
make --silent parse PORT=test/two.ubx ARGS=--dump | yq -P
```

## GNSS Messages list

For now only one message type per constellation has been transcribed:

| Status | Constellation | Name | Signal | Satellites | ICD |
|:------:|:--------------|:-----|:-------|-----------:|:----|
| ✅ | GPS | LNAV-L ($D$) | L1, L2 | PRN 1-32 | [gps.gov/icwg/IS-GPS-200N.pdf](https://www.gps.gov/technical/icwg/IS-GPS-200N.pdf) Appendix II
| | GPS | LNAV-U ($D$) | L1, L2 | PRN 33-63 | [gps.gov/icwg/IS-GPS-200N.pdf](https://www.gps.gov/technical/icwg/IS-GPS-200N.pdf) Appendix IV
| | GPS | CNAV ($D_C$) | L1, L2 | | [gps.gov/icwg/IS-GPS-200N.pdf](https://www.gps.gov/technical/icwg/IS-GPS-200N.pdf) Appendix III
| | GPS | L5 CNAV ($D_5$) | L5 | | [gps.gov/icwg/IS-GPS-705J.pdf](https://www.gps.gov/technical/icwg/IS-GPS-705J.pdf)
| | GPS | CNAV-2 (L1C) | L1 | | [gps.gov/icwg/IS-GPS-800J.pdf](https://www.gps.gov/technical/icwg/IS-GPS-800J.pdf)
| ✅ | Galileo | F/NAV | E5a-I | | [gsc-europa.eu/Galileo_OS_SIS_ICD_v2.1.pdf](https://www.gsc-europa.eu/sites/default/files/sites/all/files/Galileo_OS_SIS_ICD_v2.1.pdf) section 4.2
| | Galileo | I/NAV | E5b-I, E1-B | | [gsc-europa.eu/Galileo_OS_SIS_ICD_v2.1.pdf](https://www.gsc-europa.eu/sites/default/files/sites/all/files/Galileo_OS_SIS_ICD_v2.1.pdf) section 4.3
| ✅ | Glonass | | L1, L2 | | [unavco.org/ICD_GLONASS_5.0_en.pdf](https://www.unavco.org/help/glossary/docs/ICD_GLONASS_5.0_(2002)_en.pdf)
| ✅ | BeiDou | D1 | B1I, B3I | MEO/IGSO | [beidou.gov.cn/ICD/OpenServiceSignalB1I.pdf](http://en.beidou.gov.cn/SYSTEMS/ICD/201902/P020190227702348791891.pdf) [beidou.gov.cn/ICD/OpenServiceSignalB3I.pdf](http://en.beidou.gov.cn/SYSTEMS/ICD/201806/P020180608516798097666.pdf) 5.2
| | BeiDou | D2 | B1I, B3I | GEO | [beidou.gov.cn/ICD/OpenServiceSignalB1I.pdf](http://en.beidou.gov.cn/SYSTEMS/ICD/201902/P020190227702348791891.pdf) [beidou.gov.cn/ICD/OpenServiceSignalB3I.pdf](http://en.beidou.gov.cn/SYSTEMS/ICD/201806/P020180608516798097666.pdf) 5.3
| | BeiDou | B-CNAV1 | B1C | | [beidou.gov.cn/ICD/OpenServiceSignalB1C.pdf](http://en.beidou.gov.cn/SYSTEMS/ICD/201806/P020180608519640359959.pdf)
| | BeiDou | B-CNAV2 | B2a | | [beidou.gov.cn/ICD/OpenServiceSignalB2a.pdf](http://en.beidou.gov.cn/SYSTEMS/ICD/201806/P020180608518432765621.pdf)
| | BeiDou | B-CNAV3 | B2b-I | | [beidou.gov.cn/ICD/OpenServiceSignalB2b.pdf](http://en.beidou.gov.cn/SYSTEMS/ICD/202008/P020231201537880833625.pdf)

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
- $\dot{i}$ the derivative of $i$
- $\Omega$
- $\dot{\Omega}$ the derivative of $\Omega$
- $\omega$
- $M$ Mean anomaly
- $\Delta_n$ the mean motion difference

The mean anomaly M is a mathematically convenient fictitious "angle" which varies linearly with time, but which does not correspond to a real geometric angle.
The mean motion can be seen as the derivative of the mean anomaly.

## GNSS Receivers

For now only u-blox receivers are supported, and the YAMLs contain a section about how subframes are transmitted by ublox.
Note that the ICD mappings in the YAMLs are agnostic of the receiver, as they describe the raw message as it is emitted by the satellites.

### u-blox

For a list of GNSS messages supported by F9P receivers, see [u-blox.com/u-blox-F9-HPG-1.51_InterfaceDescription.pdf](https://content.u-blox.com/sites/default/files/documents/u-blox-F9-HPG-1.51_InterfaceDescription_UBXDOC-963802114-13124.pdf) section 1.5.4 page 20. To get raw messages we use the `RXM-SFRBX` messages. The general words layout per constellation is described in [u-blox.com/ZED-F9P_IntegrationManual_UBX.pdf](https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf) from page 74 to 81

#### Ordering

Regardless of the order bits are transmitted from the satellite to the receiver, ublox provides the subframes as an array of 4-bytes little-endian unsigned integers
