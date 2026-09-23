# Executive Summary

## System Capacity & Care Load Analytics for Unaccompanied Children

This analysis describes observed CBP and HHS care-load and flow measures in the supplied aggregated dataset. It does not estimate official capacity, individual outcomes, or an official operational backlog.

- **Dataset period:** 2023-01-12 to 2025-12-21
- **Usable observations:** 720
- **Maximum observed Total System Load:** 11,762 on 2023-12-20
- **High-load observations:** 180
- **Positive Net Intake Pressure observations:** 238
- **Sustained positive-pressure periods:** 8

## Interpretation

Positive Net Intake Pressure means transfers exceeded discharges in that observation. Cumulative Net Intake is an analytical flow-balance indicator and should not be interpreted as an official operational backlog unless validated against official backlog data. High-load labels use a relative percentile threshold, not an official capacity limit.

## Data-quality limitations

The source file contains 1,170 rows, including 450 fully blank rows. The cleaning pipeline preserves those rows in validation outputs, while dated analytical calculations use valid observations. Flagged anomalies: 536.

## Recommendations for further analysis

Add an authoritative capacity denominator if one becomes available, document reporting cadence and missing dates, and compare flow-balance indicators with validated operational backlog data before using them for capacity decisions.
