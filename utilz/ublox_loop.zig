const std = @import("std");
const o2s = @import("o2s");

const UbloxCallback = *const fn (message: [*c]o2s.ublox_message_t) callconv(.C) void;

const ReadUbloxOptions = struct {
    /// If this is true, the stream will be considered infinite, and the port will be configured
    is_serial_port: bool,
    /// If the file is a serial port, its baudrate needs to be configured
    baudrate: ?i64 = null,
    /// Function to call everytime a message is received
    callback: UbloxCallback = default_callback,
    /// Exit if no valid messages were received for this number of milliseconds
    timeout_ms: u32 = 1000,
};

const SerialPort = opaque {};
extern fn serial_new_readwrite(filename: [*:0]const u8) *SerialPort;
extern fn serial_make_raw(port: *SerialPort, baudrate: i64) bool;

/// Parse all RXM-SFRBX messages from the specified file.
pub fn read_ublox_from(path: [:0]const u8, options: ReadUbloxOptions) !void {
    var file: *o2s.ifstream_t = undefined;

    if (options.is_serial_port) {
        file = @alignCast(@ptrCast(serial_new_readwrite(path)));
    } else {
        file = try std.heap.c_allocator.create(o2s.ifstream_t);
        file.* = o2s.file_open(path, o2s.O_RDONLY);
    }
    defer {
        o2s.file_close(file);
        std.heap.c_allocator.destroy(file);
    }

    if (!file.opened)
        return error.UnableToOpenFile;
    if (options.is_serial_port and !serial_make_raw(@ptrCast(file), options.baudrate orelse return error.missingBaudrateForSerialPort))
        return error.UnableToConfigurePort;

    var ublox_reader = o2s.ublox_reader_init(&file.stream);
    defer o2s.ublox_reader_close(&ublox_reader);

    ublox_reader.timeout_ms = options.timeout_ms;
    if (!o2s.ublox_subscribe(&ublox_reader, options.callback))
        return error.OutOfMemory;
    if (!o2s.ublox_reader_loop(&ublox_reader))
        return error.UnableToStartTimer;
}

export fn default_callback(c_message: [*c]o2s.ublox_message_t) callconv(.C) void {
    const message: *o2s.ublox_message_t = c_message;
    var string: o2s.string_t = o2s.ublox_header_tostring(message);
    defer o2s.string_clear(&string);
    std.log.debug("Received a message: {s}", .{o2s.string_to_cstring(&string)});
}
