from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import numpy as np

from ..anomalies import Anomaly


class BaseOscillationInterface(ABC):
    def __init__(self, *args, **kwargs):
        self.length = kwargs["length"]
        self.frequency = kwargs["frequency"]
        self.amplitude = kwargs["amplitude"]
        self.channels = kwargs["channels"]
        self.variance = kwargs["variance"]
        self.avg_pattern_length = kwargs["avg-pattern-length"]
        self.variance_pattern_length = kwargs["variance-pattern-length"]
        self.heart_rate = kwargs["heart-rate"]

        self.anomalies: List[Anomaly] = []
        self.timeseries: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None
        self.noise = self.generate_noise(self.variance, self.length)

    def inject_anomalies(self, anomalies: List[Anomaly]) -> BaseOscillationInterface:
        self.anomalies.extend(anomalies)
        if issubclass(self.__class__, BaseOscillationInterface):
            return self
        raise NotImplementedError("Base class BaseOscillationInterface should not call 'inject_anomaly'. "
                                  "This method is implemented for its subclasses. Guten Tag!")

    def generate_noise(self, variance: float, length: int) -> np.ndarray:
        return np.random.normal(0, variance, length).reshape(length, 1)

    @abstractmethod
    def generate(self) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        raise NotImplementedError()

    @abstractmethod
    def generate_only_base(self, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError()

    @classmethod
    def __subclasshook__(cls, C):
        if cls is BaseOscillationInterface:
            if any("generate" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
