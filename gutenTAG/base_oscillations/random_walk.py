import numpy as np
from sklearn.preprocessing import MinMaxScaler

from ..utils.types import BaseOscillationKind
from .interface import BaseOscillationInterface


class RandomWalk(BaseOscillationInterface):
    def generate(self) -> np.ndarray:
        self.timeseries = self.generate_only_base()

        for anomaly in self.anomalies:
            protocol = anomaly.generate(self, self.frequency, BaseOscillationKind.RandomWalk)
            self.timeseries[protocol.start:protocol.end, anomaly.channel] = protocol.subsequences

        return self.timeseries

    def generate_only_base(self, *args, **kwargs) -> np.ndarray:
        origin = np.zeros((1, self.channels))
        steps = np.random.choice([-1., 0., 1.], size=(self.length, self.channels))
        ts = np.concatenate([origin, steps]).cumsum(0)
        return MinMaxScaler(feature_range=[-self.amplitude, self.amplitude]).fit_transform(ts / np.abs(ts).max())
