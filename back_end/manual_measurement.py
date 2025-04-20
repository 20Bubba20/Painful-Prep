"""
@file manual_measurement.py
@brief Manually select corners of window and markers to compute dimensions.

This tool allows for manually selecting the corners of a window for dimension calculation.

Usage:
    python manual_measurement.py <filepath> <marker_size>

@note The marker size must be provided in millimeters (mm).
"""

import cv2 as cv
import sys
import two_marker_detect
from pathlib import Path

def main():
    path = Path(sys.argv[1])

    if len(sys.argv) != 2:
        print(__doc__)
        exit()
    if not path.exists():
        print(__doc__)
        exit()

    marker_size_mm = sys.argv[2]
    window_name = path.name
    marker_coords, window_coords = []

    image = cv.imread(path, cv.IMREAD_COLOR_RGB)
    cv.imshow(window_name, image)
    cv.setMouseCallback(window_name, click_handler, (image, marker_coords))
    cv.waitKey(0)

    if len(marker_coords) != 4:
        raise ValueError("too many corner coordinates for marker")

    cv.imshow(window_name, image)
    cv.setMouseCallback(window_name, click_handler, (image, window_coords))
    cv.waitKey(0)

    if len(window_coords) != 4:
        raise ValueError("too many corner coordinates for window")

def click_handler(event, x, y, _, params: tuple[list, list]):
    """Mouse click event handler. Only reacts to left mouse clicks."""
    if event is not cv.EVENT_LBUTTONDOWN:
        return
    image, coords = params
    coords.append((x, y))
    cv.circle(image, (x, y), 5, (0, 255, 0), -1)
    cv.imshow('Image', image)

if __name__ == "__main__":
    main()