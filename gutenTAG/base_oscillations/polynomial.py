from typing import Optional, List

import numpy as np

from .interface import BaseOscillationInterface
from ..utils.types import BaseOscillationKind


class Polynomial(BaseOscillationInterface):
    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.Polynomial

    def get_timeseries_periods(self) -> Optional[int]:
        return None

    def generate_only_base(self,
                           length: Optional[int] = None,
                           polynomial: Optional[List[float]] = None,
                           *args, **kwargs) -> np.ndarray:
        length = length or self.length
        polynomial = polynomial or self.polynomial

        base_ts = np.polynomial.Polynomial(polynomial).linspace(length)[1]

        return base_ts
