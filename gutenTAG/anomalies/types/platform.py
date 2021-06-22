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
        super().__init__()
        self.value = parameters.value

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        length = anomaly_protocol.end - anomaly_protocol.start
        values = np.zeros(length) + self.value
        anomaly_protocol.subsequences.append(values)
        return anomaly_protocol
