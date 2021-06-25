import random
from math import ceil

import numpy as np
import neurokit2 as nk
from typing import Tuple, Optional
import signal

from .interface import BaseOscillationInterface
from ..utils.types import BaseOscillationKind


class ECG(BaseOscillationInterface):
    def get_timeseries_periods(self) -> Optional[int]:
        return int((self.length / 100) * self.frequency)

    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.ECG

    def generate(self) -> Tuple[np.ndarray, np.ndarray]:
        self.timeseries = self.generate_only_base()
        self._generate_anomalies()
        return self.timeseries, self.labels

    def generate_only_base(self, frequency: Optional[float] = None, *args, **kwargs) -> np.ndarray:
        frequency = int(frequency or self.frequency)

        periods = (self.length / 100) * frequency
        sampling_rate = ceil(self.length / 10.0)
        ts = []
        for channel in range(self.channels):
            ecg = nk.ecg_simulate(duration=10,
                                  sampling_rate=sampling_rate,
                                  heart_rate=periods*6,
                                  random_state=np.random.get_state()[1][channel],
                                  method='simple')[:self.length]
            ts.append(ecg)
        return np.column_stack(ts)
