# paperdash.py

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from PIL import Image, ImageDraw, ImageFont

sys.path.append('./epd')
from epd7in5_V2 import EPD

from modules.config import load_config
from modules.network import get_ip_address
from modules.weather import get_weather_summary
from modules.system_stats import get_system_usage

# Fixed pickup schedule for Monday through Friday with icon descriptors
SCHEDULE = [
    ("Monday", "17:00", "rollerblade"),
    ("Tuesday", "17:00", "magic"),
    ("Wednesday", "16:30", "gymnastics"),
    ("Thursday", "17:30", "blocks"),
    ("Friday", "15:30", "pilates"),
]

ICON_FILES = {
    "rollerblade": "assets/pickup_icons/rollerblade.bmp",
    "magic": "assets/pickup_icons/magic.bmp",
    "gymnastics": "assets/pickup_icons/gymnastics.bmp",
    "blocks": "assets/pickup_icons/blocks.bmp",
    "pilates": "assets/pickup_icons/pilates.bmp",
}

ICON_SIZE = (64, 64)  # width, height in pixels for the schedule bitmaps
ROW_HEIGHT = 72
SCHEDULE_RIGHT_MARGIN = 6
SCHEDULE_BOTTOM_MARGIN = 10
ICON_TEXT_GAP = 4  # tightened spacing between the time text and icon


_ICON_CACHE: Dict[str, Optional[Image.Image]] = {}

WEATHER_ICON_FILES = {
    "clear": "assets/weather_icons/clear.bmp",
    "mostly_clear": "assets/weather_icons/mostly_clear.bmp",
    "partly_cloudy": "assets/weather_icons/partly_cloudy.bmp",
    "cloudy": "assets/weather_icons/cloudy.bmp",
    "fog": "assets/weather_icons/fog.bmp",
    "rime_fog": "assets/weather_icons/rime_fog.bmp",
    "drizzle": "assets/weather_icons/drizzle.bmp",
    "light_rain": "assets/weather_icons/light_rain.bmp",
    "rain": "assets/weather_icons/rain.bmp",
    "heavy_rain": "assets/weather_icons/heavy_rain.bmp",
    "snow": "assets/weather_icons/snow.bmp",
    "rain_showers": "assets/weather_icons/rain_showers.bmp",
}

_WEATHER_ICON_CACHE: Dict[str, Optional[Image.Image]] = {}


def load_icon(name: str) -> Optional[Image.Image]:
    path = ICON_FILES.get(name)
    if not path:
        return None

    if path not in _ICON_CACHE:
        try:
            icon = Image.open(path)
            if icon.size != ICON_SIZE:
                icon = icon.resize(ICON_SIZE, Image.NEAREST)
            if icon.mode != '1':
                icon = icon.convert('1')
            _ICON_CACHE[path] = icon
        except Exception as exc:
            print(f"[WARN] Failed to load icon '{name}' from '{path}': {exc}")
            _ICON_CACHE[path] = None

    return _ICON_CACHE[path]


def load_weather_icon(category: str) -> Optional[Image.Image]:
    path = WEATHER_ICON_FILES.get(category)
    if not path:
        return None

    if path not in _WEATHER_ICON_CACHE:
        icon_path = Path(path)
        if not icon_path.exists():
            print(f"[INFO] Weather icon '{category}' not found at '{path}'. Using logo fallback.")
            _WEATHER_ICON_CACHE[path] = None
        else:
            try:
                icon = Image.open(path)
                if icon.mode != '1':
                    icon = icon.convert('1')
                _WEATHER_ICON_CACHE[path] = icon
            except Exception as exc:
                print(f"[WARN] Failed to load weather icon '{category}' from '{path}': {exc}")
                _WEATHER_ICON_CACHE[path] = None

    return _WEATHER_ICON_CACHE[path]

