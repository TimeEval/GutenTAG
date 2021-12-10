from typing import List, Optional, Tuple

import numpy as np

from gutenTAG.anomalies import AnomalyProtocol, LabelRange, Anomaly
from gutenTAG.base_oscillations.interface import BaseOscillationInterface


class Consolidator:
    def __init__(self, base_oscillations: List[BaseOscillationInterface], anomalies: List[Anomaly]):
        self.consolidated_channels: List[BaseOscillationInterface] = base_oscillations
        self.anomalies: List[Anomaly] = anomalies
        self.generated_anomalies: List[Tuple[AnomalyProtocol, int]] = []
        self.timeseries: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None

    def add_channel(self, channel: BaseOscillationInterface):
        self.consolidated_channels.append(channel)

    def get_channel(self, channel: int) -> BaseOscillationInterface:
        return self.consolidated_channels[channel]

    def generate(self) -> Tuple[np.ndarray, np.ndarray]:
        channels: List[np.ndarray] = []
        for c, bo in enumerate(self.consolidated_channels):
            bo.generate_timeseries_and_variations(c, prev_channels=channels)  # type: ignore  # timeseries gets set in generate_timeseries_and_variations()
            if bo.timeseries is not None:
                channels.append(bo.timeseries)
        self.timeseries = self._stack_channels(channels)
        self.labels = np.zeros(self.timeseries.shape[0], dtype=np.int8)
        self.generate_anomalies()

        self.apply_variations()
        self.apply_anomalies()
        return self.timeseries, self.labels

    def apply_variations(self):
        for c, bo in enumerate(self.consolidated_channels):
            self.timeseries[:, c] += bo.noise + bo.trend_series + bo.offset

    def apply_anomalies(self):
        label_ranges: List[LabelRange] = []
        for (protocol, channel) in self.generated_anomalies:
            if len(protocol.subsequences) > 0:
                subsequence = np.vstack(protocol.subsequences).sum(axis=0)
                self.timeseries[protocol.start:protocol.end, channel] = subsequence
            label_ranges.append(protocol.labels)

        self._add_label_ranges_to_labels(label_ranges)

    def generate_anomalies(self):
        positions: List[Tuple[int, int]] = []
        for anomaly in self.anomalies:
            current_base_oscillation = self.consolidated_channels[anomaly.channel]
            anomaly_protocol = anomaly.generate(current_base_oscillation,
                                                current_base_oscillation.get_timeseries_periods(),
                                                current_base_oscillation.get_base_oscillation_kind(),
                                                positions)
            positions.append((anomaly_protocol.start, anomaly_protocol.end))
            self.generated_anomalies.append((anomaly_protocol, anomaly.channel))


    def _stack_channels(self, channels: List[np.ndarray]) -> np.ndarray:
        assert all([len(x.shape) == 1 for x in channels]), "The resulting channels have the wrong shape. Correct shape: `(l, d)`."
        return np.vstack(channels).transpose()

    def _add_label_ranges_to_labels(self, label_ranges: List[LabelRange]):
        if self.labels is not None:
            for label_range in label_ranges:
                self.labels[label_range.start:label_range.start + label_range.length] = 1
        else:
            raise AssertionError("You cannot run this method before initializing the `labels` field!")
