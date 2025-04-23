from typing import Protocol, Literal
import numpy as np

class StageContext:
    def __init__(
        self, 
        images: dict | None = None, 
        intermediates: dict | None = None
        ):
        self.images = images
        self.intermediates = intermediates

class MarkerDetector(Protocol):
    context: StageContext | None
    marker_size_mm: int | None
    marker_quantity: int | None
    marker_type: Literal["AprilTag", "ArUco", "Custom"]

    def get_scale(self, image: np.ndarray) -> np.ndarray:
        ...

class WindowDetector(Protocol):
    context: StageContext | None

    def detect(self, image: np.ndarray) -> np.ndarray:
        ...

class DimensionCalculator(Protocol):
    context: StageContext | None
    scale_mm: float

    def calculate(self, window_corners: np.ndarray) -> tuple[float, float]:
        ...
