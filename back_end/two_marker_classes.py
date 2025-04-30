from typing import Literal
import cv2 as cv
import numpy as np
import interfaces
import custom_exceptions
import two_marker_detect
import pipeline

class TwoMarkerDetector():
    def __init__(self, marker_size_mm, marker_type, context: interfaces.StageContext):
        self.marker_size_mm = marker_size_mm
        self.marker_quantity = 2
        self.marker_type: Literal["ArUco", "AprilTag"] = marker_type
        self.context = context
        self._corners = None
        self.MM_IN_RATIO = 25.4
        self.scale_mm: float | None = None
    
    def get_scale(self, image: np.ndarray) -> float:
        """
        @brief Computes the pixel scale from an ArUco marker.

        Given an image, this function calculates the scale in millimeters of the markers in the image.

        @param image An opencv image.

        @return The average scale of the markers in the image.
        """
        if len(image.shape) == 3 and image.shape[2] == 3:
            reload_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        else:
            reload_image = image
        
        # Find markers.
        if self.marker_type == "ArUco":
            corners, ids, failed = cv.aruco.detectMarkers(
            image       =reload_image,
            dictionary  =cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
            )
        elif self.marker_type == "AprilTag":
            dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_16H5)
            params = cv.aruco.DetectorParameters()
            params.markerBorderBits = 2
            params.adaptiveThreshWinSizeStep = 1

            corners, ids, failed = cv.aruco.detectMarkers(
                image       = reload_image,
                dictionary  = dictionary,
                parameters  = params
            )
        
         # Exit if there are too few or too many markers.
        if ids is None:
            debug_image = cv.aruco.drawDetectedMarkers(
                image=detected_image,
                corners=failed,
                borderColor=(0, 0, 255)
            )
            
            self.context.images["debug_image"] = debug_image

            raise custom_exceptions.MarkerNotFoundError(
                message=f"expected {self.marker_quantity} markers but found 0 markers",
                errors=custom_exceptions.MarkerDetectionErrorDetails(
                    expected_quantity=self.marker_quantity,
                    detected_quantity=0,
                    detected_ids=None
                )
            )

        elif len(ids) != self.marker_quantity:
            detected_image = cv.aruco.drawDetectedMarkers(
                image       =image,
                corners     =corners,
                ids         =ids,
                borderColor =(0, 255, 0)
                )
            
            debug_image = cv.aruco.drawDetectedMarkers(
                image=detected_image,
                corners=failed,
                borderColor=(0, 0, 255)
            )

            self.context.images["debug_image"] = debug_image

            raise custom_exceptions.MarkerNotFoundError(
                message=f"expected {self.marker_quantity} markers but found 0 markers",
                errors=custom_exceptions.MarkerDetectionErrorDetails(
                    expected_quantity=self.marker_quantity,
                    detected_quantity=len(ids),
                    detected_ids=ids
                )
            )
        
        self._corners = corners

        scale_px = (two_marker_detect.get_scale(corners[0][0]) + two_marker_detect.get_scale(corners[1][0])) / 2
        scale_mm = self.marker_size_mm / scale_px
        return scale_mm
    
    def detect(self, image: np.ndarray) -> np.ndarray:
        if not self._corners:
            self.get_scale(image)
        return self._corners
    
    def calculate(self, window_corners: np.ndarray) -> tuple[float, float]:
        # Clean corner coordinates.
        corners = [arr.squeeze() for arr in window_corners]
        corners = [[[round(x) for x in row] for row in marker] for marker in corners]
        corner_coords = np.concatenate(corners)

        # Find which marker is the top marker. OpenCV image
        # coordinate origin (0, 0) is the top left corner of images. 
        if corners[0][0][0] < corners[1][0][0]:
            top_marker_coords = corners[0]
            bottom_marker_coords = corners[1] 
        else:
            top_marker_coords = corners[1]
            bottom_marker_coords = corners[0]

        is_top_marker_left = top_marker_coords[0][1] < bottom_marker_coords[0][1]

        # Top left, bottom right diagonal case.
        if is_top_marker_left:
            t_coord_x, t_coord_y, b_coord_x, b_coord_y = two_marker_detect.get_diff_two_markers_px(corner_coords, "TLBR")
        # Top right, bottom left diagonal case.
        else:
            t_coord_x, t_coord_y, b_coord_x, b_coord_y = two_marker_detect.get_diff_two_markers_px(corner_coords, "TRBL")

        # Get width and height in pixels.
        h_px = abs(t_coord_x - b_coord_x)
        w_px = abs(t_coord_y - b_coord_y)

        h_in = (h_px * self.scale_mm) / self.MM_IN_RATIO
        w_in = (w_px * self.scale_mm) / self.MM_IN_RATIO

        return h_in + 0.25, w_in + 0.25

if __name__ == "__main__":
    detector = TwoMarkerDetector(20, "AprilTag", interfaces.StageContext())
    image = cv.imread("/home/tminnich/projects/capstone/Painful-Prep/back_end/tests/test-images/img_047.JPG", cv.IMREAD_COLOR_BGR)
    my_pipeline = pipeline.Pipeline(detector, detector, detector)
    print(my_pipeline.run(image))
