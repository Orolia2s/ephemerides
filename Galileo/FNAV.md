# Galileo FNAV

Transmitted on the E5a-I signal, the F-band (1278.75 MHz)
is used for the transmission of Galileo System Time (GST)
and other system messages, such as almanacs and health status messages.

Note that compared to the ICD, the notion of page and subframe has been swapped here

## Header

6 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{Type}$|subframe_id|6|||

## Subframe 1

SVID, clock correction, SISA, Ionospheric correction, BGD,
Signal health status, GST and Data validity status


208 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{SV}_{ID}$|satellite_id|6|||
|$\text{IOD}_{\text{nav}}$|issue_of_data_ephemeris|10|||
|$t_{oc}$|time_of_clock|14|||
|$a_{f0}$|clock_bias_correction|31|||
|$a_{f1}$|clock_drift_correction|21|||
|$a_{f2}$|clock_drift_rate_correction|6|||
|$\text{SISA}$|_ignored_|8|||
|$a_{i0}$|_ignored_|11|||
|$a_{i1}$|_ignored_|11|||
|$a_{i2}$|_ignored_|14|||
||ionospheric_disturbance_region_1|1|||
||ionospheric_disturbance_region_2|1|||
||ionospheric_disturbance_region_3|1|||
||ionospheric_disturbance_region_4|1|||
||ionospheric_disturbance_region_5|1|||
|$BGD$|_ignored_|10|||
|$\text{E5a}_{HS}$|_ignored_|2|||
|$\text{WN}$|week_number|12|||
|$\text{TOW}$|time_of_week|20|||
|$\text{E5a}_{DVS}$|_ignored_|1|||
||_ignored_|26|||

## Subframe 2

Ephemeris (1/3) and GST

208 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{IOD}_{\text{nav}}$|issue_of_data_ephemeris|10|||
|$M_0$|mean_anomaly|32|||
|$\dot{\Omega}$|rate_of_right_ascension|24|||
|$e$|eccentricity|32|||
|$\sqrt{A}$|square_root_of_semi_major_axis|32|||
|$\Omega_0$|ascending_node_longitude|32|||
|$\dot{i}$|rate_of_inclination_angle|14|||
|$\text{WN}$|week_number|12|||
|$\text{TOW}$|time_of_week|20|||

## Subframe 3

Ephemeris (2/3) and GST

176 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{IOD}_{\text{nav}}$|issue_of_data_ephemeris|10|||
|$i_0$|inclination_angle|32|||
|$\omega$|argument_of_perigee|32|||
|$\Delta_n$|mean_motion_difference|16|||
|$C_{uc}$|argument_of_latitude_cosine_correction|16|||
|$C_{us}$|argument_of_latitude_sine_correction|16|||
|$C_{rc}$|orbit_radius_cosine_correction|16|||
|$C_{rs}$|orbit_radius_sine_correction|16|||
|$t_{0e}$|ephemeris_reference_time|14|||
||_ignored_|8|||
