from __future__ import annotations

from enum import Enum
from typing import List, Optional, Tuple

from .types import AnomalyProtocol, BaseAnomaly, LabelRange
from .types.kind import AnomalyKind
from ..utils.types import AnomalyGenerationContext


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
                 channel: int = 0,
                 creep_length: int = 0):
        self.position = position
        self.exact_position = exact_position
        self.anomaly_length = anomaly_length
        self.channel = channel
        self.creep_length = creep_length

        self.anomaly_kinds: List[BaseAnomaly] = []

    def set_anomaly(self, anomaly_kind: BaseAnomaly) -> Anomaly:
        self.anomaly_kinds.append(anomaly_kind)
        return self

    def generate(self, ctx: AnomalyGenerationContext) -> AnomalyProtocol:
        if self.exact_position is None:
            start, end = self._get_position_range(ctx)
            while end > ctx.base_oscillation.length:
                start, end = self._get_position_range(ctx)
                start, end = self._maybe_repair_position((start, end), ctx.previous_anomaly_positions)
        else:
            start, end = self.exact_position, self.exact_position + self.anomaly_length

        length = end - start
        label_range = LabelRange(start, length)
        protocol = AnomalyProtocol(start, end, self.channel, ctx, label_range, creep_length=self.creep_length)

        for anomaly in self.anomaly_kinds:
            protocol = anomaly.generate(protocol)

        return protocol

    def _get_position_range(self, ctx: AnomalyGenerationContext) -> Tuple[int, int]:
        timeseries_length = ctx.base_oscillation.length
        timeseries_periods = ctx.timeseries_periods
        if timeseries_periods is None or timeseries_periods <= 6:
            return self._get_position_range_no_periodicity(ctx)

        start_period = 0
        period_size = int(timeseries_length / timeseries_periods)
        periods_per_section = int(timeseries_periods / 3)
        if periods_per_section > 1:
            start_period = ctx.rng.choice(list(range(periods_per_section)))

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

    def _get_position_range_no_periodicity(self, ctx: AnomalyGenerationContext) -> Tuple[int, int]:
        timeseries_length = ctx.base_oscillation.length
        section_size = timeseries_length // 3
        position_in_section = ctx.rng.choice(list(range(section_size - self.anomaly_length)))

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
