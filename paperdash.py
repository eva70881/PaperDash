# paperdash.py

import sys
import time
from datetime import datetime
from typing import Dict, Optional

from PIL import Image, ImageDraw, ImageFont

sys.path.append('./epd')
from epd7in5_V2 import EPD

from modules.config import load_config
from modules.network import get_ip_address
from modules.weather import get_weather_summary

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
    weather_text = "Weather: --"

    try:
        logo = Image.open(logo_path)
        if logo.mode != '1':
            logo = logo.convert('1')
        logo_w, logo_h = logo.size
    except Exception as e:
        print("[WARN] Failed to load logo:", e)
        logo = None
        logo_w, logo_h = 0, 0

    try:
        while True:
            now_full = datetime.now()
            now_str = now_full.strftime('%Y/%m/%d %H:%M')
            current_minute = now_full.strftime('%Y%m%d%H%M')

            if int(now_full.minute) % weather_interval == 0 and current_minute != last_weather_update:
                weather_text = get_weather_summary()
                last_weather_update = current_minute

            if current_minute != last_minute:
                draw.rectangle(PARTIAL_REGION, fill=255)

                ip = get_ip_address()
                ip_label = f"Paper Dash - IP Address: {ip}"

                ip_label_w, _ = draw.textsize(ip_label, font=font_small)
                time_w, _     = draw.textsize(now_str, font=font_large)
                weather_w, _  = draw.textsize(weather_text, font=font_medium)

                # Top content
                draw.text(((width - ip_label_w) // 2, 20), ip_label, font=font_small, fill=0)
                draw.text(((width - time_w) // 2, 60), now_str, font=font_large, fill=0)
                draw.text(((width - weather_w) // 2, 120), weather_text, font=font_medium, fill=0)

                # Logo
                if logo:
                    image.paste(logo, (10, height - logo_h - 10))

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

