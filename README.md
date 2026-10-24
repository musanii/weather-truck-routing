# RouteCast — Weather-Aware Truck Routing

RouteCast is a web application that compares driving routes using weather forecasts and truck-specific risk rules. Instead of choosing a route based only on distance or travel time, it assesses weather conditions along each route and recommends the safest fully assessed option.

## Features

- Retrieves alternative driving routes using OpenRouteService.
- Assesses weather conditions at configurable route checkpoints.
- Estimates checkpoint arrival times to select relevant hourly forecasts.
- Classifies wind, rain, and snow risks using configurable business rules.
- Considers cargo weight when evaluating wind risk.
- Summarizes route risk, including severe-risk miles, high-risk miles, assessed miles, and unknown miles.
- Recommends a route using risk-first scoring, with travel time as a later tie-breaker.
- Displays routes and their assessments in an interactive map interface.
- Provides a health-check endpoint for the backend API.

## Technology stack

| Component | Technology |
|---|---|
| Frontend | React, Vite |
| Map | Leaflet, React Leaflet |
| Backend | Python, Django, Django REST Framework |
| Routing data | OpenRouteService |
| Weather forecasts | Open-Meteo |
| Backend configuration | Environment variables and `python-dotenv` |

## How it works

1. The user provides a start point, destination, departure time, cargo weight, and checkpoint interval.
2. The backend requests alternative routes from OpenRouteService.
3. Each route is divided into checkpoints based on the selected interval.
4. The application estimates arrival times at the checkpoints and obtains the nearest available hourly weather forecasts.
5. Wind, rain, and snow conditions are classified into risk levels.
6. Route-level risk summaries are calculated.
7. The application recommends the route with the lowest risk according to its scoring rules, provided at least one route is fully assessed.

### Risk levels

The application uses the following ordered risk levels:

`LOW` → `MODERATE` → `HIGH` → `SEVERE` → `NO_TRAVEL`

The highest applicable weather risk determines the checkpoint's overall risk.

#### Wind rules

| Condition | Risk |
|---|---|
| Wind speed ≥ 55 mph | `NO_TRAVEL` |
| Wind speed ≥ 45 mph and cargo weight > 30,000 lb | `NO_TRAVEL` |
| Wind speed ≥ 35 mph and cargo weight > 40,000 lb | `SEVERE` |
| Wind speed ≥ 45 mph, when earlier rules do not apply | `SEVERE` |
| Wind speed ≥ 35 mph | `HIGH` |
| Wind speed ≥ 25 mph | `MODERATE` |
| Otherwise | `LOW` |

#### Rain rules

| Rainfall per hour | Risk |
|---|---|
| > 1.00 inches | `NO_TRAVEL` |
| ≥ 0.50 inches | `SEVERE` |
| ≥ 0.25 inches | `HIGH` |
| ≥ 0.10 inches | `MODERATE` |
| Otherwise | `LOW` |

#### Snow rules

| Snowfall per hour | Risk |
|---|---|
| > 3.0 inches | `NO_TRAVEL` |
| ≥ 2.0 inches | `SEVERE` |
| ≥ 1.0 inch | `HIGH` |
| ≥ 0.5 inches | `MODERATE` |
| Otherwise | `LOW` |

These are the application's implemented assessment thresholds, not a substitute for official road-safety guidance.

### Route recommendation

Routes are compared in this order:

1. Lowest number of severe-risk miles.
2. Lowest number of high-risk miles.
3. Lowest average risk score.
4. Shortest estimated travel time.

A route is eligible for recommendation only if it has zero unknown miles and a non-null average risk score. If no route meets these conditions, `recommended_route` is `null`.

## Project structure

```text
weather-truck-routing/
├── backend/
│   ├── config/
│   ├── routing/
│   ├── manage.py
│   └── requirements.txt
├── frontend/
└── README.md
```

## Prerequisites

- Python compatible with the project's Django version.
- Node.js and npm.
- An OpenRouteService API key.

The frontend and backend run as separate development servers.

## Environment configuration

Create a local `.env` file in the project root. Do not commit secrets to version control.

Configure the following variables:

```dotenv
ORS_API_KEY=your_openrouteservice_api_key
DJANGO_SECRET_KEY=your_django_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Use your actual local configuration values. Keep `.env` out of Git.

The backend loads configuration from this file. Open-Meteo is used for weather forecasts.

## Run locally

### 1. Start the backend

From the project root, activate your Python virtual environment and install the backend dependencies:

```bash
python -m pip install -r backend/requirements.txt
```

Run the Django development server:

```bash
python backend/manage.py runserver
```

The API will be available at:

`http://127.0.0.1:8000`

### 2. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env.local` with the backend API URL:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the frontend:

```bash
npm run dev
```

Open the local URL printed by Vite, normally:

`http://localhost:5173`

## API overview

### Health check

`GET /api/health/`

Returns the backend service status.

Example response:

```json
{
  "status": "ok",
  "service": "weather-truck-routing-api"
}
```

### Assess routes

`POST /api/routes/`

Accepts a JSON request containing the route endpoints, departure time, cargo weight, and checkpoint interval.

Example request:

```json
{
  "start": [36.821888, -1.292074],
  "end": [37.069459, -1.032584],
  "start_time": "2026-10-22T14:00:00",
  "cargo_weight_lb": 25000,
  "interval_miles": 10
}
```

Coordinates use `[longitude, latitude]` order. The departure time is Nairobi local time, written without a timezone offset. Supported checkpoint intervals are 10, 25, and 50 miles.

A successful response contains the assessed routes and the recommended route name, or `null` when no fully assessed route qualifies.

Route assessment results include fields such as:

- `name`
- `distance_km` and `distance_miles`
- `travel_minutes`
- `checkpoints`
- `severe_miles`
- `high_miles`
- `average_risk`
- `assessed_miles`
- `unknown_miles`

Each checkpoint includes its distance along the route, coordinates, estimated arrival time, forecast, and risk classification.

### Error responses

The API uses HTTP error responses for invalid requests and upstream service failures. Examples include:

| Status | Meaning |
|---|---|
| `400` | Invalid request data, coordinates, departure time, cargo weight, or checkpoint interval |
| `502` | A routing or weather provider could not be reached or returned invalid data |
| `503` | A required service is not configured |

## Testing and validation

The backend has a routing test suite. The frontend has lint and production-build checks.

The following checks were previously completed successfully during development:

- Backend routing tests: 22 passed.
- Frontend lint: passed.
- Frontend production build: passed.
- Frontend API base URL: configurable through `VITE_API_BASE_URL`.

Run the backend tests from the project root:

```bash
python backend/manage.py test routing
```

Run frontend checks from the `frontend/` directory:

```bash
npm run lint
npm run build
```

## Configuration and deployment notes

The project has been configured to use environment variables for important settings and to allow the frontend API URL to be changed without editing application code.

The local development configuration is not, by itself, a production deployment configuration. Before production use, review Django's debug setting, allowed hosts, secret management, database configuration, static files, and deployment server setup.

## Limitations

- Route recommendations depend on the available routing and weather-provider data.
- Weather forecasts may not cover every checkpoint. Routes with unknown weather coverage are excluded from recommendation.
- Risk classifications depend on the thresholds implemented in the application.
- A route recommendation supports decision-making; it does not guarantee safe driving conditions.
