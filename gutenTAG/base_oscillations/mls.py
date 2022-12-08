from typing import Optional

import numpy as np
from scipy import signal
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler

from . import BaseOscillation
from .interface import BaseOscillationInterface
from .utils.math_func_support import SAMPLING_F
from ..utils.global_variables import BASE_OSCILLATION_NAMES
from ..utils.types import BOGenerationContext


class MLS(BaseOscillationInterface):
    KIND = BASE_OSCILLATION_NAMES.MLS

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return self.length // (2 ** self.complexity - 1)

    def get_period_size(self) -> Optional[int]:
        return 2 ** self.complexity - 1

    def generate_only_base(self,
                           ctx: BOGenerationContext,
                           length: Optional[int] = None,
                           amplitude: Optional[float] = None,
                           smoothing: Optional[float] = None,
                           complexity: Optional[int] = None,
                           *args, **kwargs) -> np.ndarray:
        n: int = length or self.length  # in points
        a: float = amplitude or self.amplitude
        v_smoothing: float = smoothing or self.smoothing
        v_complexity: int = complexity or self.complexity

        assert 1 < v_complexity < 16, "Complexity should be between 1 and 16 inclusive!"

        taps = ctx.rng.integers(1, v_complexity, endpoint=True, size=ctx.rng.integers(1, 3))
        state = np.r_[1, ctx.rng.integers(0, 1, endpoint=True, size=v_complexity - 1, dtype=np.int8)]
        period_size = 2 ** v_complexity - 1
        print("period length", period_size)
        print("N periods", n // period_size)
        if v_smoothing is not None and v_smoothing > 0:
            filter_size = int(v_smoothing * SAMPLING_F)
            new_n = n + filter_size - 1
            gaussian = norm.pdf(np.linspace(-1.5, 1.4, filter_size))
            gaussian = gaussian / gaussian.sum()
            data = signal.max_len_seq(nbits=v_complexity, state=state, taps=taps)[0] * 2 - 1
            data = data.cumsum()
            data = np.tile(data, (new_n // data.shape[0]) + 1)[:new_n]
            data = np.convolve(data, gaussian, "valid")
        else:
            data = signal.max_len_seq(nbits=v_complexity, state=state, taps=taps)[0] * 2 - 1
            data = data.cumsum()
            data = np.tile(data, (n // data.shape[0]) + 1)[:n]

        data = MinMaxScaler((-a, a)).fit_transform(data.reshape(-1, 1)).reshape(-1)
        return data


BaseOscillation.register(MLS.KIND, MLS)
