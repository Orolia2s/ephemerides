const std = @import("std");

fn BitReader(comptime word_count: usize, comptime WordType: type) type {
    return struct {
        words: [word_count]WordType,
        current_word: u16 = 0,
        current_bit: u8 = @bitSizeOf(WordType) - 1,
        bit_consumed: u16 = 0,

        const Self = @This();

        pub fn init(words: [word_count]WordType) Self {
            return .{ .words = words };
        }

        pub fn next(self: *Self) ?bool {
            if (self.current_word == self.words.len)
                return null;
            const mask: WordType = std.math.shl(WordType, 1, self.current_bit);
            const result = (self.words[self.current_word] & mask) != 0;
            if (self.current_bit == 0) {
                self.current_word += 1;
                self.current_bit = @bitSizeOf(WordType) - 1;
            } else {
                self.current_bit -= 1;
            }
            return result;
        }

        pub fn consume(self: *Self, count: u8, comptime Target: type) !Target {
            var result: Target = 0;

            for (0..count) |_| {
                const bit = self.next() orelse return error.NotEnoughBits;
                result <<= 1;
                if (bit)
                    result += 1;
            }
            return result;
        }
    };
}

test BitReader {
    var reader: BitReader(4, u16) = .init(.{ 0xcafe, 0xbabe, 0xdead, 0xbeef });
    try std.testing.expectEqual(0xc, reader.consume(4, u8));
    try std.testing.expectEqual(0xaf, reader.consume(8, u8));
    try std.testing.expectEqual(0xeBabe, reader.consume(20, u32));
    try std.testing.expectEqual(0xdead, reader.consume(16, u16));
    try std.testing.expectEqual(0xbee, reader.consume(12, u12));
    try std.testing.expectError(error.NotEnoughBits, reader.consume(5, u16));
}
