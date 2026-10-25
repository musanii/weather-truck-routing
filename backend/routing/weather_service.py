import requests
from functools import lru_cache

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

@lru_cache(maxsize=512)
def get_hourly_forecast(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude":longitude,
        "hourly":"wind_speed_10m,rain,snowfall",
        "wind_speed_unit":"mph",
        "precipitation_unit":"inch",
        "forecast_hours":48,
        "timezone":"Africa/Nairobi",
    }


    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data =response.json()
    hourly = data.get("hourly")

    if not hourly:
        raise ValueError("Weather provider returned no hourly forecast")

    times = hourly.get("time",[])
    winds = hourly.get("wind_speed_10m",[])
    rainfall = hourly.get("rain",[])
    snowfall = hourly.get("snowfall",[])

    if not times or not (
        len(times) == len(winds) == len(rainfall) == len(snowfall)
    ):
        raise ValueError("Weather provider returned incomplete hourly data")

    forecasts = []

    for time, wind, rain, snow_cm in zip(
        times, winds, rainfall,snowfall
    ):
        if wind is None or rain is None or snow_cm is None:
            continue

        forecasts.append({
            "time":time,
            "wind_speed_mph":wind,
            "rain_inches_per_hour":rain,
            "snow_inches_per_hour":snow_cm/ 2.54,
        })
        
    return forecasts

