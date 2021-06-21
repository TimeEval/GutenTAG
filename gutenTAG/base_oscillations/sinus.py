import numpy as np
from typing import Optional

from ..utils.types import BaseOscillationKind
from .interface import BaseOscillationInterface


class Sinus(BaseOscillationInterface):
    def generate(self) -> np.ndarray:
        self.timeseries = self.generate_only_base(self.length, self.frequency, self.amplitude, self.channels)

        for anomaly in self.anomalies:
            protocol = anomaly.generate(self, self.frequency, BaseOscillationKind.Sinus)
            self.timeseries[protocol.start:protocol.end, anomaly.channel] = protocol.subsequence

        return self.timeseries

    def generate_only_base(self, length: Optional = None, frequency: Optional = None, amplitude: Optional = None, channels: Optional = 1) -> np.ndarray:
        length = length or self.length
        frequency = frequency or self.frequency
        amplitude = amplitude or self.amplitude
        channels = channels or self.channels

        end = 2 * np.pi * frequency
        base_ts = np.arange(0, end, end / length).reshape(length, 1)
        base_ts = np.repeat(base_ts, repeats=channels, axis=1)
        return np.sin(base_ts) * amplitude
