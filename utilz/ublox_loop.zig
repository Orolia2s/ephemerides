const std = @import("std");

const o2s = @import("o2s");

const ReadUbloxOptions = struct {
    /// If this is true, the stream will be considered infinite, and the port will be configured
    is_serial_port: bool,
    /// If the file is a serial port, its baudrate needs to be configured
    baudrate: ?i64 = null,
};

/// Parse all RXM-SFRBX messages from the specified file.
pub fn read_ublox_from(path: [:0]const u8, options: ReadUbloxOptions) !void {
    var file: o2s.ifstream_t = undefined;
    if (options.is_serial_port) {
        unreachable;
        //const port: o2s.serial_port_t = o2s.serial_open_readwrite(path);
        //errdefer o2s.serial_close(&port);
        //o2s.serial_make_raw(&port, options.baudrate orelse return error.missingBaudrateForSerialPort);
        //file = port.file;
    } else {
        file = o2s.file_open(path, o2s.O_RDONLY);
        if (!file.opened)
            return error.UnableToOpenFile;
    }
    defer o2s.file_close(&file);

    var ublox_reader = o2s.ublox_reader_init(&file.stream);
    defer o2s.ublox_reader_close(&ublox_reader);

    if (!o2s.ublox_subscribe(&ublox_reader, &ublox_callback))
        return error.OutOfMemory;
    if (!o2s.ublox_reader_loop(&ublox_reader))
        return error.UnableToStartTimer;
}

export fn ublox_callback(c_message: [*c]o2s.ublox_message_t) callconv(.C) void {
    const message: *o2s.ublox_message_t = c_message;
    if (message.ublox_class == o2s.RXM and message.type == o2s.SFRBX) {
        const subframe: *o2s.struct_ublox_navigation_data = @ptrCast(message);
        std.debug.assert(subframe.word_count * @sizeOf(u32) + @sizeOf(o2s.struct_ublox_navigation_data) - @sizeOf(o2s.struct_ublox_header) == message.length);
        std.debug.print("Got one: {any}\n", .{subframe});
        std.log.info("Received a subframe of {s}, {}\n", .{ o2s.ublox_constellation_to_cstring(subframe.constellation), subframe.signal });
    }
}
