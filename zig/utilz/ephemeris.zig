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

pub const Ephemeris = struct {
    square_root_of_semi_major_axis: m,
    eccentricity: unitless,

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
