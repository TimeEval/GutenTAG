from typing import Optional

import numpy as np

from .interface import BaseOscillationInterface
from .utils.math_func_support import prepare_base_signal, generate_periodic_signal, calc_n_periods
from ..utils.base_oscillation_kind import BaseOscillationKind
from ..utils.types import BOGenerationContext


class Cosine(BaseOscillationInterface):
    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.Cosine

    def get_timeseries_periods(self) -> Optional[int]:
        return calc_n_periods(self.length, self.frequency)

    def generate_only_base(self,
                           ctx: BOGenerationContext,
                           length: Optional[int] = None,
                           frequency: Optional[float] = None,
                           amplitude: Optional[float] = None,
                           freq_mod: Optional[float] = None,
                           *args, **kwargs) -> np.ndarray:
        n: int = length or self.length  # in points
        f: float = frequency or self.frequency  # in Hz
        a: float = amplitude or self.amplitude
        v_freq_mod: float = freq_mod or self.freq_mod  # factor of f

        base_ts = prepare_base_signal(n, f)
        return generate_periodic_signal(base_ts, np.cos, a, v_freq_mod)
