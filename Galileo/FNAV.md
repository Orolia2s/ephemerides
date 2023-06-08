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
|$\text{SV}_{\text{ID}}$|satellite_id|6|||
|$\text{IOD}_{\text{nav}}$|issue_of_data_ephemeris|10|||
|$t_{oc}$|time_of_clock|14|60|$\mathrm{s}$|
|$a_{f0}$|clock_bias_correction|$^*31$|$2^{-34}$|$\mathrm{s}$|
|$a_{f1}$|clock_drift_correction|$^*21$|$2^{-46}$|$\mathrm{}$|
|$a_{f2}$|clock_drift_rate_correction|$^*6$|$2^{-59}$|$\mathrm{\frac{1}{s}}$|
|$\text{SISA}$|_ignored_|8|||
|$a_{i0}$|ionisation_level_1st_order|11|$2^{-2}$|$\mathrm{sfu}$|
|$a_{i1}$|ionisation_level_2nd_order|$^*11$|$2^{-8}$|$\mathrm{\frac{sfu}{{}^{\circ}}}$|
|$a_{i2}$|ionisation_level_3rd_order|$^*14$|$2^{-15}$|$\mathrm{\frac{sfu}{deg^{2}}}$|
|$\text{SF}_1$|ionospheric_disturbance_region_1|1|||
|$\text{SF}_2$|ionospheric_disturbance_region_2|1|||
|$\text{SF}_3$|ionospheric_disturbance_region_3|1|||
|$\text{SF}_4$|ionospheric_disturbance_region_4|1|||
|$\text{SF}_5$|ionospheric_disturbance_region_5|1|||
|$\text{BGD}$|broadcast_group_delay|$^*10$|$2^{-32}$|$\mathrm{s}$|
|$\text{E5a}_{\text{HS}}$|_ignored_|2|||
|$\text{WN}$|week_number|12|||
|$\text{TOW}$|time_of_week|20|||
|$\text{E5a}_{\text{DVS}}$|_ignored_|1|||
||_ignored_|26|||

## Subframe 2

Ephemeris (1/3) and GST

208 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{IOD}_{\text{nav}}$|issue_of_data_ephemeris|10|||
|$M_0$|mean_anomaly|$^*32$|$2^{-31}$|$\mathrm{semicircle}$|
|$\dot{\Omega}$|rate_of_right_ascension|$^*24$|$2^{-43}$|$\mathrm{\frac{semicircle}{s}}$|
|$e$|eccentricity|32|$2^{-33}$||
|$\sqrt{A}$|square_root_of_semi_major_axis|32|$2^{-19}$|$\mathrm{m^{1/2}}$|
|$\Omega_0$|ascending_node_longitude|$^*32$|$2^{-31}$|$\mathrm{semicircle}$|
|$\dot{i}$|rate_of_inclination_angle|$^*14$|$2^{-43}$|$\mathrm{\frac{semicircle}{s}}$|
|$\text{WN}$|week_number|12|||
|$\text{TOW}$|time_of_week|20|||

## Subframe 3

Ephemeris (2/3) and GST

208 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{IOD}_{\text{nav}}$|issue_of_data_ephemeris|10|||
|$i_0$|inclination_angle|$^*32$|$2^{-31}$|$\mathrm{semicircle}$|
|$\omega$|argument_of_perigee|$^*32$|$2^{-31}$|$\mathrm{semicircle}$|
|$\Delta_n$|mean_motion_difference|$^*16$|$2^{-43}$|$\mathrm{\frac{semicircle}{s}}$|
|$C_{uc}$|argument_of_latitude_cosine_correction|$^*16$|$2^{-29}$|$\mathrm{rad}$|
|$C_{us}$|argument_of_latitude_sine_correction|$^*16$|$2^{-29}$|$\mathrm{rad}$|
|$C_{rc}$|orbit_radius_cosine_correction|$^*16$|$2^{-5}$|$\mathrm{m}$|
|$C_{rs}$|orbit_radius_sine_correction|$^*16$|$2^{-5}$|$\mathrm{m}$|
|$t_{oe}$|ephemeris_reference_time|14|60|$\mathrm{s}$|
|$\text{WN}$|week_number|12|||
|$\text{TOW}$|time_of_week|20|||
||_ignored_|8|||

## Subframe 4

Ephemeris (3/3), GST-UTC conversion, GST-GPS conversion and TOW

208 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{IOD}_{\text{nav}}$|issue_of_data_ephemeris|10|||
|$C_{ic}$|inclination_angle_cosine_correction|$^*16$|$2^{-29}$|$\mathrm{rad}$|
|$C_{is}$|inclination_angle_sine_correction|$^*16$|$2^{-29}$|$\mathrm{rad}$|
|$A_0$|galileo_bias_correction|32|||
|$A_1$|galileo_drift_correction|24|||
|$\Delta{}t_{Ls}$|leap_seconds_delta|8|||
|$t_{0t}$|_ignored_|8|||
|$\text{WN}_{0t}$|_ignored_|8|||
|$\text{WN}_{\text{LSF}}$|future_leap_seconds_week_number|8|||
|$\text{DN}$|future_leap_seconds_day_number|3|||
|$\Delta{}t_{\text{LSF}}$|future_leap_seconds_delta|8|||
|$t_{0G}$|_ignored_|8|||
|$A_{0G}$|gps_bias_correction|16|||
|$A_{1G}$|gps_drift_correction|12|||
|$\text{WN}_{0G}$|_ignored_|6|||
|$\text{TOW}$|time_of_week|20|||
||_ignored_|5|||
