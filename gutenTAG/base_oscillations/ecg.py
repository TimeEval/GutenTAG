from typing import Optional

import neurokit2 as nk
import numpy as np

from .interface import BaseOscillationInterface
from ..utils.types import BOGenerationContext
from gutenTAG.utils.base_oscillation_kind import BaseOscillationKind


class ECG(BaseOscillationInterface):
    def get_timeseries_periods(self) -> Optional[int]:
        return int((self.length / 100) * self.frequency)

    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.ECG

    def generate_only_base(self,
                           ctx: BOGenerationContext,
                           length: Optional[int] = None,
                           frequency: Optional[float] = None,
                           *args, **kwargs) -> np.ndarray:
        length = length or self.length
        frequency = int(frequency or self.frequency)

        periods = (length / 100) * frequency
        sampling_rate = np.ceil(length / 10.0)
        ecg = nk.ecg_simulate(duration=10,
                              sampling_rate=sampling_rate,
                              heart_rate=periods * 6,
                              random_state=ctx.rng.integers(0, 1e9),
                              method="simple")[:length]
        return ecg
