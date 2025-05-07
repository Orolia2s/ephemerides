const std = @import("std");
const utils = @import("utils");
const o2s = @import("o2s");
const axe = @import("axe");
const argsParser = @import("args");
const icds = @import("generated.zig");

const Constellation = icds.Constellation;
const GnssMessageType = icds.GnssMessageType;
const GnssSubframe = icds.GnssSubframe;
const Subframe = icds.Subframe;

const SatelliteKey = struct { id: u8, signal: GnssMessageType };
const SubframeAccumulator = std.AutoArrayHashMapUnmanaged(GnssSubframe.Key, GnssSubframe);
const SatelliteAccumulator = std.AutoArrayHashMapUnmanaged(SatelliteKey, SubframeAccumulator);

const Options = struct {
    baudrate: ?i64 = null,
    help: bool = false,

    pub const shorthands = .{ .b = "baudrate", .h = "help" };
    pub const meta = .{
        .usage_summary = "PATH [-b UINT]",
        .full_text = "Parse ublox stream",
        .option_docs = .{
            .baudrate = "The specified path is a serial port and must be configured with this baudrate",
            .help = "Print this help",
        },
    };
};

const log = axe.Axe(.{
    .format = "[%l%s%L] %m\n",
    .scope_format = " %",
    .loc_format = " %f:%F:%l",
});
pub const std_options: std.Options = .{ .logFn = log.log };

var buffered_out = std.io.bufferedWriter(std.io.getStdOut().writer());
const out = buffered_out.writer();

var gpa_instance: std.heap.GeneralPurposeAllocator(.{}) = .init;
const gpa = gpa_instance.allocator();
var accumulator: SatelliteAccumulator = .empty;

const Warning = enum(u4) { MissingMessage };
var seen_warnings: std.StaticBitSet(@typeInfo(Warning).@"enum".fields.len) = .initEmpty();

inline fn show_warning_once(warning: Warning, text: []const u8, args: anytype) void {
    if (seen_warnings.isSet(@intFromEnum(warning)))
        return;
    seen_warnings.set(@intFromEnum(warning));
    std.log.warn(text, args);
}

pub fn main() !void {
    defer _ = gpa_instance.deinit();

    const options = try argsParser.parseForCurrentProcess(Options, gpa, .print);
    defer options.deinit();

    var env = try std.process.getEnvMap(gpa);
    defer env.deinit();

    try log.init(gpa, null, &env);
    defer log.deinit(gpa);

    if (options.options.help) {
        try argsParser.printHelp(Options, "ephemerides", out);
        try buffered_out.flush();
        return;
    }

    if (options.positionals.len < 1) {
        log.errAt(@src(), "Missing path of file / port to parse.", .{});
        try argsParser.printHelp(Options, "ephemerides", out);
        try buffered_out.flush();
        return;
    }

    log.infoAt(@src(), "Starting with arguments: {any}", .{options.options});

    try utils.read_ublox_from(
        options.positionals[0],
        if (options.options.baudrate) |baudrate|
            .{ .is_serial_port = true, .baudrate = baudrate, .callback = c_ublox_callback }
        else
            .{ .is_serial_port = false, .callback = c_ublox_callback },
    );
}

fn c_ublox_callback(message: [*c]o2s.ublox_message_t) callconv(.C) void {
    if (message.*.ublox_class != o2s.RXM or message.*.type != o2s.SFRBX)
        return;
    const subframe: *o2s.struct_ublox_navigation_data = @ptrCast(message);
    receive_ublox_subframe(subframe) catch |err| {
        switch (err) {
            error.MissingMessage => show_warning_once(.MissingMessage, "Unsupported GNSS message: {s} {}", .{ o2s.ublox_constellation_to_cstring(subframe.constellation), subframe.signal }),
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
        std.log.debug("First subframe of {s} {s}", .{ @tagName(subframe.constellation), @tagName(subframe.message) });
    const subframeAccumulator = (try accumulator.getOrPutValue(gpa, satKey, .empty)).value_ptr;
    if (!subframeAccumulator.contains(subframe.key))
        std.log.debug("First subframe {} {?} of {c}{:02}", .{ subframe.key.subframe, subframe.key.page, utils.prefix.get(@tagName(subframe.constellation)) orelse '?', subframe.satellite });
    try subframeAccumulator.put(gpa, subframe.key, subframe.message);

    try std.json.stringify(subframe, .{}, out);
    try out.writeAll("\n---\n");
    try buffered_out.flush();
}
