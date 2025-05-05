const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const utils = b.dependency("ephemerides_utilities", .{ .target = target });
    const axe = b.dependency("axe", .{ .target = target, .optimize = optimize });

    const exe_mod = b.createModule(.{
        .root_source_file = b.path("main.zig"),
        .target = target,
        .optimize = optimize,
    });
    exe_mod.addImport("utils", utils.module("utilz"));
    exe_mod.addImport("o2s", utils.module("o2s"));
    exe_mod.addImport("axe", axe.module("axe"));
    const exe = b.addExecutable(.{
        .name = "ephemerides",
        .root_module = exe_mod,
    });
    b.installArtifact(exe);

    { // Run
        const run_step = b.step("run", "Run the app");
        const run_cmd = b.addRunArtifact(exe);
        run_cmd.step.dependOn(b.getInstallStep());
        if (b.args) |args| {
            run_cmd.addArgs(args);
        }
        run_step.dependOn(&run_cmd.step);
    }
}
