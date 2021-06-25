import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from typing import Type, Dict
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler

from . import BaseAnomaly, AnomalyProtocol


@dataclass
class AnomalyTrendParameters:
    trend: 'BaseOscillationInterface'


class AnomalyTrend(BaseAnomaly):
    @staticmethod
    def get_parameter_class() -> Type[AnomalyTrendParameters]:
        return AnomalyTrendParameters

    def __init__(self, parameters: AnomalyTrendParameters):
        super().__init__()
        self.trend = parameters.trend

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        length = anomaly_protocol.end - anomaly_protocol.start
        transition_length = int(length * 0.2)
        plateau_length = int(length * 0.6)
        start_transition = norm.pdf(np.linspace(-3, 0, transition_length), scale=1.05)
        end_transition = norm.pdf(np.linspace(0, 3, transition_length), scale=1.05)
        amplitude_bell = np.concatenate([start_transition / start_transition.max(), np.ones(plateau_length), end_transition / end_transition.max()])
        amplitude_bell = MinMaxScaler(feature_range=(0,1)).fit_transform(amplitude_bell.reshape(-1, 1)).reshape(-1)

        timeseries, _ = self.trend.generate()
        timeseries = timeseries[:length, 0] * amplitude_bell

        anomaly_protocol.base_oscillation.trend_series[anomaly_protocol.start:anomaly_protocol.end, anomaly_protocol.channel] += timeseries

        return anomaly_protocol
