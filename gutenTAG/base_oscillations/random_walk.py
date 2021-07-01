from typing import Optional

import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler

from .interface import BaseOscillationInterface
from ..utils.types import BaseOscillationKind


class RandomWalk(BaseOscillationInterface):
    def get_timeseries_periods(self) -> Optional[int]:
        return None

    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.RandomWalk

    def generate_only_base(self,
                           length: Optional[int] = None,
                           amplitude: Optional[float] = None,
                           channels: Optional[int] = None,
                           smoothing: Optional[float] = None,
                           *args, **kwargs) -> np.ndarray:
        length = length or self.length
        amplitude = amplitude or self.amplitude
        channels = channels or self.channels
        smoothing = smoothing or self.smoothing

        origin = np.zeros((1, channels))
        steps = np.random.choice([-1., 0., 1.], size=(length - 1, channels))
        ts = np.concatenate([origin, steps]).cumsum(0)

        if smoothing:
            gaussian = norm.pdf(np.linspace(-1.5, 1.5, int(smoothing * length)))
            filter = gaussian / gaussian.max()
            for ch in range(ts.shape[1]):
                ts[:, ch] = np.convolve(ts[:, ch], filter, 'same')

        return MinMaxScaler(feature_range=[-amplitude, amplitude]).fit_transform(ts / np.abs(ts).max())
