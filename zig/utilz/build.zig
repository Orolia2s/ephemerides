const std = @import("std");

pub fn build(b: *std.Build) !void {
    var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    defer arena.deinit();

    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{ .preferred_optimize_mode = .ReleaseSafe });

    const ublox = b.dependency("ublox_parser", .{ .target = target });
    const o2s = b.dependency("libo2s", .{ .target = target });
    const blackmagic = b.dependency("blackmagic", .{});
    const argsParser = b.dependency("args", .{ .target = target, .optimize = optimize });
    const ansiterm = b.dependency("ansi_term", .{ .target = target, .optimize = optimize });
    const units = b.dependency("unitz", .{ .target = target, .optimize = optimize });

    const include_all = b.addWriteFile("ublox.h",
        \\#include <ublox_enums.h>
        \\#include <ublox_messages.h>
        \\#include <ublox_reader.h>
        \\#include <fcntl.h>
    );

    const bind = b.addTranslateC(.{
        .root_source_file = try include_all.getDirectory().join(arena.allocator(), "ublox.h"),
        .target = target,
        .optimize = optimize,
    });
    bind.addIncludePath(ublox.path("include"));
    bind.addIncludePath(o2s.path("include"));
    bind.addIncludePath(blackmagic.path("include"));
    const generated = b.addInstallFile(bind.getOutput(), "translated.zig");
    b.getInstallStep().dependOn(&generated.step);

    const utils = b.addModule("utilz", .{
        .root_source_file = b.path("root.zig"),
        .target = target,
        .optimize = optimize,
    });
    const o2z = bind.addModule("o2s");
    utils.addImport("o2s", o2z);
    utils.linkLibrary(ublox.artifact("ublox_parser"));
    utils.addImport("unitz", units.module("unitz"));

    const exe = b.addExecutable(.{
        .name = "ublox_dumper",
        .root_source_file = b.path("main.zig"),
        .target = target,
        .optimize = optimize,
    });
    exe.root_module.addImport("utils", utils);
    exe.root_module.addImport("o2s", o2z);
    exe.root_module.addImport("args", argsParser.module("args"));
    exe.root_module.addImport("ansi_term", ansiterm.module("ansi_term"));
    b.getInstallStep().dependOn(&b.addInstallArtifact(exe, .{}).step);

    { // Run
        const run_step = b.step("run", "Run the app");
        const run_cmd = b.addRunArtifact(exe);

        if (b.args) |args| {
            run_cmd.addArgs(args);
        }
        run_step.dependOn(&run_cmd.step);
    }
    { // Test
        const test_step = b.step("test", "Run unit tests");
        const unit_tests = b.addTest(.{
            .root_module = utils,
        });
        test_step.dependOn(&b.addRunArtifact(unit_tests).step);
    }
    { // Documentation
        const docs_step = b.step("docs", "Build the project documentation");

        const docs_obj = b.addObject(.{
            .name = "ephemerides_utilities",
            .root_module = utils,
        });

        const install_docs = b.addInstallDirectory(.{
            .source_dir = docs_obj.getEmittedDocs(),
            .install_dir = .prefix,
            .install_subdir = "docs",
        });
        docs_step.dependOn(&install_docs.step);
    }
}
