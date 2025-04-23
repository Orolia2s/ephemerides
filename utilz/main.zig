const std = @import("std");
const o2s = @import("o2s");
const utils = @import("utils");
const argsParser = @import("args");

const Mode = enum {
    header,
    message,
};

const Options = struct {
    baudrate: ?i64 = null,
    mode: Mode = .message,
    help: bool = false,

    pub const shorthands = .{ .b = "baudrate", .m = "mode", .h = "help" };
    pub const meta = .{
        .usage_summary = "PATH [-b UINT] [-m (header|message)]",
        .full_text = "Parse ublox stream",
        .option_docs = .{
            .baudrate = "The specified path is a serial port and must be configured with this baudrate",
            .mode = "What to output:\n\t\t\t'header' to dump class, type and length of all messages,\n\t\t\t'message' to show ublox content of all messages",
            .help = "Print this help",
        },
    };
};

fn get_callback(mode: Mode) utils.UbloxCallback {
    return switch (mode) {
        .header => dump_header,
        .message => dump_message,
    };
}

var buffered_out = std.io.bufferedWriter(std.io.getStdOut().writer());
const out = buffered_out.writer();

fn dump_header(c_message: [*c]o2s.ublox_message_t) callconv(.C) void {
    const message: *o2s.ublox_message_t = c_message;
    var string: o2s.string_t = o2s.ublox_header_tostring(message);
    defer o2s.string_clear(&string);

    out.writeByte('{') catch unreachable;
    out.print("{s}", .{o2s.string_to_cstring(&string)}) catch unreachable;
    _ = out.write("}\n---\n") catch unreachable;
    buffered_out.flush() catch unreachable;
}

fn dump_message(c_message: [*c]o2s.ublox_message_t) callconv(.C) void {
    const message: *o2s.ublox_message_t = c_message;
    var string: o2s.string_t = outer: switch (message.ublox_class) {
        o2s.MON => switch (message.type) {
            o2s.HW => o2s.ublox_monitoring_hardware_tostring(@ptrCast(c_message)),
            o2s.RF => o2s.ublox_monitoring_rf_tostring(@ptrCast(c_message)),
            else => continue :outer 0,
        },
        o2s.RXM => switch (message.type) {
            o2s.SFRBX => o2s.ublox_navigation_data_tostring(@ptrCast(c_message)),
            else => continue :outer 0,
        },
        o2s.NAV => switch (message.type) {
            o2s.PVT => o2s.ublox_position_time_tostring(@ptrCast(c_message)),
            else => continue :outer 0,
        },
        else => o2s.ublox_header_tostring(message),
    };
    defer o2s.string_clear(&string);

    out.writeByte('{') catch unreachable;
    out.print("{s}", .{o2s.string_to_cstring(&string)}) catch unreachable;
    _ = out.write("}\n---\n") catch unreachable;
    buffered_out.flush() catch unreachable;
}

pub fn main() !void {
    var gpa: std.heap.GeneralPurposeAllocator(.{}) = .{};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const options = try argsParser.parseForCurrentProcess(Options, allocator, .print);
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
}
