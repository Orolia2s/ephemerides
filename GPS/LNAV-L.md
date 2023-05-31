# GPS LNAV-L

Legacy Navigation, for the Lower set of PRN numbers (PRN 1-32)

## Header

48 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|`10001011`|preamble|8|||
||telemetry|14|||
||integrity_status|1|||
||_ignored_|1|||
||time_of_week|17|||
|`0`|alert|1|||
||anti_spoof|1|||
||subframe_id|3|||
||_ignored_|2|||

## Header extension to paged subframes

8 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|`01`|data_id|2|||
||page_id|6|||

## Subframe 1

192 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{WN}$|week_number|10|||
||ca_or_p_on_l2|2|||
||user_range_accuracy_index|4|||
||satellite_health|6|||
||issue_of_data_clock (msb)|2|||
||l2p_data_flag|1|||
||_ignored_|87|||
|$T_{GD}$|group_delay_differential|8|$2^{-31}$|$\mathrm{s}$|
||issue_of_data_clock (lsb)|8|||
|$t_{oc}$|time_of_clock|16|$2^{4}$|$\mathrm{s}$|
|$a_{f2}$|clock_drift_rate_correction|8|$2^{-55}$|$\mathrm{\frac{1}{s}}$|
|$a_{f1}$|clock_drift_correction|16|$2^{-43}$|$\mathrm{}$|
|$a_{f0}$|clock_bias_correction|22|$2^{-31}$|$\mathrm{s}$|
||_ignored_|2|||

## Subframe 2

192 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||issue_of_data_ephemeris|8|||
|$C_{rs}$|orbit_radius_sine_correction|16|$2^{-5}$|$\mathrm{m}$|
|$\Delta n$|mean_motion_difference|16|$2^{-43}$|$\mathrm{\frac{semicircle}{s}}$|
|$M_0$|mean_anomaly|32|$2^{-31}$|$\mathrm{semicircle}$|
|$C_{uc}$|argument_of_latitude_cosine_correction|16|$2^{-29}$|$\mathrm{rad}$|
|$e$|eccentricity|32|$2^{-33}$||
|$C_{us}$|argument_of_latitude_sine_correction|16|$2^{-29}$|$\mathrm{rad}$|
|$\sqrt{A}$|square_root_of_semi_major_axis|32|$2^{-19}$|$\mathrm{m^{1/2}}$|
|$t_{oe}$|reference_time_ephemeris|16|$2^{4}$|$\mathrm{s}$|
||fit_interval_flag|1|||
||age_of_data_offset|5|||
||_ignored_|2|||

## Subframe 3

192 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$C_{ic}$|inclination_angle_cosine_correction|16|$2^{-29}$|$\mathrm{rad}$|
|$\Omega_0$|ascending_node_longitude|32|$2^{-31}$|$\mathrm{semicircle}$|
|$C_{is}$|inclination_angle_sine_correction|16|$2^{-29}$|$\mathrm{rad}$|
|$i_0$|inclination_angle|32|$2^{-31}$|$\mathrm{semicircle}$|
|$C_{rc}$|orbit_radius_cosine_correction|16|$2^{-5}$|$\mathrm{m}$|
|$\omega$|argument_of_perigee|32|$2^{-31}$|$\mathrm{semicircle}$|
|$\dot{\Omega}$|rate_of_right_ascension|24|$2^{-43}$|$\mathrm{\frac{semicircle}{s}}$|
||issue_of_data_ephemeris|8|||
|$\text{IDOT}$|rate_of_inclination_angle|14|$2^{-43}$|$\mathrm{\frac{semicircle}{s}}$|
||_ignored_|2|||

## Subframe 4

### Pages 1, 6, 11, 12, 14 to 17, 19 to 24

184 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||_ignored_|184|||

### Pages 2 to 5, 7 to 10

184 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$e$|eccentricity|16|$2^{-21}$||
|$t_{oa}$|almanach_reference_time|8||$\mathrm{s}$|
|$\delta_i$|delta_i|16|$2^{-14}$||
|$\dot{\Omega}$|rate_of_right_ascension|16|$2^{-38}$||
||satellite_health|8|||
|$\sqrt{A}$|square_root_of_semi_major_axis|24|$2^{-11}$|$\mathrm{m^{1/2}}$|
|$\Omega_0$|longitude_of_ascending_node_of_orbit_plane|24|$2^{-23}$||
|$\omega$|argument_of_perigee|24|$2^{-23}$||
|$M_0$|mean_anomaly|24|$2^{-23}$||
|$a_{f0}$|clock_bias_correction (msb)|8|$2^{-20}$|$\mathrm{s}$|
|$a_{f1}$|clock_drift_correction|11|$2^{-38}$|$\mathrm{}$|
|$a_{f0}$|clock_bias_correction (lsb)|3|$2^{-20}$|$\mathrm{s}$|
||_ignored_|2|||

### Page 13

184 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||availability|2|||
||edr_1|6|||
||edr_2|6|||
||edr_3|6|||
||edr_4|6|||
||edr_5|6|||
||edr_6|6|||
||edr_7|6|||
||edr_8|6|||
||edr_9|6|||
||edr_10|6|||
||edr_11|6|||
||edr_12|6|||
||edr_13|6|||
||edr_14|6|||
||edr_15|6|||
||edr_16|6|||
||edr_17|6|||
||edr_18|6|||
||edr_19|6|||
||edr_20|6|||
||edr_21|6|||
||edr_22|6|||
||edr_23|6|||
||edr_24|6|||
||edr_25|6|||
||edr_26|6|||
||edr_27|6|||
||edr_28|6|||
||edr_29|6|||
||edr_30|6|||
||_ignored_|2|||

