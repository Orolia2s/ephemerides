const std = @import("std");
const reader = @import("bit_reader.zig");
const ublox = @import("ublox_loop.zig");

pub const SimpleBitReader = reader.SimpleBitReader;
pub const SkippingBitReader = reader.SkippingBitReader;
pub const read_ublox_from = ublox.read_ublox_from;
pub const UbloxCallback = ublox.UbloxCallback;

pub const prefix: std.StaticStringMap(u8) = .initComptime(.{
    .{ "GPS", 'G' },
    .{ "Galileo", 'E' },
    .{ "BeiDou", 'C' },
    .{ "GLONASS", 'R' },
});
