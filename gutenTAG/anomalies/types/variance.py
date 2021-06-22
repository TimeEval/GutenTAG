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
        if anomaly_protocol.base_oscillation_kind == BaseOscillationKind.Sinus:
            sinus = anomaly_protocol.base_oscillation
            length = anomaly_protocol.end - anomaly_protocol.start
            sinus.noise[anomaly_protocol.start:anomaly_protocol.end] = sinus.generate_noise(self.value, length)
        else:  # elif anomaly_protocol.base_oscillation_kind == BaseOscillationKind.RandomWalk:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
        return anomaly_protocol

    @staticmethod
    def get_parameter_class() -> Type[AnomalyVarianceParameters]:
        return AnomalyVarianceParameters
