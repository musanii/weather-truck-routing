import os

import requests
from dotenv import load_dotenv

load_dotenv()

ORS_API_URL = (
    "https://api.heigit.org/openrouteservice/v2/"
    "directions/driving-car/geojson"
)

def get_routes(start_coordinates, end_coordinates):
    api_key = os.getenv("ORS_API_KEY")

    if not api_key:
        raise RuntimeError("ORS_API_KEY is not configured")

    payload = {
        "coordinates":[start_coordinates,end_coordinates],
        "instructions":True,
        "alternative_routes":{
            "target_count":3,
            "weight_factor":1.6,
            "share_factor":0.6,
        },
    }

    headers = {
        "Authorization": api_key,
        "Content-Type":"application/json",
    }

    response = requests.post(
        ORS_API_URL,
        json=payload,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    routes = []

    for index, feature in enumerate(data["features"], start=1):
        summary = feature["properties"]["summary"]
        segments = feature["properties"].get("segments",[])

        steps = [
            {
                "distance_m": step["distance"],
                "duration_seconds": step["duration"],
                "way_points": step["way_points"],
            }
            for segment in segments
            for step in segment.get("steps", [])
        ]

        routes.append({
            "name":f"Route {index}",
            "distance_km":round(summary["distance"] / 1000,2),
            "distance_miles": round(summary["distance"] / 1609.344, 2),
            "travel_minutes": round(summary["duration"] / 60, 1),
            "geometry": feature["geometry"],
            "steps":steps,
        })

    return routes
