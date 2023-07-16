from functools import partial
from typing import Optional

import numpy as np
import scipy.special

from . import BaseOscillation
from .interface import BaseOscillationInterface
from .utils.math_func_support import (
    prepare_base_signal,
    generate_periodic_signal,
    calc_n_periods,
)
from ..utils.default_values import default_values
from ..utils.global_variables import (
    BASE_OSCILLATION_NAMES,
    BASE_OSCILLATIONS,
    PARAMETERS,
)
from ..utils.types import BOGenerationContext


class Dirichlet(BaseOscillationInterface):
    KIND = BASE_OSCILLATION_NAMES.DIRICHLET

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return calc_n_periods(self.length, self.frequency) // (
            (self.periodicity % 2 == 0) + 1
        )

    def generate_only_base(
        self,
        ctx: BOGenerationContext,
        length: Optional[int] = None,
        frequency: Optional[float] = None,
        amplitude: Optional[float] = None,
        freq_mod: Optional[float] = None,
        periodicity: Optional[float] = None,
        *args,
        **kwargs
    ) -> np.ndarray:
        n: int = length or self.length  # in points
        f: float = frequency or self.frequency  # in Hz
        a: float = amplitude or self.amplitude
        p: float = periodicity or self.periodicity

        return dirichlet(n, f, a, p)


def dirichlet(
    length: int = default_values[BASE_OSCILLATIONS][PARAMETERS.LENGTH],
    frequency: float = default_values[BASE_OSCILLATIONS][PARAMETERS.COMPLEXITY],
    amplitude: float = default_values[BASE_OSCILLATIONS][PARAMETERS.AMPLITUDE],
    periodicity: float = default_values[BASE_OSCILLATIONS][PARAMETERS.PERIODICITY],
) -> np.ndarray:
    assert (
        periodicity > 1
    ), "periodicity must be > 1, otherwise the dirichlet wave collapses"
    base_ts = prepare_base_signal(length, frequency)
    func = partial(scipy.special.diric, n=periodicity)
    return generate_periodic_signal(base_ts, func, amplitude)


BaseOscillation.register(Dirichlet.KIND, Dirichlet)
