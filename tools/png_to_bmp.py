"""Command-line utility for converting PNG images to BMP with optional resizing.

Usage examples
--------------
Convert a PNG file to BMP keeping the original size::

    python tools/png_to_bmp.py input.png output.bmp

Convert a PNG file to BMP and resize it to 800x600::

    python tools/png_to_bmp.py input.png output.bmp --width 800 --height 600

Specify only one dimension to preserve the aspect ratio::

    python tools/png_to_bmp.py input.png output.bmp --width 800

The script requires the Pillow package to be installed.
"""

from __future__ import annotations

import argparse
import pathlib
from typing import Tuple

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a PNG image to BMP with optional resizing."
    )
    parser.add_argument("input", type=pathlib.Path, help="Path to the source PNG file")
    parser.add_argument(
        "output",
        type=pathlib.Path,
        nargs="?",
        help="Path to the destination BMP file (defaults to the input name with .bmp)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Target width in pixels. If only width or height is provided, the other dimension is scaled proportionally.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Target height in pixels. If only width or height is provided, the other dimension is scaled proportionally.",
    )
    args = parser.parse_args()

    if args.output is None:
        args.output = args.input.with_suffix(".bmp")

    if args.input.suffix.lower() != ".png":
        parser.error("Input file must be a PNG image.")

    if args.output.suffix.lower() != ".bmp":
        parser.error("Output file must have a .bmp extension.")

    if args.width is not None and args.width <= 0:
        parser.error("Width must be a positive integer.")

    if args.height is not None and args.height <= 0:
        parser.error("Height must be a positive integer.")

    return args


def calculate_target_size(
    original_size: Tuple[int, int], width: int | None, height: int | None
) -> Tuple[int, int]:
    original_width, original_height = original_size

    if width is not None and height is not None:
        return width, height

    if width is not None:
        scale = width / original_width
        return width, max(1, int(round(original_height * scale)))

    if height is not None:
        scale = height / original_height
        return max(1, int(round(original_width * scale))), height

    return original_size


def convert_png_to_bmp(
    input_path: pathlib.Path,
    output_path: pathlib.Path,
    width: int | None,
    height: int | None,
) -> None:
    with Image.open(input_path) as image:
        target_size: Tuple[int, int] | None = None
        if width is not None or height is not None:
            target_size = calculate_target_size(image.size, width, height)

        image = image.convert("RGB")
        if target_size is not None and image.size != target_size:
            image = image.resize(target_size, Image.LANCZOS)
        image.save(output_path, format="BMP")


def main() -> None:
    args = parse_args()
    convert_png_to_bmp(args.input, args.output, args.width, args.height)


if __name__ == "__main__":
    main()
