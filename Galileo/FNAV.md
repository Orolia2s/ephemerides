# Galileo FNAV

Transmitted on the E5a-I signal, the F-band (1278.75 MHz)
is used for the transmission of Galileo System Time (GST)
and other system messages, such as almanacs and health status messages.

Note that compared to the ICD, the notion of page and subframe has been swapped here

## Header

6 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
||subframe_id|6|||

## Subframe 1

SVID, clock correction, SISA, Ionospheric correction, BGD,
Signal health status, GST and Data validity status


208 bits mapped as follows:

|notation|name|bits|factor|unit|
|:------:|:---|---:|:-----|:--:|
|$\text{SV}_{ID}$|satellite_id|6|||
|$\text{IOD}_{nav}$|issue_of_data_ephemeris|10|||
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
||BGD|10|||
|$E5a_{HS}$|_ignored_|2|||
|$\text{WN}$|week_number|12|||
|$\text{TOW}$|time_of_week|20|||
|$E5a_{DVS}$|_ignored_|1|||
||_ignored_|26|||
