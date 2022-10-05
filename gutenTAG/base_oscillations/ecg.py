from typing import Optional

import neurokit2 as nk
import numpy as np

from .interface import BaseOscillationInterface
from ..utils.base_oscillation_kind import BaseOscillationKind
from ..utils.types import BOGenerationContext

# we fix the sampling rate to 100 points = 1s
sampling_rate = 100


class ECG(BaseOscillationInterface):
    def get_timeseries_periods(self) -> Optional[int]:
        return int((self.length // sampling_rate) * (self.frequency / 100 * sampling_rate))

    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.ECG

    def generate_only_base(self,
                           ctx: BOGenerationContext,
                           length: Optional[int] = None,
                           frequency: Optional[float] = None,
                           amplitude: Optional[float] = None,
                           *args, **kwargs) -> np.ndarray:
        length = length or self.length
        frequency = frequency or self.frequency
        amplitude = amplitude or self.amplitude

        duration = length // sampling_rate
        # frequency = beats per 100 points = beats per second
        heart_rate = frequency / 100 * sampling_rate * 60

        ecg = nk.ecg_simulate(duration=duration,
                              sampling_rate=sampling_rate,
                              heart_rate=heart_rate,
                              length=length,
                              random_state=ctx.rng.integers(0, int(1e9)),
                              noise=0,
                              method=self.ecg_sim_method)
        return ecg * amplitude
