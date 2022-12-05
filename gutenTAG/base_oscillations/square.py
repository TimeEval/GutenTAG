from functools import partial
from typing import Optional

import numpy as np
from scipy import signal

from . import BaseOscillation
from .interface import BaseOscillationInterface
from .utils.math_func_support import prepare_base_signal, generate_periodic_signal, calc_n_periods
from ..utils.global_variables import BASE_OSCILLATION_NAMES
from ..utils.types import BOGenerationContext


class Square(BaseOscillationInterface):
    KIND = BASE_OSCILLATION_NAMES.SQUARE

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return calc_n_periods(self.length, self.frequency)

    def generate_only_base(self,
                           ctx: BOGenerationContext,
                           length: Optional[int] = None,
                           frequency: Optional[float] = None,
                           amplitude: Optional[float] = None,
                           freq_mod: Optional[float] = None,
                           duty: Optional[float] = None,
                           *args, **kwargs) -> np.ndarray:
        n: int = length or self.length  # in points
        f: float = frequency or self.frequency  # in Hz
        a: float = amplitude or self.amplitude
        v_freq_mod: float = freq_mod or self.freq_mod  # factor of f
        v_duty: float = duty or self.duty

        base_ts = prepare_base_signal(n, f)
        func = partial(signal.square, duty=v_duty)
        return generate_periodic_signal(base_ts, func, a, v_freq_mod)


BaseOscillation.register(Square.KIND, Square)
