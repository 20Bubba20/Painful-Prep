import cv2 as cv
import numpy as np

MARKER_LENGTH_MM = 100

def get_window_dimensions():
    path = "/home/tminnich/projects/capstone/Painful-Prep/back-end/test/test-images/img_001.JPG"
    image = cv.imread(path, cv.IMREAD_GRAYSCALE)

    aruco_corners, ids, _ = cv.aruco.detectMarkers(
        image,
        cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
        )
    
    marker_detect_success = False
    for i, marker_id in enumerate(ids.flatten()):
        if marker_id == 0:
            marker_detect_success = True
            break

    if not marker_detect_success:
        raise Exception
    
    marker_corners = aruco_corners[i][0]
    top_left_corner_vector = marker_corners[0]
    top_right_corner_vector = marker_corners[1]
    displacement_vector = top_left_corner_vector - top_right_corner_vector

    # Compute the Euclidean norm (magnitude) of the displacement vector.
    marker_length_px = np.linalg.norm(displacement_vector)
    


if __name__ == "__main__":
    get_window_dimensions()