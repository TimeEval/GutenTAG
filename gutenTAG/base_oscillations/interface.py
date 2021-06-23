from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import numpy as np

from ..anomalies import Anomaly, LabelRange
from ..utils.types import BaseOscillationKind


class BaseOscillationInterface(ABC):
    def __init__(self, *args, **kwargs):
        self.length = kwargs.get("length", 10000)
        self.frequency = kwargs.get("frequency", 10.0)
        self.amplitude = kwargs.get("amplitude", 1.0)
        self.channels = kwargs.get("channels", 2.0)
        self.variance = kwargs.get("variance", 0.0)
        self.avg_pattern_length = kwargs.get("avg-pattern-length", 10)
        self.variance_pattern_length = kwargs.get("variance-pattern-length", 0.0)
        self.heart_rate = kwargs.get("heart-rate", 60.0)

        self.anomalies: List[Anomaly] = []
        self.timeseries: Optional[np.ndarray] = None
        self.labels: np.ndarray = np.zeros(self.length, dtype=np.int)
        self.noise = self.generate_noise(self.variance * self.amplitude, self.length)

    def inject_anomalies(self, anomalies: List[Anomaly]) -> BaseOscillationInterface:
        self.anomalies.extend(anomalies)
        if issubclass(self.__class__, BaseOscillationInterface):
            return self
        raise NotImplementedError("Base class BaseOscillationInterface should not call 'inject_anomaly'. "
                                  "This method is implemented for its subclasses. Guten Tag!")

    def generate_noise(self, variance: float, length: int) -> np.ndarray:
        return np.random.normal(0, variance, length).reshape(length, 1)

    def _generate_anomalies(self):
        label_ranges: List[LabelRange] = []

        protocols = [(anomaly.generate(self, self.get_timeseries_periods(), self.get_base_oscillation_kind()), anomaly.channel) for anomaly in
                     self.anomalies]

        for protocol, channel in protocols:
            if len(protocol.subsequences) > 0:
                subsequence = np.vstack(protocol.subsequences).sum(axis=0)
                self.timeseries[protocol.start:protocol.end, channel] = subsequence
            label_ranges.append(protocol.labels)

        self._add_label_ranges_to_labels(label_ranges)
        self.timeseries += self.noise

    def _add_label_ranges_to_labels(self, label_ranges: List[LabelRange]):
        for label_range in label_ranges:
            self.labels[label_range.start:label_range.start + label_range.length] = 1

    @abstractmethod
    def generate(self) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        raise NotImplementedError()

    @abstractmethod
    def get_timeseries_periods(self) -> Optional[int]:
        """
        How many same-sized periods do occur in the time series? If no periodicity is given, return None!
        :return: Optional[int]
        """
        raise NotImplementedError()

    @abstractmethod
    def get_base_oscillation_kind(self) -> BaseOscillationKind:
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
