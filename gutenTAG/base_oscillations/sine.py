from typing import Optional

import numpy as np

from .interface import BaseOscillationInterface
from ..utils.base_oscillation_kind import BaseOscillationKind
from ..utils.types import BOGenerationContext


class Sine(BaseOscillationInterface):
    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.Sine

    def get_timeseries_periods(self) -> Optional[int]:
        return int((self.length / 100) * self.frequency)

    def generate_only_base(self,
                           ctx: BOGenerationContext,
                           length: Optional[int] = None,
                           frequency: Optional[float] = None,
                           amplitude: Optional[float] = None,
                           freq_mod: Optional[float] = None,
                           *args, **kwargs) -> np.ndarray:
        v_length: int = length or self.length
        v_frequency: float = frequency or self.frequency
        v_amplitude: float = amplitude or self.amplitude
        v_freq_mod: float = freq_mod or self.freq_mod

        periods = (v_length / 100) * v_frequency

        end = 2 * np.pi * periods
        base_ts = np.linspace(0, end, v_length)

        arr_amplitude: np.ndarray = np.array(v_amplitude)
        if v_freq_mod:
            arr_amplitude = np.sin(np.linspace(0, end * v_freq_mod, v_length)) * v_amplitude

        return np.sin(base_ts) * arr_amplitude
