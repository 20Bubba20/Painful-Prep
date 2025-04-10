"""
Gets dimensions for window in picture file.

Usage: python demo_tool.py <file_path>
"""

import cv2 as cv
import numpy as np
import sys
from pathlib import Path

MARKER_LENGTH_MM = 100
MM_IN_RATIO = 25.4

def find_windowpane(path: Path) -> np.ndarray:
    """Finds window.

    Args:
        path (pathlib.Path): File path to picture containing window.

    Returns:
        numpy.ndarray: Coordinates of corners of window.
    """
    image = cv.imread(path, cv.IMREAD_COLOR_RGB)
    grayscale_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    canny_image = cv.Canny(
        image       =grayscale_image, 
        threshold1  =200, 
        threshold2  =255
        )
    
    canny_image = cv.dilate(
        src         =canny_image, 
        kernel      =np.ones((5, 5), np.uint8), 
        iterations  =2
        )
    
    canny_image = cv.morphologyEx(
        src         =canny_image, 
        op          =cv.MORPH_CLOSE, 
        kernel      =np.ones((5, 5), np.uint8), 
        iterations  =2
        )

    if __name__ == "__main__":
        cv.imwrite("canny.jpg", canny_image)

    height, width = grayscale_image.shape
    lines_image = np.zeros(
        shape=(height, width), 
        dtype=np.uint8
        )

    lines = cv.HoughLinesP(
        image           =canny_image, 
        rho             =1, 
        theta           =np.pi / 180, 
        threshold       =25, 
        minLineLength   =1000, 
        maxLineGap      =55
        )
    
    for line in lines:
        x1, y1, x2, y2 = line[0]  # Extract line endpoints
        cv.line(
            img         =lines_image, 
            pt1         =(x1, y1), 
            pt2         =(x2, y2), 
            color       =255, 
            thickness   =1
            )
        
    lines_image = cv.morphologyEx(
        src         =lines_image,
        op          =cv.MORPH_CLOSE,
        kernel      =np.ones((5, 5), np.uint8),
        iterations  =2
    )
    
    if __name__ == "__main__":
        cv.imwrite("lines_image.jpg", lines_image)
    
    contours, _ = cv.findContours(
        image   =lines_image, 
        mode    =cv.RETR_EXTERNAL, 
        method  =cv.CHAIN_APPROX_SIMPLE
        )
    
    window_candidate = None
    contours = sorted(contours, key=cv.contourArea, reverse=True)
    if contours:
        contour = contours[0]

        window_candidate = cv.approxPolyDP(
            curve   =contour,
            epsilon =0.015 * cv.arcLength(curve=contour, closed=True),
            closed  =True
        )

        cv.polylines(
            img         =image,
            pts         =[window_candidate],
            isClosed    =True,
            color       =(0, 255, 0),
            thickness   =25
        )

        # Does the shape have four distinct sides?
        if len(window_candidate) == 4:
            cv.drawContours(
                image       =image,
                contours    =[window_candidate],
                contourIdx  =-1,   # This draws all contours in the array.
                color       =(0, 0, 255),
                thickness   =10
            )
    
    if __name__ == "__main__":
        cv.imwrite("contours.jpg", image)

    return window_candidate

def get_window_dimensions(path: str, quadrilateral: np.ndarray) -> tuple:
    """Finds window dimensions.

    Args:
        path (pathlib.Path): File path to picture containing window.
        quadrilateral (numpy.ndarray): Array object containing corner coordinates of window.

    Returns:
        tuple: Width and height of window in inches in that order.
    """
    image = cv.imread(path, cv.IMREAD_GRAYSCALE)

    aruco_corners, ids, _ = cv.aruco.detectMarkers(
        image,
        cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
        )
    
    marker_detect_success = False
    marker_corners = None
    for i, marker_id in enumerate(ids.flatten()):
        if marker_id == 0:
            marker_corners = aruco_corners[i][0]
            marker_detect_success = True
            break

    if not marker_detect_success:
        raise ValueError("No reference marker found in the image, please take or upload another image.")
    
    tl_marker = marker_corners[0]
    tr_marker = marker_corners[1]
    displacement_marker = tl_marker - tr_marker
    # Compute Euclidean norm (distance) between two points.
    norm_marker_px = np.linalg.norm(displacement_marker)
    
    scale_mm = MARKER_LENGTH_MM / norm_marker_px

    window_corners = quadrilateral.reshape(-1, 2)

    tl_window = window_corners[0]
    tr_window = window_corners[1]
    displacement_width_window = tl_window - tr_window
    norm_width_px = np.linalg.norm(displacement_width_window)
    window_width_mm = norm_width_px * scale_mm
    
    bl_window = window_corners[3]
    displacement_height_window = tl_window - bl_window
    norm_height_px = np.linalg.norm(displacement_height_window)
    window_height_mm = norm_height_px * scale_mm

    window_width_in = window_width_mm / MM_IN_RATIO
    window_height_in = window_height_mm / MM_IN_RATIO
    
    return window_width_in, window_height_in

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        exit()
    if not Path(sys.argv[1]).exists():
        print(__doc__)
        exit()

    windowpane = find_windowpane(sys.argv[1])
    width, height = get_window_dimensions(sys.argv[1], windowpane)
    print(f"Width: {height:.2f} in")
    print(F"Height: {width:.2f} in")
