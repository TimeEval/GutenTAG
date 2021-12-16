from dataclasses import dataclass
from typing import Type

import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler

from . import BaseAnomaly, AnomalyProtocol
from ...utils.types import BaseOscillationKind


@dataclass
class AnomalyAmplitudeParameters:
    amplitude_factor: float = 1.0


class AnomalyAmplitude(BaseAnomaly):
    @staticmethod
    def get_parameter_class() -> Type[AnomalyAmplitudeParameters]:
        return AnomalyAmplitudeParameters

    def __init__(self, parameters: AnomalyAmplitudeParameters):
        super().__init__()
        self.amplitude_factor = parameters.amplitude_factor

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind == BaseOscillationKind.Polynomial:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
            return anomaly_protocol

        length = anomaly_protocol.end - anomaly_protocol.start
        if anomaly_protocol.creep_length == 0:
            transition_length = int(length * 0.2)
            plateau = np.ones(int(length * 0.6))
            start_transition = norm.pdf(np.linspace(-3, 0, transition_length), scale=1.05)
            end_transition = norm.pdf(np.linspace(0, 3, transition_length), scale=1.05)
            amplitude_bell = np.concatenate([start_transition / start_transition.max(), plateau, end_transition / end_transition.max()])
        else:
            anomaly_length = length - anomaly_protocol.creep_length
            creep = self.generate_creep(anomaly_protocol, custom_anomaly_length=int(anomaly_length * 0.8))
            end_transition = norm.pdf(np.linspace(0, 3, int(anomaly_length * 0.2)), scale=1.05)
            amplitude_bell = np.concatenate([creep, end_transition / end_transition.max()])
        if self.amplitude_factor < 1.0:
            amplitude_bell = MinMaxScaler(feature_range=(1.0, 2.0 - self.amplitude_factor)).fit_transform(amplitude_bell.reshape(-1, 1)).reshape(-1)
            amplitude_bell = amplitude_bell * -1 + 2
        else:
            amplitude_bell = MinMaxScaler(feature_range=(1.0, self.amplitude_factor)).fit_transform(amplitude_bell.reshape(-1, 1)).reshape(-1)

        subsequence = anomaly_protocol.base_oscillation.timeseries[anomaly_protocol.start:anomaly_protocol.end] * amplitude_bell
        anomaly_protocol.subsequences.append(subsequence)
        return anomaly_protocol
