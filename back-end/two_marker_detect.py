"""
@file two_marker_detect.py
@brief Gets dimensions of a window in an image containing two markers in opposing corners.

This script detects two ArUco markers in an image and calculates the width and height 
of a window using the known size of the markers.

Usage:
    python two_marker_detect.py <filepath> <marker_size>

@note The marker size must be provided in millimeters (mm).
"""

import cv2 as cv
import numpy as np
import sys
from pathlib import Path
from typing import Literal

from demo_tool import MM_IN_RATIO

def calculate_two_markers(path: Path, marker_size_mm: int) -> tuple[int, int]:
    """
    @brief Finds the width and height of a window using two ArUco markers.

    This function detects exactly two ArUco markers in an image, computes the scale 
    based on their known size, and calculates the dimensions of the window in inches.

    @param path Path to the image file.
    @param marker_size_mm Known size of the marker in millimeters.

    @return Tuple (width, height) of the window in inches. Returns None if the number 
            of markers detected is not exactly two.
    """
    image = cv.imread(path, cv.IMREAD_COLOR_RGB)

    # Find markers.
    corners, ids, _ = cv.aruco.detectMarkers(
        image       =image,
        dictionary  =cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
        )

    # Exit if there are too few or too many markers.
    if len(ids) != 2:
        return None
    
    # Get the average scale.
    scale_px = (get_scale(corners[0][0]) + get_scale(corners[1][0])) / 2

    # Clean corner coordinates.
    corners = [arr.squeeze() for arr in corners]
    corners = [[[round(x) for x in row] for row in marker] for marker in corners]
    corner_coords = np.concatenate(corners)

    # Find which marker is the top marker. OpenCV image
    # coordinate origin (0, 0) is the top left corner of images. 
    if corners[0][0][1] < corners[1][0][1]:
        top_marker_coords = corners[0]
        bottom_marker_coords = corners[1] 
    else:
        top_marker_coords = corners[1]
        bottom_marker_coords = corners[0]
    
    is_top_marker_left = top_marker_coords[0][1] < bottom_marker_coords[0][1]

    # Use this for verbose debugging:
    # if __debug__:
    #     print(f"coords: {corners}\n")
    #     print(f"top marker: {top_marker_coords}\n")
    #     print(f"Is top marker left? {is_top_marker_left} because:")
    #     print(f"{top_marker_coords[0][1]} < {bottom_marker_coords[0][1]}")

    # Top left, bottom right diagonal case.
    if is_top_marker_left:
        t_coord_x, t_coord_y, b_coord_x, b_coord_y = get_diff_two_markers_px(corner_coords, "TLBR")
    # Top right, bottom left diagonal case.
    else:
        t_coord_x, t_coord_y, b_coord_x, b_coord_y = get_diff_two_markers_px(corner_coords, "TRBL")
    
    # Get width and height in pixels.
    h_px = abs(t_coord_x - b_coord_x)
    w_px = abs(t_coord_y - b_coord_y)

    if __debug__:
        corner_img = cv.circle(image, (t_coord_x, t_coord_y), 5, (0, 255, 0), 5)
        corner_img = cv.circle(image, (b_coord_x, b_coord_y), 5, (0, 255, 0), 5)
        cv.imwrite("corners.jpg", corner_img)

    # Convert width and height to inches.
    scale_mm = marker_size_mm / scale_px

    h_in = (h_px * scale_mm) / MM_IN_RATIO
    w_in = (w_px * scale_mm) / MM_IN_RATIO

    return h_in, w_in

def get_scale(corners: np.ndarray) -> float:
    """
    @brief Computes the pixel scale from an ArUco marker.

    Given the four corners of a detected marker, this function calculates the 
    average length of its sides, which is used to determine the scale.

    @param corners A 4x2 NumPy array containing the corner coordinates of a marker.

    @return The average pixel length of the marker's sides.
    """
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

def get_diff_two_markers_px(coords: list[int], diagonal: Literal["TLBR", "TRBL"] = "TLBR") -> tuple[int, int, int, int]:
    # More or less than two markers is not valid.
    if len(coords) != 8:
        return None
    
    # Isolate just the y coordinates.
    y_coords = [coord[1] for coord in coords]
    y_coords_tmp = y_coords.copy()

    # Find the two highest vectors.
    y_1 = min(y_coords_tmp)
    y_1_idx = y_coords.index(y_1)
    y_coords_tmp.remove(y_1)

    y_2 = min(y_coords_tmp)
    y_2_idx = y_coords.index(y_2)

    # Find the bottom most two vectors.
    y_3 = max(y_coords_tmp)
    y_3_idx = y_coords.index(y_3)
    y_coords_tmp.remove(y_3)

    y_4 = max(y_coords_tmp)
    y_4_idx = y_coords.index(y_4)

    if diagonal == "TLBR":
        # Find the top left most vector.
        if coords[y_1_idx][0] < coords[y_2_idx][0]:
            tl_coord_x, tl_coord_y = coords[y_1_idx]
        else:
            tl_coord_x, tl_coord_y = coords[y_2_idx]

        # Check which one is the bottom right vector.
        if coords[y_3_idx][0] > coords[y_4_idx][0]:
            br_coord_x, br_coord_y = coords[y_3_idx]
        else:
            br_coord_x, br_coord_y = coords[y_4_idx]

        return tl_coord_x, tl_coord_y, br_coord_x, br_coord_y
    
    elif diagonal == "TRBL":
        # Find the top right most vector.
        if coords[y_1_idx][0] > coords[y_2_idx][0]:
            tr_coord_x, tr_coord_y = coords[y_1_idx]
        else:
            tr_coord_x, tr_coord_y = coords[y_2_idx]

        # Check which one is the bottom left most vector.
        if coords[y_3_idx][0] < coords[y_4_idx][0]:
            bl_coord_x, bl_coord_y = coords[y_3_idx]
        else:
            bl_coord_x, bl_coord_y = coords[y_4_idx]

        return tr_coord_x, tr_coord_y, bl_coord_x, bl_coord_y
    else:
        return None

if __name__ == "__main__":
    """
    @brief Main execution point for the script.

    This script takes an image file path and a marker size in mm as input, 
    processes the image to find two ArUco markers, and calculates the 
    window dimensions in inches.
    """
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