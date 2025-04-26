# Ephemerides utilities

This zig module contains code to be used by the generated ephemerides zig parser.

## u-blox dumper

There is also an executable that can help quickly visualize what your GNSS receiver outputs.

```shell
zig build run -- --help
```

The first paramter to provide is the path the receiver's serial port, or a file containing pre-recorded ublox messages.

If the file is a serial port, provide the baudrate via the `--baudrate` option.

Finally, specify a `--mode` option to choose what to display:

### Header

Just print the header of each ublox message received as a YAML stream

```console
$ zig build run -- /dev/ttyACM0 --baudrate 115200 --mode header
{group: RXM, type: RAWX, length: 368}
---
{group: NAV, type: PVT, length: 92}
---
{group: NAV, type: CLOCK, length: 20}
---
{group: MON, type: RF, length: 52}
---
```

### Message

Print the content of certain messages like `NAV-PVT`, `MON-RF` and `MON-HW`, and the header of other messages, as a YAML stream.

```console
$ zig build run -- /dev/ttyACM0 --baudrate 115200  --mode message
{group: MON, type: RF, length: 52, version: 0, block_count: 2, blocks: [{ID: 0, jamming_state: unknown, antenna_status: unknown, antenna_power: unknown, post_status: 0, noise_per_ms: 79, agc_count: 4563, jam_level: 5, offset_i: 8, magnitude_i: 139, offset_q: 5, magnitude_q: 145},{ID: 0, jamming_state: unknown, antenna_status: unknown, antenna_power: unknown, post_status: 0, noise_per_ms: 35, agc_count: 4212, jam_level: 6, offset_i: 11, magnitude_i: 160, offset_q: 5, magnitude_q: 151}]}
---
```

Don't hesitate to pipe the output to [yq](https://github.com/mikefarah/yq) to make it more readable
```console
$ zig build run -- /dev/ttyACM0 --baudrate 115200  --mode message | yq -P
group: MON
type: RF
length: 52
version: 0
block_count: 2
blocks:
  - ID: 0
    jamming_state: unknown
    antenna_status: unknown
    antenna_power: unknown
    post_status: 0
    noise_per_ms: 79
    agc_count: 4563
    jam_level: 5
    offset_i: 8
    magnitude_i: 139
    offset_q: 5
    magnitude_q: 145
  - ID: 0
    jamming_state: unknown
    antenna_status: unknown
    antenna_power: unknown
    post_status: 0
    noise_per_ms: 35
    agc_count: 4212
    jam_level: 6
    offset_i: 11
    magnitude_i: 160
    offset_q: 5
    magnitude_q: 151
---
```

### Constellation

Shows how many subframes were received per constellation.

Every time a subframe is received, the line is updated, and the constellation of that subframe is highlighted in bold.

```console
$ zig build run -- /dev/ttyACM0 --baudrate 115200 --mode constellation
Galileo: 47  GLONASS: 15  GPS: 15
```

### Satellite

Display a 2D table containing the number of subframes received per satellite.

The satellite of the latest subframe will be highlighted in bold.

```console
$ zig build run -- /dev/ttyACM0 --baudrate 115200 --mode satellite
GLONASS     BeiDou      GPS         Galileo
15: 106     23:  35     11:  34     13: 117
            25:   8     14:   8
                        20:   3
```
