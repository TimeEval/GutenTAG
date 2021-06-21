from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from typing import Optional

from ...utils.types import BaseOscillationKind


@dataclass
class AnomalyProtocol:
    start: int
    end: int
    base_oscillation: 'BaseOscillationInterface'
    base_oscillation_kind: BaseOscillationKind
    subsequence: Optional[np.ndarray] = None


class BaseAnomaly(ABC):
    @abstractmethod
    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        return anomaly_protocol
