from __future__ import annotations
from dataclasses import dataclass
from typing import Type
import numpy as np

from . import BaseAnomaly, IsDataclass
from .. import AnomalyProtocol
from ...utils.logger import GutenTagLogger
from ...utils.types import BaseOscillationKind


@dataclass
class AnomalyExtremumParameters:
    min: bool = False
    local: bool = False
    context_window: int = 5


class AnomalyExtremum(BaseAnomaly):
    @staticmethod
    def get_parameter_class() -> Type[AnomalyExtremumParameters]:
        return AnomalyExtremumParameters

    def __init__(self, parameters: AnomalyExtremumParameters):
        self.min = parameters.min
        self.local = parameters.local
        self.context_window = parameters.context_window
        self.logger = GutenTagLogger()

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind == BaseOscillationKind.Sinus:
            sinus = anomaly_protocol.base_oscillation
            length = anomaly_protocol.end - anomaly_protocol.start
            base: np.ndarray = sinus.generate_only_base()
            if self.local:
                base = base[anomaly_protocol.start:anomaly_protocol.end]
                context = base[:self.context_window]
                diff = context.max() - context.min()
                extremum = np.random.rand() * diff
                min_pos = base.argmin(axis=0)
                base[min_pos] += extremum
            else:
                diff = base.max() - base.min()
                extremum = (np.random.rand() + 0.5) * diff
                base = base[anomaly_protocol.start:anomaly_protocol.end]
                base[length // 2] += extremum
            anomaly_protocol.subsequence = base[:, 0]
        else:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
        return anomaly_protocol
