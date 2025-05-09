const std = @import("std");
const raylib = @import("raylib");

const Camera = raylib.Camera3D;
const Vector3 = raylib.Vector3;

const X: Vector3 = .{ .x = 1, .y = 0, .z = 0 };
const Y: Vector3 = .{ .x = 0, .y = 1, .z = 0 };
const Z: Vector3 = .{ .x = 0, .y = 0, .z = 1 };

pub fn main() anyerror!void {
    const screenWidth = 1200;
    const screenHeight = 600;

    raylib.initWindow(screenWidth, screenHeight, "Visualize GNSS satellite orbits");
    defer raylib.closeWindow();
    raylib.setTargetFPS(60);

    const earthPos: Vector3 = .{ .x = 0, .y = 0, .z = 0 };
    const earthMesh = raylib.genMeshSphere(1, 64, 64);
    var earthModel = try raylib.loadModelFromMesh(earthMesh);
    defer earthModel.unload();
    var earthImage = try raylib.loadImage("assets/earth_daymap.jpg");
    defer earthImage.unload();
    earthImage.flipVertical();
    earthImage.rotateCCW();
    const earthTexture = try raylib.loadTextureFromImage(earthImage);
    defer earthTexture.unload();
    earthModel.materials[0].maps[0].texture = earthTexture;
    earthModel.transform = raylib.Matrix.rotateX(90 * std.math.rad_per_deg);

    var camera: Camera = .{
        .position = .{ .x = 7, .y = 7, .z = 7 },
        .target = earthPos,
        .up = Y,
        .fovy = 70.0,
        .projection = .perspective,
    };

    while (!raylib.windowShouldClose()) {
        camera.update(.orbital);

        {
            raylib.beginDrawing();
            defer raylib.endDrawing();

            raylib.clearBackground(.black);
            {
                camera.begin();
                defer camera.end();

                earthModel.draw(earthPos, 1, .white);
                raylib.drawCircle3D(earthPos, 2.0, X.add(Y), 90.0, .light_gray);
                raylib.drawCircle3D(earthPos, 3.0, X, 90.0, .gray);
            }
        }
    }
}
