#!/usr/bin/env python3
"""Fetch a day-planning weather summary from Open-Meteo (free, no API key).

Read-only against the network; writes only data/weather.json.
Usage: python3 scripts/fetch_weather.py [--lat 41.7943] [--lon -87.5907] [--days 3]
Default location: Hyde Park, Chicago.
"""
import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "weather.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, default=41.7943)
    ap.add_argument("--lon", type=float, default=-87.5907)
    ap.add_argument("--days", type=int, default=3)
    a = ap.parse_args()

    params = {
        "latitude": a.lat,
        "longitude": a.lon,
        "timezone": "America/Chicago",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "forecast_days": a.days,
        "current": "temperature_2m,apparent_temperature,precipitation,wind_speed_10m,weather_code",
        "hourly": "temperature_2m,apparent_temperature,precipitation_probability,precipitation,wind_speed_10m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,"
                 "precipitation_probability_max,precipitation_sum,snowfall_sum,wind_speed_10m_max,sunrise,sunset,weather_code",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as r:
        data = json.load(r)

    data["_meta"] = {
        "source": "open-meteo.com",
        "location": "Hyde Park, Chicago",
        "units": "F, mph, inches",
        "note": "hourly arrays are indexed by hourly.time; use for a morning/afternoon/evening split",
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
