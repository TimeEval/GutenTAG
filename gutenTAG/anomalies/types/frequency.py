from __future__ import annotations
from . import BaseAnomaly, AnomalyProtocol
from ...utils.types import BaseOscillationKind
from ...utils.logger import GutenTagLogger


class AnomalyFrequency(BaseAnomaly):
    def __init__(self, factor: float):
        self.factor = factor
        self.logger = GutenTagLogger()

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind == BaseOscillationKind.Sinus:
            sinus = anomaly_protocol.base_oscillation
            length = anomaly_protocol.end - anomaly_protocol.start
            subsequence = sinus.generate_only_base(length, sinus.frequency * self.factor * (length / sinus.length), sinus.amplitude).reshape(-1)
            anomaly_protocol.subsequence = subsequence
        else: #elif anomaly_protocol.base_oscillation_kind == BaseOscillationKind.RandomWalk:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
        return anomaly_protocol
