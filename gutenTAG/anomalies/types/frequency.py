from __future__ import annotations

from typing import Type
from dataclasses import dataclass

from . import BaseAnomaly, AnomalyProtocol, IsDataclass, LabelRange
from ...utils.types import BaseOscillationKind
from ...utils.logger import GutenTagLogger


@dataclass
class AnomalyFrequencyParameters:
    factor: float = 1.0


class AnomalyFrequency(BaseAnomaly):
    @staticmethod
    def get_parameter_class() -> Type[AnomalyFrequencyParameters]:
        return AnomalyFrequencyParameters

    def __init__(self, parameters: AnomalyFrequencyParameters):
        self.factor = parameters.factor
        self.logger = GutenTagLogger()

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind == BaseOscillationKind.Sinus:
            sinus = anomaly_protocol.base_oscillation
            length = anomaly_protocol.end - anomaly_protocol.start
            subsequence = sinus.generate_only_base(length, sinus.frequency * self.factor * (length / sinus.length)).reshape(-1)
            anomaly_protocol.subsequence = subsequence
            anomaly_protocol.labels.append(LabelRange(start=anomaly_protocol.start, length=length))
        else: #elif anomaly_protocol.base_oscillation_kind == BaseOscillationKind.RandomWalk:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
        return anomaly_protocol
