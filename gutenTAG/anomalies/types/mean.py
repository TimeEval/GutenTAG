from dataclasses import dataclass
from typing import Type
import numpy as np

from . import BaseAnomaly
from .. import AnomalyProtocol


@dataclass
class AnomalyMeanParameters:
    offset: float = 0.0


class AnomalyMean(BaseAnomaly):
    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        base = anomaly_protocol.base_oscillation
        ts: np.ndarray = base.timeseries
        subsequence = ts[anomaly_protocol.start:anomaly_protocol.end, anomaly_protocol.channel] + self.offset
        anomaly_protocol.subsequences.append(subsequence)
        return anomaly_protocol

    @staticmethod
    def get_parameter_class() -> Type[AnomalyMeanParameters]:
        return AnomalyMeanParameters

    def __init__(self, parameters: AnomalyMeanParameters):
        super().__init__()
        self.offset = parameters.offset
