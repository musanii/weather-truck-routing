
from django.test import SimpleTestCase

from .route_scoring import recommend_route


class RouteRecommendationTests(SimpleTestCase):
    def setUp(self):
        self.routes = [
            {
                "name": "Route A",
                "severe_miles": 5,
                "high_miles": 10,
                "average_risk": 2.1,
                "travel_minutes": 120,
            },
            {
                "name": "Route B",
                "severe_miles": 0,
                "high_miles": 15,
                "average_risk": 2.5,
                "travel_minutes": 90,
            },
            {
                "name": "Route C",
                "severe_miles": 0,
                "high_miles": 10,
                "average_risk": 2.0,
                "travel_minutes": 110,
            },
        ]

    def test_fewest_severe_miles_has_highest_priority(self):
        self.assertEqual(recommend_route(self.routes)["name"], "Route C")

    def test_empty_route_list_is_rejected(self):
        with self.assertRaises(ValueError):
            recommend_route([])

    
    def test_excludes_routes_with_unknown_weather(self):
        routes = [
            {
                "name": "Route A",
                "severe_miles": 0,
                "high_miles": 0,
                "average_risk": 1.0,
                "travel_minutes": 60,
                "unknown_miles": 10,
            },
            {
                "name": "Route B",
                "severe_miles": 2,
                "high_miles": 3,
                "average_risk": 2.0,
                "travel_minutes": 80,
                "unknown_miles": 0,
            },
        ]

        self.assertEqual(recommend_route(routes)["name"], "Route B")

    def test_returns_none_when_all_routes_have_unknown_weather(self):
        routes = [
            {
                "name": "Route A",
                "severe_miles": 0,
                "high_miles": 0,
                "average_risk": 1.0,
                "travel_minutes": 60,
                "unknown_miles": 10,
            },
        ]

        self.assertIsNone(recommend_route(routes))

    
    def test_lowest_average_risk_beats_shorter_travel_time(self):
        routes = [
            {
                "name": "Faster Route",
                "severe_miles": 0,
                "high_miles": 0,
                "average_risk": 2.0,
                "travel_minutes": 60,
                "unknown_miles": 0,
            },
            {
                "name": "Safer Route",
                "severe_miles": 0,
                "high_miles": 0,
                "average_risk": 1.5,
                "travel_minutes": 90,
                "unknown_miles": 0,
            },
        ]

        self.assertEqual(recommend_route(routes)["name"], "Safer Route")

    
    def test_shorter_travel_time_breaks_a_tie(self):
        routes = [
            {
                "name": "Slower Route",
                "severe_miles": 0,
                "high_miles": 2,
                "average_risk": 1.5,
                "travel_minutes": 80,
                "unknown_miles": 0,
            },
            {
                "name": "Faster Route",
                "severe_miles": 0,
                "high_miles": 2,
                "average_risk": 1.5,
                "travel_minutes": 50,
                "unknown_miles": 0,
            },
        ]

        self.assertEqual(recommend_route(routes)["name"], "Faster Route")



