from typing import Optional

import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler

from . import BaseOscillation
from .interface import BaseOscillationInterface
from ..utils.default_values import default_values
from ..utils.global_variables import BASE_OSCILLATION_NAMES, BASE_OSCILLATIONS, PARAMETERS
from ..utils.types import BOGenerationContext


class RandomWalk(BaseOscillationInterface):
    KIND = BASE_OSCILLATION_NAMES.RANDOM_WALK

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return None

    def generate_only_base(self,
                           ctx: BOGenerationContext,
                           length: Optional[int] = None,
                           amplitude: Optional[float] = None,
                           smoothing: Optional[float] = None,
                           *args, **kwargs) -> np.ndarray:
        length = length or self.length
        amplitude = amplitude or self.amplitude
        smoothing = smoothing or self.smoothing

        return random_walk(ctx.rng, length, amplitude, smoothing)


def _gen_steps(rng: np.random.Generator, length: int) -> np.ndarray:
    steps = rng.choice([-1., 0., 1.], size=length - 1)
    return np.r_[0, steps].cumsum()


def random_walk(rng: np.random.Generator = np.random.default_rng(),
                length: int = default_values[BASE_OSCILLATIONS][PARAMETERS.LENGTH],
                amplitude: float = default_values[BASE_OSCILLATIONS][PARAMETERS.AMPLITUDE],
                smoothing: float = default_values[BASE_OSCILLATIONS][PARAMETERS.SMOOTHING]) -> np.ndarray:
    if smoothing:
        filter_size = int(smoothing * length)
        ts = _gen_steps(rng, length + filter_size - 1)
        gaussian = norm.pdf(np.linspace(-1.5, 1.5, filter_size))
        ts_filter = gaussian / gaussian.sum()
        ts = np.convolve(ts, ts_filter, "valid")
    else:
        ts = _gen_steps(rng, length)

    return MinMaxScaler(feature_range=(-amplitude, amplitude)).fit_transform(ts.reshape(-1, 1)).reshape(-1)


BaseOscillation.register(RandomWalk.KIND, RandomWalk)