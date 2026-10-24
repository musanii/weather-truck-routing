
from math import asin, cos, radians, sin, sqrt


EARTH_RADIUS_MILES = 3958.8


def distance_between(point_a, point_b):
    """Calculate the distance between two [longitude, latitude] points."""
    lon1, lat1 = point_a
    lon2, lat2 = point_b

    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lat_difference = radians(lat2 - lat1)
    lon_difference = radians(lon2 - lon1)

    a = (
        sin(lat_difference / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(lon_difference / 2) ** 2
    )

    return 2 * EARTH_RADIUS_MILES * asin(sqrt(a))



def get_checkpoints(
    coordinates,
    interval_miles,
    route_distance_miles=None,
):
    """Return checkpoints at selected distances along a route."""
    if interval_miles not in (10, 25, 50):
        raise ValueError("Interval must be 10, 25, or 50 miles")

    if len(coordinates) < 2:
        raise ValueError("Route must contain at least two coordinates")

    segment_distances = [
        distance_between(coordinates[i - 1], coordinates[i])
        for i in range(1, len(coordinates))
    ]

    geometry_distance = sum(segment_distances)

    if geometry_distance <= 0:
        raise ValueError("Route geometry must have a positive length")

    target_distance = (
        route_distance_miles
        if route_distance_miles is not None
        else geometry_distance
    )

    if target_distance <= 0:
        raise ValueError("Route distance must be positive")

    scale = target_distance / geometry_distance
    checkpoints = []
    cumulative_distance = 0.0
    next_checkpoint = float(interval_miles)

    for index, segment_distance in enumerate(segment_distances, start=1):
        segment_start = cumulative_distance
        cumulative_distance += segment_distance * scale

        while next_checkpoint <= cumulative_distance:
            fraction = (
                (next_checkpoint - segment_start)
                / (segment_distance * scale)
            )

            previous_point = coordinates[index - 1]
            current_point = coordinates[index]

            lon = previous_point[0] + fraction * (
                current_point[0] - previous_point[0]
            )
            lat = previous_point[1] + fraction * (
                current_point[1] - previous_point[1]
            )

            checkpoints.append({
                "distance_miles": round(next_checkpoint, 2),
                "coordinates": [lon, lat],
            })

            next_checkpoint += interval_miles

    checkpoints.append({
        "distance_miles": round(target_distance, 2),
        "coordinates": coordinates[-1],
    })

    return checkpoints
