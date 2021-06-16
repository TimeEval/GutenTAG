import numpy as np

from .__base__ import BaseOscillationInterface


class Sinus(BaseOscillationInterface):
    def generate(self) -> np.ndarray:
        end = 2 * np.pi * self.frequency
        base_ts = np.arange(0, end, end / self.length).reshape(self.length, 1)
        base_ts = np.repeat(base_ts, repeats=self.channels, axis=1)
        self.timeseries = np.sin(base_ts) * self.amplitude

        for anomaly in self.anomalies:
            protocol = anomaly.generate(self.timeseries, self.length, self.frequency, "sinus")
            self.timeseries[protocol.start:protocol.end, anomaly.channel] = protocol.subsequence

        return self.timeseries