### Page 18

184 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\alpha_0$|alpha_0|8|$2^{-30}$|$\mathrm{s}$|
|$\alpha_1$|alpha_1|8|$2^{-27}$|$\mathrm{\frac{s}{semicircle}}$|
|$\alpha_2$|alpha_2|8|$2^{-24}$|$\mathrm{\frac{s}{semicircle^{2}}}$|
|$\alpha_3$|alpha_3|8|$2^{-24}$|$\mathrm{\frac{s}{semicircle^{3}}}$|
|$\beta_0$|beta_0|8|$2^{11}$|$\mathrm{s}$|
|$\beta_1$|beta_1|8|$2^{14}$|$\mathrm{\frac{s}{semicircle}}$|
|$\beta_2$|beta_2|8|$2^{16}$|$\mathrm{\frac{s}{semicircle^{2}}}$|
|$\beta_3$|beta_3|8|$2^{16}$|$\mathrm{\frac{s}{semicircle^{3}}}$|
|$A_1$|A_1|24|$2^{-50}$|$\mathrm{}$|
|$A_0$|A_0|32|$2^{-30}$|$\mathrm{s}$|
|$t_{ot}$|utc_reference_time|8|$2^{12}$|$\mathrm{s}$|
|$\text{WN}_t$|utc_week_number|8|||
|$\Delta t_{LS}$|leap_seconds_delta|8||$\mathrm{s}$|
|$\text{WN}_{LSF}$|future_leap_seconds_week_number|8|||
|$\text{DN}$|future_leap_seconds_day_number|8|||
|$\Delta t_{LSF}$|future_leap_seconds_delta|8||$\mathrm{s}$|
||_ignored_|16|||

### Page 25

184 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||satellite_1_config|4|||
||satellite_2_config|4|||
||satellite_3_config|4|||
||satellite_4_config|4|||
||satellite_5_config|4|||
||satellite_6_config|4|||
||satellite_7_config|4|||
||satellite_8_config|4|||
||satellite_9_config|4|||
||satellite_10_config|4|||
||satellite_11_config|4|||
||satellite_12_config|4|||
||satellite_13_config|4|||
||satellite_14_config|4|||
||satellite_15_config|4|||
||satellite_16_config|4|||
||satellite_17_config|4|||
||satellite_18_config|4|||
||satellite_19_config|4|||
||satellite_20_config|4|||
||satellite_21_config|4|||
||satellite_22_config|4|||
||satellite_23_config|4|||
||satellite_24_config|4|||
||satellite_25_config|4|||
||satellite_26_config|4|||
||satellite_27_config|4|||
||satellite_28_config|4|||
||satellite_29_config|4|||
||satellite_30_config|4|||
||satellite_31_config|4|||
||satellite_32_config|4|||
||_ignored_|2|||
||satellite_25_health|6|||
||satellite_26_health|6|||
||satellite_27_health|6|||
||satellite_28_health|6|||
||satellite_29_health|6|||
||satellite_30_health|6|||
||satellite_31_health|6|||
||satellite_32_health|6|||
||_ignored_|6|||

## Subframe 5

### Pages 1 to 24

184 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$e$|eccentricity|16|$2^{-21}$||
|$t_{oa}$|almanach_reference_time|8||$\mathrm{s}$|
|$\delta_i$|delta_i|16|$2^{-14}$||
|$\dot{\Omega}$|rate_of_right_ascension|16|$2^{-38}$||
||satellite_health|8|||
|$\sqrt{A}$|square_root_of_semi_major_axis|24|$2^{-11}$|$\mathrm{m^{1/2}}$|
|$\Omega_0$|longitude_of_ascending_node_of_orbit_plane|24|$2^{-23}$||
|$\omega$|argument_of_perigee|24|$2^{-23}$||
|$M_0$|mean_anomaly|24|$2^{-23}$||
|$a_{f0}$|clock_bias_correction (msb)|8|$2^{-20}$|$\mathrm{s}$|
|$a_{f1}$|clock_drift_correction|11|$2^{-38}$|$\mathrm{}$|
|$a_{f0}$|clock_bias_correction (lsb)|3|$2^{-20}$|$\mathrm{s}$|
||_ignored_|2|||

### Page 25

184 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$t_{oa}$|almanach_reference_time|8|$2^{12}$|$\mathrm{s}$|
|$\text{WN}_a$|almanach_week_number|8|||
||satellite_1_health|6|||
||satellite_2_health|6|||
||satellite_3_health|6|||
||satellite_4_health|6|||
||satellite_5_health|6|||
||satellite_6_health|6|||
||satellite_7_health|6|||
||satellite_8_health|6|||
||satellite_9_health|6|||
||satellite_10_health|6|||
||satellite_11_health|6|||
||satellite_12_health|6|||
||satellite_13_health|6|||
||satellite_14_health|6|||
||satellite_15_health|6|||
||satellite_16_health|6|||
||satellite_17_health|6|||
||satellite_18_health|6|||
||satellite_19_health|6|||
||satellite_20_health|6|||
||satellite_21_health|6|||
||satellite_22_health|6|||
||satellite_23_health|6|||
||satellite_24_health|6|||
||_ignored_|24|||
