from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from typing import Optional


@dataclass
class AnomalyProtocol:
    start: int
    end: int
    values: np.ndarray
    subsequence: Optional[np.ndarray] = None


class BaseAnomaly(ABC):
    @abstractmethod
    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        return anomaly_protocol
