# RouteCast Risk Assessment

## 1. Purpose

RouteCast assesses driving routes using weather forecasts and truck-specific risk rules. It evaluates conditions at checkpoints along each route, summarizes the risk exposure, and recommends a route using risk-first scoring.

The implemented thresholds are application rules, not a substitute for official road-safety guidance.

## 2. Risk Levels

Risk levels are ordered from lowest to highest:

1. `LOW`
2. `MODERAfTE`
3. `HIGH`
4. `SEVERE`
5. `NO_TRAVEL`

When multiple weather hazards are assessed at a checkpoint, the highest applicable risk level becomes the checkpoint's overall risk.

## 3. Wind Risk

Wind risk depends on wind speed and cargo weight.

| Condition | Risk |
|---|---|
| Wind speed ≥ 55 mph | `NO_TRAVEL` |
| Wind speed ≥ 45 mph and cargo weight > 30,000 lb | `NO_TRAVEL` |
| Wind speed ≥ 35 mph and cargo weight > 40,000 lb | `SEVERE` |
| Wind speed ≥ 45 mph, when earlier rules do not apply | `SEVERE` |
| Wind speed ≥ 35 mph | `HIGH` |
| Wind speed ≥ 25 mph | `MODERATE` |
| Otherwise | `LOW` |

Rules are evaluated in order. The first matching rule determines the wind classification.

## 4. Rain Risk

Rainfall is assessed in inches per hour.

| Rainfall | Risk |
|---|---|
| > 1.00 inches/hour | `NO_TRAVEL` |
| ≥ 0.50 inches/hour | `SEVERE` |
| ≥ 0.25 inches/hour | `HIGH` |
| ≥ 0.10 inches/hour | `MODERATE` |
| Otherwise | `LOW` |

## 5. Snow Risk

Snowfall is assessed in inches per hour.

| Snowfall | Risk |
|---|---|
| > 3.0 inches/hour | `NO_TRAVEL` |
| ≥ 2.0 inches/hour | `SEVERE` |
| ≥ 1.0 inch/hour | `HIGH` |
| ≥ 0.5 inches/hour | `MODERATE` |
| Otherwise | `LOW` |

## 6. Checkpoint Assessment

The application divides each route into checkpoints using the selected interval of 10, 25, or 50 miles.

It estimates the arrival time at each checkpoint and uses the nearest available hourly weather forecast to assess conditions. The checkpoint risk is the highest classification among wind, rain, and snow.

If a suitable forecast is unavailable for a checkpoint, its risk is marked `UNAVAILABLE`. This means the application cannot assess that checkpoint from the available forecast data; it does not mean the conditions are safe.

## 7. Route Risk Summary

RouteCast summarizes the assessed checkpoint segments using fields including:

- `severe_miles`: miles assigned severe risk, including `NO_TRAVEL` segments.
- `no_travel_miles`: miles assigned `NO_TRAVEL` risk.
- `high_miles`: miles assigned high risk.
- `average_risk`: distance-weighted average risk score across assessed segments, or `null` when no miles can be assessed.
- `assessed_miles`: miles with usable risk assessments.
- `unknown_miles`: miles whose weather risk could not be assessed.
- `travel_minutes`: estimated route travel time in minutes.

Segments with `UNAVAILABLE` risk are excluded from the weighted average-risk calculation and from `assessed_miles`. `unknown_miles` is calculated as the route's total distance minus `assessed_miles`. `NO_TRAVEL` segments count toward both `severe_miles` and `no_travel_miles`. Therefore, average risk should be interpreted alongside assessed and unknown mileage, not in isolation.

## 8. Route Recommendation

A route is eligible for recommendation only when:

- `unknown_miles` equals zero.
- `average_risk` is not `null`.

Eligible routes are compared in this order:

1. Lowest `severe_miles`.
2. Lowest `high_miles`.
3. Lowest `average_risk`.
4. Lowest `travel_minutes`.

This ordering prioritizes reducing severe and high-risk exposure before comparing average risk and travel time.

If no route qualifies, the API returns `null` for `recommended_route`.

## 9. Limitations

- Risk results depend on the available routing and weather-provider data.
- Forecasts may not cover every checkpoint.
- The implemented thresholds are application-specific rules and are not a guarantee of safe driving conditions.
- A recommendation is decision support; drivers and operators must still consider current road conditions and applicable safety guidance.
