from __future__ import annotations
from enum import Enum
from typing import List, Optional, Union, Any, Tuple
import math

import numpy as np

from ..utils.types import BaseOscillationKind
from .types import AnomalyProtocol
from .types.extremum import AnomalyExtremum
from .types.frequency import AnomalyFrequency
from .types.mean import AnomalyMean
from .types.pattern import AnomalyPattern
from .types.pattern_shift import AnomalyPatternShift
from .types.platform import AnomalyPlatform
from .types.variance import AnomalyVariance


def list_or_wrap(value: Union[Any, List[Any]]) -> List[Any]:
    if not isinstance(value, List):
        value = [value]
    return value


class Position(Enum):
    Beginning = "beginning"
    Middle = "middle"
    End = "end"


def exist_together(list_optionals: List[Optional]) -> bool:
    return all(list(map(lambda x: x is not None, list_optionals)))


class Anomaly:
    """This class acts like a generator graph, that collects all options in the beginning and,
    while being injected to a BaseOscillation, performs the changes."""

    def __init__(self,
                 position: Position,
                 anomaly_length: int,
                 channel: int = 0):
        self.position = position
        self.anomaly_length = anomaly_length
        self.channel = channel

        # kinds
        self.anomaly_extremum: Optional[AnomalyExtremum] = None
        self.anomaly_frequency: Optional[AnomalyFrequency] = None
        self.anomaly_platform: Optional[AnomalyPlatform] = None
        self.anomaly_pattern: Optional[AnomalyPattern] = None
        self.anomaly_mean: Optional[AnomalyMean] = None
        self.anomaly_variance: Optional[AnomalyVariance] = None
        self.anomaly_pattern_shift: Optional[AnomalyPatternShift] = None

    def _validate(self):
        if not exist_together([self.anomaly_platform, self.anomaly_extremum]) and \
                not exist_together([self.anomaly_platform, self.anomaly_frequency]) and \
                not exist_together([self.anomaly_platform, self.anomaly_pattern]) and \
                not exist_together([self.anomaly_platform, self.anomaly_mean]) and \
                not exist_together([self.anomaly_platform, self.anomaly_pattern_shift]):
            return
        raise ValueError("The combination of anomaly options for this anomaly is not supported. Guten Tag!")

    def set_extrema(self, anomaly_extremum: AnomalyExtremum) -> Anomaly:
        self.anomaly_extremum = anomaly_extremum
        return self

    def set_frequencies(self, anomaly_frequency: AnomalyFrequency) -> Anomaly:
        self.anomaly_frequency = anomaly_frequency
        return self

    def set_platform(self, anomaly_platform: AnomalyPlatform) -> Anomaly:
        self.anomaly_platform = anomaly_platform
        return self

    def set_pattern(self, anomaly_pattern: AnomalyPattern) -> Anomaly:
        self.anomaly_pattern = anomaly_pattern
        return self

    def set_mean(self, anomaly_mean: AnomalyMean) -> Anomaly:
        self.anomaly_mean = anomaly_mean
        return self

    def set_variance(self, anomaly_variance: AnomalyVariance) -> Anomaly:
        self.anomaly_variance = anomaly_variance
        return self

    def set_pattern_shift(self, anomaly_pattern_shift: AnomalyPatternShift) -> Anomaly:
        self.anomaly_pattern_shift = anomaly_pattern_shift
        return self

    def generate(self, base_oscillation: 'BaseOscillationInterface', timeseries_periods: int, base_oscillation_kind: BaseOscillationKind) -> AnomalyProtocol:
        self._validate()
        start, end = self.get_position_range(base_oscillation.length, timeseries_periods)
        protocol = AnomalyProtocol(start, end, base_oscillation, base_oscillation_kind)

        if self.anomaly_platform:
            protocol = self.anomaly_platform.generate(protocol)
        if self.anomaly_frequency:
            protocol = self.anomaly_frequency.generate(protocol)
        if self.anomaly_extremum:
            protocol = self.anomaly_extremum.generate(protocol)

        return protocol

    def get_position_range(self, timeseries_length: int, timeseries_periods: int) -> Tuple[int, int]:
        start_period = 0
        period_size = timeseries_length / timeseries_periods
        periods_per_section = timeseries_periods / 3
        if periods_per_section > 1:
            start_period = math.floor(periods_per_section / 2)

        position = self.position
        if position == Position.Beginning:
            start = int(period_size) * start_period
        elif position == Position.Middle:
            start = int(period_size) * (int(periods_per_section) + start_period)
        elif position == Position.End:
            start = int(period_size) * (2 * int(periods_per_section) + start_period)
        else:
            raise ValueError(f"The position '{position}' is not yet supported! Guten Tag!")

        end = start + self.anomaly_length
        return start, end
