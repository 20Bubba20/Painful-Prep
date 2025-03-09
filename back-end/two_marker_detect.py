import cv2 as cv
import numpy as np
import sys
from pathlib import Path

def get_markers(path: Path, marker_size_mm: int) -> np.ndarray:
    image = cv.imread(path, cv.IMREAD_COLOR_RGB)

    # ids is of type np.ndarray
    corners, ids, _ = cv.aruco.detectMarkers(
        image,
        cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
        )
    
    print(corners[0][0])
    
    # if len(ids) != 2:
    #     return None

    corners = [np.round(corner).astype(int) for corner in corners]
    
    for corner in corners[0][0]:
        cv.circle(
            img=image,
            center=(corner[0], corner[1]),
            radius=20,
            color=(0, 0, 255),
            thickness=-1
            )
    
    cv.imwrite("corners.jpg", image)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        exit()
    if not Path(sys.argv[1]).exists():
        exit()
    if not sys.argv[2].isdigit():
        exit()

    get_markers(sys.argv[1], sys.argv[2])
