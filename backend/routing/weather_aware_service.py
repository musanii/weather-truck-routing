from datetime import datetime,timedelta

from .arrival_service import estimate_elapsed_seconds
from .checkpoint_service import get_checkpoints
from .forecast_service import find_nearest_forecast
from .risk_engine import assess_checkpoint_risk
from .route_scoring import recommend_route
from .weather_service import get_hourly_forecast


def estimate_checkpoint_arrival(start_time, steps, distance_miles):
    """Estimate when the truck reaches a checkpoint."""
    elapsed_seconds = estimate_elapsed_seconds(
        steps,
        distance_miles,
    )

    return start_time + timedelta(seconds=elapsed_seconds)


def assess_checkpoint(
    checkpoint,
    start_time,
    steps,
    forecasts,
    cargo_weight_lb,
):
    """Estimate arrival and assess weather risk at one checkpoint."""
    arrival_time = estimate_checkpoint_arrival(
        start_time,
        steps,
        checkpoint["distance_miles"],
    )

    forecast = find_nearest_forecast(forecasts, arrival_time)

    forecast_series = []

    for hourly_forecast in forecasts:
        hourly_risk = assess_checkpoint_risk(
            wind_speed_mph=hourly_forecast["wind_speed_mph"],
            rain_inches_per_hour=hourly_forecast["rain_inches_per_hour"],
            snow_inches_per_hour=hourly_forecast["snow_inches_per_hour"],
            cargo_weight_lb=cargo_weight_lb,
        )

        forecast_series.append({
            **hourly_forecast,
            "risk": hourly_risk,
        })

    result = {
        **checkpoint,
        "arrival_time": arrival_time.isoformat(),
        "forecast": forecast,
        "forecasts": forecast_series,
    }

    if forecast is None:
        result["risk"] = "UNAVAILABLE"
        return result

    result["risk"] = assess_checkpoint_risk(
        wind_speed_mph=forecast["wind_speed_mph"],
        rain_inches_per_hour=forecast["rain_inches_per_hour"],
        snow_inches_per_hour=forecast["snow_inches_per_hour"],
        cargo_weight_lb=cargo_weight_lb,
    )

    return result


def assess_route_checkpoints(
    route,
    interval_miles,
    start_time,
    cargo_weight_lb,
):
    """Assess weather risk at every checkpoint on a route."""
    coordinates = route["geometry"]["coordinates"]

    checkpoints = get_checkpoints(
        coordinates,
        interval_miles,
        route["distance_miles"],
    )

    assessed_checkpoints = []

    for checkpoint in checkpoints:
        latitude = checkpoint["coordinates"][1]
        longitude = checkpoint["coordinates"][0]

        forecasts = get_hourly_forecast(latitude, longitude)

        assessed = assess_checkpoint(
            checkpoint=checkpoint,
            start_time=start_time,
            steps=route["steps"],
            forecasts=forecasts,
            cargo_weight_lb=cargo_weight_lb,
        )

        assessed_checkpoints.append(assessed)

    return assessed_checkpoints



RISK_LEVELS = {
    "LOW": 1,
    "MODERATE": 2,
    "HIGH": 3,
    "SEVERE": 4,
    "NO_TRAVEL": 5,
}


def summarize_route_risk(checkpoints, route_distance_miles, travel_minutes):
    """Summarize estimated route risk from checkpoint assessments."""
    if not checkpoints:
        raise ValueError("At least one checkpoint is required")

    severe_miles = 0.0
    no_travel_miles=0.0
    high_miles = 0.0
    weighted_risk = 0.0
    assessed_miles = 0.0
    previous_distance = 0.0

    for checkpoint in checkpoints:
        distance = checkpoint["distance_miles"]
        segment_miles = distance - previous_distance
        previous_distance = distance

        risk = checkpoint["risk"]

        if risk == "UNAVAILABLE":
            continue

        if risk == "NO_TRAVEL":
            severe_miles += segment_miles
            no_travel_miles += segment_miles
        elif risk == "SEVERE":
            severe_miles += segment_miles
        elif risk == "HIGH":
            high_miles += segment_miles

        weighted_risk += RISK_LEVELS[risk] * segment_miles
        assessed_miles += segment_miles

    average_risk = (
        weighted_risk / assessed_miles if assessed_miles else None
    )

    return {
        "severe_miles": round(severe_miles, 2),
        "no_travel_miles":round(no_travel_miles,2),
        "high_miles": round(high_miles, 2),
        "average_risk": (
            round(average_risk, 2) if average_risk is not None else None
        ),
        "assessed_miles": round(assessed_miles, 2),
        "unknown_miles": round(route_distance_miles - assessed_miles, 2),
        "travel_minutes": travel_minutes,
    }


def assess_routes(
    routes,
    interval_miles,
    start_time,
    cargo_weight_lb,
):
    """Assess routes, summarize risk, and select a recommendation."""
    assessed_routes = []

    for route in routes:
        checkpoints = assess_route_checkpoints(
            route=route,
            interval_miles=interval_miles,
            start_time=start_time,
            cargo_weight_lb=cargo_weight_lb,
        )

        risk_summary = summarize_route_risk(
            checkpoints=checkpoints,
            route_distance_miles=route["distance_miles"],
            travel_minutes=route["travel_minutes"],
        )

        assessed_route = {
            **route,
            "checkpoints": checkpoints,
            **risk_summary,
        }

        assessed_routes.append(assessed_route)

    recommended_route = recommend_route(assessed_routes)

    return {
        "routes": assessed_routes,
        "recommended_route": (
            recommended_route["name"]
            if recommended_route is not None
            else None
        ),
    }