def main():
    config = load_config()
    weather_interval = config["weather_update_interval"]
    logo_path = config["logo_path"]

    epd = EPD()
    epd.init()
    epd.Clear()
    time.sleep(2)
    epd.init_part()

    width, height = epd.width, epd.height
    PARTIAL_REGION = (0, 0, width, height)

    image = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(image)

    font_small  = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 18)
    font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 32)
    font_large  = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 40)

    last_minute = ""
    last_weather_update = ""
    last_system_update = ""
    weather_text = "--°C | RH --%"
    system_usage_text = "CPU --% - MEM --% - DRIVE --%"

    try:
        logo = Image.open(logo_path)
        if logo.mode != '1':
            logo = logo.convert('1')
    except Exception as e:
        print("[WARN] Failed to load logo:", e)
        logo = None

    weather_image: Optional[Image.Image] = logo

    try:
        while True:
            now_full = datetime.now()
            now_str = now_full.strftime('%Y/%m/%d %H:%M')
            current_minute = now_full.strftime('%Y%m%d%H%M')

            if int(now_full.minute) % weather_interval == 0 and current_minute != last_weather_update:
                weather_text, weather_category = get_weather_summary()
                weather_candidate = load_weather_icon(weather_category)
                weather_image = weather_candidate if weather_candidate else logo
                last_weather_update = current_minute

            if int(now_full.minute) % weather_interval == 0 and current_minute != last_system_update:
                cpu_percent, memory_percent, drive_percent = get_system_usage()
                system_usage_text = (
                    f"CPU {cpu_percent:.0f}% - MEM {memory_percent:.0f}% - DRIVE {drive_percent:.0f}%"
                )
                last_system_update = current_minute

            if current_minute != last_minute:
                draw.rectangle(PARTIAL_REGION, fill=255)

                ip = get_ip_address()
                top_label = f"Paper Dash - {ip} - {system_usage_text}"

                top_label_w, _ = draw.textsize(top_label, font=font_small)
                time_w, time_h = draw.textsize(now_str, font=font_large)
                weather_w, _  = draw.textsize(weather_text, font=font_medium)

                # Top content
                draw.text(((width - top_label_w) // 2, 20), top_label, font=font_small, fill=0)
                time_x = (width - time_w) // 2
                time_y = 60
                draw.text((time_x, time_y), now_str, font=font_large, fill=0)
                left_region_width = width // 2
                weather_x = max(0, (left_region_width - weather_w) // 2)
                draw.text((weather_x, 120), weather_text, font=font_medium, fill=0)

                # Logo
                if weather_image:
                    weather_wi, weather_hi = weather_image.size
                    left_region_width = width // 2
                    weather_icon_x = max(0, (left_region_width - weather_wi) // 2)
                    image.paste(weather_image, (weather_icon_x, height - weather_hi - 10))

                # Schedule section
                schedule_height = ROW_HEIGHT * len(SCHEDULE)
                y_pos = height - schedule_height - SCHEDULE_BOTTOM_MARGIN
                icon_x = width - ICON_SIZE[0] - SCHEDULE_RIGHT_MARGIN

                for day, pickup_time, icon_name in SCHEDULE:
                    text = f"{day}  {pickup_time}"
                    text_w, text_h = draw.textsize(text, font=font_medium)
                    text_x = max(10, icon_x - ICON_TEXT_GAP - text_w)
                    text_y = y_pos + (ROW_HEIGHT - text_h) // 2
                    icon_y = y_pos + (ROW_HEIGHT - ICON_SIZE[1]) // 2

                    draw.text((text_x, text_y), text, font=font_medium, fill=0)

                    icon_image = load_icon(icon_name)
                    if icon_image:
                        image.paste(icon_image, (icon_x, icon_y))
                    else:
                        draw.rectangle(
                            (
                                icon_x,
                                icon_y,
                                icon_x + ICON_SIZE[0],
                                icon_y + ICON_SIZE[1],
                            ),
                            outline=0,
                            fill=255,
                        )

                    y_pos += ROW_HEIGHT

                epd.display_Partial(epd.getbuffer(image), *PARTIAL_REGION)
                last_minute = current_minute

            time.sleep(10)

    except KeyboardInterrupt:
        print("\n[INFO] Ctrl+C detected, exiting gracefully.")

    finally:
        print("[INFO] Shutting down e-Paper...")
        epd.sleep()

if __name__ == "__main__":
    main()

