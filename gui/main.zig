const raylib = @import("raylib");

const Camera = raylib.Camera3D;
const Vector3 = raylib.Vector3;

const X: Vector3 = .{ .x = 1, .y = 0, .z = 0 };
const Y: Vector3 = .{ .x = 0, .y = 1, .z = 0 };
const Z: Vector3 = .{ .x = 0, .y = 0, .z = 1 };

pub fn main() anyerror!void {
    const screenWidth = 1200;
    const screenHeight = 600;

    const earthPos: Vector3 = .{ .x = 0, .y = 0, .z = 0 };

    raylib.initWindow(screenWidth, screenHeight, "Visualize GNSS satellite orbits");
    defer raylib.closeWindow();
    raylib.setTargetFPS(60);

    var camera: Camera = .{
        .position = .{ .x = 7, .y = 7, .z = 7 },
        .target = earthPos,
        .up = Y,
        .fovy = 70.0,
        .projection = .perspective,
    };

    while (!raylib.windowShouldClose()) {
        raylib.updateCamera(&camera, .orbital);

        {
            raylib.beginDrawing();
            defer raylib.endDrawing();

            raylib.clearBackground(.black);
            {
                camera.begin();
                defer camera.end();

                raylib.drawSphere(earthPos, 1.0, .blue);
                raylib.drawCircle3D(earthPos, 2.0, X.add(Y), 90.0, .gray);
            }

            raylib.drawText("Congrats! You created your first window!", 10, 20, 20, .light_gray);
        }
    }
}
