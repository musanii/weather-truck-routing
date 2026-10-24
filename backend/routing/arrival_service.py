
def estimate_elapsed_seconds(steps, distance_miles):
    """Estimate elapsed travel time at a distance along a route."""
    if distance_miles < 0:
        raise ValueError("Distance cannot be negative")

    target_distance_m = distance_miles * 1609.344
    distance_covered_m = 0.0
    elapsed_seconds = 0.0

    for step in steps:
        step_distance = step["distance_m"]
        step_duration = step["duration_seconds"]

        if step_distance <= 0:
            continue

        remaining_distance = target_distance_m - distance_covered_m

        if remaining_distance <= 0:
            break

        if remaining_distance >= step_distance:
            distance_covered_m += step_distance
            elapsed_seconds += step_duration
        else:
            fraction = remaining_distance / step_distance
            elapsed_seconds += fraction * step_duration
            break

    return round(elapsed_seconds)
