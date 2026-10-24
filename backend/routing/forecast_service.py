
from datetime import datetime


def find_nearest_forecast(forecasts, arrival_time):
    """Find the nearest hourly forecast, if arrival is in range."""
    if not forecasts:
        return None

    if isinstance(arrival_time, str):
        arrival_time = datetime.fromisoformat(arrival_time)

    forecast_times = [
        datetime.fromisoformat(forecast["time"])
        for forecast in forecasts
    ]

    earliest = min(forecast_times)
    latest = max(forecast_times)

    if arrival_time < earliest or arrival_time > latest:
        return None

    return min(
        forecasts,
        key=lambda forecast: abs(
            datetime.fromisoformat(forecast["time"]) - arrival_time
        ),
    )
