from __future__ import annotations
from enum import Enum
from typing import List, Optional, Union, Any, Tuple, Dict
import math
import random

import numpy as np

from ..utils.types import BaseOscillationKind
from .types import AnomalyProtocol, BaseAnomaly, LabelRange
from .types.kind import AnomalyKind
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

        self.anomaly_kinds: List[AnomalyKind] = []

    def set_anomaly(self, anomaly_kind: AnomalyKind) -> Anomaly:
        self.anomaly_kinds.append(anomaly_kind)
        return self

    def generate(self, base_oscillation: 'BaseOscillationInterface', timeseries_periods: int, base_oscillation_kind: BaseOscillationKind) -> AnomalyProtocol:
        # AnomalyKind.validate(self.anomaly_kinds)
        start, end = self.get_position_range(base_oscillation.length, timeseries_periods)
        length = end - start
        label_range = LabelRange(start, length)
        protocol = AnomalyProtocol(start, end, base_oscillation, base_oscillation_kind, label_range)

        for anomaly in self.anomaly_kinds:
            protocol = anomaly.generate(protocol)

        return protocol

    def get_position_range(self, timeseries_length: int, timeseries_periods: int) -> Tuple[int, int]:
        start_period = 0
        period_size = int(timeseries_length / timeseries_periods)
        periods_per_section = int(timeseries_periods / 3)
        if periods_per_section > 1:
            start_period = random.choice(list(range(periods_per_section)))

        position = self.position
        if position == Position.Beginning:
            start = period_size * start_period
        elif position == Position.Middle:
            start = period_size * (periods_per_section + start_period)
        elif position == Position.End:
            start = period_size * (2 * periods_per_section + start_period)
        else:
            raise ValueError(f"The position '{position}' is not yet supported! Guten Tag!")

        end = start + self.anomaly_length
        return start, end
