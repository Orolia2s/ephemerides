const std = @import("std");
const o2s = @import("o2s");
const utils = @import("utils");
const argsParser = @import("args");
const terminal = @import("ansi_term");

const Mode = enum {
    header,
    message,
    constellation,
    satellite,
};

const Options = struct {
    baudrate: ?i64 = null,
    mode: Mode = .message,
    help: bool = false,

    pub const shorthands = .{ .b = "baudrate", .m = "mode", .h = "help" };
    pub const meta = .{
        .usage_summary = "PATH [-b UINT] [-m {header|message|constellation|satellite}]",
        .full_text = "Parse ublox stream",
        .option_docs = .{
            .baudrate = "The specified path is a serial port and must be configured with this baudrate",
            .mode =
            \\What to output:
            \\                     'header' to dump class, type and length of all messages,
            \\                     'message' to show ublox content of all messages",
            \\                     'constellation' to show how many subframe have been received per constellation,
            \\                     'satellite' to show how many subframe have been received per satellite per constellation (2D table),
            ,
            .help = "Print this help",
        },
    };
};

var buffered_out = std.io.bufferedWriter(std.io.getStdOut().writer());
const out = buffered_out.writer();

var gpa_instance: std.heap.GeneralPurposeAllocator(.{}) = .{};
const gpa = gpa_instance.allocator();

pub fn main() !void {
    const options = try argsParser.parseForCurrentProcess(Options, gpa, .print);
    defer options.deinit();

    if (options.options.help) {
        try argsParser.printHelp(Options, "ublox dumper", out);
        try buffered_out.flush();
        return;
    }

    for (options.positionals) |arg| {
        if (options.options.baudrate) |baudrate| {
            try utils.read_ublox_from(arg, .{ .is_serial_port = true, .baudrate = baudrate, .callback = get_callback(options.options.mode) });
        } else {
            try utils.read_ublox_from(arg, .{ .is_serial_port = false, .callback = get_callback(options.options.mode) });
        }
    }
    try out.writeByte('\n');
    try buffered_out.flush();
}

fn get_callback(mode: Mode) utils.UbloxCallback {
    return switch (mode) {
        .header => c_dump_header,
        .message => c_dump_message,
        .constellation => c_count_constellations,
        .satellite => c_count_satellite,
    };
}

fn c_dump_header(message: [*c]o2s.ublox_message_t) callconv(.C) void {
    dump_header(message) catch unreachable;
}
fn dump_header(message: *o2s.ublox_message_t) !void {
    var string: o2s.string_t = o2s.ublox_header_tostring(message);
    defer o2s.string_clear(&string);

    try out.writeByte('{');
    try out.print("{s}", .{o2s.string_to_cstring(&string)});
    try out.writeAll("}\n---\n");
    try buffered_out.flush();
}

fn c_dump_message(message: [*c]o2s.ublox_message_t) callconv(.C) void {
    dump_message(message) catch unreachable;
}
fn dump_message(message: *o2s.ublox_message_t) !void {
    var string: o2s.string_t = outer: switch (message.ublox_class) {
        o2s.MON => switch (message.type) {
            o2s.HW => o2s.ublox_monitoring_hardware_tostring(@ptrCast(message)),
            o2s.RF => o2s.ublox_monitoring_rf_tostring(@ptrCast(message)),
            else => continue :outer 0,
        },
        o2s.RXM => switch (message.type) {
            o2s.SFRBX => o2s.ublox_navigation_data_tostring(@ptrCast(message)),
            else => continue :outer 0,
        },
        o2s.NAV => switch (message.type) {
            o2s.PVT => o2s.ublox_position_time_tostring(@ptrCast(message)),
            else => continue :outer 0,
        },
        else => o2s.ublox_header_tostring(message),
    };
    defer o2s.string_clear(&string);

    try out.writeByte('{');
    try out.print("{s}", .{o2s.string_to_cstring(&string)});
    try out.writeAll("}\n---\n");
    try buffered_out.flush();
}

var constellation_count: std.AutoArrayHashMapUnmanaged(o2s.ublox_constellation, u32) = .empty;

fn c_count_constellations(message: [*c]o2s.ublox_message_t) callconv(.C) void {
    if (message.*.ublox_class != o2s.RXM or message.*.type != o2s.SFRBX)
        return;
    count_constellations(@ptrCast(message)) catch unreachable;
}
fn count_constellations(subframe: *o2s.struct_ublox_navigation_data) !void {
    {
        const entry = try constellation_count.getOrPutValue(gpa, subframe.constellation, 0);
        entry.value_ptr.* += 1;
    }

    try terminal.cursor.setCursorColumn(out, 0);
    var ite = constellation_count.iterator();
    while (ite.next()) |entry| {
        try terminal.format.updateStyle(out, .{ .font_style = .{ .bold = entry.key_ptr.* == subframe.constellation } }, null);
        try out.print("{s}: {}  ", .{ o2s.ublox_constellation_to_cstring(entry.key_ptr.*), entry.value_ptr.* });
    }
    try buffered_out.flush();
}

var satellite_count: std.AutoArrayHashMapUnmanaged(o2s.ublox_constellation, std.AutoArrayHashMapUnmanaged(u8, u32)) = .empty;

fn c_count_satellite(message: [*c]o2s.ublox_message_t) callconv(.C) void {
    if (message.*.ublox_class != o2s.RXM or message.*.type != o2s.SFRBX)
        return;
    count_satellite(@ptrCast(message)) catch unreachable;
}
fn count_satellite(subframe: *o2s.struct_ublox_navigation_data) !void {
    {
        const constellation = try satellite_count.getOrPutValue(gpa, subframe.constellation, .empty);
        const satellite = try constellation.value_ptr.getOrPutValue(gpa, subframe.satellite, 0);
        satellite.value_ptr.* += 1;
    }

    try terminal.cursor.setCursorColumn(out, 0);
    var outer = satellite_count.iterator();
    while (outer.next()) |constellation| {
        try terminal.cursor.saveCursor(out);
        var inner = constellation.value_ptr.iterator();
        while (inner.next()) |satellite| {
            try terminal.cursor.cursorDown(out, 1);
            try terminal.format.updateStyle(out, .{ .font_style = .{
                .bold = (constellation.key_ptr.* == subframe.constellation and satellite.key_ptr.* == subframe.satellite),
                .underline = false,
            } }, null);
            try out.print("{c}{s}: {:4}", .{
                utils.prefix.get(std.mem.span(o2s.ublox_constellation_to_cstring(constellation.key_ptr.*))) orelse '?',
                if (satellite.key_ptr.* == 255) .{ '?', '?' } else std.fmt.digits2(satellite.key_ptr.*),
                satellite.value_ptr.*,
            });
            try terminal.cursor.cursorBackward(out, 9);
        }
        try terminal.cursor.restoreCursor(out);
        try terminal.format.updateStyle(out, .{ .font_style = .{ .underline = true } }, null);
        try out.print("{s:<16}", .{o2s.ublox_constellation_to_cstring(constellation.key_ptr.*)});
    }
    try buffered_out.flush();
}
