import numpy as np
from typing import Optional, List, Tuple

from ..anomalies.types import LabelRange
from ..utils.types import BaseOscillationKind
from .interface import BaseOscillationInterface


class Sinus(BaseOscillationInterface):
    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.Sinus

    def get_timeseries_periods(self) -> Optional[int]:
        return int(self.frequency)

    def generate(self) -> Tuple[np.ndarray, np.ndarray]:
        self.timeseries = self.generate_only_base(self.length, self.frequency, self.amplitude, self.variance, self.channels, self.freq_mod)
        self._generate_anomalies()
        return self.timeseries, self.labels

    def generate_only_base(self,
                           length:    Optional = None,
                           frequency: Optional = None,
                           amplitude: Optional = None,
                           variance:  Optional = None,
                           channels:  Optional = 1,
                           freq_mod: bool = True) -> np.ndarray:
        length = length or self.length
        frequency = frequency or self.frequency
        amplitude = amplitude or self.amplitude
        channels = channels or self.channels

        end = 2 * np.pi * frequency
        base_ts = np.arange(0, end, end / length).reshape(length, 1)
        base_ts = np.repeat(base_ts, repeats=channels, axis=1)

        if freq_mod:
            amplitude = (np.sin(np.linspace(0, end * 0.3, length)) * amplitude).reshape(-1, 1)

        return (np.sin(base_ts) * amplitude)
