from abc import ABC, abstractmethod
from typing import Optional

import numpy as np

from ..utils.default_values import default_values
from ..utils.global_variables import PARAMETERS, BASE_OSCILLATIONS
from ..utils.types import BOGenerationContext


class BaseOscillationInterface(ABC):
    def __init__(self, *args, **kwargs):
        self.length = kwargs.get(PARAMETERS.LENGTH, default_values[BASE_OSCILLATIONS][PARAMETERS.LENGTH])
        self.frequency = kwargs.get(PARAMETERS.FREQUENCY, default_values[BASE_OSCILLATIONS][PARAMETERS.FREQUENCY])
        self.amplitude = kwargs.get(PARAMETERS.AMPLITUDE, default_values[BASE_OSCILLATIONS][PARAMETERS.AMPLITUDE])
        self.variance = kwargs.get(PARAMETERS.VARIANCE, default_values[BASE_OSCILLATIONS][PARAMETERS.VARIANCE])
        self.avg_pattern_length = kwargs.get(PARAMETERS.AVG_PATTERN_LENGTH, default_values[BASE_OSCILLATIONS][PARAMETERS.AVG_PATTERN_LENGTH])
        self.variance_pattern_length = kwargs.get(PARAMETERS.VARIANCE_PATTERN_LENGTH, default_values[BASE_OSCILLATIONS][PARAMETERS.VARIANCE_PATTERN_LENGTH])
        self.variance_amplitude = kwargs.get(PARAMETERS.VARIANCE_AMPLITUDE, default_values[BASE_OSCILLATIONS][PARAMETERS.VARIANCE_AMPLITUDE])
        self.freq_mod = kwargs.get(PARAMETERS.FREQ_MOD, default_values[BASE_OSCILLATIONS][PARAMETERS.FREQ_MOD])
        self.polynomial = kwargs.get(PARAMETERS.POLYNOMIAL, default_values[BASE_OSCILLATIONS][PARAMETERS.POLYNOMIAL])
        self.trend: Optional[BaseOscillationInterface] = kwargs.get(PARAMETERS.TREND, default_values[BASE_OSCILLATIONS][PARAMETERS.TREND])
        self.offset = kwargs.get(PARAMETERS.OFFSET, default_values[BASE_OSCILLATIONS][PARAMETERS.OFFSET])
        self.smoothing = kwargs.get(PARAMETERS.SMOOTHING, default_values[BASE_OSCILLATIONS][PARAMETERS.SMOOTHING])
        self.channel_diff = kwargs.get(PARAMETERS.CHANNEL_DIFF, default_values[BASE_OSCILLATIONS][PARAMETERS.CHANNEL_DIFF])
        self.channel_offset = kwargs.get(PARAMETERS.CHANNEL_OFFSET, self.amplitude)
        self.random_seed = kwargs.get(PARAMETERS.RANDOM_SEED, default_values[BASE_OSCILLATIONS][PARAMETERS.RANDOM_SEED])
        self.formula = kwargs.get(PARAMETERS.FORMULA, default_values[BASE_OSCILLATIONS][PARAMETERS.FORMULA])
        self.ecg_sim_method = kwargs.get(PARAMETERS.ECG_SIM_METHOD, default_values[BASE_OSCILLATIONS][PARAMETERS.ECG_SIM_METHOD])
        self.width = kwargs.get(PARAMETERS.WIDTH, default_values[BASE_OSCILLATIONS][PARAMETERS.WIDTH])
        self.duty = kwargs.get(PARAMETERS.DUTY, default_values[BASE_OSCILLATIONS][PARAMETERS.DUTY])
        self.periodicity = kwargs.get(PARAMETERS.PERIODICITY, default_values[BASE_OSCILLATIONS][PARAMETERS.PERIODICITY])
        self.complexity = kwargs.get(PARAMETERS.COMPLEXITY, default_values[BASE_OSCILLATIONS][PARAMETERS.COMPLEXITY])
        self.input_timeseries_path = kwargs.get(PARAMETERS.INPUT_TIMESERIES_PATH, default_values[BASE_OSCILLATIONS][PARAMETERS.INPUT_TIMESERIES_PATH])

        self.timeseries: Optional[np.ndarray] = None
        self.noise: Optional[np.ndarray] = None
        self.trend_series: Optional[np.ndarray] = None

    def generate_noise(self, ctx: BOGenerationContext, variance: float, length: int) -> np.ndarray:
        return ctx.rng.normal(0, variance, length)

    def _generate_trend(self, ctx: BOGenerationContext) -> np.ndarray:
        trend_series = np.zeros(self.length)
        if self.trend:
            self.trend.length = self.length
            self.trend.generate_timeseries_and_variations(ctx)
            if self.trend.timeseries is not None:
                trend_series = self.trend.timeseries
        return trend_series

    def generate_timeseries_and_variations(self, ctx: BOGenerationContext, **kwargs):
        self.timeseries = self.generate_only_base(ctx, **kwargs)
        self.trend_series = self._generate_trend(ctx.to_trend())
        self.noise = self.generate_noise(ctx, self.variance * self.amplitude, self.length)

    def is_periodic(self) -> bool:
        periods = self.get_timeseries_periods()
        return periods is not None and periods > 1

    @abstractmethod
    def get_timeseries_periods(self) -> Optional[int]:
        """
        How many same-sized periods do occur in the time series? If no periodicity is given, return None!
        :return: Optional[int]
        """
        raise NotImplementedError()

    def get_period_size(self) -> Optional[int]:
        """
        Returns the number of points within on period. period_size * n_periods might not be exactly equal to the time
        series length! If no periodicity is given, return None.
        """
        if self.is_periodic():
            return self.length // self.get_timeseries_periods()
        else:
            return None

    @abstractmethod
    def get_base_oscillation_kind(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def generate_only_base(self, ctx: BOGenerationContext, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError()

    @classmethod
    def __subclasshook__(cls, C):
        if cls is BaseOscillationInterface:
            if any("generate" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
