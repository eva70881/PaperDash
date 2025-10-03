# Weather Icons Placeholder

PaperDash expects you to provide monochrome 300×300 BMP icons for each weather
condition listed below. Place the bitmaps in this folder using the exact file
names so the dashboard can discover them at runtime.

| Weather code | Display text  | Bitmap filename        |
|--------------|---------------|------------------------|
| 0            | Clear         | `clear.bmp`            |
| 1            | Mostly clr    | `mostly_clear.bmp`     |
| 2            | Partly cldy   | `partly_cloudy.bmp`    |
| 3            | Cloudy        | `cloudy.bmp`           |
| 45           | Fog           | `fog.bmp`              |
| 48           | Rime fog      | `rime_fog.bmp`         |
| 51           | Drizzle       | `drizzle.bmp`          |
| 61           | Light rain    | `light_rain.bmp`       |
| 63           | Rain          | `rain.bmp`             |
| 65           | Heavy rain    | `heavy_rain.bmp`       |
| 71           | Snow          | `snow.bmp`             |
| 80           | Rain showers  | `rain_showers.bmp`     |

If an icon file is missing, PaperDash automatically falls back to the configured
logo so the dashboard still renders cleanly.
