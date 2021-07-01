from dataclasses import dataclass
from typing import Type

import numpy as np
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
        plateau_length = int(length * 0.8)
        start_transition = norm.pdf(np.linspace(-3, 0, transition_length), scale=1.05)
        amplitude_bell = np.concatenate([start_transition / start_transition.max(), np.ones(plateau_length)])
        amplitude_bell = MinMaxScaler(feature_range=(0, 1)).fit_transform(amplitude_bell.reshape(-1, 1)).reshape(-1)

        self.trend.length = length
        timeseries, _ = self.trend.generate()
        timeseries = timeseries[:, anomaly_protocol.channel]  # use only one channel

        timeseries *= amplitude_bell
        end_point = timeseries[-1]

        anomaly_protocol.base_oscillation.trend_series[anomaly_protocol.start:anomaly_protocol.end, anomaly_protocol.channel] += timeseries
        anomaly_protocol.base_oscillation.trend_series[anomaly_protocol.end:, anomaly_protocol.channel] += end_point

        return anomaly_protocol
