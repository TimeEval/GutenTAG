import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from typing import Type
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler

from . import BaseAnomaly, AnomalyProtocol


@dataclass
class AnomalyAmplitudeParameters:
    factor: float = 1.0


class AnomalyAmplitude(BaseAnomaly):
    @staticmethod
    def get_parameter_class() -> Type[AnomalyAmplitudeParameters]:
        return AnomalyAmplitudeParameters

    def __init__(self, parameters: AnomalyAmplitudeParameters):
        super().__init__()
        self.factor = parameters.factor

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        length = anomaly_protocol.end - anomaly_protocol.start
        transition_length = int(length * 0.2)
        plateau_length = int(length * 0.6)
        start_transition = norm.pdf(np.linspace(-3, 0, transition_length), scale=1.05)
        end_transition = norm.pdf(np.linspace(0, 3, transition_length), scale=1.05)
        amplitude_bell = np.concatenate([start_transition / start_transition.max(), np.ones(plateau_length), end_transition / end_transition.max()])
        if self.factor < 1.0:
            amplitude_bell = MinMaxScaler(feature_range=(1.0, 2.0 - self.factor)).fit_transform(amplitude_bell.reshape(-1, 1)).reshape(-1)
            amplitude_bell = amplitude_bell * -1 + 2
        else:
            amplitude_bell = MinMaxScaler(feature_range=(1.0, self.factor)).fit_transform(amplitude_bell.reshape(-1, 1)).reshape(-1)

        subsequence = anomaly_protocol.base_oscillation.timeseries[anomaly_protocol.start:anomaly_protocol.end, anomaly_protocol.channel] * amplitude_bell
        anomaly_protocol.subsequences.append(subsequence)
        return anomaly_protocol
