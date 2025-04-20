# GLONASS L1OC

Transmitted on the L1 sub-band (~1.6 GHz)

Translation from the ICD to the YAML:
  - superframe -> frame
  - frame -> subframe
  - string -> page

## Ublox words layout

GLONASS L1OC corresponds to gnssId 6, sigId 0

Words|MSB skipped|Data bits|LSB skipped
:-|-:|-:|-:
1 to 2|0|32|0
3|0|13|19

## Header

1 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|`0`|idle_chip|1|||

## Header extension for paged subframes

4 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||page_id|4|||

## Subframe 1

### Page 1

Satellite's X data and date

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||_ignored_|2|||
||time_interval_duration|2|||
||hour|5||$\mathrm{h}$|
||minute|6||$\mathrm{min}$|
||second|1|30|$\mathrm{s}$|
|$x'$|x_speed|$^*24$|$2^{-20}$|$\mathrm{\frac{km}{s}}$|
|$x''$|x_acceleration|$^*5$|$2^{-30}$|$\mathrm{\frac{km}{s^{2}}}$|
|$x$|x|$^*27$|$2^{-11}$|$\mathrm{km}$|

### Page 2

Satellite's Y data and time interval

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||satellite_health_B|3|||
||time_interval_parity|1|||
||time_interval_index|7|||
||_ignored_|5|||
|$y'$|y_speed|$^*24$|$2^{-20}$|$\mathrm{\frac{km}{s}}$|
|$y''$|y_acceleration|$^*5$|$2^{-30}$|$\mathrm{\frac{km}{s^{2}}}$|
|$y$|y|$^*27$|$2^{-11}$|$\mathrm{km}$|

### Page 3

Satellite's Z data and other data

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||almanac_for_satellites|1|||
||carrier_frequency_deviation|$^*11$|$2^{-40}$||
||_ignored_|1|||
||c_computation_location|1|||
||gps_computation_location|1|||
||satellite_health_l|1|||
|$z'$|z_speed|$^*24$|$2^{-20}$|$\mathrm{\frac{km}{s}}$|
|$z''$|z_acceleration|$^*5$|$2^{-30}$|$\mathrm{\frac{km}{s^{2}}}$|
|$z$|z|$^*27$|$2^{-11}$|$\mathrm{km}$|

### Page 4

Other data

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||satellite_to_glonass_time_correction|$^*22$|$2^{-30}$|$\mathrm{s}$|
||navigation_aviation_time_difference|$^*5$|$2^{-30}$|$\mathrm{s}$|
||age_of_data|5|||
||_ignored_|14|||
||is_ephemeris_present|1|||
||user_range_accuracy_index|4|||
||_ignored_|3|||
||day_number|11||$\mathrm{d}$|
||transmitting_satellite|5|||
||transmitting_satellite_type|2|||

### Page 5

Almanac global data

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||day_number_almanac|11||$\mathrm{d}$|
|$\tau_{C}$|utc_correction|$^*32$|$2^{-31}$|$\mathrm{s}$|
||_ignored_|1|||
||four_year_interval_number|5|4|$\mathrm{yr}$|
|$\tau_{GPS}$|gps_correction|$^*22$|$2^{-30}$|$\mathrm{d}$|
||satellite_health_l|1|||

### Pages 6, 8, 10, 12, 14

Almanac (1/2)

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||satellite_operability|1|||
||satellite_type|2|||
|$n$|satellite_id|5|||
|$\tau_n$|glonass_correction|10|$2^{-18}$|$\mathrm{s}$|
|$\lambda_n$|longitude_of_first_ascending_node|$^*21$|$2^{-20}$|$\mathrm{semicircle}$|
|$\Delta i_n$|inclination_angle_correction|$^*18$|$2^{-20}$|$\mathrm{semicircle}$|
|$\epsilon_n$|eccentricity|15|$2^{-20}$||

### Pages 7, 9, 11, 13, 15

Almanac (2/2)

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\omega_n$|argument_of_perigee|$^*16$|$2^{-15}$|$\mathrm{semicircle}$|
|$t_{\lambda n}$|time_of_first_ascending_node|21|$2^{-5}$|$\mathrm{s}$|
|$\Delta T_n$|revolution_period|$^*22$|$2^{-9}$|$\mathrm{\frac{s}{cycle}}$|
|$\Delta T_n'$|revolution_period_drift|$^*7$|$2^{-14}$|$\mathrm{\frac{s}{cycle^{2}}}$|
||carrier_frequency_number|5|||
||satellite_health_l|1|||

