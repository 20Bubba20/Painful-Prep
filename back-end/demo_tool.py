"""
Gets dimensions for window in picture file.

Usage: python demo_tool.py <file_path>
"""

import cv2 as cv
import numpy as np
import sys
from pathlib import Path

from numpy.ma.core import bitwise_and

MARKER_LENGTH_MM = 100
MM_IN_RATIO = 25.4


def apply_dog(image: np.ndarray, sigma1=1.0, sigma2=2.0) -> np.ndarray:
    blur1 = cv.GaussianBlur(image, (0, 0), sigma1)
    blur2 = cv.GaussianBlur(image, (0, 0), sigma2)
    dog = cv.subtract(blur1, blur2)

    # Normalize to 0-255 for visibility
    dog = cv.normalize(dog, None, 0, 255, cv.NORM_MINMAX).astype(np.uint8)

    return dog

def apply_canny(image: np.ndarray):

    canny_image = cv.Canny(
        image=image,
        threshold1=200,
        threshold2=255
    )

    canny_image = cv.dilate(
        src=canny_image,
        kernel=np.ones((5, 5), np.uint8),
        iterations=2
    )

    canny_image = cv.morphologyEx(
        src=canny_image,
        op=cv.MORPH_CLOSE,
        kernel=np.ones((5, 5), np.uint8),
        iterations=2
    )
    return canny_image

def find_windowpane(path: Path) -> np.ndarray:
    """Finds window.

    Args:
        path (pathlib.Path): File path to picture containing window.

    Returns:
        numpy.ndarray: Coordinates of corners of window.
    """
    image = cv.imread(path, cv.IMREAD_COLOR_RGB)
    grayscale_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Apply Canny Pass
    canny_image = apply_canny(grayscale_image)
    cv.imwrite("canny.jpg", canny_image)

    # Apply 2 DoG passes to find well and poorly defined edges
    dog_pass_1 = apply_dog(image=grayscale_image, sigma1=4.0, sigma2=7.0)
    dog_pass_2 = apply_dog(image=grayscale_image, sigma1=20.0, sigma2=25.0)

    cv.imwrite("dog1.jpg", dog_pass_1)
    cv.imwrite("dog2.jpg", dog_pass_2)

    # Combine DoG passes by weighted sum, blur to cull noise,
    # apply another DoG pass and crush to black and white with ostu threshold
    dog_combined = cv.addWeighted(dog_pass_1, 0.6, dog_pass_2, 0.4, 0)
    dog_combined = apply_dog(dog_combined, sigma1=10.0, sigma2=13.0)
    dog_combined = cv.blur(dog_combined, (10, 10))
    _, dog_final = cv.threshold(dog_combined, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    cv.imwrite("dog_combined.jpg", dog_combined)
    cv.imwrite("dog.jpg", dog_final)

    # Combine DoG with canny by using it as a mask
    combined_image = cv.bitwise_and(dog_final, canny_image)
    cv.imwrite("combined.jpg", combined_image)

    height, width = grayscale_image.shape
    lines_image = np.zeros(
        shape=(height, width), 
        dtype=np.uint8
        )

    lines = cv.HoughLinesP(
        image           =combined_image,
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
        raise Exception
    
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
