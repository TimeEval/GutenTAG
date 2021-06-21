from __future__ import annotations

import numpy as np

from . import BaseAnomaly
from .. import AnomalyProtocol
from ...utils.logger import GutenTagLogger
from ...utils.types import BaseOscillationKind


class AnomalyExtremum(BaseAnomaly):
    def __init__(self, factor: float, local: bool = False, context_window: int = 5):
        self.factor = factor
        self.local = local
        self.context_window = context_window
        self.logger = GutenTagLogger()

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind == BaseOscillationKind.Sinus:
            sinus = anomaly_protocol.base_oscillation
            length = anomaly_protocol.end - anomaly_protocol.start
            base: np.ndarray = sinus.generate_only_base()[:length]
            if self.local:
                context = base[:self.context_window]
                extremum = context.max() * self.factor
                min_pos = base.argmin(axis=0)
                base[min_pos] = extremum
            else:
                extremum = sinus.amplitude * self.factor
                base[length // 2] = extremum
            anomaly_protocol.subsequence = base[:, 0]
        else:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
        return anomaly_protocol

    @staticmethod
    def Global(factor: float) -> AnomalyExtremum:
        return AnomalyExtremum(factor, local=False)

    @staticmethod
    def Local(factor: float, context_window: int = 5) -> AnomalyExtremum:
        return AnomalyExtremum(factor, local=True, context_window=context_window)
