from typing import Optional, Sequence, Callable

import numpy as np

from .interface import BaseOscillationInterface
from ..utils.base_oscillation_kind import BaseOscillationKind
from ..utils.types import BOGenerationContext


class CylinderBellFunnel(BaseOscillationInterface):
    def get_timeseries_periods(self) -> Optional[int]:
        if self.avg_pattern_length > 0:
            return self.length // self.avg_pattern_length
        return None

    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.CylinderBellFunnel

    def generate_only_base(self,
                           ctx: BOGenerationContext,
                           length: Optional[int] = None,
                           variance: Optional[float] = None,
                           amplitude: Optional[float] = None,
                           variance_pattern_length: Optional[int] = None,
                           *args, **kwargs) -> np.ndarray:
        length = length or self.length
        variance = variance or self.variance
        amplitude = amplitude or self.amplitude
        variance_pattern_length = variance_pattern_length or self.variance_pattern_length

        cbf = generate_pattern_data(
            ctx,
            length=length,
            avg_pattern_length=self.avg_pattern_length,
            avg_amplitude=amplitude,
            default_variance=variance,
            variance_pattern_length=variance_pattern_length,
            variance_amplitude=self.variance_amplitude
        )
        return cbf

    def generate_timeseries_and_variations(self, ctx: BOGenerationContext, **kwargs) -> BaseOscillationInterface:
        super().generate_timeseries_and_variations(ctx)
        if self.timeseries is not None and self.noise is not None:
            self.timeseries -= self.noise
        else:
            raise AssertionError("`timeseries` and `noise` are None. Please, generate `timeseries` and `noise` before calling this method!")
        return self


# Taken from https://github.com/KDD-OpenSource/data-generation/blob/master/generation/cbf.py
# cylinder bell funnel based on "Learning comprehensible descriptions of multivariate time series"
def generate_pattern_data(ctx: BOGenerationContext, length, avg_pattern_length, avg_amplitude, default_variance=1,
                          variance_pattern_length=10, variance_amplitude=2, include_negatives=True):
    def generate_bell(n: int, a: float, v: float) -> np.ndarray:
        bell = ctx.rng.normal(0, v, n) + a * np.arange(n) / n
        return bell

    def generate_funnel(n: int, a: float, v: float) -> np.ndarray:
        funnel = ctx.rng.normal(0, v, n) + a * np.arange(n)[::-1] / n
        return funnel

    def generate_cylinder(n: int, a: float, v: float) -> np.ndarray:
        cylinder = ctx.rng.normal(0, v, n) + a
        return cylinder

    generators: Sequence[Callable[[int, float, float], np.ndarray]] = (generate_bell, generate_funnel, generate_cylinder)
    data = ctx.rng.normal(0, default_variance, length)
    current_start = ctx.rng.integers(0, avg_pattern_length)
    current_length = max(1, int(np.ceil(ctx.rng.normal(avg_pattern_length, variance_pattern_length))))

    while current_start + current_length < length:
        generator: Callable[[int, float, float], np.ndarray] = ctx.rng.choice(generators)  # type: ignore  # strange numpy type prevents chosing a callable
        current_amplitude = ctx.rng.normal(avg_amplitude, variance_amplitude)

        while current_length <= 0:
            current_length = -(current_length - 1)
        pattern = generator(current_length, current_amplitude, default_variance)

        if include_negatives and ctx.rng.random() > 0.5:
            pattern = -1 * pattern

        data[current_start: current_start + current_length] = pattern

        current_start = current_start + current_length + ctx.rng.integers(0, avg_pattern_length)
        current_length = max(1, int(np.ceil(ctx.rng.normal(avg_pattern_length, variance_pattern_length))))

    return data
