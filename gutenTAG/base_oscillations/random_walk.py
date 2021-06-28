import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, Optional
from scipy.stats import norm

from .interface import BaseOscillationInterface
from ..utils.types import BaseOscillationKind


class RandomWalk(BaseOscillationInterface):
    def get_timeseries_periods(self) -> Optional[int]:
        return None

    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.RandomWalk

    def generate(self) -> Tuple[np.ndarray, np.ndarray]:
        self.timeseries = self.generate_only_base()
        self._generate_anomalies()
        return self.timeseries, self.labels

    def generate_only_base(self, *args, **kwargs) -> np.ndarray:
        origin = np.zeros((1, self.channels))
        steps = np.random.choice([-1., 0., 1.], size=(self.length - 1, self.channels))
        ts = np.concatenate([origin, steps]).cumsum(0)

        if self.smoothing:
            gaussian = norm.pdf(np.linspace(-1.5, 1.5, int(self.smoothing * self.length)))
            filter = gaussian / gaussian.max()
            for ch in range(ts.shape[1]):
                ts[:, ch] = np.convolve(ts[:, ch], filter, 'same')

        return MinMaxScaler(feature_range=[-self.amplitude, self.amplitude]).fit_transform(ts / np.abs(ts).max())
