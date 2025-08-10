# utils_forecast.py
import numpy as np
import pandas as pd

def forecast_baseline(df: pd.DataFrame, horizon_days: int = 30):
    """
    Baseline légère:
    - Agrège ventes/jour
    - MA7 (moyenne mobile 7j)
    - Régression linéaire sur MA7 pour extrapoler horizon_days
    """
    if "Date" not in df or "Total (€)" not in df:
        return None, None
    daily = df.groupby("Date", as_index=False)["Total (€)"].sum().sort_values("Date")
    if len(daily) < 5:
        return None, None

    daily["ma7"] = daily["Total (€)"].rolling(7, min_periods=1).mean()
    x = np.arange(len(daily))
    slope, intercept = np.polyfit(x, daily["ma7"], 1)

    future_idx = np.arange(len(daily), len(daily) + horizon_days)
    y_pred = slope * future_idx + intercept
    future_dates = pd.date_range(daily["Date"].max() + pd.Timedelta(days=1), periods=horizon_days)

    forecast = pd.DataFrame({"Date": future_dates, "Prévision (€)": np.clip(y_pred, 0, None)})
    return daily, forecast
