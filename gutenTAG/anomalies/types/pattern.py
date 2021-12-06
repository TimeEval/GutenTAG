from dataclasses import dataclass
from typing import Type
from sklearn.preprocessing import MinMaxScaler

import numpy as np

from . import BaseAnomaly
from .. import AnomalyProtocol
from ...utils.types import BaseOscillationKind


@dataclass
class AnomalyPatternParameters:
    sinusoid_k: float = 10.0
    cbf_pattern_factor: float = 2.0


class AnomalyPattern(BaseAnomaly):
    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind == BaseOscillationKind.Sine:
            def sinusoid(t: np.ndarray, k: float, amplitude: float) -> np.ndarray:
                pattern = (np.arctan(k * t) / np.arctan(k))
                scaled = MinMaxScaler(feature_range=(-amplitude, amplitude)).fit_transform(pattern.reshape(-1, 1)).reshape(-1)
                return scaled

            sine = anomaly_protocol.base_oscillation
            subsequence = sinusoid(sine.timeseries[anomaly_protocol.start:anomaly_protocol.end, anomaly_protocol.channel], self.sinusoid_k, sine.amplitude)
            anomaly_protocol.subsequences.append(subsequence)
        elif anomaly_protocol.base_oscillation_kind == BaseOscillationKind.RandomWalk:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
        elif anomaly_protocol.base_oscillation_kind == BaseOscillationKind.CylinderBellFunnel:
            cbf = anomaly_protocol.base_oscillation
            subsequence = cbf.generate_only_base(variance_pattern_length=cbf.variance_pattern_length * self.cbf_pattern_factor)[anomaly_protocol.start:anomaly_protocol.end, anomaly_protocol.channel]
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
    def get_parameter_class() -> Type[AnomalyPatternParameters]:
        return AnomalyPatternParameters

    def __init__(self, parameters: AnomalyPatternParameters):
        super().__init__()
        self.sinusoid_k = parameters.sinusoid_k
        self.cbf_pattern_factor = parameters.cbf_pattern_factor
