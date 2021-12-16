from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from ...utils.logger import GutenTagLogger
from ...utils.types import BaseOscillationKind


@dataclass
class LabelRange:
    start: int
    length: int


@dataclass
class AnomalyProtocol:
    start: int
    end: int
    channel: int
    base_oscillation: 'BaseOscillationInterface'  # type: ignore # otherwise we have a circular import
    base_oscillation_kind: BaseOscillationKind
    labels: LabelRange
    creep_length: int = 0
    subsequences: List[np.ndarray] = field(default_factory=lambda: [])

    @property
    def length(self) -> int:
        return self.end - self.start

    @property
    def length_without_creep(self) -> int:
        return self.length - self.creep_length


class BaseAnomaly(ABC):
    def __init__(self):
        self.logger = GutenTagLogger()

    @abstractmethod
    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        return anomaly_protocol

    def generate_creep(self, anomaly_protocol: AnomalyProtocol, custom_anomaly_length: Optional[int] = None) -> np.ndarray:
        creep_length = anomaly_protocol.creep_length
        anomaly_length = anomaly_protocol.length_without_creep if custom_anomaly_length is None else custom_anomaly_length
        return np.concatenate([
            np.linspace(0, 1, creep_length),  # creep
            np.ones(anomaly_length)           # anomaly
        ])

    @staticmethod
    @abstractmethod
    def get_parameter_class():
        raise NotImplementedError()
