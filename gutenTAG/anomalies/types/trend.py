from dataclasses import dataclass
from typing import Type

import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler

from . import BaseAnomaly, AnomalyProtocol


@dataclass
class AnomalyTrendParameters:
    trend: 'BaseOscillationInterface'  # type: ignore # otherwise we have a circular import


class AnomalyTrend(BaseAnomaly):
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
        self.trend.generate_timeseries_and_variations(anomaly_protocol.ctx.to_bo())
        timeseries = self.trend.timeseries

        timeseries *= amplitude_bell
        end_point = timeseries[-1]

        anomaly_protocol.base_oscillation.trend_series[anomaly_protocol.start:anomaly_protocol.end] += timeseries
        anomaly_protocol.base_oscillation.trend_series[anomaly_protocol.end:] += end_point

        return anomaly_protocol

    @property
    def requires_period_start_position(self) -> bool:
        return False

    @staticmethod
    def get_parameter_class() -> Type[AnomalyTrendParameters]:
        return AnomalyTrendParameters
