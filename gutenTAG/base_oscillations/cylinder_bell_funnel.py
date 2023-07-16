from typing import Optional, Sequence, Callable

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


class CylinderBellFunnel(BaseOscillationInterface):
    KIND = BASE_OSCILLATION_NAMES.CYLINDER_BELL_FUNNEL

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        if self.avg_pattern_length > 0:
            return self.length // self.avg_pattern_length
        return None

    def is_periodic(self) -> bool:
        """CylinderBellFunnel has reoccurring patterns but no fixed periodicity!"""
        return False

    def generate_only_base(
        self,
        ctx: BOGenerationContext,
        length: Optional[int] = None,
        variance: Optional[float] = None,
        amplitude: Optional[float] = None,
        variance_pattern_length: Optional[int] = None,
        *args,
        **kwargs
    ) -> np.ndarray:
        length = length or self.length
        variance = variance or self.variance
        amplitude = amplitude or self.amplitude
        variance_pattern_length = (
            variance_pattern_length or self.variance_pattern_length
        )

        return cylinder_bell_funnel(
            ctx.rng,
            length=length,
            avg_pattern_length=self.avg_pattern_length,
            avg_amplitude=amplitude,
            default_variance=variance,
            variance_pattern_length=variance_pattern_length,
            variance_amplitude=self.variance_amplitude,
        )

    def generate_timeseries_and_variations(
        self, ctx: BOGenerationContext, **kwargs
    ) -> BaseOscillationInterface:
        super().generate_timeseries_and_variations(ctx)
        if self.timeseries is not None and self.noise is not None:
            self.timeseries -= self.noise
        else:
            raise AssertionError(
                "`timeseries` and `noise` are None. Please, generate `timeseries` and `noise` before calling this method!"
            )
        return self


BaseOscillation.register(CylinderBellFunnel.KIND, CylinderBellFunnel)


# Taken from https://github.com/KDD-OpenSource/data-generation/blob/master/generation/cbf.py
# cylinder bell funnel based on "Learning comprehensible descriptions of multivariate time series"
def cylinder_bell_funnel(
    rng: np.random.Generator = np.random.default_rng(),
    length: int = default_values[BASE_OSCILLATIONS][PARAMETERS.LENGTH],
    avg_pattern_length: int = default_values[BASE_OSCILLATIONS][
        PARAMETERS.AVG_PATTERN_LENGTH
    ],
    avg_amplitude: float = default_values[BASE_OSCILLATIONS][PARAMETERS.AMPLITUDE],
    default_variance: float = default_values[BASE_OSCILLATIONS][PARAMETERS.VARIANCE],
    variance_pattern_length: int = default_values[BASE_OSCILLATIONS][
        PARAMETERS.VARIANCE_PATTERN_LENGTH
    ],
    variance_amplitude: float = default_values[BASE_OSCILLATIONS][
        PARAMETERS.VARIANCE_AMPLITUDE
    ],
    include_negatives: bool = True,
) -> np.ndarray:
    def generate_bell(n: int, a: float, v: float) -> np.ndarray:
        bell = rng.normal(0, v, n) + a * np.arange(n) / n
        return bell

    def generate_funnel(n: int, a: float, v: float) -> np.ndarray:
        funnel = rng.normal(0, v, n) + a * np.arange(n)[::-1] / n
        return funnel

    def generate_cylinder(n: int, a: float, v: float) -> np.ndarray:
        cylinder = rng.normal(0, v, n) + a
        return cylinder

    generators: Sequence[Callable[[int, float, float], np.ndarray]] = (
        generate_bell,
        generate_funnel,
        generate_cylinder,
    )
    data = rng.normal(0, default_variance, length)
    current_start = rng.integers(0, avg_pattern_length)
    current_length = max(
        1, int(np.ceil(rng.normal(avg_pattern_length, variance_pattern_length)))
    )

    while current_start + current_length < length:
        generator: Callable[[int, float, float], np.ndarray] = rng.choice(generators)  # type: ignore  # strange numpy type prevents chosing a callable
        current_amplitude = rng.normal(avg_amplitude, variance_amplitude)

        while current_length <= 0:
            current_length = -(current_length - 1)
        pattern = generator(current_length, current_amplitude, default_variance)

        if include_negatives and rng.random() > 0.5:
            pattern = -1 * pattern

        data[current_start : current_start + current_length] = pattern

        current_start = (
            current_start + current_length + rng.integers(0, avg_pattern_length)
        )
        current_length = max(
            1, int(np.ceil(rng.normal(avg_pattern_length, variance_pattern_length)))
        )

    return data
