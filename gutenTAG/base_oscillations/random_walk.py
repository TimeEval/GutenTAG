from typing import Optional

import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler

from .interface import BaseOscillationInterface
from ..utils.base_oscillation_kind import BaseOscillationKind
from ..utils.types import BOGenerationContext


class RandomWalk(BaseOscillationInterface):
    def get_timeseries_periods(self) -> Optional[int]:
        return None

    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.RandomWalk

    def generate_only_base(self,
                           ctx: BOGenerationContext,
                           length: Optional[int] = None,
                           amplitude: Optional[float] = None,
                           smoothing: Optional[float] = None,
                           *args, **kwargs) -> np.ndarray:
        length = length or self.length
        amplitude = amplitude or self.amplitude
        smoothing = smoothing or self.smoothing

        origin = np.zeros(1)
        steps = ctx.rng.choice([-1., 0., 1.], size=length - 1)
        ts = np.concatenate([origin, steps]).cumsum(0)

        if smoothing:
            gaussian = norm.pdf(np.linspace(-1.5, 1.5, int(smoothing * length)))
            filter = gaussian / gaussian.max()
            ts = np.convolve(ts, filter, 'same').reshape(-1, 1)

        return MinMaxScaler(feature_range=[-amplitude, amplitude]).fit_transform(ts / np.abs(ts).max()).reshape(-1)
