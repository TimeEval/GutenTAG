from dataclasses import dataclass
from typing import Type

import numpy as np

from . import BaseAnomaly
from .. import AnomalyProtocol


@dataclass
class AnomalyExtremumParameters:
    min: bool = False
    local: bool = False
    context_window: int = 10


class AnomalyExtremum(BaseAnomaly):
    def __init__(self, parameters: AnomalyExtremumParameters):
        super().__init__()
        self.min = parameters.min
        self.local = parameters.local
        self.context_window = parameters.context_window

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        length = anomaly_protocol.end - anomaly_protocol.start
        if length != 1:
            self.logger.logger.warn(f"Extremum anomaly can only have a length of 1 (was set to {length})! Ignoring.")
            anomaly_protocol.end = anomaly_protocol.start + 1
            anomaly_protocol.labels.length = 1

        base: np.ndarray = anomaly_protocol.base_oscillation.timeseries
        if self.local:
            context_start = max(anomaly_protocol.start - self.context_window//2, 0)
            context_end = min(anomaly_protocol.end + self.context_window//2, base.shape[0])
            context = base[context_start:context_end]
            diff = context.max() - context.min()
            extremum = anomaly_protocol.rng.random() * diff
        else:
            diff = base.max() - base.min()
            extremum = (anomaly_protocol.rng.random() + 0.5) * diff

        # let extremum be significant enough to be distinguishable from noise
        max_noise: float = np.max(np.abs(anomaly_protocol.base_oscillation.noise))
        if extremum < 2*max_noise:
            extremum += 2*max_noise

        if self.min:
            value = base[anomaly_protocol.start] - extremum
        else:
            value = base[anomaly_protocol.start] + extremum
        anomaly_protocol.subsequences.append(np.array([value]))
        return anomaly_protocol

    @property
    def requires_period_start_position(self) -> bool:
        return False

    @staticmethod
    def get_parameter_class() -> Type[AnomalyExtremumParameters]:
        return AnomalyExtremumParameters
