from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np

from ..utils.types import BaseOscillationKind
from ..utils.default_values import default_values


class BaseOscillationInterface(ABC):
    def __init__(self, *args, **kwargs):
        self.length = kwargs.get("length", default_values["base_oscillations"]["length"])
        self.frequency = kwargs.get("frequency", default_values["base_oscillations"]["frequency"])
        self.amplitude = kwargs.get("amplitude", default_values["base_oscillations"]["amplitude"])
        self.variance = kwargs.get("variance", default_values["base_oscillations"]["variance"])
        self.avg_pattern_length = kwargs.get("avg-pattern-length", default_values["base_oscillations"]["avg-pattern-length"])
        self.variance_pattern_length = kwargs.get("variance-pattern-length", default_values["base_oscillations"]["variance-pattern-length"])
        self.variance_amplitude = kwargs.get("variance-amplitude", default_values["base_oscillations"]["variance-amplitude"])
        self.freq_mod = kwargs.get("freq-mod", default_values["base_oscillations"]["freq-mod"])
        self.polynomial = kwargs.get("polynomial", default_values["base_oscillations"]["polynomial"])
        self.trend: Optional[BaseOscillationInterface] = kwargs.get("trend", default_values["base_oscillations"]["trend"])
        self.offset = kwargs.get("offset", default_values["base_oscillations"]["offset"])
        self.smoothing = kwargs.get("smoothing", default_values["base_oscillations"]["smoothing"])
        self.channel_diff = kwargs.get("channel_diff", default_values["base_oscillations"]["channel_diff"])
        self.channel_offset = kwargs.get("channel_offset", self.amplitude)
        self.random_seed = kwargs.get("random_seed", default_values["base_oscillations"]["random_seed"])

        self.timeseries: Optional[np.ndarray] = None
        self.noise: Optional[np.ndarray] = None
        self.trend_series: Optional[np.ndarray] = None

    def generate_noise(self, variance: float, length: int) -> np.ndarray:
        return np.random.normal(0, variance, length)

    def _generate_trend(self) -> np.ndarray:
        trend_series = np.zeros(self.length)
        if self.trend:
            self.trend.length = self.length
            self.trend.generate_timeseries_and_variations()
            if (timeseries := self.trend.timeseries) is not None:
                trend_series = timeseries
        return trend_series

    def generate_timeseries_and_variations(self, channel: int = 0):
        self.timeseries = self.generate_only_base(channel=channel)
        self.trend_series = self._generate_trend()
        self.noise = self.generate_noise(self.variance * self.amplitude, self.length)

    @abstractmethod
    def get_timeseries_periods(self) -> Optional[int]:
        """
        How many same-sized periods do occur in the time series? If no periodicity is given, return None!
        :return: Optional[int]
        """
        raise NotImplementedError()

    @abstractmethod
    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        raise NotImplementedError()

    @abstractmethod
    def generate_only_base(self, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError()

    @classmethod
    def __subclasshook__(cls, C):
        if cls is BaseOscillationInterface:
            if any("generate" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
