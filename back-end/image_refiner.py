import cv2 as cv
import numpy as np
from pathlib import Path

def image_refiner(image: np.ndarray, gamma=1.0) -> np.ndarray:
    """
    The image refiner uses gamma correction to increase contrast. 
    It also uses Gaussian blur to increase sharpness of images.
    """
    invgamma = 1.0 / gamma
    # This looks at each pixel value and assigns a gamma correction for each pixel.
    table = np.array([((i / 255.0) ** invgamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")

    # The lookup table quickly adjusts each pixel to match the corrected gamma amount calculated earlier.
    gamma_adjusted_image = cv.LUT(image, table)

    return gamma_adjusted_image