const std = @import("std");
const utils = @import("utils");
const o2s = @import("o2s");
const axe = @import("axe");
const icds = @import("generated.zig");

const GnssMessage = icds.GnssMessage;
const SubframeAccumulator = std.AutoArrayHashMapUnmanaged(Subframe.Key, Subframe);
const SatelliteAccumulator = std.AutoArrayHashMapUnmanaged(u8, SubframeAccumulator);
const MessageAccumulator = std.AutoArrayHashMapUnmanaged(GnssMessage, SatelliteAccumulator);

const log = axe.Axe(.{
    .format = "[%l%s%L] %m\n",
    .scope_format = " %",
    .loc_format = " %f:%F:%l",
});
pub const std_options: std.Options = .{ .logFn = log.log };

const Subframe = struct {
    id: ?u8 = null,
    page: ?u8 = null,
    satellite: u8,
    constellation: u8,
    message: GnssMessage,
    data: []u32,

    pub const Key = struct { subframe: u8, page: ?u8 };

    pub fn from_ublox(subframe: *o2s.struct_ublox_navigation_data) !Subframe {
        const multi_ptr: [*]o2s.struct_ublox_navigation_data = @ptrCast(subframe);
        const words: [*]u32 = @alignCast(@ptrCast(multi_ptr + 1));
        return .{ .satellite = subframe.satellite, .constellation = subframe.constellation, .message = try .from_ublox_message(subframe), .data = words[0..subframe.word_count] };
    }

    pub fn get_subframe_id(self: Subframe) !u8 {
        if (self.message == .L1OC)
            return self.data[4] & 0xff;
    }

    pub fn key(self: Subframe) Key {
        return .{ .subframe = self.id orelse unreachable, .page = self.page };
    }
};

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
    receive_ublox_subframe(@ptrCast(message)) catch unreachable;
}

fn receive_ublox_subframe(ublox: *o2s.struct_ublox_navigation_data) !void {
    if (ublox.constellation == o2s.GLONASS and ublox.satellite == 255) {
        log.debugAt(@src(), "Discarding subframe of unidentified GLONASS satellite", .{});
        return;
    }

    const subframe: Subframe = try .from_ublox(ublox);
    if (!accumulator.contains(subframe.message))
        std.log.info("First subframe of {s} {s}", .{ o2s.ublox_constellation_to_cstring(subframe.constellation), @tagName(subframe.message) });
    const satelliteAccumulator = (try accumulator.getOrPutValue(gpa, subframe.message, .empty)).value_ptr;
    if (!satelliteAccumulator.contains(subframe.satellite))
        std.log.info("First subframe of {c}{}", .{ utils.prefix.get(std.mem.span(o2s.ublox_constellation_to_cstring(subframe.constellation))) orelse '?', subframe.satellite });
    const subframeAccumulator = (try satelliteAccumulator.getOrPutValue(gpa, subframe.satellite, .empty)).value_ptr;
    try subframeAccumulator.put(gpa, subframe.key(), subframe);
}
