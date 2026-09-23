import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _layout(figure: go.Figure, title: str, y_title: str) -> go.Figure:
    figure.update_layout(title=title, xaxis_title="Date", yaxis_title=y_title, hovermode="x unified", height=420)
    figure.update_xaxes(tickformat="%b %Y")
    return figure


def load_trend(data: pd.DataFrame, rolling_window: int | None = None) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=data["date"], y=data["total_system_load"], name="Total System Load", mode="lines+markers"))
    if rolling_window:
        column = f"total_system_load_{rolling_window}d_avg"
        figure.add_trace(go.Scatter(x=data["date"], y=data[column], name=f"{rolling_window}-observation average", mode="lines"))
    return _layout(figure, "Total System Load over time", "Children")


def cbp_hhs_trend(data: pd.DataFrame) -> go.Figure:
    figure = px.line(data, x="date", y=["cbp_load", "hhs_load", "total_system_load"], labels={"value": "Children", "variable": "Measure"})
    return _layout(figure, "CBP, HHS, and combined care load", "Children")


def flow_chart(data: pd.DataFrame) -> go.Figure:
    figure = px.line(data, x="date", y=["transfers_to_hhs", "hhs_discharges", "net_intake_pressure"], labels={"value": "Children", "variable": "Flow measure"})
    return _layout(figure, "Transfers, discharges, and net intake pressure", "Children")


def cumulative_chart(data: pd.DataFrame) -> go.Figure:
    figure = px.line(data, x="date", y="cumulative_net_intake", labels={"cumulative_net_intake": "Cumulative Net Intake"})
    return _layout(figure, "Cumulative Net Intake", "Analytical flow-balance units")


def monthly_chart(monthly: pd.DataFrame) -> go.Figure:
    figure = px.line(monthly, x="date", y=["total_system_load", "cbp_load", "hhs_load"], labels={"value": "Average children", "variable": "Measure"})
    return _layout(figure, "Monthly average care load", "Average children")


def volatility_chart(data: pd.DataFrame) -> go.Figure:
    figure = px.line(data, x="date", y="care_load_volatility_14d", labels={"care_load_volatility_14d": "14-observation rolling standard deviation"})
    return _layout(figure, "Care load volatility", "Standard deviation of children")


def quality_timeline(data: pd.DataFrame) -> go.Figure:
    flagged = data[data["anomaly_flag"]].copy()
    figure = px.scatter(flagged, x="date", y="anomaly_flag", hover_data=["source_row_number"], title="Flagged data-quality observations")
    return _layout(figure, "Data-quality/anomaly timeline", "Flagged")
