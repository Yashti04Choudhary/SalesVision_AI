import pandas as pd
from prophet import Prophet


def create_monthly_ts(df, filter_type=None, filter_value=None):
    """Aggregate transactions into a chronological monthly sales series."""
    filtered = df.copy()
    filtered["Order Date"] = pd.to_datetime(filtered["Order Date"], errors="coerce")
    filtered["Sales"] = pd.to_numeric(filtered["Sales"], errors="coerce")
    filtered = filtered.dropna(subset=["Order Date", "Sales"])
    if filter_type is not None and filter_value is not None:
        filtered = filtered.loc[filtered[filter_type] == filter_value]
    monthly = filtered.groupby(pd.Grouper(key="Order Date", freq="ME"))["Sales"].sum().to_frame()
    return monthly.sort_index()


def generate_prophet_forecast(df, filter_type=None, filter_value=None, horizon=3):
    """Fit Prophet on the selected history and forecast the next months."""
    empty_history = pd.DataFrame(columns=["YearMonth", "Sales"])
    empty_forecast = pd.DataFrame(columns=["YearMonth", "Forecast"])
    monthly = create_monthly_ts(df, filter_type, filter_value)
    if monthly.empty:
        return empty_history, empty_forecast

    history = monthly.reset_index().rename(columns={"Order Date": "YearMonth"})
    if len(history) < 2:
        return history, empty_forecast

    training = history.rename(columns={"YearMonth": "ds", "Sales": "y"})
    model = Prophet(
        yearly_seasonality=len(training) >= 24,
        weekly_seasonality=False,
        daily_seasonality=False,
        uncertainty_samples=0,
    )
    model.fit(training)

    dates = pd.date_range(
        start=monthly.index.max() + pd.offsets.MonthEnd(1),
        periods=max(1, int(horizon)),
        freq="ME",
    )
    future = pd.DataFrame({"ds": dates})
    predicted = model.predict(future)
    forecast = pd.DataFrame({
        "YearMonth": predicted["ds"],
        "Forecast": predicted["yhat"].clip(lower=0).round(2),
    })
    return history, forecast
