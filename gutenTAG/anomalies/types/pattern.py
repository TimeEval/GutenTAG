from dataclasses import dataclass
from typing import Type
from sklearn.preprocessing import MinMaxScaler

import numpy as np

from . import BaseAnomaly
from .. import AnomalyProtocol
from ...utils.types import BaseOscillationKind


@dataclass
class AnomalyMeanParameters:
    sinusoid_k: float = 10.0


class AnomalyPattern(BaseAnomaly):
    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind == BaseOscillationKind.Sinus:
            def sinusoid(t: np.ndarray, k: float, amplitude: float) -> np.ndarray:
                pattern = (np.arctan(k * t) / np.arctan(k))
                scaled = MinMaxScaler(feature_range=(-amplitude, amplitude)).fit_transform(pattern.reshape(-1, 1)).reshape(-1)
                return scaled

            sinus = anomaly_protocol.base_oscillation
            subsequence = sinusoid(sinus.timeseries[anomaly_protocol.start:anomaly_protocol.end, anomaly_protocol.channel], self.sinusoid_k, sinus.amplitude)
            anomaly_protocol.subsequences.append(subsequence)
        elif anomaly_protocol.base_oscillation_kind == BaseOscillationKind.RandomWalk:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
        elif anomaly_protocol.base_oscillation_kind == BaseOscillationKind.CylinderBellFunnel:
            cbf = anomaly_protocol.base_oscillation
            subsequence = cbf.generate_only_base(variance_pattern_length=cbf.variance_pattern_length * self.factor).reshape(-1)[anomaly_protocol.start:anomaly_protocol.end]
            anomaly_protocol.subsequences.append(subsequence)
        elif anomaly_protocol.base_oscillation_kind == BaseOscillationKind.ECG:
            ecg = anomaly_protocol.base_oscillation
            length = anomaly_protocol.end - anomaly_protocol.start
            window = int(length * 0.05)

            for slide in range(-3, 3):
                start = ecg.timeseries[anomaly_protocol.start+slide:anomaly_protocol.start+window, anomaly_protocol.channel]
                if np.argmax(start) == 0:
                    break
            else:
                slide = 0

            subsequence = ecg.timeseries[anomaly_protocol.start + slide:anomaly_protocol.end + slide, anomaly_protocol.channel][::-1]
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
