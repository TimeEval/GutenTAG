from dataclasses import dataclass
from typing import Type

import numpy as np

from . import BaseAnomaly, AnomalyProtocol


@dataclass
class AnomalyPlatformParameters:
    value: float = 0.0


class AnomalyPlatform(BaseAnomaly):
    def __init__(self, parameters: AnomalyPlatformParameters):
        super().__init__()
        self.value = parameters.value

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        length = anomaly_protocol.end - anomaly_protocol.start
        values = np.zeros(length) + self.value
        anomaly_protocol.subsequences.append(values)
        self.turn_off_trend(anomaly_protocol)
        return anomaly_protocol

    @staticmethod
    def get_parameter_class() -> Type[AnomalyPlatformParameters]:
        return AnomalyPlatformParameters
