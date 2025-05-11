# modules/weather.py

import requests
from datetime import datetime

LAT = 25.0585178
LON = 121.6532539

def get_weather_summary():
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={LAT}&longitude={LON}"
            f"&current=temperature_2m,relative_humidity_2m,weathercode"
            f"&timezone=Asia/Taipei"
        )
        response = requests.get(url, timeout=5)
        data = response.json()

        current = data.get("current", {})
        temp = current.get("temperature_2m")
        rh = current.get("relative_humidity_2m")
        code = current.get("weathercode")

        if temp is None or rh is None or code is None:
            return "Weather: --"

        summary = f"{temp:.1f}°C | RH {rh}% | {weather_code_to_text(code)}"
        return summary

    except Exception:
        return "Weather: --"

def weather_code_to_text(code):
    mapping = {
        0: "Clear",
        1: "Mostly clr",
        2: "Partly cldy",
        3: "Cloudy",
        45: "Fog",
        48: "Rime fog",
        51: "Drizzle",
        53: "Drizzle",
        61: "Light rain",
        63: "Rain",
        65: "Heavy rain",
        71: "Snow",
        80: "Rain showers",
    }
    return mapping.get(code, "Unknown")

