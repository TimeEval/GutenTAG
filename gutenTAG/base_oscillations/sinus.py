from typing import Optional, Tuple

import numpy as np

from .interface import BaseOscillationInterface
from ..utils.types import BaseOscillationKind


class Sinus(BaseOscillationInterface):
    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.Sinus

    def get_timeseries_periods(self) -> Optional[int]:
        return int((self.length / 100) * self.frequency)

    def generate(self) -> Tuple[np.ndarray, np.ndarray]:
        self.timeseries = self.generate_only_base(self.length, self.frequency, self.amplitude, self.variance, self.channels, self.freq_mod)
        self._generate_anomalies()
        return self.timeseries, self.labels

    def generate_only_base(self,
                           length:    Optional[int] = None,
                           frequency: Optional[float] = None,
                           amplitude: Optional[float] = None,
                           variance:  Optional[float] = None,
                           channels:  Optional[int] = None,
                           freq_mod: float = .0) -> np.ndarray:
        length = length or self.length
        frequency = frequency or self.frequency
        amplitude = amplitude or self.amplitude
        channels = channels or self.channels

        periods = (length / 100) * frequency

        end = 2 * np.pi * periods
        base_ts = np.linspace(0, end, length).reshape(length, 1)
        base_ts = np.repeat(base_ts, repeats=channels, axis=1)

        if freq_mod:
            amplitude = (np.sin(np.linspace(0, end * freq_mod, length)) * amplitude).reshape(-1, 1)

        return np.sin(base_ts) * amplitude
