from dataclasses import dataclass
from typing import Type, Optional

import numpy as np

from . import BaseAnomaly
from .. import AnomalyProtocol
from ...utils.types import BaseOscillationKind


@dataclass
class AnomalyMeanParameters:
    sinusoid_k: Optional[float] = 10.0
    factor: Optional[float] = 10


class AnomalyPattern(BaseAnomaly):
    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind == BaseOscillationKind.Sinus:
            def sinusoid(t: np.ndarray, k: float) -> np.ndarray:
                return np.arctan(k * t) / np.arctan(k)

            sinus = anomaly_protocol.base_oscillation
            subsequence = sinusoid(sinus.timeseries[anomaly_protocol.start:anomaly_protocol.end, anomaly_protocol.channel], self.sinusoid_k)
            anomaly_protocol.subsequences.append(subsequence)
        elif anomaly_protocol.base_oscillation_kind == BaseOscillationKind.RandomWalk:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
        elif anomaly_protocol.base_oscillation_kind == BaseOscillationKind.CylinderBellFunnel:
            cbf = anomaly_protocol.base_oscillation
            subsequence = cbf.generate_only_base(variance_pattern_length=cbf.variance_pattern_length * self.factor).reshape(-1)[anomaly_protocol.start:anomaly_protocol.end]
            anomaly_protocol.subsequences.append(subsequence)
        else:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
        return anomaly_protocol

    @staticmethod
    def get_parameter_class() -> Type[AnomalyMeanParameters]:
        return AnomalyMeanParameters

    def __init__(self, parameters: AnomalyMeanParameters):
        super().__init__()
        self.sinusoid_k = parameters.sinusoid_k
        self.factor = parameters.factor
