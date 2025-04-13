const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{ .preferred_optimize_mode = .ReleaseSafe });

    const ublox = b.dependency("ublox_parser", .{ .target = target });
    const bind = b.addTranslateC(.{
        .root_source_file = ublox.path("include/ublox_reader.h"),
        .target = target,
        .optimize = .Debug,
    });

    const utils = b.addModule("utilz", .{
        .root_source_file = b.path("root.zig"),
        .target = target,
        .optimize = optimize,
    });
    utils.addImport("o2s", bind.createModule());
}