## Subframe 5

### Page 1

Satellite's X data and date

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||_ignored_|2|||
||time_interval_duration|2|||
||hour|5||$\mathrm{h}$|
||minute|6||$\mathrm{min}$|
||second|1|30|$\mathrm{s}$|
|$x'$|x_speed|$^*24$|$2^{-20}$|$\mathrm{\frac{km}{s}}$|
|$x''$|x_acceleration|$^*5$|$2^{-30}$|$\mathrm{\frac{km}{s^{2}}}$|
|$x$|x|$^*27$|$2^{-11}$|$\mathrm{km}$|

### Page 2

Satellite's Y data and time interval

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||satellite_health_B|3|||
||time_interval_parity|1|||
||time_interval_index|7|||
||_ignored_|5|||
|$y'$|y_speed|$^*24$|$2^{-20}$|$\mathrm{\frac{km}{s}}$|
|$y''$|y_acceleration|$^*5$|$2^{-30}$|$\mathrm{\frac{km}{s^{2}}}$|
|$y$|y|$^*27$|$2^{-11}$|$\mathrm{km}$|

### Page 3

Satellite's Z data and other data

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||almanac_for_satellites|1|||
||carrier_frequency_deviation|$^*11$|$2^{-40}$||
||_ignored_|1|||
||c_computation_location|1|||
||gps_computation_location|1|||
||satellite_health_l|1|||
|$z'$|z_speed|$^*24$|$2^{-20}$|$\mathrm{\frac{km}{s}}$|
|$z''$|z_acceleration|$^*5$|$2^{-30}$|$\mathrm{\frac{km}{s^{2}}}$|
|$z$|z|$^*27$|$2^{-11}$|$\mathrm{km}$|

### Page 4

Other data

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||satellite_to_glonass_time_correction|$^*22$|$2^{-30}$|$\mathrm{s}$|
||navigation_aviation_time_difference|$^*5$|$2^{-30}$|$\mathrm{s}$|
||age_of_data|5|||
||_ignored_|14|||
||is_ephemeris_present|1|||
||user_range_accuracy_index|4|||
||_ignored_|3|||
||day_number|11||$\mathrm{d}$|
||transmitting_satellite|5|||
||transmitting_satellite_type|2|||

### Page 5

Almanac global data

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||day_number_almanac|11||$\mathrm{d}$|
|$\tau_{C}$|utc_correction|$^*32$|$2^{-31}$|$\mathrm{s}$|
||_ignored_|1|||
||four_year_interval_number|5|4|$\mathrm{yr}$|
|$\tau_{GPS}$|gps_correction|$^*22$|$2^{-30}$|$\mathrm{d}$|
||satellite_health_l|1|||

### Pages 6, 8, 10, 12

Almanac (1/2)

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||satellite_operability|1|||
||satellite_type|2|||
|$n$|satellite_id|5|||
|$\tau_n$|glonass_correction|10|$2^{-18}$|$\mathrm{s}$|
|$\lambda_n$|longitude_of_first_ascending_node|$^*21$|$2^{-20}$|$\mathrm{semicircle}$|
|$\Delta i_n$|inclination_angle_correction|$^*18$|$2^{-20}$|$\mathrm{semicircle}$|
|$\epsilon_n$|eccentricity|15|$2^{-20}$||

### Pages 7, 9, 11, 13

Almanac (2/2)

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\omega_n$|argument_of_perigee|$^*16$|$2^{-15}$|$\mathrm{semicircle}$|
|$t_{\lambda n}$|time_of_first_ascending_node|21|$2^{-5}$|$\mathrm{s}$|
|$\Delta T_n$|revolution_period|$^*22$|$2^{-9}$|$\mathrm{\frac{s}{cycle}}$|
|$\Delta T_n'$|revolution_period_drift|$^*7$|$2^{-14}$|$\mathrm{\frac{s}{cycle^{2}}}$|
||carrier_frequency_number|5|||
||satellite_health_l|1|||

### Page 14

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$B_1$|utc_ut1_bias_correction|$^*11$|$2^{-10}$|$\mathrm{s}$|
|$B_2$|utc_ut1_drift_correction|$^*10$|$2^{-16}$|$\mathrm{s}$|
||four_year_intervalnd_notification|2|||
||_ignored_|49|||

### Page 15

72 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||_ignored_|71|||
||satellite_health_l|1|||
