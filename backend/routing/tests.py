from datetime import datetime
from django.test import SimpleTestCase
from .forecast_service import find_nearest_forecast
from .weather_aware_service import summarize_route_risk
from .risk_engine import (
    assess_checkpoint_risk,
    classify_rain,
    classify_snow,
    classify_wind,
)


class WeatherClassificationTests(SimpleTestCase):
    def test_wind_at_55_mph_means_no_travel(self):
        self.assertEqual(classify_wind(55, 10000), "NO_TRAVEL")

    def test_heavy_cargo_triggers_no_travel_in_high_wind(self):
        self.assertEqual(classify_wind(50, 30001), "NO_TRAVEL")

    def test_heavy_cargo_triggers_severe_risk(self):
        self.assertEqual(classify_wind(40, 40001), "SEVERE")

    def test_light_cargo_in_40_mph_wind_is_high(self):
        self.assertEqual(classify_wind(40, 30000), "HIGH")

    def test_rain_of_030_inches_per_hour_is_high(self):
        self.assertEqual(classify_rain(0.30), "HIGH")

    def test_rain_above_1_inch_per_hour_means_no_travel(self):
        self.assertEqual(classify_rain(1.01), "NO_TRAVEL")

    def test_snow_above_3_inches_per_hour_means_no_travel(self):
        self.assertEqual(classify_snow(3.1), "NO_TRAVEL")

    def test_checkpoint_uses_highest_weather_risk(self):
        self.assertEqual(
            assess_checkpoint_risk(20, 0.30, 0.2, 10000),
            "HIGH",
        )


class ForecastSelectionTests(SimpleTestCase):
    def setUp(self):
        self.forecasts = [
            {
                "time": "2026-10-22T14:00",
                "wind_speed_mph": 8.0,
                "rain_inches_per_hour": 0.0,
                "snow_inches_per_hour": 0.0,
            },
            {
                "time": "2026-10-22T15:00",
                "wind_speed_mph": 10.5,
                "rain_inches_per_hour": 0.1,
                "snow_inches_per_hour": 0.0,
            },
        ]

    def test_selects_closest_forecast(self):
        result = find_nearest_forecast(
            self.forecasts,
            datetime.fromisoformat("2026-10-22T14:35"),
        )

        self.assertEqual(result["time"], "2026-10-22T15:00")

    def test_returns_none_after_forecast_window(self):
        result = find_nearest_forecast(
            self.forecasts,
            datetime.fromisoformat("2026-10-23T16:00"),
        )

        self.assertIsNone(result)

    def test_returns_none_before_forecast_window(self):
        result = find_nearest_forecast(
            self.forecasts,
            datetime.fromisoformat("2026-10-22T13:00"),
        )

        self.assertIsNone(result)

    def test_returns_none_for_empty_forecasts(self):
        self.assertIsNone(
            find_nearest_forecast([], "2026-10-22T14:00")
        )



class RouteRiskSummaryTests(SimpleTestCase):
    def test_calculates_risk_miles_and_average(self):
        checkpoints = [
            {"distance_miles": 10, "risk": "LOW"},
            {"distance_miles": 20, "risk": "HIGH"},
            {"distance_miles": 30, "risk": "SEVERE"},
        ]

        result = summarize_route_risk(
            checkpoints,
            route_distance_miles=30,
            travel_minutes=45,
        )

        self.assertEqual(result["severe_miles"], 10)
        self.assertEqual(result["high_miles"], 10)
        self.assertEqual(result["average_risk"], 2.67)
        self.assertEqual(result["assessed_miles"], 30)
        self.assertEqual(result["unknown_miles"], 0)
        self.assertEqual(result["travel_minutes"], 45)

    def test_excludes_unavailable_weather_from_average(self):
        checkpoints = [
            {"distance_miles": 10, "risk": "LOW"},
            {"distance_miles": 20, "risk": "UNAVAILABLE"},
        ]

        result = summarize_route_risk(
            checkpoints,
            route_distance_miles=20,
            travel_minutes=30,
        )

        self.assertEqual(result["assessed_miles"], 10)
        self.assertEqual(result["unknown_miles"], 10)
        self.assertEqual(result["average_risk"], 1.0)

    def test_rejects_empty_checkpoints(self):
        with self.assertRaises(ValueError):
            summarize_route_risk([], 20, 30)


    def test_tracks_no_travel_miles_separately(self):
        checkpoints = [
            {"distance_miles": 10, "risk": "LOW"},
            {"distance_miles": 20, "risk": "NO_TRAVEL"},
        ]

        result = summarize_route_risk(
            checkpoints,
            route_distance_miles=20,
            travel_minutes=30,
        )

        self.assertEqual(result["severe_miles"], 10)
        self.assertEqual(result["no_travel_miles"], 10)

                           