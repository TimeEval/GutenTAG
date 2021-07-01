from dataclasses import dataclass
from typing import Type

from . import BaseAnomaly
from .. import AnomalyProtocol
from ...utils.types import BaseOscillationKind


@dataclass
class AnomalyVarianceParameters:
    variance: float = 0.0


class AnomalyVariance(BaseAnomaly):
    def __init__(self, parameters: AnomalyVarianceParameters):
        super().__init__()
        self.variance = parameters.variance

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        base = anomaly_protocol.base_oscillation
        if anomaly_protocol.base_oscillation_kind == BaseOscillationKind.CylinderBellFunnel:
            subsequence = base.generate_only_base(variance=self.variance, channels=1)[anomaly_protocol.start:anomaly_protocol.end, anomaly_protocol.channel]
            anomaly_protocol.subsequences.append(subsequence)
        else:
            length = anomaly_protocol.end - anomaly_protocol.start
            base.noise[anomaly_protocol.start:anomaly_protocol.end, anomaly_protocol.channel] = base.generate_noise(self.variance * base.amplitude, length, channels=1).reshape(-1)
        return anomaly_protocol

    @staticmethod
    def get_parameter_class() -> Type[AnomalyVarianceParameters]:
        return AnomalyVarianceParameters
