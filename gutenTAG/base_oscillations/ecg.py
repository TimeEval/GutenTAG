from typing import Optional

import neurokit2 as nk
import numpy as np

from . import BaseOscillation
from .interface import BaseOscillationInterface
from ..utils.default_values import default_values
from ..utils.global_variables import (
    BASE_OSCILLATION_NAMES,
    BASE_OSCILLATIONS,
    PARAMETERS,
)
from ..utils.types import BOGenerationContext


# we fix the sampling rate to 100 points = 1s
sampling_rate = 100


class ECG(BaseOscillationInterface):
    KIND = BASE_OSCILLATION_NAMES.ECG

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return int(
            (self.length // sampling_rate) * (self.frequency / 100 * sampling_rate)
        )

    def generate_only_base(
        self,
        ctx: BOGenerationContext,
        length: Optional[int] = None,
        frequency: Optional[float] = None,
        amplitude: Optional[float] = None,
        *args,
        **kwargs,
    ) -> np.ndarray:
        length = length or self.length
        frequency = frequency or self.frequency
        amplitude = amplitude or self.amplitude

        return ecg(ctx.rng, length, frequency, amplitude, self.ecg_sim_method)


def ecg(
    rng: np.random.Generator = np.random.default_rng(),
    length: int = default_values[BASE_OSCILLATIONS][PARAMETERS.LENGTH],
    frequency: float = default_values[BASE_OSCILLATIONS][PARAMETERS.FREQUENCY],
    amplitude: float = default_values[BASE_OSCILLATIONS][PARAMETERS.AMPLITUDE],
    ecg_sim_method: str = default_values[BASE_OSCILLATIONS][PARAMETERS.ECG_SIM_METHOD],
) -> np.ndarray:
    duration = length // sampling_rate
    # frequency = beats per 100 points = beats per second
    heart_rate = int(frequency / 100 * sampling_rate * 60)
    ecg = nk.ecg_simulate(
        duration=duration,
        sampling_rate=sampling_rate,
        heart_rate=heart_rate,
        length=length,
        random_state=rng.integers(0, int(1e9)),
        noise=0,
        method=ecg_sim_method,
    )
    return ecg * amplitude


BaseOscillation.register(ECG.KIND, ECG)
