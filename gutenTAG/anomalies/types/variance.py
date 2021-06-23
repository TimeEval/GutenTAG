from dataclasses import dataclass
from typing import Type

from . import BaseAnomaly
from .. import AnomalyProtocol
from ...utils.types import BaseOscillationKind


@dataclass
class AnomalyVarianceParameters:
    value: float = 0.0


class AnomalyVariance(BaseAnomaly):
    def __init__(self, parameters: AnomalyVarianceParameters):
        super().__init__()
        self.value = parameters.value

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        base = anomaly_protocol.base_oscillation
        length = anomaly_protocol.end - anomaly_protocol.start
        base.noise[anomaly_protocol.start:anomaly_protocol.end, anomaly_protocol.channel] = base.generate_noise(self.value * base.amplitude, length, channels=1).reshape(-1)
        return anomaly_protocol

    @staticmethod
    def get_parameter_class() -> Type[AnomalyVarianceParameters]:
        return AnomalyVarianceParameters
