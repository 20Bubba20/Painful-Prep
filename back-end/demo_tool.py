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
    
    canny_image = cv.Canny(
        image       =grayscale_image, 
        threshold1  =220, 
        threshold2  =255
        )
    
    canny_image = cv.dilate(
        src         =canny_image, 
        kernel      =np.ones((5, 5), np.uint8), 
        iterations  =1
        )
    
    canny_image = cv.morphologyEx(
        src         =canny_image, 
        op          =cv.MORPH_CLOSE, 
        kernel      =np.ones((5, 5), np.uint8), 
        iterations  =2
        )

    cv.imwrite("canny.jpg", canny_image)

    x, y = grayscale_image.shape
    lines_image = np.zeros(
        shape=(x, y), 
        dtype=np.uint8
        )

    lines = cv.HoughLinesP(
        image           =canny_image, 
        rho             =1, 
        theta           =np.pi / 180, 
        threshold       =30, 
        minLineLength   =1000, 
        maxLineGap      =50
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
    
    cv.imwrite("lines_image.jpg", lines_image)
    
    contours, _ = cv.findContours(
        image   =lines_image, 
        mode    =cv.RETR_EXTERNAL, 
        method  =cv.CHAIN_APPROX_SIMPLE
        )
    
    for contour in contours:
        window_candidate = cv.approxPolyDP(
            curve   =contour,
            epsilon =0.003 * cv.arcLength(curve=contour, closed=True),
            closed  =True
        )

        cv.polylines(
            img=image,
            pts=[window_candidate],
            isClosed=True,
            color=(0, 255, 0),
            thickness=3
        )

        # Does the shape have foru distinct sides?
        if len(window_candidate) == 4 and cv.isContourConvex(window_candidate):
            print("Success!")
            cv.drawContours(
                image       =image,
                contours    =[window_candidate],
                contourIdx  =-1,   # This draws all contours in the array.
                color       =(0, 0, 255),
                thickness   =10
            )
    
    cv.imwrite("contours.jpg", image)

if __name__ == "__main__":
    get_window_dimensions()