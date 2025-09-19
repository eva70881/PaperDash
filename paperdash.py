# paperdash.py

import sys
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

sys.path.append('./epd')
from epd7in5_V2 import EPD

from modules.config import load_config
from modules.network import get_ip_address
from modules.weather import get_weather_summary

# Fixed pickup schedule for Monday through Friday
SCHEDULE = [
    ("Monday", "Pick up at 17:00"),
    ("Tuesday", "Pick up at 17:00"),
    ("Wednesday", "Pick up at 16:30"),
    ("Thursday", "Pick up at 17:30"),
    ("Friday", "Pick up at 15:30"),
]

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
                schedule_height = 30 * len(SCHEDULE)
                y_pos = height - schedule_height - 10
                for day, pickup in SCHEDULE:
                    text = f"{day}: {pickup}"
                    text_w, _ = draw.textsize(text, font=font_medium)
                    draw.text((width - text_w - 10, y_pos), text, font=font_medium, fill=0)
                    y_pos += 30

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

