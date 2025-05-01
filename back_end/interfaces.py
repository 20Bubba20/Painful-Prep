"""
@file interfaces.py
@brief Protocols for classes to be passed to Pipeline.

Interfaces declares several protocols and classes that make code more modular
and testable.
"""

from typing import Protocol, Literal
import numpy as np

class StageContext:
    """
    Context class that provides Pipeline stages access to image transformations
    and other steps in the stage. Pass a context class to a pipeline stage such
    as WindowDetector and WindowDetector classes should add valuable debugging 
    information into StageContext objects when they are given one. Outside of the
    stage, the main program can then dictate what to do with stage metadata/
    transformations.
    """
    def __init__(
        self, 
        images: dict | None = None, 
        intermediates: dict | None = None
        ):
        self.images = images
        self.intermediates = intermediates

class MarkerDetector(Protocol):
    'Protocol to define what a MarkerDetector should look like.'
    context: StageContext | None
    marker_size_mm: int | None
    marker_quantity: int | None
    marker_type: Literal["AprilTag", "ArUco", "Custom"]

    def get_scale(self, image: np.ndarray) -> np.ndarray:
        ...

class WindowDetector(Protocol):
    'Protocol to define what a WindowDetector should look like.'
    context: StageContext | None

    def detect(self, image: np.ndarray) -> np.ndarray:
        ...

class DimensionCalculator(Protocol):
    'Protocol to define what a DimensionCalculator should look like.'
    context: StageContext | None
    scale_mm: float

    def calculate(self, window_corners: np.ndarray) -> tuple[float, float]:
        ...
