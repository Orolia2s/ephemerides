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

const Mode = enum { subframe, raw_ephemeris, ephemeris };
var mode: Mode = .subframe;

const Options = struct {
    baudrate: ?i64 = null,
    mode: Mode = .subframe,
    help: bool = false,

    pub const shorthands = .{ .b = "baudrate", .m = "mode", .h = "help" };
    pub const meta = .{
        .usage_summary = "PATH [-b UINT] [-m {subframe}]",
        .full_text = "Parse ublox stream",
        .option_docs = .{
            .baudrate = "The specified path is a serial port and must be configured with this baudrate",
            .mode =
            \\Choose what to output:
            \\                     'subframe': Dump individual subframes
            \\                     'raw_ephemeris': Dump the integer content of accumulated ephemerides
            \\                     'ephemeris': Dump the interpreted ephemerides
            ,
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
    defer {
        var iterator = accumulator.iterator();
        while (iterator.next()) |entry| entry.value_ptr.deinit(gpa);
        accumulator.deinit(gpa);
    }

    const options = try argsParser.parseForCurrentProcess(Options, gpa, .print);
    defer options.deinit();

    var env = try std.process.getEnvMap(gpa);
    defer env.deinit();

    try log.init(gpa, null, &env);
    defer log.deinit(gpa);

    if (options.options.help or options.positionals.len < 1) {
        if (!options.options.help)
            log.errAt(@src(), "Missing path of file / port to parse.", .{});
        try argsParser.printHelp(Options, "ephemerides", out);
        try buffered_out.flush();
        return;
    }

    mode = options.options.mode;
    log.infoAt(@src(), "Starting to parse ublox messages from '{s}' with arguments: {any}", .{ options.positionals[0], options.options });

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
            else => log.errAt(@src(), "Error: {s}. Subframe: {any}", .{ @errorName(err), subframe }),
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
    const subframeAccumulator = (try accumulator.getOrPutValue(gpa, satKey, .empty)).value_ptr;
    try subframeAccumulator.put(gpa, subframe.key, subframe.message);

    if (mode == .subframe) {
        try std.json.stringify(subframe, .{}, out);
        try out.writeAll("\n---\n");
        try buffered_out.flush();
        return;
    }

    if (subframe.messageType == .LNAVL and subframe.key.subframe == 3) {
        if (subframeAccumulator.get(.{ .subframe = 1 })) |first| {
            if (first.LNAVL.header.time_of_week != subframe.message.LNAVL.header.time_of_week - 2)
                return;
            if (subframeAccumulator.get(.{ .subframe = 2 })) |second| {
                if (second.LNAVL.header.time_of_week != subframe.message.LNAVL.header.time_of_week - 1)
                    return;
                log.info("{s}: Ephemeris of {s} {} (TOW: {})", .{ @tagName(subframe.messageType), @tagName(subframe.constellation), subframe.satellite, first.LNAVL.header.time_of_week });
                if (mode == .raw_ephemeris) {
                    try std.json.stringify(.{ first.LNAVL, second.LNAVL, subframe.message.LNAVL }, .{}, out);
                } else {}
                try out.writeAll("\n---\n");
                try buffered_out.flush();
            }
        }
    }
    if (subframe.messageType == .D1 and subframe.key.subframe == 3) {
        if (subframeAccumulator.get(.{ .subframe = 1 })) |first| {
            if (first.D1.header.time_of_week != subframe.message.D1.header.time_of_week - 12)
                return;
            if (subframeAccumulator.get(.{ .subframe = 2 })) |second| {
                if (second.D1.header.time_of_week != subframe.message.D1.header.time_of_week - 6)
                    return;
                log.info("{s}: Ephemeris of {s} {} (TOW: {})", .{ @tagName(subframe.messageType), @tagName(subframe.constellation), subframe.satellite, first.D1.header.time_of_week });
                if (mode == .raw_ephemeris) {
                    try std.json.stringify(.{ first.D1, second.D1, subframe.message.D1 }, .{}, out);
                } else {}
                try out.writeAll("\n---\n");
                try buffered_out.flush();
            }
        }
    }
}
