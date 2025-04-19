const std = @import("std");

const utils = @import("utils");

pub fn main() !void {
    try utils.read_ublox_from("../../test/sample_sfrbx.ubx", .{ .is_serial_port = false });
}
