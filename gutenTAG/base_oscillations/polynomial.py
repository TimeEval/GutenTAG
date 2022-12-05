from typing import Optional, List

import numpy as np

from . import BaseOscillation
from .interface import BaseOscillationInterface
from ..utils.global_variables import BASE_OSCILLATION_NAMES
from ..utils.types import BOGenerationContext


class Polynomial(BaseOscillationInterface):
    KIND = BASE_OSCILLATION_NAMES.POLYNOMIAL

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return None

    def generate_only_base(self,
                           ctx: BOGenerationContext,
                           length: Optional[int] = None,
                           polynomial: Optional[List[float]] = None,
                           *args, **kwargs) -> np.ndarray:
        length = length or self.length
        polynomial = polynomial or self.polynomial

        base_ts = np.polynomial.Polynomial(polynomial)(np.arange(length))
        return base_ts


BaseOscillation.register(Polynomial.KIND, Polynomial)
