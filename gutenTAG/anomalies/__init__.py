from __future__ import annotations
from enum import Enum
from typing import List, Optional, Union, Any, Tuple
import random

from ..utils.types import BaseOscillationKind
from .types import AnomalyProtocol, BaseAnomaly, LabelRange
from .types.kind import AnomalyKind


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
                 exact_position: Optional[int],
                 anomaly_length: int,
                 channel: int = 0):
        self.position = position
        self.exact_position = exact_position
        self.anomaly_length = anomaly_length
        self.channel = channel

        self.anomaly_kinds: List[BaseAnomaly] = []

    def set_anomaly(self, anomaly_kind: BaseAnomaly) -> Anomaly:
        self.anomaly_kinds.append(anomaly_kind)
        return self

    def generate(self, base_oscillation: 'BaseOscillationInterface', timeseries_periods: Optional[int], base_oscillation_kind: BaseOscillationKind, positions: List[Tuple[int, int]]) -> AnomalyProtocol:  # type: ignore # otherwise we have a circular import
        if self.exact_position is None:
            start, end = self._get_position_range(base_oscillation.length, timeseries_periods)
            while end > base_oscillation.length:
                start, end = self._get_position_range(base_oscillation.length, timeseries_periods)
                start, end = self._maybe_repair_position((start, end), positions)
        else:
            start, end = self.exact_position, self.exact_position + self.anomaly_length

        length = end - start
        label_range = LabelRange(start, length)
        protocol = AnomalyProtocol(start, end, self.channel, base_oscillation, base_oscillation_kind, label_range)

        for anomaly in self.anomaly_kinds:
            protocol = anomaly.generate(protocol)

        return protocol

    def _get_position_range(self, timeseries_length: int, timeseries_periods: Optional[int]) -> Tuple[int, int]:
        if timeseries_periods is None or timeseries_periods <= 6:
            return self._get_position_range_no_periodicity(timeseries_length)

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

    def _get_position_range_no_periodicity(self, timeseries_length: int) -> Tuple[int, int]:
        section_size = timeseries_length // 3
        position_in_section = random.choice(list(range(section_size - self.anomaly_length)))

        position = self.position
        if position == Position.Beginning:
            start = position_in_section
        elif position == Position.Middle:
            start = section_size + position_in_section
        elif position == Position.End:
            start = 2 * section_size + position_in_section
        else:
            raise ValueError(f"The position '{position}' is not yet supported! Guten Tag!")

        end = start + self.anomaly_length
        return start, end

    def _maybe_repair_position(self, current: Tuple[int, int], others: List[Tuple[int, int]]) -> Tuple[int, int]:
        start, end = current
        current_length = current[1] - current[0]
        for other in others:
            if other[0] <= current[0] <= other[1] or other[0] <= current[1] <= other[1]:
                start = other[1] + 1
                end = start + current_length
        return start, end
