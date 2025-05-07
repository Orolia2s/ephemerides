const std = @import("std");

pub fn SimpleBitReader(comptime word_count: usize, comptime WordType: type) type {
    return struct {
        words: [word_count]WordType,
        bit_consumed: u16 = 0,

        const Self = @This();

        pub fn init(words: [word_count]WordType) Self {
            return .{ .words = words };
        }

        pub fn next(self: *Self) ?bool {
            const word = @divTrunc(self.bit_consumed, @bitSizeOf(WordType));
            const bit = @bitSizeOf(WordType) - 1 - @mod(self.bit_consumed, @bitSizeOf(WordType));

            if (word == self.words.len)
                return null;
            const mask: WordType = std.math.shl(WordType, 1, bit);
            self.bit_consumed += 1;
            return (self.words[word] & mask) != 0;
        }

        pub fn consume(self: *Self, count: u8, comptime Target: type) !Target {
            var result: Target = 0;

            for (0..count) |_| {
                result <<= 1;
                if (self.next() orelse return error.NotEnoughBits)
                    result += 1;
            }
            return result;
        }
    };
}

pub fn SkippingBitReader(comptime word_count: usize, comptime WordType: type, comptime to_skip: [word_count]u8, comptime to_keep: [word_count]u8) type {
    return struct {
        words: [word_count]WordType,
        current_word: u16 = 0,
        current_bit: u8 = @bitSizeOf(WordType) - 1 - to_skip[0],
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
            if (self.current_bit == @bitSizeOf(WordType) - to_skip[self.current_word] - to_keep[self.current_word]) {
                self.current_word += 1;
                if (self.current_word != self.words.len)
                    self.current_bit = @bitSizeOf(WordType) - 1 - to_skip[self.current_word];
            } else {
                self.current_bit -= 1;
            }
            self.bit_consumed += 1;
            return result;
        }

        pub fn consume(self: *Self, count: u8, comptime Target: type) !Target {
            var result: Target = 0;

            for (0..count) |_| {
                result = std.math.shl(Target, result, 1);
                if (self.next() orelse return error.NotEnoughBits)
                    result += 1;
            }
            return result;
        }
    };
}

test SimpleBitReader {
    var reader: SimpleBitReader(4, u16) = .init(.{ 0xcafe, 0xbabe, 0xdead, 0xbeef });
    try std.testing.expectEqual(0xc, reader.consume(4, u8));
    try std.testing.expectEqual(4, reader.bit_consumed);
    try std.testing.expectEqual(-81, reader.consume(8, i8)); // 0xaf = 128 + 47 unsigned, -128 + 47 signed
    try std.testing.expectEqual(12, reader.bit_consumed);
    try std.testing.expectEqual(0xeBabe, reader.consume(20, u32));
    try std.testing.expectEqual(32, reader.bit_consumed);
    try std.testing.expectEqual(0xdead, reader.consume(16, u16));
    try std.testing.expectEqual(48, reader.bit_consumed);
    try std.testing.expectEqual(0xbee, reader.consume(12, u12));
    try std.testing.expectError(error.NotEnoughBits, reader.consume(5, u16));
    try std.testing.expectEqual(64, reader.bit_consumed);
}

test SkippingBitReader {
    var reader: SkippingBitReader(4, u16, .{ 8, 4, 0, 12 }, .{ 4, 12, 12, 4 }) = .init(.{ 0xcafe, 0xbabe, 0xdead, 0xbeef });
    try std.testing.expectEqual(0xfab, reader.consume(12, u16));
    try std.testing.expectEqual(12, reader.bit_consumed);
    try std.testing.expectEqual(-2, reader.consume(4, i4)); // 0xe = 8 + 6 unsigned, -8 + 6 signed
    try std.testing.expectEqual(16, reader.bit_consumed);
    try std.testing.expectEqual(0xdeaf, reader.consume(16, u16));
    try std.testing.expectEqual(32, reader.bit_consumed);
    try std.testing.expectError(error.NotEnoughBits, reader.consume(1, u8));
}

test "Smol" {
    var reader: SkippingBitReader(2, u16, .{ 8, 4 }, .{ 4, 12 }) = .init(.{ 0xcafe, 0xbabe });
    try std.testing.expectEqual(0xf, reader.consume(4, u4));
    try std.testing.expectEqual(2, reader.consume(2, u2));
    try std.testing.expectEqual(1, reader.consume(1, u1));
    try std.testing.expectEqual(0, reader.consume(1, u1));
}
