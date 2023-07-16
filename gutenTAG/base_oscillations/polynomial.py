from typing import Optional, List

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


class Polynomial(BaseOscillationInterface):
    KIND = BASE_OSCILLATION_NAMES.POLYNOMIAL

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return None

    def generate_only_base(
        self,
        ctx: BOGenerationContext,
        length: Optional[int] = None,
        polynom: Optional[List[float]] = None,
        *args,
        **kwargs
    ) -> np.ndarray:
        length = length or self.length
        polynom = polynom or self.polynomial

        return polynomial(length, polynom)


def polynomial(
    length: int = default_values[BASE_OSCILLATIONS][PARAMETERS.LENGTH],
    polynomial: List[float] = default_values[BASE_OSCILLATIONS][PARAMETERS.POLYNOMIAL],
) -> np.ndarray:
    return np.polynomial.Polynomial(polynomial)(np.arange(length))


BaseOscillation.register(Polynomial.KIND, Polynomial)
