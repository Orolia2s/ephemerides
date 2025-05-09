const std = @import("std");
const reader = @import("bit_reader.zig");
const ublox = @import("ublox_loop.zig");
const ephemeris = @import("ephemeris.zig");

pub const SimpleBitReader = reader.SimpleBitReader;
pub const SkippingBitReader = reader.SkippingBitReader;
pub const read_ublox_from = ublox.read_ublox_from;
pub const UbloxCallback = ublox.UbloxCallback;

/// Single letter used as prefix of space vehicle number to specify its constellation
pub const prefix: std.StaticStringMap(u8) = .initComptime(.{
    .{ "GPS", 'G' },
    .{ "Galileo", 'E' },
    .{ "BeiDou", 'C' },
    .{ "GLONASS", 'R' },
});

test {
    std.testing.refAllDeclsRecursive(@This());
}
