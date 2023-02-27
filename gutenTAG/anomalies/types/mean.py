from dataclasses import dataclass
from typing import Type

import numpy as np

from . import BaseAnomaly
from .. import AnomalyProtocol
from ...base_oscillations import RandomModeJump


@dataclass
class AnomalyMeanParameters:
    offset: float = 0.0


class AnomalyMean(BaseAnomaly):
    def __init__(self, parameters: AnomalyMeanParameters):
        super().__init__()
        self.offset = parameters.offset

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind == RandomModeJump.KIND:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind)
            return anomaly_protocol

        base = anomaly_protocol.base_oscillation
        ts: np.ndarray = base.timeseries
        creeping = self.generate_creeping(anomaly_protocol)
        subsequence = ts[anomaly_protocol.start:anomaly_protocol.end] + self.offset * creeping
        anomaly_protocol.subsequences.append(subsequence)
        return anomaly_protocol

    @property
    def requires_period_start_position(self) -> bool:
        return False

    @staticmethod
    def get_parameter_class() -> Type[AnomalyMeanParameters]:
        return AnomalyMeanParameters
