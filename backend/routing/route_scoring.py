
def recommend_route(routes):
    """Recommend the best fully assessed route using the priority rules."""
    if not routes:
        raise ValueError("At least one route is required")

    fully_assessed_routes = [
        route
        for route in routes
        if route.get("unknown_miles", 0) == 0
        and route.get("average_risk") is not None
    ]

    if not fully_assessed_routes:
        return None

    return min(
        fully_assessed_routes,
        key=lambda route: (
            route["severe_miles"],
            route["high_miles"],
            route["average_risk"],
            route["travel_minutes"],
        ),
    )
