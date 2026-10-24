RISK_LEVELS = {
    "LOW":1,
    "MODERATE":2,
    "HIGH":3,
    "SEVERE":4,
    "NO_TRAVEL":5
}


def classify_wind(wind_speed_mph, cargo_weight_lb):
    if wind_speed_mph >= 55:
        return "NO_TRAVEL"

    if wind_speed_mph >= 45 and cargo_weight_lb > 30000:
        return "NO_TRAVEL"

    if wind_speed_mph >= 35 and cargo_weight_lb > 40000:
        return "SEVERE"

    if wind_speed_mph >= 45:
        return "SEVERE"

    if wind_speed_mph >= 35:
        return "HIGH"

    if wind_speed_mph >= 25:
        return "MODERATE"

    return "LOW"


def classify_rain(rain_inches_per_hour):
    if rain_inches_per_hour > 1.00:
        return "NO_TRAVEL"

    if rain_inches_per_hour >=0.50:
        return "SEVERE"

    if rain_inches_per_hour >= 0.25:
        return "HIGH"

    if rain_inches_per_hour >= 0.10:
        return "MODERATE"

    return "LOW"

def classify_snow(snow_inches_per_hour):
    if snow_inches_per_hour > 3.0:
        return "NO_TRAVEL"

    if snow_inches_per_hour >= 2.0:
        return "SEVERE"

    if snow_inches_per_hour >= 1.0:
        return "HIGH"

    if snow_inches_per_hour >= 0.5:
        return "MODERATE"

    return "LOW"

def assess_checkpoint_risk(
    wind_speed_mph,
    rain_inches_per_hour,
    snow_inches_per_hour,
    cargo_weight_lb,
):
    risks = [
        classify_wind(wind_speed_mph,cargo_weight_lb),
        classify_rain(rain_inches_per_hour),
        classify_snow(snow_inches_per_hour),
    ]

    return max(risks, key=lambda risk:RISK_LEVELS[risk])