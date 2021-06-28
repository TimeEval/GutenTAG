from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import numpy as np
from typing import Optional, List, Dict

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
    base_oscillation: 'BaseOscillationInterface'
    base_oscillation_kind: BaseOscillationKind
    labels: LabelRange
    subsequences: List[np.ndarray] = field(default_factory=lambda: [])


class BaseAnomaly(ABC):
    def __init__(self):
        self.logger = GutenTagLogger()

    @abstractmethod
    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        return anomaly_protocol

    @staticmethod
    @abstractmethod
    def get_parameter_class():
        raise NotImplementedError()
