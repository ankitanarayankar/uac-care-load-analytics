from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis import executive_summary, research_paper, summarize
from src.metrics import add_metrics, monthly_summary
from src.preprocessing import analysis_frame, load_and_clean
from src.visualizations import (
    cbp_hhs_trend,
    cumulative_chart,
    flow_chart,
    load_trend,
    monthly_chart,
    quality_timeline,
    volatility_chart,
)

st.set_page_config(page_title="UAC Care Load Analytics", page_icon="📊", layout="wide")

PROJECT_ROOT = Path(__file__).parent
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "uac_dataset.csv"


def fmt(value: object, decimals: int = 0) -> str:
    if isinstance(value, str):
        return value
    if pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def display_frame(data: pd.DataFrame, granularity: str) -> pd.DataFrame:
    if granularity == "Daily":
        return data
    rule = "W-MON" if granularity == "Weekly" else "MS"
    result = data.set_index("date").resample(rule).agg(
        total_system_load=("total_system_load", "mean"),
        cbp_load=("cbp_load", "mean"),
        hhs_load=("hhs_load", "mean"),
        transfers_to_hhs=("transfers_to_hhs", "sum"),
        hhs_discharges=("hhs_discharges", "sum"),
        net_intake_pressure=("net_intake_pressure", "sum"),
        cumulative_net_intake=("cumulative_net_intake", "last"),
        care_load_volatility_14d=("care_load_volatility_14d", "mean"),
    ).dropna(subset=["total_system_load"]).reset_index()
    return result


@st.cache_data
def prepare_data(threshold_quantile: float, pressure_duration: int):
    cleaned, quality = load_and_clean(RAW_PATH)
    data = add_metrics(analysis_frame(cleaned), threshold_quantile, pressure_duration)
    return cleaned, data, quality


