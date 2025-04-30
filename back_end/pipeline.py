from dataclasses import dataclass
import numpy as np
from interfaces import *

@dataclass
class PipelineContext:
    marker_detector_context: StageContext
    window_detector_context: StageContext
    dimension_calculator_context: StageContext

class Pipeline:
    def __init__(
        self,
        marker_detector: MarkerDetector,
        window_detector: WindowDetector | None,
        dimension_calculator: DimensionCalculator
        ):
        self.contexts = PipelineContext(
            marker_detector_context=StageContext(),
            window_detector_context=StageContext(),
            dimension_calculator_context=StageContext()
            )

        self.marker_detector = marker_detector
        self.marker_detector.context = self.contexts.marker_detector_context

        self.window_detector = window_detector
        self.window_detector.context = self.contexts.window_detector_context

        self.dimension_calculator = dimension_calculator
        self.dimension_calculator.context = self.contexts.dimension_calculator_context
    
    def run(self, image: np.ndarray) -> tuple[float, float]:
        scale = self.marker_detector.get_scale(image)
        corners = self.window_detector.detect(image)
        self.dimension_calculator.scale_mm = scale
        height, width = self.dimension_calculator.calculate(corners)
        return height, width