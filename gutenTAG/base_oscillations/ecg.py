import random

import numpy as np
import neurokit2 as nk
from typing import Tuple, Optional

from .interface import BaseOscillationInterface
from ..utils.types import BaseOscillationKind


class ECG(BaseOscillationInterface):
    def get_timeseries_periods(self) -> Optional[int]:
        return int(self.frequency)

    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.ECG

    def generate(self) -> Tuple[np.ndarray, np.ndarray]:
        self.timeseries = self.generate_only_base()
        self._generate_anomalies()
        return self.timeseries, self.labels

    def generate_only_base(self, frequency: Optional[float] = None, heart_rate: Optional[float] = None, *args, **kwargs) -> np.ndarray:
        frequency = int(frequency or self.frequency)
        heart_rate = heart_rate or self.heart_rate
        sampling_rate = self.length // frequency
        ts = []
        for channel in range(self.channels):
            ecg = nk.ecg_simulate(duration=frequency,
                                  sampling_rate=sampling_rate,
                                  heart_rate=heart_rate,
                                  random_state=np.random.get_state()[1][channel],
                                  method='standard')
            ts.append(ecg)
        return np.column_stack(ts)
