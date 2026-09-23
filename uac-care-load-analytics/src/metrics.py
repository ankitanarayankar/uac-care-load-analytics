import numpy as np
import pandas as pd


def add_metrics(data: pd.DataFrame, high_load_quantile: float = 0.75, pressure_duration: int = 7) -> pd.DataFrame:
    """Add flow, rolling, volatility, and transparent relative-load indicators."""
    result = data.sort_values("date").copy()
    result["total_system_load"] = result["cbp_load"] + result["hhs_load"]
    result["net_intake_pressure"] = result["transfers_to_hhs"] - result["hhs_discharges"]
    result["cumulative_net_intake"] = result["net_intake_pressure"].cumsum()
    previous_load = result["total_system_load"].shift(1)
    result["care_load_growth_rate"] = result["total_system_load"].pct_change().replace([np.inf, -np.inf], np.nan) * 100
    result["care_load_growth_rate"] = result["care_load_growth_rate"].where(previous_load.ne(0))

    for window in (7, 14):
        result[f"total_system_load_{window}d_avg"] = result["total_system_load"].rolling(window, min_periods=1).mean()
        result[f"cbp_load_{window}d_avg"] = result["cbp_load"].rolling(window, min_periods=1).mean()
        result[f"hhs_load_{window}d_avg"] = result["hhs_load"].rolling(window, min_periods=1).mean()
        result[f"net_intake_pressure_{window}d_avg"] = result["net_intake_pressure"].rolling(window, min_periods=1).mean()
    result["care_load_volatility_14d"] = result["total_system_load"].rolling(14, min_periods=2).std()
    result["discharge_offset_ratio"] = result["hhs_discharges"].div(result["transfers_to_hhs"].replace(0, np.nan))

    threshold = result["total_system_load"].quantile(high_load_quantile)
    result["high_load_threshold"] = threshold
    result["high_load"] = result["total_system_load"] >= threshold

    positive = result["net_intake_pressure"].gt(0)
    groups = positive.ne(positive.shift()).cumsum()
    run_lengths = positive.groupby(groups).transform("sum")
    result["sustained_positive_pressure"] = positive & run_lengths.ge(pressure_duration)
    result["pressure_run_id"] = groups.where(positive, np.nan)
    result["pressure_duration"] = run_lengths.where(positive, 0).astype(int)
    return result


def monthly_summary(data: pd.DataFrame) -> pd.DataFrame:
    result = data.set_index("date").resample("MS").agg(
        total_system_load=("total_system_load", "mean"),
        cbp_load=("cbp_load", "mean"),
        hhs_load=("hhs_load", "mean"),
        transfers_to_hhs=("transfers_to_hhs", "sum"),
        hhs_discharges=("hhs_discharges", "sum"),
        net_intake_pressure=("net_intake_pressure", "sum"),
    ).reset_index()
    return result


def pressure_periods(data: pd.DataFrame) -> pd.DataFrame:
    sustained = data[data["sustained_positive_pressure"]].copy()
    if sustained.empty:
        return pd.DataFrame(columns=["start_date", "end_date", "observations", "net_intake_pressure"])
    groups = sustained["pressure_run_id"].dropna().unique()
    rows = []
    for group in groups:
        period = data[data["pressure_run_id"] == group]
        rows.append({
            "start_date": period["date"].min(),
            "end_date": period["date"].max(),
            "observations": len(period),
            "net_intake_pressure": period["net_intake_pressure"].sum(),
        })
    return pd.DataFrame(rows).sort_values("start_date").reset_index(drop=True)
