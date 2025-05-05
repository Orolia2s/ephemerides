const std = @import("std");
const utils = @import("utils");
const o2s = @import("o2s");
const axe = @import("axe");
const icds = @import("generated.zig");

const GnssMessage = icds.GnssMessage;
const SubframeAccumulator = std.AutoArrayHashMapUnmanaged(SubframePage, []u8);
const SatelliteAccumulator = std.AutoArrayHashMapUnmanaged(u8, SubframeAccumulator);
const MessageAccumulator = std.AutoArrayHashMapUnmanaged(GnssMessage, SatelliteAccumulator);

const SubframePage = struct { subframe: u8, page: u8 };

const log = axe.Axe(.{
    .format = "[%l%s%L] %m\n",
    .scope_format = " %",
    .loc_format = " %f:%F:%l",
});
pub const std_options: std.Options = .{ .logFn = log.log };

var gpa_instance: std.heap.GeneralPurposeAllocator(.{}) = .init;
const gpa = gpa_instance.allocator();
var accumulator: MessageAccumulator = .empty;

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
    receive_subframe(@ptrCast(message)) catch unreachable;
}

fn receive_subframe(subframe: *o2s.struct_ublox_navigation_data) !void {
    if (subframe.constellation == o2s.GLONASS and subframe.satellite == 255) {
        log.debugAt(@src(), "Discarding subframe of unidentified GLONASS satellite", .{});
        return;
    }

    const message: GnssMessage = try .from_ublox_message(subframe);
    if (!accumulator.contains(message))
        std.log.info("First subframe of {s} {s}", .{ o2s.ublox_constellation_to_cstring(subframe.constellation), @tagName(message) });
    const satelliteAccumulator = try accumulator.getOrPutValue(gpa, message, .empty);
    if (!satelliteAccumulator.value_ptr.contains(subframe.satellite))
        std.log.info("First subframe of {c}{}", .{ utils.prefix.get(std.mem.span(o2s.ublox_constellation_to_cstring(subframe.constellation))) orelse '?', subframe.satellite });
}
