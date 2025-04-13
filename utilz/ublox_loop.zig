const std = @import("std");

const o2s = @import("o2s");

const ReadUbloxOptions = struct {
    /// If this is true, the stream will be considered infinite, and the port will be configured
    is_serial_port: bool,
    /// If the file is a serial port, its baudrate needs to be configured
    baudrate: ?i64 = null,
};

/// Parse all RXM-SFRBX messages from the specified file.
pub fn read_ublox_from(path: []const u8, options: ReadUbloxOptions) !void {
    var file: o2s.ifstream_t = undefined;
    if (options.is_serial_port) {
        const port: o2s.serial_port_t = o2s.serial_open_readwrite(path);
        errdefer o2s.serial_close(&port);
        o2s.serial_make_raw(&port, options.baudrate orelse return error.missingBaudrateForSerialPort);
        file = port.file;
    } else {
        file = o2s.file_open(path, o2s.O_RDONLY);
    }
    defer o2s.file_close(&file);

    var ublox_reader = o2s.ublox_reader_init(&file.stream);
    defer o2s.ublox_reader_close(&ublox_reader);

    o2s.ublox_subscribe(&ublox_reader, &ublox_callback);
    o2s.ublox_reader_loop(&ublox_reader);
}

export fn ublox_callback(message: *o2s.ublox_message_t) callconv(.C) void {
    if (message.ublox_class == o2s.RXM and message.type == o2s.SFRBX) {
        std.debug.print("Got one");
    }
}
