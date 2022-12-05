from dataclasses import dataclass
from typing import Type

import numpy as np

from . import BaseAnomaly, AnomalyProtocol
from ...base_oscillations import RandomModeJump


@dataclass
class AnomalyPlatformParameters:
    value: float = 0.0


class AnomalyPlatform(BaseAnomaly):
    def __init__(self, parameters: AnomalyPlatformParameters):
        super().__init__()
        self.value = parameters.value

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind == RandomModeJump.KIND:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind)
            return anomaly_protocol

        length = anomaly_protocol.end - anomaly_protocol.start
        values = np.zeros(length) + self.value
        anomaly_protocol.subsequences.append(values)
        self.turn_off_trend(anomaly_protocol)
        return anomaly_protocol

    @property
    def requires_period_start_position(self) -> bool:
        return False

    @staticmethod
    def get_parameter_class() -> Type[AnomalyPlatformParameters]:
        return AnomalyPlatformParameters
