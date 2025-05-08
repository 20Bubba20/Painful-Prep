"""
Gets dimensions for window in picture file.

Usage: python demo_tool.py <file_path>
"""

import cv2 as cv
import numpy as np
import sys
from pathlib import Path
import line_finder


MARKER_LENGTH_MM = 100
MM_IN_RATIO = 25.4
OUTPUT_PASSES = False


def apply_dog(image: np.ndarray, sigma1=1.0, sigma2=2.0) -> np.ndarray:
    blur1 = cv.GaussianBlur(image, (0, 0), sigma1)
    blur2 = cv.GaussianBlur(image, (0, 0), sigma2)
    dog = cv.subtract(blur1, blur2)

    # Normalize to 0-255 for visibility
    dog = cv.normalize(dog, None, 0, 255, cv.NORM_MINMAX).astype(np.uint8)

    return dog


def apply_canny(image: np.ndarray):

    # Use Otsu's method to find threshold for canny detection
    thresh, otsu_thresh = cv.threshold(image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    canny_image = cv.Canny(
        image=image,
        threshold1=thresh,
        threshold2=thresh*1.5
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

    # Apply 2 DoG passes to find well and poorly defined edges
    dog_pass_1 = apply_dog(image=grayscale_image, sigma1=4.0, sigma2=7.0)
    dog_pass_2 = apply_dog(image=grayscale_image, sigma1=20.0, sigma2=25.0)

    # Combine DoG passes by weighted sum, blur to cull noise and artifacts,
    # apply another DoG pass and crush to black and white with ostu threshold
    dog_combined = cv.addWeighted(dog_pass_1, 0.6, dog_pass_2, 0.4, 0)
    dog_combined = apply_dog(dog_combined, sigma1=10.0, sigma2=13.0)
    dog_combined = cv.blur(dog_combined, (10, 10))
    _, dog_final = cv.threshold(dog_combined, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    # Dilate B/W DoG output for masking
    dog_final = cv.dilate(dog_final, kernel=np.ones((5, 5), np.uint8), iterations=3)

    # Combine DoG with canny by using it as a mask
    combined_image = cv.bitwise_and(canny_image, dog_final)

    # Output every pass in order
    if OUTPUT_PASSES is True:
        cv.imwrite("1_canny.jpg", canny_image)
        cv.imwrite("2_dog1.jpg", dog_pass_1)
        cv.imwrite("3_dog2.jpg", dog_pass_2)
        cv.imwrite("4_dog_combined.jpg", dog_combined)
        cv.imwrite("5_dog_final.jpg", dog_final)
        cv.imwrite("6_combined.jpg", combined_image)

    # Pass DoG output to Hough Lines pipeline
    quad, lines_image = line_finder.process_lines(combined_image, show_output=False)

    if quad is not None:
        # Ensure quad is a NumPy array of type int32
        quad = np.array(quad, dtype=np.int32).reshape((-1, 1, 2))

        # Draw quadrilateral on a copy of the original image
        orig = image.copy()
        cv.polylines(orig, [quad], True, (0, 255, 0), 20)

        cv.imwrite("contours.jpg", orig)
    else:
        print("No quadrilateral found.")
        for line in lines_image:
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

    lines_output = cv.dilate(lines_image, kernel=np.ones((5, 5), np.uint8), iterations=3)

    cv.imwrite("lines_image.jpg", lines_output)


    return quad

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
