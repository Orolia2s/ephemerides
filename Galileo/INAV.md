# Galileo INAV

Translation from the ICD to the YAML:
- word type -> subframe_id

## Ublox words layout

Galileo INAV corresponds to gnssId 2, sigId 1, 5

Words|MSB skipped|Data bits|LSB skipped
:-|-:|-:|-:
1|2|30|0
2, 3|0|32|0
4|0|18|14
5|2|16|14
6 to 8|0|0|32

## Header

6 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{Type}$|subframe_id|6|||

## Subframe 1

Ephemeris (1/4)

122 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{IOD}_{\text{nav}}$|issue_of_data_ephemeris|10|||
|$t_{oc}$|time_of_clock|14|60|$\mathrm{s}$|
|$M_0$|mean_anomaly|$^*32$|$2^{-31}$|$\mathrm{semicircle}$|
|$e$|eccentricity|32|$2^{-33}$||
|$\sqrt{A}$|square_root_of_semi_major_axis|32|$2^{-19}$|$\mathrm{m^{1/2}}$|
||_ignored_|2|||

## Subframe 2

Ephemeris (2/4)

122 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{IOD}_{\text{nav}}$|issue_of_data_ephemeris|10|||
|$\Omega_0$|ascending_node_longitude|$^*32$|$2^{-31}$|$\mathrm{semicircle}$|
|$i_0$|inclination_angle|$^*32$|$2^{-31}$|$\mathrm{semicircle}$|
|$\omega$|argument_of_perigee|$^*32$|$2^{-31}$|$\mathrm{semicircle}$|
|$\dot{i}$|rate_of_inclination_angle|$^*14$|$2^{-43}$|$\mathrm{\frac{semicircle}{s}}$|
||_ignored_|2|||

## Subframe 3

Ephemeris (3/4)

122 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{IOD}_{\text{nav}}$|issue_of_data_ephemeris|10|||
|$\dot{\Omega}$|rate_of_right_ascension|$^*24$|$2^{-43}$|$\mathrm{\frac{semicircle}{s}}$|
|$\Delta_n$|mean_motion_difference|$^*16$|$2^{-43}$|$\mathrm{\frac{semicircle}{s}}$|
|$C_{uc}$|argument_of_latitude_cosine_correction|$^*16$|$2^{-29}$|$\mathrm{rad}$|
|$C_{us}$|argument_of_latitude_sine_correction|$^*16$|$2^{-29}$|$\mathrm{rad}$|
|$C_{rc}$|orbit_radius_cosine_correction|$^*16$|$2^{-5}$|$\mathrm{m}$|
|$C_{rs}$|orbit_radius_sine_correction|$^*16$|$2^{-5}$|$\mathrm{m}$|
|$\text{SISA}$|_ignored_|8|||

## Subframe 4

SVID, Ephemeris (4/4), and Clock correction parameters

122 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{IOD}_{\text{nav}}$|issue_of_data_ephemeris|10|||
|$\text{SV}_{\text{ID}}$|satellite_id|6|||
|$C_{ic}$|inclination_angle_cosine_correction|$^*16$|$2^{-29}$|$\mathrm{rad}$|
|$C_{is}$|inclination_angle_sine_correction|$^*16$|$2^{-29}$|$\mathrm{rad}$|
|$t_{oc}$|time_of_clock|14|60|$\mathrm{s}$|
|$a_{f0}$|clock_bias_correction|$^*31$|$2^{-34}$|$\mathrm{s}$|
|$a_{f1}$|clock_drift_correction|$^*21$|$2^{-46}$|$\mathrm{}$|
|$a_{f2}$|clock_drift_rate_correction|$^*6$|$2^{-59}$|$\mathrm{\frac{1}{s}}$|
||_ignored_|2|||

## Subframe 5

Ionospheric correction, BGD, signal health and data validity status and GST

122 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$a_{i0}$|ionisation_level_1st_order|11|$2^{-2}$|$\mathrm{sfu}$|
|$a_{i1}$|ionisation_level_2nd_order|$^*11$|$2^{-8}$|$\mathrm{\frac{sfu}{{}^{\circ}}}$|
|$a_{i2}$|ionisation_level_3rd_order|$^*14$|$2^{-15}$|$\mathrm{\frac{sfu}{deg^{2}}}$|
|$\text{SF}_1$|ionospheric_disturbance_region_1|1|||
|$\text{SF}_2$|ionospheric_disturbance_region_2|1|||
|$\text{SF}_3$|ionospheric_disturbance_region_3|1|||
|$\text{SF}_4$|ionospheric_disturbance_region_4|1|||
|$\text{SF}_5$|ionospheric_disturbance_region_5|1|||
|$\text{BGD}(E1, E5a)$|_ignored_|10|||
|$\text{BGD}(E1, E5b)$|_ignored_|10|||
|$\text{E5b}_\text{HS}$|_ignored_|2|||
|$\text{E1B}_\text{HS}$|_ignored_|2|||
|$\text{E5b}_\text{DVS}$|_ignored_|1|||
|$\text{E1B}_\text{DVS}$|_ignored_|1|||
|$\text{WN}$|week_number|12|||
|$\text{TOW}$|time_of_week|20|||
||_ignored_|23|||
