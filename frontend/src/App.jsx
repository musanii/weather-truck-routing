import "./App.css";
import { useState } from "react";
import RouteMap from "./RouteMap";

function getLocalDateTime() {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60_000;

  return new Date(now.getTime() - offset).toISOString().slice(0, 16);
}

function App() {
  const [start, setStart] = useState("36.8219, -1.2921");
  const [end, setEnd] = useState("37.0693, -1.0333");
  const [startTime, setStartTime] = useState(getLocalDateTime);
  const [cargoWeight, setCargoWeight] = useState("25000");
  const [interval, setInterval] = useState("10");
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [forecastHour, setForecastHour] = useState(0);

  const selectedTime = new Date(
    new Date(startTime).getTime() + forecastHour * 60 * 60 * 1000,
  );

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResults(null);
    setForecastHour(0);

    try {
      const startCoordinates = start.split(",").map(Number);
      const endCoordinates = end.split(",").map(Number);

      if (
        startCoordinates.length !== 2 ||
        endCoordinates.length !== 2 ||
        [...startCoordinates, ...endCoordinates].some(
          (value) => !Number.isFinite(value),
        ) ||
        [...startCoordinates, ...endCoordinates].some(
          (value) => Math.abs(value) > 180,
        ) ||
        Math.abs(startCoordinates[1]) > 90 ||
        Math.abs(endCoordinates[1]) > 90
      ) {
        throw new Error("Enter valid longitude, latitude coordinates.");
      }

      const weight = Number(cargoWeight);
      if (!Number.isFinite(weight) || weight <= 0) {
        throw new Error("Cargo weight must be greater than zero.");
      }

      const response = await fetch("http://127.0.0.1:8000/api/routes/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start: startCoordinates,
          end: endCoordinates,
          start_time: startTime,
          cargo_weight_lb: weight,
          interval_miles: Number(interval),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `Request failed: ${response.status}`);
      }

      setResults(data);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  const recommended = results?.routes?.find(
    (route) => route.name === results.recommended_route,
  );

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top">
          <span className="brand-icon">WR</span>
          <span>
            Route<span className="brand-accent">Cast</span>
          </span>
        </a>
        <span className="topbar-label">WEATHER-AWARE LOGISTICS</span>
      </header>

      <div className="dashboard" id="top">
        <section className="hero">
          <div className="eyebrow">ROUTE INTELLIGENCE / LIVE ASSESSMENT</div>
          <h1>
            Plan the route.
            <br />
            <span>Anticipate the weather.</span>
          </h1>
          <p>
            Compare driving alternatives against forecast conditions, cargo
            weight and estimated travel time before choosing a route.
          </p>
        </section>

        <section className="panel form-panel">
          <div className="section-heading">
            <div>
              <div className="eyebrow">01 / TRIP CONFIGURATION</div>
              <h2>Journey details</h2>
            </div>
            <span className="step-badge">INPUT</span>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <label className="field">
                <span>Origin coordinates</span>
                <input
                  value={start}
                  onChange={(event) => setStart(event.target.value)}
                  placeholder="Longitude, latitude"
                  required
                />
                <small>Longitude, latitude</small>
              </label>

              <label className="field">
                <span>Destination coordinates</span>
                <input
                  value={end}
                  onChange={(event) => setEnd(event.target.value)}
                  placeholder="Longitude, latitude"
                  required
                />
                <small>Longitude, latitude</small>
              </label>

              <label className="field">
                <span>Departure time</span>
                <input
                  type="datetime-local"
                  value={startTime}
                  onChange={(event) => setStartTime(event.target.value)}
                  required
                />
                <small>Local time at the departure location</small>
              </label>

              <label className="field">
                <span>Cargo weight (lb)</span>
                <input
                  type="number"
                  min="0.01"
                  step="any"
                  value={cargoWeight}
                  onChange={(event) => setCargoWeight(event.target.value)}
                  required
                />
                <small>Used to assess wind-related risk</small>
              </label>

              <label className="field field-wide">
                <span>Checkpoint frequency</span>
                <select
                  value={interval}
                  onChange={(event) => setInterval(event.target.value)}
                >
                  <option value="10">
                    Every 10 miles — detailed monitoring
                  </option>
                  <option value="25">
                    Every 25 miles — balanced monitoring
                  </option>
                  <option value="50">Every 50 miles — wider intervals</option>
                </select>
              </label>
            </div>

            <button className="primary-button" type="submit" disabled={loading}>
              {loading ? "Assessing routes…" : "Assess available routes"}
              {!loading && <span aria-hidden="true"> →</span>}
            </button>
          </form>

          {loading && (
            <div className="loading-note" role="status">
              Requesting route alternatives and assessing checkpoint weather.
              This can take a little while.
            </div>
          )}

          {error && (
            <div className="error-note" role="alert">
              {error}
            </div>
          )}
        </section>

        {results && (
          <>
            <section className="results-heading">
              <div>
                <div className="eyebrow">02 / ROUTE ANALYSIS</div>
                <h2>Assessment overview</h2>
                <p>Compare risk exposure across the available alternatives.</p>
              </div>
              <span className="result-count">
                {results.routes.length} ROUTE OPTIONS
              </span>
            </section>

            {recommended ? (
              <section className="recommendation-banner">
                <div className="recommendation-icon">
                  {recommended.no_travel_miles > 0 ? "!" : "✓"}
                </div>
                <div>
                  <div className="eyebrow">
                    {recommended.no_travel_miles > 0
                      ? "SAFETY WARNING — NO-TRAVEL CONDITIONS"
                      : "RECOMMENDED BY RISK PRIORITY"}
                  </div>
                  <h3>{recommended.name}</h3>
                  <p>
                    {recommended.distance_miles} miles ·{" "}
                    {recommended.travel_minutes} minutes ·{" "}
                    {recommended.unknown_miles} unknown-weather miles
                  </p>

                  {recommended.no_travel_miles > 0 && (
                    <p role="alert">
                      Warning: {recommended.no_travel_miles} miles have No
                      Travel conditions. Do not treat this route as safe to
                      drive. Review the alternatives and current safety
                      guidance.
                    </p>
                  )}
                </div>
              </section>
            ) : (
              <div className="error-note">
                No route has enough complete weather data for a recommendation.
                Review the unknown-weather miles before choosing a route.
              </div>
            )}

            <section className="metric-grid">
              <Metric
                label="Route distance"
                value={recommended ? `${recommended.distance_miles} mi` : "—"}
              />
              <Metric
                label="Estimated duration"
                value={recommended ? `${recommended.travel_minutes} min` : "—"}
              />
              <Metric
                label="Severe-risk miles"
                value={recommended ? `${recommended.severe_miles} mi` : "—"}
              />
              <Metric
                label="Average risk score"
                value={
                  recommended
                    ? (recommended.average_risk ?? "Unavailable")
                    : "—"
                }
              />
            </section>

            <section className="panel map-panel">
              <div className="section-heading">
                <div>
                  <div className="eyebrow">03 / SPATIAL VIEW</div>
                  <h2>Route & checkpoint map</h2>
                </div>
                <span className="map-live-label">
                  <span className="status-dot" /> {results.routes.length} ROUTES
                </span>
              </div>

              <RouteMap
                routes={results.routes}
                recommendedRoute={results.recommended_route}
                selectedTime={selectedTime}
              />

              <div className="map-legend">
                <Legend color="#16a34a" label="Low" />
                <Legend color="#eab308" label="Moderate" />
                <Legend color="#ea580c" label="High" />
                <Legend color="#dc2626" label="Severe" />
                <Legend color="#7f1d1d" label="No travel" />
                <Legend color="#64748b" label="Unavailable" />
              </div>

              <p className="map-help">
                Route segments and checkpoint markers show the forecast risk at
                the selected timeline hour. Select a checkpoint to inspect its
                estimated arrival time and the forecast used for its risk
                assessment. Segment colours are approximations based on the
                nearest checkpoint, not measurements for every point along the
                road.
              </p>
            </section>

            <section className="panel timeline-panel">
              <div className="section-heading">
                <div>
                  <div className="eyebrow">04 / FORECAST EXPLORER</div>
                  <h2>Weather timeline</h2>
                </div>
                <span className="time-chip">+{forecastHour} HOURS</span>
              </div>
              <p className="timeline-date">
                {Number.isNaN(selectedTime.getTime())
                  ? "Choose a valid departure time"
                  : selectedTime.toLocaleString()}
              </p>
              <input
                className="forecast-slider"
                type="range"
                min="0"
                max="48"
                step="1"
                value={forecastHour}
                onChange={(event) =>
                  setForecastHour(Number(event.target.value))
                }
                aria-label="Forecast hours from departure"
              />
              <div className="slider-labels">
                <span>Departure · 0h</span>
                <span>24h</span>
                <span>48h</span>
              </div>
              <p className="map-help">
                Checkpoint colours update when hourly forecast data is available
                near the selected time. Grey indicates unavailable forecast
                data.
              </p>
            </section>

            <section className="results-heading">
              <div>
                <div className="eyebrow">05 / ALTERNATIVE COMPARISON</div>
                <h2>Route breakdown</h2>
              </div>
            </section>

            <section className="route-card-grid">
              {results.routes.map((route, index) => {
                const isRecommended = route.name === results.recommended_route;
                return (
                  <article
                    className={`route-card ${isRecommended ? "route-card-recommended" : ""}`}
                    key={route.name}
                  >
                    <div className="route-card-top">
                      <span className="route-number">0{index + 1}</span>
                      {isRecommended && (
                        <span className="recommended-tag">RECOMMENDED</span>
                      )}
                    </div>
                    <h3>{route.name}</h3>
                    <p className="route-distance">
                      {route.distance_miles} <span>miles</span>
                    </p>
                    <div className="route-detail">
                      <span>Travel time</span>
                      <strong>{route.travel_minutes} min</strong>
                    </div>
                    <div className="route-detail">
                      <span>Severe-risk miles</span>
                      <strong>{route.severe_miles}</strong>
                    </div>
                    <div className="route-detail">
                      <span>No Travel miles</span>
                      <strong>{route.no_travel_miles ?? 0}</strong>
                    </div>
                    <div className="route-detail">
                      <span>High-risk miles</span>
                      <strong>{route.high_miles}</strong>
                    </div>
                    <div className="route-detail">
                      <span>Average risk</span>
                      <strong>{route.average_risk ?? "Unavailable"}</strong>
                    </div>
                    <div className="route-detail">
                      <span>Unknown-weather miles</span>
                      <strong>{route.unknown_miles}</strong>
                    </div>
                    <div className="route-detail">
                      <span>Checkpoints</span>
                      <strong>{route.checkpoints.length}</strong>
                    </div>
                  </article>
                );
              })}
            </section>
          </>
        )}

        <footer className="footer">
          <span>RouteCast · Weather-aware truck routing</span>
          <span>
            Route decisions should be verified against current road and safety
            guidance.
          </span>
        </footer>
      </div>
    </main>
  );
}

function Metric({ label, value }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function Legend({ color, label }) {
  return (
    <span className="legend-item">
      <span className="legend-dot" style={{ backgroundColor: color }} />
      {label}
    </span>
  );
}

export default App;
