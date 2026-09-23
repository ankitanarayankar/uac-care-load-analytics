from pathlib import Path

import pandas as pd

from .metrics import monthly_summary, pressure_periods


def summarize(data: pd.DataFrame, pressure_duration: int = 7) -> dict[str, object]:
    """Build factual summaries from the selected, already-metricized observations."""
    if data.empty:
        return {"record_count": 0, "insights": [], "monthly": pd.DataFrame(), "pressure_periods": pd.DataFrame()}
    peak = data.loc[data["total_system_load"].idxmax()]
    periods = pressure_periods(data)
    longest = int(periods["observations"].max()) if not periods.empty else 0
    cbp_higher_pct = float(data["cbp_load"].gt(data["hhs_load"]).mean() * 100)
    high = data[data["high_load"]]
    outside = data[~data["high_load"]]
    insights = [
        f"The maximum observed Total System Load was {peak['total_system_load']:,.0f} on {peak['date']:%Y-%m-%d}.",
        f"The average Total System Load during the selected period was {data['total_system_load'].mean():,.1f}.",
        f"There were {int(data['net_intake_pressure'].gt(0).sum())} observations where Net Intake Pressure was positive.",
        f"{len(periods)} sustained positive-pressure period(s) met the {pressure_duration}-observation rule; the longest lasted {longest} observations.",
        f"CBP load was higher than HHS load on {cbp_higher_pct:.1f}% of observed dates.",
    ]
    return {
        "record_count": len(data),
        "date_min": data["date"].min(),
        "date_max": data["date"].max(),
        "peak": peak,
        "current": data.iloc[-1],
        "high_load_days": int(data["high_load"].sum()),
        "high_load_average": float(high["total_system_load"].mean()) if not high.empty else None,
        "outside_high_load_average": float(outside["total_system_load"].mean()) if not outside.empty else None,
        "positive_pressure_days": int(data["net_intake_pressure"].gt(0).sum()),
        "pressure_periods": periods,
        "monthly": monthly_summary(data),
        "insights": insights,
    }


def executive_summary(summary: dict[str, object], quality: dict[str, object]) -> str:
    if not summary.get("record_count"):
        return "No valid dated observations are available for an executive summary."
    peak = summary["peak"]
    return f"""# Executive Summary

## System Capacity & Care Load Analytics for Unaccompanied Children

This analysis describes observed CBP and HHS care-load and flow measures in the supplied aggregated dataset. It does not estimate official capacity, individual outcomes, or an official operational backlog.

- **Dataset period:** {summary['date_min']:%Y-%m-%d} to {summary['date_max']:%Y-%m-%d}
- **Usable observations:** {summary['record_count']:,}
- **Maximum observed Total System Load:** {peak['total_system_load']:,.0f} on {peak['date']:%Y-%m-%d}
- **High-load observations:** {summary['high_load_days']:,}
- **Positive Net Intake Pressure observations:** {summary['positive_pressure_days']:,}
- **Sustained positive-pressure periods:** {len(summary['pressure_periods']):,}

## Interpretation

Positive Net Intake Pressure means transfers exceeded discharges in that observation. Cumulative Net Intake is an analytical flow-balance indicator and should not be interpreted as an official operational backlog unless validated against official backlog data. High-load labels use a relative percentile threshold, not an official capacity limit.

## Data-quality limitations

The source file contains {quality['raw_rows']:,} rows, including {quality['blank_rows']:,} fully blank rows. The cleaning pipeline preserves those rows in validation outputs, while dated analytical calculations use valid observations. Flagged anomalies: {quality['flagged_anomalies']:,}.

## Recommendations for further analysis

Add an authoritative capacity denominator if one becomes available, document reporting cadence and missing dates, and compare flow-balance indicators with validated operational backlog data before using them for capacity decisions.
"""


def research_paper(summary: dict[str, object], quality: dict[str, object]) -> str:
    if not summary.get("record_count"):
        return "# Research Paper\n\nNo valid dated observations are available."
    peak = summary["peak"]
    return f"""# System Capacity & Care Load Analytics for Unaccompanied Children

## Abstract
This study presents an analytics-only workflow for describing observed daily CBP and HHS care-load measures, transfer and discharge flows, relative high-load periods, and data-quality conditions. The supplied aggregate CSV contained {summary['record_count']:,} usable dated observations from {summary['date_min']:%Y-%m-%d} through {summary['date_max']:%Y-%m-%d}. The maximum observed combined load was {peak['total_system_load']:,.0f} on {peak['date']:%Y-%m-%d}. No machine-learning model or official capacity claim is made.

## Keywords
Unaccompanied children; healthcare operations analytics; care load; flow balance; CBP; HHS; Streamlit; data quality

## Introduction and Background
The UAC care pipeline includes intake into CBP custody, transfers into HHS care, care delivery, and discharge to placement. Daily aggregate measures can support transparent operational monitoring without inferring individual-level information.

## Problem Statement and Objectives
The objective is to transform raw daily records into reproducible load, flow, rolling-average, volatility, relative high-load, and validation indicators. The project explicitly distinguishes observed counts from interpretation.

## Dataset Description
The source file contains Date plus five aggregate measures: apprehended and placed in CBP custody, children in CBP custody, transfers out of CBP custody, children in HHS care, and HHS discharges. The raw file had {quality['raw_rows']:,} rows and {quality['raw_columns']:,} columns; {quality['blank_rows']:,} rows were fully blank.

## Data Preprocessing and Methodology
Column names are canonicalized, dates are parsed with invalid dates retained as flags, numeric strings are trimmed and stripped of commas, and records are chronologically sorted. Duplicate rows, duplicate dates, missing values, negative values, and logical comparisons are flagged rather than silently removed. Valid dated observations feed the metrics and dashboard.

## Derived Metrics
Total System Load equals CBP Load plus HHS Load. Net Intake Pressure equals transfers minus discharges. Cumulative Net Intake is the cumulative sum of that flow difference and is not an official backlog. Growth is period-over-period percentage change with zero denominators treated as missing. Seven- and fourteen-observation rolling means, fourteen-observation rolling standard deviation, discharge offset ratio, a 75th-percentile relative high-load flag, and seven-observation sustained positive-pressure periods are calculated.

## System Architecture
CSV Dataset -> Data Loading -> Data Cleaning -> Data Validation -> Metric Engineering -> EDA -> Statistical Analysis -> Interactive Visualizations -> Streamlit Dashboard -> Insights and Executive Summary.

## Dashboard Design
The Streamlit dashboard provides date, granularity, rolling-average, threshold, pressure-duration, metric, and anomaly controls. It displays KPI cards, trends, flow balance, monthly summaries, data quality, insights, downloadable processed data, and this report.

## Results
{chr(10).join('- ' + insight for insight in summary['insights'])}

## Discussion, Limitations, and Future Scope
The results describe relative load and observed flow behavior. They do not establish official capacity exceedance, causal effects, individual outcomes, policy success, or an official backlog. Blank trailing rows and reporting cadence should be documented in future source releases. Future work should add validated capacity and backlog denominators, calendar-gap analysis, and stakeholder-reviewed operational definitions.

## Conclusion
A reproducible analytics pipeline makes the supplied UAC aggregate data easier to inspect, validate, and monitor while keeping claims bounded by the available evidence.

## References
- U.S. Department of Health and Human Services, Office of Refugee Resettlement, Unaccompanied Children Program data source supplied for this project.
- pandas, NumPy, Plotly, and Streamlit project documentation.
"""
