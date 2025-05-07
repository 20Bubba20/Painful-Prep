from typing import TypedDict
import numpy as np

class MarkerDetectionErrorDetails(TypedDict):
    expected_quantity: int
    detected_quantity: int
    detected_ids: list[int]

class MarkerNotFoundError(Exception):
    def __init__(
        self, 
        message, 
        errors: MarkerDetectionErrorDetails | None = None,
        debug_image: np.ndarray | None = None
        ):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
            
        # Now for your custom code...
        self.errors = errors
        self.debug_image = debug_image