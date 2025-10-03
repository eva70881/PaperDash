"""Utilities for retrieving weather information and categorising icons."""

import requests

LAT = 25.0585178
LON = 121.6532539

FALLBACK_SUMMARY = "--°C | RH --%"

WEATHER_TEXT_MAP = {
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

WEATHER_CATEGORY_MAP = {
    0: "clear",
    1: "mostly_clear",
    2: "partly_cloudy",
    3: "cloudy",
    45: "fog",
    48: "rime_fog",
    51: "drizzle",
    53: "drizzle",
    61: "light_rain",
    63: "rain",
    65: "heavy_rain",
    71: "snow",
    80: "rain_showers",
}


def get_weather_summary():
    """Return a tuple with display text and icon category for the current weather."""

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
            return FALLBACK_SUMMARY, "unknown"

        summary = f"{temp:.1f}°C | RH {rh}%"
        category = weather_code_to_category(code)
        return summary, category

    except Exception:
        return FALLBACK_SUMMARY, "unknown"


def weather_code_to_text(code):
    return WEATHER_TEXT_MAP.get(code, "Unknown")


def weather_code_to_category(code):
    return WEATHER_CATEGORY_MAP.get(code, "unknown")

