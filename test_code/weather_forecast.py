import time
import signal
import requests
from datetime import datetime
from threading import Event

# Weather code mapping with icons
WEATHER_MAPPING = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Drizzle: Light", "🌦️"),
    53: ("Drizzle: Moderate", "🌦️"),
    55: ("Drizzle: Dense", "🌧️"),
    56: ("Freezing Drizzle: Light", "🌧️"),
    57: ("Freezing Drizzle: Dense", "🌧️"),
    61: ("Rain: Slight", "🌧️"),
    63: ("Rain: Moderate", "🌧️"),
    65: ("Rain: Heavy", "🌧️"),
    66: ("Freezing Rain: Light", "🌧️"),
    67: ("Freezing Rain: Heavy", "🌧️"),
    71: ("Snowfall: Slight", "❄️"),
    73: ("Snowfall: Moderate", "❄️"),
    75: ("Snowfall: Heavy", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Rain showers: Slight", "🌦️"),
    81: ("Rain showers: Moderate", "🌧️"),
    82: ("Rain showers: Violent", "🌧️"),
    85: ("Snow showers: Slight", "❄️"),
    86: ("Snow showers: Heavy", "❄️"),
    95: ("Thunderstorm: Slight", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️")
}

def get_weather():
    LAT = 25.0585178  # Latitude from Google Maps
    LON = 121.6532539  # Longitude from Google Maps
    URL = (f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}" 
           f"&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,weathercode"
           f"&timezone=Asia/Taipei")
    
    try:
        response = requests.get(URL)
        data = response.json()
        
        if "hourly" not in data:
            print("[ERROR] Unable to fetch weather data:", data)
            return None, None
        
        now = datetime.now().strftime("%Y-%m-%dT%H:00")
        if now in data["hourly"]["time"]:
            start_index = data["hourly"]["time"].index(now)
        else:
            print("[WARNING] Current time not found in weather data, using first available hour.")
            start_index = 0
        
        current_weather = {
            "temperature": data["hourly"]["temperature_2m"][start_index],
            "humidity": data["hourly"]["relative_humidity_2m"][start_index],
            "precipitation": data["hourly"]["precipitation_probability"][start_index],
            "weather_code": data["hourly"]["weathercode"][start_index],
            "time": data["hourly"]["time"][start_index]
        }
        
        forecast = []
        for i in range(start_index, start_index + 12):
            if i < len(data["hourly"]["time"]):
                forecast.append({
                    "time": data["hourly"]["time"][i],
                    "temperature": data["hourly"]["temperature_2m"][i],
                    "humidity": data["hourly"]["relative_humidity_2m"][i],
                    "precipitation": data["hourly"]["precipitation_probability"][i],
                    "weather_code": data["hourly"]["weathercode"][i]
                })
        
        return current_weather, forecast
    except Exception as e:
        print(f"[ERROR] Failed to retrieve weather data: {e}")
        return None, None

def signal_handler(signum, frame):
    print("\n[INFO] Received termination signal, exiting...")
    exit_event.set()

exit_event = Event()
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

current_weather, forecast = get_weather()
next_weather_update = time.time() - 1

while not exit_event.is_set():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\r[Current Time] {now}", end="", flush=True)
    
    if time.time() >= next_weather_update:
        print("\n[INFO] Updating weather data...")
        current_weather, forecast = get_weather()
        next_weather_update = time.time() + 3600
        
        if current_weather:
            description, icon = WEATHER_MAPPING.get(current_weather['weather_code'], ("Unknown", "❓"))
            print(f"[Current Weather] {current_weather['time']}, {current_weather['temperature']}°C, "
                  f"Humidity: {current_weather['humidity']}%, Precipitation: {current_weather['precipitation']}%, "
                  f"Weather: {description} {icon}")
        if forecast:
            print("[Next 12 Hours Forecast]:")
            for entry in forecast:
                description, icon = WEATHER_MAPPING.get(entry['weather_code'], ("Unknown", "❓"))
                print(f"  {entry['time']}: {entry['temperature']}°C, Humidity: {entry['humidity']}%, "
                      f"Precipitation: {entry['precipitation']}%, Weather: {description} {icon}")
    
    time.sleep(1)

