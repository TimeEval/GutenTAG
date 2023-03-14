from typing import List, Optional, Tuple

import numpy as np

from gutenTAG.anomalies import Anomaly, AnomalyProtocol, LabelRange
from gutenTAG.base_oscillations import BaseOscillationInterface
from gutenTAG.utils.types import GenerationContext


class Consolidator:
    def __init__(self,
                 base_oscillations: List[BaseOscillationInterface],
                 anomalies: List[Anomaly],
                 random_seed: Optional[int] = None):
        self.consolidated_channels: List[BaseOscillationInterface] = base_oscillations
        self.anomalies: List[Anomaly] = anomalies
        self.generated_anomalies: List[Tuple[AnomalyProtocol, int]] = []
        self.timeseries: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None
        self.random_seed: Optional[int] = random_seed

    def add_channel(self, channel: BaseOscillationInterface):
        self.consolidated_channels.append(channel)

    def get_channel(self, channel: int) -> BaseOscillationInterface:
        return self.consolidated_channels[channel]

    def generate(self, ctx: GenerationContext) -> Tuple[np.ndarray, np.ndarray]:
        channels: List[np.ndarray] = []
        for c, bo in enumerate(self.consolidated_channels):
            bo.generate_timeseries_and_variations(ctx.to_bo(c, channels))  # type: ignore  # timeseries gets set in generate_timeseries_and_variations()
            if bo.timeseries is not None:
                channels.append(bo.timeseries)
        self.timeseries = self._stack_channels(channels)
        self.labels = np.zeros(self.timeseries.shape[0], dtype=np.int8)
        self.generate_anomalies(ctx)

        self.apply_anomalies()
        self.apply_variations()
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

    def generate_anomalies(self, ctx: GenerationContext):
        positions: List[Tuple[int, int]] = []
        for anomaly in self.anomalies:
            current_base_oscillation = self.consolidated_channels[anomaly.channel]
            anomaly_protocol = anomaly.generate(ctx.to_anomaly(current_base_oscillation, positions))
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
