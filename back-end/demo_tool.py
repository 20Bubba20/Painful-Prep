import cv2 as cv
import numpy as np

MARKER_LENGTH_MM = 100

def get_window_dimensions():
    path = "/home/tminnich/projects/capstone/Painful-Prep/back-end/test/test-images/img_002.JPG"
    image = cv.imread(path, cv.IMREAD_COLOR_RGB)
    grayscale_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    aruco_corners, ids, _ = cv.aruco.detectMarkers(
        grayscale_image,
        cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
        )
    
    marker_detect_success = False
    for i, marker_id in enumerate(ids.flatten()):
        if marker_id == 0:
            marker_detect_success = True
            break

    if not marker_detect_success:
        raise Exception
    
    edges = cv.Canny(
        image       =grayscale_image, 
        threshold1  =200, 
        threshold2  =255
        )

    x, y = grayscale_image.shape
    lines_image = np.zeros(
        shape=(x, y), 
        dtype=np.uint8
        )

    lines = cv.HoughLinesP(
        image           =edges, 
        rho             =1, 
        theta           =np.pi / 180, 
        threshold       =50, 
        minLineLength   =800, 
        maxLineGap      =120
        )

    for line in lines:
        x1, y1, x2, y2 = line[0]  # Extract line endpoints
        cv.line(
            img         =lines_image, 
            pt1         =(x1, y1), 
            pt2         =(x2, y2), 
            color       =255, 
            thickness   =3
            )
    
    contours, _ = cv.findContours(
        image   =lines_image, 
        mode    =cv.RETR_EXTERNAL, 
        method  =cv.CHAIN_APPROX_SIMPLE
        )
    
    for contour in contours:
        window_candidate = cv.approxPolyDP(
            curve   =contour,
            epsilon =0.02 * cv.arcLength(curve=contour, closed=True),
            closed  =True
        )

        # Does the shape have foru distinct sides?
        if len(window_candidate) == 4:
            cv.drawContours(
                image       =image,
                contours    =[window_candidate],
                contourIdx  =-1,   # This draws all contours in the array.
                color       =(255, 0, 0),
                thickness   =3
            )
    
    cv.imwrite("lines_image.jpg", lines_image)

if __name__ == "__main__":
    get_window_dimensions()