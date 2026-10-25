from datetime import datetime

import logging
import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .routing_service import get_routes
from .weather_aware_service import assess_routes

logger = logging.getLogger(__name__)

@api_view(["GET"])
def health_check(request):
    return Response({
        "status":"ok",
        "service": "weather-truck-routing-api",
    })

@api_view(["POST"])
def routes_view(request):
    start = request.data.get("start")
    end = request.data.get("end")

    start_time_value = request.data.get("start_time")
    cargo_weight_value = request.data.get("cargo_weight_lb")
    interval_value = request.data.get("interval_miles")


    if not isinstance(start_time_value, str) or not start_time_value.strip():
        return Response(
            {"error": "Start time must be a valid date-time string."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        start_time = datetime.fromisoformat(start_time_value)
    except ValueError:
        return Response(
            {"error": "Start time must use ISO format, e.g. 2026-10-22T14:00:00."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if start_time.tzinfo is not None:
        return Response(
            {"error": "Start time must use Nairobi local time without a timezone offset."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        cargo_weight_lb = float(cargo_weight_value)
        if cargo_weight_lb <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return Response(
            {"error": "Cargo weight must be a positive number in pounds."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        interval_miles = int(interval_value)
        if interval_miles not in (10, 25, 50):
            raise ValueError
        if isinstance(interval_value, bool) or str(interval_value).strip() not in ("10", "25", "50"):
            raise ValueError
    except (TypeError, ValueError):
        return Response(
            {"error": "Checkpoint interval must be 10, 25, or 50 miles."},
            status=status.HTTP_400_BAD_REQUEST,
        )



    if not isinstance(start, list) or not isinstance(end,list):
        return Response(
            {"error":"Start and end must be coordinate arrays."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(start) != 2 or len(end) != 2:
        return Response(
            {"error":"Each coordinate array must contain longitude and latitude."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    try:
        start = [float(value) for value in start]
        end = [float(value) for value in end]
    except (TypeError, ValueError):
        return Response(
            {"error": "Coordinates must be numbers."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        routes = get_routes(start, end)
    except requests.RequestException:
        return Response(
            {"error":"The routing provider could not be reached."},
            status= status.HTTP_502_BAD_GATEWAY,
        )
    except (KeyError,ValueError):
        return Response(
            {"error":"The routing provider returned an invalid response."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except RuntimeError:
        return Response(
            {"error": "The routing service is not configured."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    
    try:
        result = assess_routes(
            routes=routes,
            interval_miles=interval_miles,
            start_time=start_time,
            cargo_weight_lb=cargo_weight_lb,
        )
    except requests.RequestException:
        logger.exception("Provider request failed during route assessment")
        return Response(
            {"error": "A weather or routing provider could not be reached."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except (KeyError, ValueError):
        return Response(
            {"error": "The route or weather provider returned invalid data."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except RuntimeError:
        return Response(
            {"error": "A required service is not configured."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response(result)


