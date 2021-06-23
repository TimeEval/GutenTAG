from typing import Optional, Tuple

import numpy as np
import random
import math

from .interface import BaseOscillationInterface
from ..utils.types import BaseOscillationKind


class CylinderBellFunnel(BaseOscillationInterface):
    def get_timeseries_periods(self) -> Optional[int]:
        if self.avg_pattern_length > 0:
            return self.length // self.avg_pattern_length
        return None

    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.CylinderBellFunnel

    def generate(self) -> Tuple[np.ndarray, np.ndarray]:
        self.timeseries = self.generate_only_base().reshape(-1, 1)
        self._generate_anomalies()
        return self.timeseries, self.labels

    def generate_only_base(self,
                           length: Optional[int] = None,
                           frequency: Optional[float] = None,
                           amplitude: Optional[float] = None,
                           variance_pattern_length: Optional[int] = None,
                           *args, **kwargs) -> np.ndarray:
        length = length or self.length
        frequency = frequency or self.frequency
        amplitude = amplitude or self.amplitude
        variance_pattern_length = variance_pattern_length or self.variance_pattern_length

        return generate_pattern_data(
            length,
            self.avg_pattern_length,
            amplitude,
            default_variance=frequency,
            variance_pattern_length=variance_pattern_length,
            variance_amplitude=2
        )


# Taken from https://github.com/KDD-OpenSource/data-generation/blob/master/generation/cbf.py
# cylinder bell funnel based on "Learning comprehensible descriptions of multivariate time series"

def generate_bell(length, amplitude, default_variance):
    bell = np.random.normal(0, default_variance, length) + amplitude * np.arange(length) / length
    return bell


def generate_funnel(length, amplitude, default_variance):
    funnel = np.random.normal(0, default_variance, length) + amplitude * np.arange(length)[::-1] / length
    return funnel


def generate_cylinder(length, amplitude, default_variance):
    cylinder = np.random.normal(0, default_variance, length) + amplitude
    return cylinder


std_generators = [generate_bell, generate_funnel, generate_cylinder]


def generate_pattern_data(length, avg_pattern_length, avg_amplitude, default_variance=1, variance_pattern_length=10,
                          variance_amplitude=2, generators=std_generators, include_negatives=True):
    data = np.random.normal(0, default_variance, length)
    current_start = random.randint(0, avg_pattern_length)
    current_length = max(1, math.ceil(random.gauss(avg_pattern_length, variance_pattern_length)))

    while current_start + current_length < length:
        generator = random.choice(generators)
        current_amplitude = random.gauss(avg_amplitude, variance_amplitude)

        while current_length <= 0:
            current_length = -(current_length - 1)
        pattern = generator(current_length, current_amplitude, default_variance)

        if include_negatives and random.random() > 0.5:
            pattern = -1 * pattern

        data[current_start: current_start + current_length] = pattern

        current_start = current_start + current_length + random.randint(0, avg_pattern_length)
        current_length = max(1, math.ceil(random.gauss(avg_pattern_length, variance_pattern_length)))

    return data
