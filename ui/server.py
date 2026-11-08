#!/usr/bin/env python3
"""Local server for the day page. Read-only: serves ui/ and plan/today.json. No deploy needed.

Usage: python3 ui/server.py [port]      then open http://127.0.0.1:8000
Add ?sample to the page URL to preview with ui/sample-plan.json (made-up data).
"""
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

UI = Path(__file__).resolve().parent
PLAN = UI.parent / "plan" / "today.json"
SAMPLE = UI / "sample-plan.json"
WEATHER = UI.parent / "data" / "weather.json"
TZ = ZoneInfo("America/Chicago")
LABELS = {0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Fog",
          51: "Drizzle", 53: "Drizzle", 55: "Drizzle", 56: "Freezing drizzle", 57: "Freezing drizzle",
          61: "Light rain", 63: "Rain", 65: "Heavy rain", 66: "Freezing rain", 67: "Freezing rain",
          71: "Light snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains", 80: "Showers", 81: "Showers",
          82: "Heavy showers", 85: "Snow showers", 86: "Snow showers", 95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm"}


def weather_payload(sample=False):
    """Current conditions and the next few hours, from data/weather.json. None if missing or stale."""
    if sample:
        hrs = [("14:00", 56, 52, 0, 6), ("15:00", 58, 54, 0, 7), ("16:00", 57, 52, 10, 9), ("17:00", 52, 47, 30, 11)]
        return {"label": "Mostly clear", "hi": 60, "lo": 40, "sunset": "16:37",
                "hours": [{"time": t, "temp": a, "feels": b, "rain": c, "wind": d} for t, a, b, c, d in hrs]}
    if not WEATHER.exists():
        return None
    w = json.loads(WEATHER.read_text())
    d, h = w["daily"], w["hourly"]
    now = datetime.now(TZ)
    if now.strftime("%Y-%m-%d") not in d["time"]:
        return None
    key = now.strftime("%Y-%m-%dT%H:00")
    if key not in h["time"]:
        return None
    i, n = d["time"].index(now.strftime("%Y-%m-%d")), h["time"].index(key)
    hours = [{"time": h["time"][j][11:16], "temp": round(h["temperature_2m"][j]), "feels": round(h["apparent_temperature"][j]),
              "rain": h["precipitation_probability"][j], "wind": round(h["wind_speed_10m"][j])}
             for j in range(n, min(n + 4, len(h["time"])))]
    return {"label": LABELS.get(h["weather_code"][n], ""), "hi": round(d["temperature_2m_max"][i]), "lo": round(d["temperature_2m_min"][i]),
            "sunset": d["sunset"][i][11:], "hours": hours}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI), **kwargs)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/plan":
            src = SAMPLE if "sample" in parse_qs(url.query, keep_blank_values=True) else PLAN
            if not src.exists():
                return self.send_json(404, {"error": "no plan saved yet"})
            try:
                json.loads(src.read_text())
            except json.JSONDecodeError:
                return self.send_json(503, {"error": "plan is mid-write, retry"})
            return self.send_bytes(200, src.read_bytes())
        if url.path == "/api/weather":
            try:
                payload = weather_payload("sample" in parse_qs(url.query, keep_blank_values=True))
            except (OSError, ValueError, KeyError, json.JSONDecodeError):
                payload = None
            if payload is None:
                return self.send_json(404, {"error": "no current weather"})
            return self.send_json(200, payload)
        if url.path in ("/", ""):
            self.path = "/index.html"
        elif url.path not in ("/index.html",):
            return self.send_json(404, {"error": "not found"})
        return super().do_GET()

    def send_json(self, code, obj):
        self.send_bytes(code, json.dumps(obj).encode())

    def send_bytes(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Day page: http://127.0.0.1:{port}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
