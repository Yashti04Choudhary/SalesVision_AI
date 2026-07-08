import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from xgboost import XGBRegressor

def create_monthly_ts(df, filter_type=None, filter_value=None):
    """
    Creates a monthly time series of sales.

    Parameters
    ----------
    df : pandas.DataFrame
        Original sales dataframe.

    filter_type : str, optional
        Column name to filter on (e.g., "Category" or "Region").

    filter_value : str, optional
        Value within the filter column.

    Returns
    -------
    pandas.DataFrame
        Monthly sales time series with:
        - Order Date as DatetimeIndex
        - Sales column
    """

    filtered_df = df.copy()

    # Apply filter if provided
    if filter_type is not None and filter_value is not None:
        filtered_df = filtered_df[
            filtered_df[filter_type] == filter_value
        ]

    # Aggregate monthly sales
    monthly_ts = (
        filtered_df
        .groupby(pd.Grouper(key="Order Date", freq="ME"))["Sales"]
        .sum()
        .to_frame()
    )

    # Ensure chronological order
    monthly_ts.sort_index(inplace=True)

    return monthly_ts


def prepare_features(monthly_ts):
    """
    Convert monthly time series into ML-ready features.

    Parameters
    ----------
    monthly_ts : pandas.DataFrame
        Monthly sales time series with Order Date index.

    Returns
    -------
    pandas.DataFrame
        Feature-engineered dataframe ready for XGBoost.
    """

    ts_ml = monthly_ts.copy().reset_index()

    # Lag Features
    ts_ml["Lag_1"] = ts_ml["Sales"].shift(1)
    ts_ml["Lag_2"] = ts_ml["Sales"].shift(2)
    ts_ml["Lag_3"] = ts_ml["Sales"].shift(3)

    # Rolling Mean
    ts_ml["Rolling_Mean_3"] = ts_ml["Sales"].rolling(window=3).mean()

    # Calendar Features
    ts_ml["Month"] = ts_ml["Order Date"].dt.month
    ts_ml["Quarter"] = ts_ml["Order Date"].dt.quarter

    # Season Feature
    def get_season(month):
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Autumn"

    ts_ml["Season"] = ts_ml["Month"].apply(get_season)

    # One-hot encoding
    ts_ml = pd.get_dummies(
        ts_ml,
        columns=["Season"],
        drop_first=True
    )

    # Remove missing lag values
    ts_ml = ts_ml.dropna()

    return ts_ml


def load_best_model():
    """
    Load the saved production XGBoost model.
    """

    model_path = Path("models") / "best_model.pkl"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    return joblib.load(model_path)


def generate_forecast_hybrid(df, filter_type=None, filter_value=None, horizon=3):
    """
    Generate sales forecasts using a hybrid strategy:
    - Overall sales: uses the pre-trained production model (best_model.pkl).
    - Filtered sales (by Region/Category): trains a lightweight XGBoost model on the fly.

    Uses recursive forecasting for 1 to 3 months by updating lag features.
    """

    # 1. Fetch historical monthly sales using helper
    hist_monthly_ts = create_monthly_ts(df, filter_type, filter_value)

    if hist_monthly_ts.empty:
        return pd.DataFrame(columns=["YearMonth", "Sales"]), pd.DataFrame(columns=["YearMonth", "Forecast"])

    # Prepare historical data for output
    hist_monthly = hist_monthly_ts.reset_index().rename(columns={"Order Date": "YearMonth"})

    # 2. Select / Train model based on hybrid strategy
    feature_cols = ['Lag_1', 'Lag_2', 'Lag_3', 'Rolling_Mean_3', 'Month', 'Quarter', 'Season_Spring', 'Season_Summer', 'Season_Winter']

    if filter_type is None or filter_value is None:
        model = load_best_model()
    else:
        # Train custom lightweight model on the fly
        ts_ml = prepare_features(hist_monthly_ts)
        if len(ts_ml) >= 10:
            X_train = ts_ml.drop(columns=["Order Date", "Sales"])
            y_train = ts_ml["Sales"]
            X_train = X_train.reindex(columns=feature_cols, fill_value=0)

            model = XGBRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=42
            )
            model.fit(X_train, y_train)
        else:
            # Fallback to pre-trained model if filtered data is too small to build lags
            model = load_best_model()

    # 3. Recursive Forecasting for 1-3 months
    last_date = hist_monthly_ts.index.max()
    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=horizon, freq="ME")

    sales_history = list(hist_monthly_ts['Sales'].values)
    forecast_values = []

    for h in range(horizon):
        next_date = forecast_dates[h]

        # Get Lag values
        Lag_1 = sales_history[-1]
        Lag_2 = sales_history[-2] if len(sales_history) >= 2 else Lag_1
        Lag_3 = sales_history[-3] if len(sales_history) >= 3 else Lag_2

        # Compute Rolling Mean (average of the last 3 sales observations)
        Rolling_Mean_3 = (Lag_1 + Lag_2 + Lag_3) / 3.0

        # Date features
        Month = next_date.month
        Quarter = next_date.quarter

        # Season features
        Season_Spring = 1 if Month in [3, 4, 5] else 0
        Season_Summer = 1 if Month in [6, 7, 8] else 0
        Season_Winter = 1 if Month in [12, 1, 2] else 0

        # Construct feature vector
        X_step = pd.DataFrame([{
            'Lag_1': Lag_1,
            'Lag_2': Lag_2,
            'Lag_3': Lag_3,
            'Rolling_Mean_3': Rolling_Mean_3,
            'Month': Month,
            'Quarter': Quarter,
            'Season_Spring': Season_Spring,
            'Season_Summer': Season_Summer,
            'Season_Winter': Season_Winter
        }])[feature_cols]

        # Predict next value
        y_pred = float(model.predict(X_step)[0])
        y_pred = round(max(0.0, y_pred),2)  # sales cannot be negative

        # Append to forecast lists
        # Add prediction back into history for recursive forecasting
        forecast_values.append(y_pred)
        sales_history.append(y_pred) # Recursive update

    forecast_df = pd.DataFrame({
        'YearMonth': forecast_dates,
        'Forecast': forecast_values
    })

    return hist_monthly, forecast_df