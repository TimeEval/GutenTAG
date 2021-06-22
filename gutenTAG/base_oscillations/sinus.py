import numpy as np
from typing import Optional, List, Tuple

from ..anomalies.types import LabelRange
from ..utils.types import BaseOscillationKind
from .interface import BaseOscillationInterface


class Sinus(BaseOscillationInterface):
    def generate(self) -> Tuple[np.ndarray, np.ndarray]:
        self.timeseries = self.generate_only_base(self.length, self.frequency, self.amplitude, self.variance, self.channels)
        self.labels = np.zeros(len(self.timeseries), dtype=np.int)
        self._generate_anomalies()
        return self.timeseries, self.labels

    def _generate_anomalies(self):
        label_ranges: List[LabelRange] = []

        protocols = [(anomaly.generate(self, self.frequency, BaseOscillationKind.Sinus), anomaly.channel) for anomaly in self.anomalies]

        for protocol, channel in protocols:
            if len(protocol.subsequences) > 0:
                subsequence = np.vstack(protocol.subsequences).sum(axis=0)
                self.timeseries[protocol.start:protocol.end, channel] = subsequence
            label_ranges.append(protocol.labels)

        self._add_label_ranges_to_labels(label_ranges)
        self.timeseries += self.noise

    def _add_label_ranges_to_labels(self, label_ranges: List[LabelRange]):
        for label_range in label_ranges:
            self.labels[label_range.start:label_range.start + label_range.length] = 1

    def generate_only_base(self,
                           length:    Optional = None,
                           frequency: Optional = None,
                           amplitude: Optional = None,
                           variance:  Optional = None,
                           channels:  Optional = 1) -> np.ndarray:
        length = length or self.length
        frequency = frequency or self.frequency
        amplitude = amplitude or self.amplitude
        channels = channels or self.channels

        end = 2 * np.pi * frequency
        base_ts = np.arange(0, end, end / length).reshape(length, 1)
        base_ts = np.repeat(base_ts, repeats=channels, axis=1)

        return (np.sin(base_ts) * amplitude)
