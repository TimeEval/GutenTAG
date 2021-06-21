import numpy as np
from dataclasses import dataclass
from typing import Type

from . import BaseAnomaly, AnomalyProtocol


@dataclass
class AnomalyPlatformParameters:
    value: float = 0.0


class AnomalyPlatform(BaseAnomaly):
    @staticmethod
    def get_parameter_class() -> Type[AnomalyPlatformParameters]:
        return AnomalyPlatformParameters

    def __init__(self, parameters: AnomalyPlatformParameters):
        self.value = parameters.value

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        values = np.zeros(anomaly_protocol.end - anomaly_protocol.start) + self.value
        anomaly_protocol.subsequence = values
        return anomaly_protocol
