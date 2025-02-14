from typing import Protocol, List, Dict, Any
from dataclasses import dataclass, field
import numpy as np

@dataclass
class ImageProcessingContext:
    """Context class to be passed between ImageProcessor instances."""
    image: np.ndarray
    data: Dict[str, Any] = field(default_factory=dict)

class ImageProcessor(Protocol):
    """Interface to ensure adherence to method signatures."""
    def process(self, context: ImageProcessingContext) -> None:
        ...

class ImageProcessingPipeline:
    """Pipeline to inject ImageProcessors into."""
    def __init__(self, processes: List["ImageProcessor"]):
        self.processes = processes

    def run(self, context: ImageProcessingContext) -> None:
        for process in self.processes:
            process.process(context)
