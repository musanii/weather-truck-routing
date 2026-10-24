# RouteCast API Documentation

## Base URL

For local development:

```text
http://127.0.0.1:8000
```

## 1. Health Check

Checks whether the backend API is responding.

**Endpoint:** `GET /api/health/`

### Successful response — `200 OK`

```json
{
  "status": "ok",
  "service": "weather-truck-routing-api"
}
```

## 2. Assess Routes

Requests alternative driving routes and assesses their weather risks at checkpoints.

**Endpoint:** `POST /api/routes/`

**Content-Type:** `application/json`

### Request body

```json
{
  "start": [36.821888, -1.292074],
  "end": [37.069459, -1.032584],
  "start_time": "2026-10-22T14:00:00",
  "cargo_weight_lb": 25000,
  "interval_miles": 10
}
```

### Request fields

| Field | Type | Requirements |
|---|---|---|
| `start` | Array of numbers | Exactly two values: longitude, latitude |
| `end` | Array of numbers | Exactly two values: longitude, latitude |
| `start_time` | String | Valid ISO-format date-time without a timezone offset; interpreted as Nairobi local time |
| `cargo_weight_lb` | Number | Must be greater than zero, measured in pounds |
| `interval_miles` | Integer | Must be `10`, `25`, or `50` |

Coordinates must use `[longitude, latitude]` order. The view checks the number and numeric format of the coordinate values, but does not itself enforce geographic coordinate ranges.

### Successful response

A successful request returns a JSON object with two top-level fields:

- `routes`: a list of assessed routes. Each route combines the original routing data, its checkpoint assessments, and its calculated risk summary.
- `recommended_route`: the name of the recommended route as a string, or `null` if no route qualifies.

Each assessed route contains a `checkpoints` list and the risk-summary fields produced by the assessment service. The original route data is also included.

The recommendation is selected using the application's route-scoring rules. A route must have zero unknown miles and a non-null average risk score to qualify. If no route qualifies, `recommended_route` is `null`.

### Validation errors — `400 Bad Request`

Invalid input returns a JSON object containing an `error` message.

| Problem | Error message |
|---|---|
| Missing or blank departure time | `Start time must be a valid date-time string.` |
| Invalid date-time format | `Start time must use ISO format, e.g. 2026-10-22T14:00:00.` |
| Departure time includes a timezone offset | `Start time must use Nairobi local time without a timezone offset.` |
| Missing, invalid, zero, or negative cargo weight | `Cargo weight must be a positive number in pounds.` |
| Unsupported checkpoint interval | `Checkpoint interval must be 10, 25, or 50 miles.` |
| Start or end is not a coordinate array | `Start and end must be coordinate arrays.` |
| A coordinate array does not contain two values | `Each coordinate array must contain longitude and latitude.` |
| Coordinates are not numeric | `Coordinates must be numbers.` |

Example error response:

```json
{
  "error": "Checkpoint interval must be 10, 25, or 50 miles."
}
```

### Upstream service errors

| HTTP status | Meaning |
|---|---|
| `502 Bad Gateway` | A routing or weather provider could not be reached or returned invalid data |
| `503 Service Unavailable` | A required routing or other service is not configured |

These errors return a JSON object with an `error` field describing the failure.

## Notes

- Route generation uses OpenRouteService.
- Weather assessment uses weather forecasts and the application's configured risk rules.
- Checkpoint intervals control the spacing of route weather assessments.
- Route recommendations depend on weather coverage and the application's route-scoring rules.
- A recommendation is decision support, not a guarantee of safe driving conditions.
