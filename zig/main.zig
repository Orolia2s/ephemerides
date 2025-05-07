const std = @import("std");
const utils = @import("utils");
const o2s = @import("o2s");
const axe = @import("axe");
const icds = @import("generated.zig");

const Constellation = icds.Constellation;
const GnssMessageType = icds.GnssMessageType;
const GnssSubframe = icds.GnssSubframe;
const Subframe = icds.Subframe;

const SatelliteKey = struct { id: u8, signal: GnssMessageType };
const SubframeAccumulator = std.AutoArrayHashMapUnmanaged(GnssSubframe.Key, GnssSubframe);
const SatelliteAccumulator = std.AutoArrayHashMapUnmanaged(SatelliteKey, SubframeAccumulator);

const log = axe.Axe(.{
    .format = "[%l%s%L] %m\n",
    .scope_format = " %",
    .loc_format = " %f:%F:%l",
});
pub const std_options: std.Options = .{ .logFn = log.log };

var gpa_instance: std.heap.GeneralPurposeAllocator(.{}) = .init;
const gpa = gpa_instance.allocator();
var accumulator: SatelliteAccumulator = .empty;

pub fn main() !void {
    defer _ = gpa_instance.deinit();
    var env = try std.process.getEnvMap(gpa);
    defer env.deinit();

    try log.init(gpa, null, &env);
    defer log.deinit(gpa);

    log.debugAt(@src(), "Starting", .{});
    try utils.read_ublox_from("/dev/ttyACM0", .{ .is_serial_port = true, .baudrate = 115200, .callback = c_ublox_callback });
}

fn c_ublox_callback(message: [*c]o2s.ublox_message_t) callconv(.C) void {
    if (message.*.ublox_class != o2s.RXM or message.*.type != o2s.SFRBX)
        return;
    const subframe: *o2s.struct_ublox_navigation_data = @ptrCast(message);
    receive_ublox_subframe(subframe) catch |err| {
        switch (err) {
            error.MissingMessage => log.warnAt(@src(), "Unsupported GNSS message: {s} {}", .{ o2s.ublox_constellation_to_cstring(subframe.constellation), subframe.signal }),
            else => log.errAt(@src(), "Error: {}", .{err}),
        }
    };
}

fn receive_ublox_subframe(ublox: *o2s.struct_ublox_navigation_data) !void {
    if (ublox.constellation == o2s.GLONASS and ublox.satellite == 255) {
        log.debugAt(@src(), "Discarding subframe of unidentified GLONASS satellite", .{});
        return;
    }

    const subframe: Subframe = try .from_ublox(ublox);
    const satKey: SatelliteKey = .{ .id = subframe.satellite, .signal = subframe.messageType };

    if (!accumulator.contains(satKey))
        std.log.info("First subframe of {s} {s}", .{ @tagName(subframe.constellation), @tagName(subframe.message) });
    const subframeAccumulator = (try accumulator.getOrPutValue(gpa, satKey, .empty)).value_ptr;
    if (!subframeAccumulator.contains(subframe.key))
        std.log.info("First subframe {} {?} of {c}{:02}", .{ subframe.key.subframe, subframe.key.page, utils.prefix.get(@tagName(subframe.constellation)) orelse '?', subframe.satellite });
    try subframeAccumulator.put(gpa, subframe.key, subframe.message);
}
