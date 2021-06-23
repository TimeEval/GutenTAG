from __future__ import annotations
from dataclasses import dataclass
from typing import Type
import numpy as np

from . import BaseAnomaly
from .. import AnomalyProtocol
from ...utils.types import BaseOscillationKind


@dataclass
class AnomalyExtremumParameters:
    min: bool = False
    local: bool = False
    context_window: int = 10


class AnomalyExtremum(BaseAnomaly):
    @staticmethod
    def get_parameter_class() -> Type[AnomalyExtremumParameters]:
        return AnomalyExtremumParameters

    def __init__(self, parameters: AnomalyExtremumParameters):
        super().__init__()
        self.min = parameters.min
        self.local = parameters.local
        self.context_window = parameters.context_window

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        bo = anomaly_protocol.base_oscillation
        length = anomaly_protocol.end - anomaly_protocol.start
        base: np.ndarray = bo.timeseries
        if self.local:
            base = base[anomaly_protocol.start - self.context_window:anomaly_protocol.end + self.context_window]
            diff = base.max() - base.min()
            extremum = np.random.rand() * diff
            pos = self.context_window
            if self.min:
                base[pos] -= extremum
            else:
                base[pos] += extremum
        else:
            diff = base.max() - base.min()
            extremum = (np.random.rand() + 0.5) * diff
            base = base[anomaly_protocol.start:anomaly_protocol.end]
            pos = length // 2
            if self.min:
                base[pos] -= extremum
            else:
                base[pos] += extremum
        anomaly_protocol.subsequences.append(base[[pos], 0])
        return anomaly_protocol
