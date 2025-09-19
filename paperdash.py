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

# Fixed pickup schedule for Monday through Friday with icon descriptors
SCHEDULE = [
    ("Monday", "17:00", "rollerblade"),
    ("Tuesday", "17:00", "magic"),
    ("Wednesday", "16:30", "gymnastics"),
    ("Thursday", "17:30", "blocks"),
    ("Friday", "15:30", "pilates"),
]

ICON_WIDTH = 80
ICON_HEIGHT = 40
ROW_HEIGHT = 70


def draw_rollerblade(draw: ImageDraw.Draw, x: int, y: int) -> None:
    boot_body = (x + 10, y + 8, x + 46, y + 28)
    boot_cuff = (x + 20, y + 2, x + 38, y + 12)
    draw.rectangle(boot_body, outline=0, fill=255)
    draw.rectangle(boot_cuff, outline=0, fill=255)
    draw.rectangle((x + 18, y + 14, x + 38, y + 18), fill=0)
    draw.ellipse((x + 12, y + 26, x + 24, y + 38), outline=0, fill=255)
    draw.ellipse((x + 32, y + 26, x + 44, y + 38), outline=0, fill=255)
    draw.ellipse((x + 48, y + 30, x + 58, y + 36), outline=0, fill=255)


def draw_magic(draw: ImageDraw.Draw, x: int, y: int) -> None:
    hat_top = (x + 20, y + 6, x + 60, y + 22)
    hat_brim = (x + 12, y + 22, x + 68, y + 28)
    wand = [(x + 60, y + 4), (x + 74, y + 28)]
    sparkles = [
        (x + 70, y + 6, x + 72, y + 8),
        (x + 72, y + 10, x + 74, y + 12),
        (x + 68, y + 12, x + 70, y + 14),
    ]
    draw.rectangle(hat_top, outline=0, fill=255)
    draw.rectangle(hat_brim, fill=0)
    draw.line(wand, fill=0, width=2)
    for sparkle in sparkles:
        draw.rectangle(sparkle, fill=0)


def draw_gymnastics(draw: ImageDraw.Draw, x: int, y: int) -> None:
    head = (x + 36, y + 4, x + 44, y + 12)
    torso = [(x + 40, y + 12), (x + 40, y + 28)]
    arms = [(x + 20, y + 20), (x + 60, y + 14)]
    leg_left = [(x + 40, y + 28), (x + 24, y + 38)]
    leg_right = [(x + 40, y + 28), (x + 56, y + 38)]
    draw.ellipse(head, outline=0, fill=255)
    draw.line(torso, fill=0, width=2)
    draw.line(arms, fill=0, width=2)
    draw.line(leg_left, fill=0, width=2)
    draw.line(leg_right, fill=0, width=2)


def draw_blocks(draw: ImageDraw.Draw, x: int, y: int) -> None:
    base_block = (x + 8, y + 24, x + 68, y + 36)
    mid_block = (x + 20, y + 16, x + 56, y + 28)
    top_block = (x + 32, y + 8, x + 44, y + 20)
    draw.rectangle(base_block, outline=0, fill=255)
    draw.rectangle(mid_block, outline=0, fill=255)
    draw.rectangle(top_block, outline=0, fill=255)
    draw.line((x + 8, y + 36, x + 68, y + 36), fill=0)


def draw_pilates(draw: ImageDraw.Draw, x: int, y: int) -> None:
    mat = (x + 6, y + 28, x + 74, y + 34)
    head = (x + 18, y + 16, x + 26, y + 24)
    torso = [(x + 26, y + 20), (x + 54, y + 24)]
    legs = [(x + 54, y + 24), (x + 68, y + 18)]
    draw.rectangle(mat, fill=0)
    draw.ellipse(head, outline=0, fill=255)
    draw.line(torso, fill=0, width=2)
    draw.line(legs, fill=0, width=2)


ICON_DRAWERS = {
    "rollerblade": draw_rollerblade,
    "magic": draw_magic,
    "gymnastics": draw_gymnastics,
    "blocks": draw_blocks,
    "pilates": draw_pilates,
}


def draw_icon(draw: ImageDraw.Draw, name: str, x: int, y: int) -> None:
    drawer = ICON_DRAWERS.get(name)
    if drawer:
        drawer(draw, x, y)

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
                y_pos = height - schedule_height - 10
                for day, pickup_time, icon_name in SCHEDULE:
                    text = f"{day}  {pickup_time}"
                    text_w, text_h = draw.textsize(text, font=font_medium)
                    icon_x = width - ICON_WIDTH - 10
                    text_x = max(10, icon_x - 10 - text_w)
                    text_y = y_pos + (ROW_HEIGHT - text_h) // 2
                    icon_y = y_pos + (ROW_HEIGHT - ICON_HEIGHT) // 2
                    draw.text((text_x, text_y), text, font=font_medium, fill=0)
                    draw_icon(draw, icon_name, icon_x, icon_y)
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

