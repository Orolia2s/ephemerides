const std = @import("std");
//const raylib_build = @import("raylib");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const raylib = b.dependency("raylib", .{ .target = target, .optimize = optimize, .linux_display_backend = .X11, .shared = true });
    const rayzig = b.dependency("raylib_zig", .{ .target = target, .optimize = optimize });

    const exe_mod = b.createModule(.{
        .root_source_file = b.path("main.zig"),
        .target = target,
        .optimize = optimize,
        .link_libc = true,
    });
    exe_mod.addImport("raylib", rayzig.module("raylib"));
    exe_mod.addImport("raygui", rayzig.module("raygui"));
    const exe = b.addExecutable(.{
        .name = "ephemerides_visualizer",
        .root_module = exe_mod,
    });
    exe.linkLibrary(raylib.artifact("raylib"));
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
