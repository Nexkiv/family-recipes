"""Prepare a recipe image for the site: apply phone rotation, optionally flatten a
phone photo of a page, resize, and save as JPEG with all metadata (incl. GPS) dropped.

Proper scans don't need --corners. For a phone photo of a page, pass the page's
corners (TL TR BR BL, in pixels of the rotated image) to straighten it to US Letter.

  python tools/prepare_image.py in.heic out.jpg --corners "725,1033 2373,995 2595,3275 404,3227"
  python tools/prepare_image.py photo.jpg out.jpg --max 1600
"""
import argparse

import cv2
import numpy as np
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()
LETTER_RATIO = 11 / 8.5  # height / width


def flatten(rgb, corners, width=1700):
    height = round(width * LETTER_RATIO)
    dst = np.float32([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]])
    m = cv2.getPerspectiveTransform(corners, dst)
    return cv2.warpPerspective(rgb, m, (width, height), flags=cv2.INTER_CUBIC)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--corners", help="'x,y x,y x,y x,y' as top-left, top-right, bottom-right, bottom-left")
    ap.add_argument("--max", type=int, default=1700, help="longest side in pixels")
    args = ap.parse_args()

    img = ImageOps.exif_transpose(Image.open(args.src)).convert("RGB")
    if args.corners:
        corners = np.float32([c.split(",") for c in args.corners.split()])
        img = Image.fromarray(flatten(np.array(img), corners))
    img.thumbnail((args.max, args.max), Image.LANCZOS)
    img.save(args.out, "JPEG", quality=86, optimize=True, progressive=True)  # no EXIF written
    print(f"{args.out}: {img.width}x{img.height}")


if __name__ == "__main__":
    main()