def main() -> None:
    st.title("System Capacity & Care Load Analytics for Unaccompanied Children")
    st.caption("Data-driven monitoring of CBP and HHS care load, intake, discharge, and care-pressure indicators")
    st.info("This is an analytics dashboard for observed aggregate counts. It does not estimate official capacity, individual outcomes, or an official operational backlog.")

    with st.sidebar:
        st.header("Controls")
        threshold_percentile = st.slider("High-load threshold percentile", 50, 95, 75, 5)
        pressure_duration = st.slider("Sustained-pressure observations", 2, 30, 7)
        cleaned, all_data, quality = prepare_data(threshold_percentile / 100, pressure_duration)
        min_date, max_date = all_data["date"].min().date(), all_data["date"].max().date()
        selected_dates = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        granularity = st.selectbox("Time granularity", ["Daily", "Weekly", "Monthly"])
        metric = st.selectbox("Metric", ["Total System Load", "CBP Load", "HHS Load", "Net Intake Pressure", "Care Load Volatility"])
        rolling = st.selectbox("Rolling average", ["None", "7 observations", "14 observations"])
        show_anomalies = st.checkbox("Show anomaly records", value=False)

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date, end_date = min_date, max_date
    filtered = all_data[all_data["date"].dt.date.between(start_date, end_date)].copy()
    if not show_anomalies:
        filtered = filtered[~filtered["anomaly_flag"]].copy()
    if filtered.empty:
        st.warning("No observations match the selected filters.")
        return

    summary = summarize(filtered, pressure_duration)
    plotted = display_frame(filtered, granularity)
    current = filtered.iloc[-1]
    st.subheader("Dashboard Home")
    kpis = st.columns(4)
    for column, label, value in zip(
        kpis,
        ["Current Total System Load", "Current CBP Load", "Current HHS Load", "Current Net Intake Pressure"],
        [current["total_system_load"], current["cbp_load"], current["hhs_load"], current["net_intake_pressure"]],
    ):
        column.metric(label, fmt(value))
    kpis2 = st.columns(4)
    for column, label, value in zip(
        kpis2,
        ["Cumulative Net Intake", "Current Growth Rate", "High-load Days", "Sustained-pressure Periods"],
        [current["cumulative_net_intake"], f"{fmt(current['care_load_growth_rate'], 1)}%", summary["high_load_days"], len(summary["pressure_periods"])],
    ):
        column.metric(label, fmt(value))

    st.subheader("System Load Overview")
    rolling_window = None if rolling == "None" else int(rolling.split()[0])
    st.plotly_chart(load_trend(plotted if granularity == "Daily" else filtered, rolling_window), use_container_width=True)
    peak = summary["peak"]
    st.write(f"The highest observed system load in the selected period was {fmt(peak['total_system_load'])} children on {peak['date']:%Y-%m-%d}. The relative high-load threshold is {fmt(filtered['high_load_threshold'].iloc[0])}; it is not an official capacity limit.")

    metric_columns = {
        "Total System Load": "total_system_load",
        "CBP Load": "cbp_load",
        "HHS Load": "hhs_load",
        "Net Intake Pressure": "net_intake_pressure",
        "Care Load Volatility": "care_load_volatility_14d",
    }
    st.plotly_chart(px.line(plotted, x="date", y=metric_columns[metric], title=f"Selected metric: {metric}"), use_container_width=True)

    st.subheader("CBP vs HHS Load")
    st.plotly_chart(cbp_hhs_trend(plotted if granularity == "Daily" else filtered), use_container_width=True)
    stats = filtered[["cbp_load", "hhs_load", "total_system_load"]].agg(["mean", "median", "min", "max"]).T
    st.dataframe(stats.style.format("{:,.1f}"), use_container_width=True)

    st.subheader("Intake vs Discharge")
    st.plotly_chart(flow_chart(filtered), use_container_width=True)
    st.caption("Positive Net Intake Pressure means transfers exceeded discharges. Negative values mean discharges exceeded transfers.")

    st.subheader("Backlog / Flow Pressure")
    st.plotly_chart(cumulative_chart(filtered), use_container_width=True)
    st.caption("Cumulative Net Intake is an analytical flow-balance indicator and should not be interpreted as an official operational backlog unless validated against official backlog data.")
    periods = summary["pressure_periods"]
    st.dataframe(periods, use_container_width=True)

    st.subheader("High-load Analysis")
    high_load, outside = filtered[filtered["high_load"]], filtered[~filtered["high_load"]]
    high_columns = st.columns(3)
    high_columns[0].metric("High-load observations", f"{len(high_load):,}")
    high_columns[1].metric("Average high-load", fmt(high_load["total_system_load"].mean(), 1))
    high_columns[2].metric("Average outside high-load", fmt(outside["total_system_load"].mean(), 1))
    st.dataframe(high_load.nlargest(10, "total_system_load")[["date", "total_system_load", "high_load_threshold"]], use_container_width=True)

    st.subheader("Monthly Analysis")
    monthly = monthly_summary(filtered)
    st.plotly_chart(monthly_chart(monthly), use_container_width=True)
    st.dataframe(monthly, use_container_width=True)

    st.subheader("Data Quality")
    quality_columns = st.columns(4)
    quality_columns[0].metric("Raw rows", f"{quality['raw_rows']:,}")
    quality_columns[1].metric("Raw columns", f"{quality['raw_columns']:,}")
    quality_columns[2].metric("Blank rows", f"{quality['blank_rows']:,}")
    quality_columns[3].metric("Flagged anomalies", f"{quality['flagged_anomalies']:,}")
    st.json(quality)
    st.plotly_chart(quality_timeline(cleaned[cleaned["date"].notna()]), use_container_width=True)

    st.subheader("Insights")
    for insight in summary["insights"]:
        st.write(f"- {insight}")

    st.subheader("Downloads")
    st.download_button("Download processed CSV", data=all_data.to_csv(index=False).encode("utf-8"), file_name="cleaned_uac_data.csv", mime="text/csv")
    st.download_button("Download executive summary", data=executive_summary(summary, quality), file_name="executive_summary.md", mime="text/markdown")
    st.download_button("Download research-paper support", data=research_paper(summary, quality), file_name="research_paper_support.md", mime="text/markdown")


if __name__ == "__main__":
    main()
