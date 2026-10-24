import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  Circle,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";

const RISK_COLORS = {
  LOW: "#16a34a",
  MODERATE: "#eab308",
  HIGH: "#ea580c",
  SEVERE: "#dc2626",
  NO_TRAVEL: "#7f1d1d",
  UNAVAILABLE: "#64748b",
};

function getRiskAtTime(checkpoint, selectedTime) {
  const forecasts = checkpoint.forecasts;

  if (!forecasts?.length || !selectedTime) {
    return {
      risk: checkpoint.risk || "UNAVAILABLE",
      forecastTime: "No hourly forecast attached",
    };
  }

  const selectedMs = selectedTime.getTime();
  let nearest = null;
  let smallestDifference = Infinity;

  for (const forecast of forecasts) {
    const forecastMs = new Date(forecast.time).getTime();
    const difference = Math.abs(forecastMs - selectedMs);

    if (difference < smallestDifference) {
      smallestDifference = difference;
      nearest = forecast;
    }
  }

  if (!nearest || smallestDifference > 30 * 60 * 1000) {
    return {
      risk: "UNAVAILABLE",
      forecastTime: "No forecast within 30 minutes",
    };
  }

  return {
    risk: nearest.risk || "UNAVAILABLE",
    forecastTime: nearest.time,
  };
}

function getNearestGeometryIndex(coordinates, checkpointCoordinates) {
  let nearestIndex = 0;
  let smallestDistance = Infinity;

  coordinates.forEach(([longitude, latitude], index) => {
    const deltaLongitude = longitude - checkpointCoordinates[0];
    const deltaLatitude = latitude - checkpointCoordinates[1];
    const distance =
      deltaLongitude * deltaLongitude + deltaLatitude * deltaLatitude;

    if (distance < smallestDistance) {
      smallestDistance = distance;
      nearestIndex = index;
    }
  });

  return nearestIndex;
}

function buildRiskSegments(route, selectedTime) {
  const coordinates = route.geometry?.coordinates || [];
  const checkpoints = route.checkpoints || [];

  if (coordinates.length < 2 || checkpoints.length === 0) {
    return [];
  }

  const markers = checkpoints
    .map((checkpoint) => ({
      index: getNearestGeometryIndex(coordinates, checkpoint.coordinates),
      checkpoint,
    }))
    .sort((a, b) => a.index - b.index);

  const segments = [];
  let startIndex = 0;

  for (const marker of markers) {
    const endIndex = marker.index;

    if (endIndex <= startIndex) {
      continue;
    }

    const segmentCoordinates = coordinates
      .slice(startIndex, endIndex + 1)
      .map(([longitude, latitude]) => [latitude, longitude]);

    const risk = getRiskAtTime(marker.checkpoint, selectedTime).risk;

    segments.push({
      positions: segmentCoordinates,
      risk,
      distanceMiles: marker.checkpoint.distance_miles,
    });

    startIndex = endIndex;
  }

  if (startIndex < coordinates.length - 1) {
    segments.push({
      positions: coordinates
        .slice(startIndex)
        .map(([longitude, latitude]) => [latitude, longitude]),
      risk: "UNAVAILABLE",
      distanceMiles: null,
    });
  }

  return segments;
}

function FitRoutes({ routes }) {
  const map = useMap();

  useEffect(() => {
    const points = routes.flatMap((route) =>
      (route.geometry?.coordinates || []).map(([longitude, latitude]) => [
        latitude,
        longitude,
      ]),
    );

    if (points.length) {
      map.fitBounds(points, { padding: [35, 35] });
    }
  }, [map, routes]);

  return null;
}

function RouteMap({ routes, recommendedRoute, selectedTime }) {
  if (!routes?.length) {
    return <p>No routes to display yet.</p>;
  }

  return (
    <div className="map-frame">
      <MapContainer
        center={[-1.2921, 36.8219]}
        zoom={10}
        style={{ height: "520px", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <FitRoutes routes={routes} />

        {/* Approximate risk areas around sampled checkpoints */}
        {routes.flatMap((route) =>
          (route.checkpoints || []).map((checkpoint, index) => {
            const [longitude, latitude] = checkpoint.coordinates;
            const { risk } = getRiskAtTime(checkpoint, selectedTime);
            const color = RISK_COLORS[risk] || RISK_COLORS.UNAVAILABLE;

            return (
              <Circle
                key={`risk-area-${route.name}-${index}`}
                center={[latitude, longitude]}
                radius={4000}
                interactive={false}
                pathOptions={{
                  color,
                  opacity: 0.3,
                  weight: 1,
                  fillColor: color,
                  fillOpacity: 0.14,
                }}
              />
            );
          }),
        )}

        {routes.map((route) => {
          const isRecommended = route.name === recommendedRoute;

          const segments = buildRiskSegments(route, selectedTime);

          return (
            <>
              {segments.map((segment, segmentIndex) => (
                <Polyline
                  key={`${route.name}-segment-${segmentIndex}`}
                  positions={segment.positions}
                  pathOptions={{
                    color: RISK_COLORS[segment.risk] || RISK_COLORS.UNAVAILABLE,
                    weight: isRecommended ? 7 : 4,
                    opacity: isRecommended ? 1 : 0.65,
                  }}
                >
                  <Popup>
                    <strong>{route.name}</strong>
                    {isRecommended && <p>Recommended route</p>}
                    <p>Risk: {segment.risk.replace("_", " ")}</p>
                    {segment.distanceMiles !== null && (
                      <p>Checkpoint: {segment.distanceMiles} miles</p>
                    )}
                    <p>Distance: {route.distance_miles} miles total</p>
                    <p>Travel time: {route.travel_minutes} minutes total</p>
                  </Popup>
                </Polyline>
              ))}
            </>
          );
        })}

        {routes.flatMap((route) =>
          (route.checkpoints || []).map((checkpoint, index) => {
            const [longitude, latitude] = checkpoint.coordinates;
            const forecastResult = getRiskAtTime(checkpoint, selectedTime);
            const risk = forecastResult.risk;
            const isRecommended = route.name === recommendedRoute;

            return (
              <CircleMarker
                key={`${route.name}-${checkpoint.distance_miles}-${index}`}
                center={[latitude, longitude]}
                radius={isRecommended ? 9 : 6}
                pathOptions={{
                  color: "#ffffff",
                  weight: 2,
                  fillColor: RISK_COLORS[risk] || RISK_COLORS.UNAVAILABLE,
                  fillOpacity: 1,
                }}
              >
                <Popup>
                  <strong>{route.name} checkpoint</strong>
                  <p>Distance: {checkpoint.distance_miles} miles</p>
                  <p>Risk at selected time: {risk.replace("_", " ")}</p>
                  <p>Matched forecast: {forecastResult.forecastTime}</p>

                  <p>Estimated arrival: {checkpoint.arrival_time}</p>
                  {isRecommended && <strong>Recommended route</strong>}
                </Popup>
              </CircleMarker>
            );
          }),
        )}
      </MapContainer>
    </div>
  );
}

export default RouteMap;
