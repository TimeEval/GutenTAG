from __future__ import annotations

from typing import Type
from dataclasses import dataclass

from . import BaseAnomaly, AnomalyProtocol
from ...utils.types import BaseOscillationKind


@dataclass
class AnomalyFrequencyParameters:
    factor: float = 1.0


class AnomalyFrequency(BaseAnomaly):
    @staticmethod
    def get_parameter_class() -> Type[AnomalyFrequencyParameters]:
        return AnomalyFrequencyParameters

    def __init__(self, parameters: AnomalyFrequencyParameters):
        super().__init__()
        self.factor = parameters.factor

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind == BaseOscillationKind.Sinus:
            sinus = anomaly_protocol.base_oscillation
            length = anomaly_protocol.end - anomaly_protocol.start
            subsequence = sinus.generate_only_base(length, sinus.frequency * self.factor * (length / sinus.length)).reshape(-1)
            anomaly_protocol.subsequences.append(subsequence)
        elif anomaly_protocol.base_oscillation_kind == BaseOscillationKind.RandomWalk:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
        else:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
        return anomaly_protocol
