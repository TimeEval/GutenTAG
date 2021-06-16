from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Type
import numpy as np

from ..anomalies import Anomaly


class BaseOscillationInterface(ABC):
    def __init__(self, *args, **kwargs):
        self.length = kwargs["base_length"]
        self.frequency = kwargs["base_frequency"]
        self.amplitude = kwargs["base_amplitude"]
        self.channels = kwargs["base_channels"]
        self.variance = kwargs["base_variance"]
        self.avg_pattern_length = kwargs["base_avg_pattern_length"]
        self.variance_pattern_length = kwargs["base_variance_pattern_length"]
        self.heart_rate = kwargs["base_heart_rate"]

        self.anomalies: List[Anomaly] = []
        self.timeseries: Optional[np.ndarray] = None

    def inject_anomalies(self, anomalies: List[Anomaly]) -> Type[BaseOscillationInterface]:
        self.anomalies.extend(anomalies)
        if issubclass(self.__class__, BaseOscillationInterface):
            return self
        raise NotImplementedError("Base class BaseOscillationInterface should not call 'inject_anomaly'. "
                                  "This method is implemented for its subclasses. Guten Tag!")

    @abstractmethod
    def generate(self) -> np.ndarray:
        raise NotImplementedError()

    @classmethod
    def __subclasshook__(cls, C):
        if cls is BaseOscillationInterface:
            if any("generate" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
