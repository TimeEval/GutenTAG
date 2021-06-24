import numpy as np
from typing import Optional, List, Tuple

from ..utils.types import BaseOscillationKind
from .interface import BaseOscillationInterface


class Polynomial(BaseOscillationInterface):
    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.Polynomial

    def get_timeseries_periods(self) -> Optional[int]:
        return None

    def generate(self) -> Tuple[np.ndarray, np.ndarray]:
        self.timeseries = self.generate_only_base()
        self._generate_anomalies()
        return self.timeseries, self.labels

    def generate_only_base(self,
                           length:    Optional = None,
                           polynomial: Optional = None,
                           channels:  Optional = None) -> np.ndarray:
        length = length or self.length
        polynomial = polynomial or self.polynomial
        channels = channels or self.channels

        base_ts = np.polynomial.Polynomial(polynomial).linspace(length)[1].reshape(-1, 1)
        base_ts = np.repeat(base_ts, repeats=channels, axis=1)

        return base_ts
