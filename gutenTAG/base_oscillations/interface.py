from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Type
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

    def inject_anomalies(self, anomalies: List[Anomaly]) -> Type[BaseOscillationInterface]:
        self.anomalies.extend(anomalies)
        if issubclass(self.__class__, BaseOscillationInterface):
            return self
        raise NotImplementedError("Base class BaseOscillationInterface should not call 'inject_anomaly'. "
                                  "This method is implemented for its subclasses. Guten Tag!")

    @abstractmethod
    def generate(self) -> np.ndarray:
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
