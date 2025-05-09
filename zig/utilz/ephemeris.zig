const std = @import("std");
const units = @import("units");
const q = units.quantities(f64);

const m = q.meter;
const rad = q.radian;
const unitless = q.one;
const semicircle = units.evalQuantity(f64, "180 * deg", .{});
const semicircle_per_s = units.evalQuantity(f64, "semicircle / s", .{ .semicircle = semicircle.unit });
const s = q.second;
const @"s/s" = units.evalQuantity(f64, "s / s", .{});
const @"s/s2" = units.evalQuantity(f64, "s / s^2", .{});
const @"m3/s2" = units.evalQuantity(f64, "m^3 / s^2", .{});
const @"rad/s" = units.evalQuantity(f64, "rad / s", .{});

const geocentric_gravitational_constant = 3.986004418e14;
const earth_mean_angular_velocity = 7.2921151467e-5;

/// Compute satellite current position
/// Reference: page 68 of https://www.gsc-europa.eu/sites/default/files/sites/all/files/Galileo_OS_SIS_ICD_v2.1.pdf
pub fn foo(raw: RawEphemeris) void {
    const A: m = .init(std.math.pow(f64, raw.square_root_of_semi_major_axis, 2));
    const mean_motion: @"rad/s" = .init(std.math.sqrt(geocentric_gravitational_constant / std.math.pow(f64, A.val(), 3)));
    const now: s = .init(std.time.timestamp());
    const time_from_epoch: s = now.sub(raw.reference_epoch);
    const corrected_mean_motion: @"rad/s" = mean_motion.add(raw.mean_motion_difference.to(@"rad/s"));
    const mean_anomaly: rad = raw.mean_anomaly.to(rad).add(corrected_mean_motion.mul(time_from_epoch));
    _ = mean_anomaly;
}

pub fn solve_kepler_equation(comptime epsilon: f64, eccentricity: f64, mean_anomaly: rad) rad {
    const M: f64 = mean_anomaly.val();
    var E: f64 = M;
    var delta: f64 = 1;
    var i: usize = 0;

    while (@abs(delta) > epsilon and i < 10) : (i += 1) {
        delta = (E - eccentricity * @sin(E) - M) / (1 - eccentricity * @cos(E));
        E -= delta;
    }
    return .init(E);
}

pub const RawEphemeris = struct {
    square_root_of_semi_major_axis: f64,
    eccentricity: f64,

    argument_of_perigee: semicircle,
    mean_anomaly: semicircle,
    inclination_angle: semicircle,
    ascending_node_longitude: semicircle,

    mean_motion_difference: semicircle_per_s,
    rate_of_inclination_angle: semicircle_per_s,
    rate_of_right_ascension: semicircle_per_s,

    argument_of_latitude_cosine_correction: rad, // Cuc
    argument_of_latitude_sine_correction: rad, // Cus
    inclination_angle_cosine_correction: rad, // Cic
    inclination_angle_sine_correction: rad, // Cis
    orbit_radius_cosine_correction: m, // Crc
    orbit_radius_sine_correction: m, // Crs

    clock_bias_correction: s,
    clock_drift_correction: @"s/s",
    clock_drift_rate_correction: @"s/s2",

    group_delay_differential: s,
};

test "solve_kepler_equation" {
    std.testing.expectApproxEqAbs(
        1.0084,
        solve_kepler_equation(1e-12, 0.01, .init(1)).val(),
        1e-5,
    );
}
