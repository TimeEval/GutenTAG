from typing import Optional

import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler

from .interface import BaseOscillationInterface
from ..utils.base_oscillation_kind import BaseOscillationKind
from ..utils.types import BOGenerationContext


def _gen_steps(ctx: BOGenerationContext, length: int) -> np.ndarray:
    steps = ctx.rng.choice([-1., 0., 1.], size=length - 1)
    return np.r_[0, steps].cumsum()


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

        if smoothing:
            filter_size = int(smoothing * length)
            ts = _gen_steps(ctx, length + filter_size - 1)
            gaussian = norm.pdf(np.linspace(-1.5, 1.5, filter_size))
            ts_filter = gaussian / gaussian.sum()
            ts = np.convolve(ts, ts_filter, "valid")
        else:
            ts = _gen_steps(ctx, length)

        return MinMaxScaler(feature_range=[-amplitude, amplitude]).fit_transform(ts.reshape(-1, 1)).reshape(-1)
