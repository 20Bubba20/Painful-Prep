"""
Gets dimensions of window in image that has two markers in opposing corners.

Marker size must be provided in millimeters (mm).

Usage:
    python two_marker_detect.py <filepath> <marker_size>
"""

import cv2 as cv
import numpy as np
import sys
from pathlib import Path

from demo_tool import MM_IN_RATIO

def calculate_two_markers(path: Path, marker_size_mm: int) -> tuple[int, int]:
    """Finds width and height of window that has ArUco markers in opposing corners.

    Args:
        path (Path): Relative or absolute filepath to image.
        marker_size_mm (int): Size of marker used in mm. Must be a whole number.

    Returns:
        tuple (int, int): Returns the width and height of the window in inches.
    """
    image = cv.imread(path, cv.IMREAD_COLOR_RGB)

    # Find markers.
    corners, ids, _ = cv.aruco.detectMarkers(
        image       =image,
        dictionary  =cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
        )

    # Exit if there are too few or too many markers.
    if ids is None or len(ids) != 2:
        return None, None
    
    # Get the average scale.
    scale_px = (get_scale(corners[0][0]) + get_scale(corners[1][0])) / 2

    # Clean corner coordinates.
    corners = [arr.squeeze() for arr in corners]
    corners = [[[round(x) for x in row] for row in marker] for marker in corners]
    corner_coords = np.concatenate(corners)

    # Isolate just the y coordinates.
    y_coords = [coord[1] for coord in corner_coords]
    y_coords_tmp = y_coords.copy()

    # Find the two highest vectors.
    y_1 = min(y_coords_tmp)
    y_1_idx = y_coords.index(y_1)
    y_coords_tmp.remove(y_1)

    y_2 = min(y_coords_tmp)
    y_2_idx = y_coords.index(y_2)

    # Find the top left most vector.
    if corner_coords[y_1_idx][0] < corner_coords[y_2_idx][0]:
        tl_coord = corner_coords[y_1_idx]
    else:
        tl_coord = corner_coords[y_2_idx]

    # Find the bottom most two vectors.
    y_3 = max(y_coords_tmp)
    y_3_idx = y_coords.index(y_3)
    y_coords_tmp.remove(y_3)

    y_4 = max(y_coords_tmp)
    y_4_idx = y_coords.index(y_4)

    # Check which one is the bottom right vector.
    if corner_coords[y_3_idx][0] > corner_coords[y_4_idx][0]:
        br_coord = corner_coords[y_3_idx]
    else:
        br_coord = corner_coords[y_4_idx]

    # Get width and height in pixels.
    h_px = abs(tl_coord[0] - br_coord[0])
    w_px = abs(tl_coord[1] - br_coord[1])

    if __debug__:
        corner_img = cv.circle(image, tl_coord, 5, (0, 255, 0), 5)
        corner_img = cv.circle(image, br_coord, 5, (0, 255, 0), 5)
        cv.imwrite("corners.jpg", corner_img)
    
    # Convert width and height to inches.
    scale_mm = marker_size_mm / scale_px

    h_in = (h_px * scale_mm) / MM_IN_RATIO
    w_in = (w_px * scale_mm) / MM_IN_RATIO

    return h_in, w_in

def get_scale(corners: np.ndarray) -> float:
    displ_0 = corners[0] - corners[1]
    displ_1 = corners[1] - corners[2]
    displ_2 = corners[2] - corners[3]
    displ_3 = corners[3] - corners[1]

    norms = []

    norms.append(np.linalg.norm(displ_0))
    norms.append(np.linalg.norm(displ_1))
    norms.append(np.linalg.norm(displ_2))
    norms.append(np.linalg.norm(displ_3))

    scale = np.average(norms)

    return scale

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        exit()
    if not Path(sys.argv[1]).exists():
        print(__doc__)
        exit()
    if not sys.argv[2].isdigit():
        print(__doc__)
        exit()

    width, height = calculate_two_markers(sys.argv[1], int(sys.argv[2]))

    print(f"Width: {width:.2f} in")
    print(f"Height: {height:.2f} in")