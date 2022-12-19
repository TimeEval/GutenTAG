from __future__ import annotations

import numpy as np

from enum import Enum
from typing import List, Optional, Tuple

from .types import AnomalyProtocol, BaseAnomaly, LabelRange
from .types.kind import AnomalyKind
from ..utils.types import AnomalyGenerationContext


class Position(Enum):
    Beginning = "beginning"
    Middle = "middle"
    End = "end"

    @property
    def id(self) -> int:
        if self == Position.Beginning:
            return 0
        elif self == Position.Middle:
            return 1
        elif self == Position.End:
            return 2
        else:
            raise ValueError(f"The position '{self}' is not yet supported! Guten Tag!")


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
        self._requires_period_start_position: bool = False

    def set_anomaly(self, anomaly_kind: BaseAnomaly) -> Anomaly:
        self.anomaly_kinds.append(anomaly_kind)
        self._requires_period_start_position = self._requires_period_start_position or anomaly_kind.requires_period_start_position
        return self

    def generate(self, ctx: AnomalyGenerationContext) -> AnomalyProtocol:
        if self.exact_position is None:
            start, end = self._find_position(ctx)
        else:
            start, end = self.exact_position, self.exact_position + self.anomaly_length

        length = end - start
        label_range = LabelRange(start, length, "")
        protocol = AnomalyProtocol(start, end, self.channel, ctx, label_range, creep_length=self.creep_length)

        for anomaly in self.anomaly_kinds:
            protocol = anomaly.generate(protocol)
            protocol.labels.class_label = type(anomaly).__name__

        return protocol

    def _find_position(self, ctx: AnomalyGenerationContext, max_tries: int = 50) -> Tuple[int, int]:
        n_tries = max_tries
        while n_tries > 0:
            pos = self._get_random_position(ctx)
            n_tries -= 1
            if pos[1] < ctx.base_oscillation.length and not self._has_collision(pos, ctx.previous_anomaly_positions):
                return pos
        raise ValueError(f"Giving up on finding a position for {self.anomaly_length}-point anomaly at {self.position} "
                         f"in channel {self.channel}! Maximum number of retries ({max_tries}) exceeded!")

    def _get_random_position(self, ctx: AnomalyGenerationContext) -> Tuple[int, int]:
        timeseries_periods = ctx.timeseries_periods
        period_size = ctx.timeseries_period_size
        if (
                not self._requires_period_start_position
                or timeseries_periods is None
                or timeseries_periods <= 6
                or period_size is None
                or period_size <= 2
        ):
            return self._get_random_position_no_periodicity(ctx)

        start_period = 0
        periods_per_section = timeseries_periods // 3
        if periods_per_section > 1:
            start_period = ctx.rng.choice(list(range(periods_per_section)))

        position = self.position.id
        start = period_size * (position*periods_per_section + start_period)
        end = start + self.anomaly_length
        return start, end

    def _get_random_position_no_periodicity(self, ctx: AnomalyGenerationContext) -> Tuple[int, int]:
        timeseries_length = ctx.base_oscillation.length
        section_size = timeseries_length // 3
        position_in_section = ctx.rng.choice(np.arange(section_size))

        position = self.position.id
        start = (position * section_size) + position_in_section
        end = start + self.anomaly_length
        return start, end

    @staticmethod
    def _has_collision(current_pos: Tuple[int, int], other_pos: List[Tuple[int, int]]) -> bool:
        if len(other_pos) == 0:
            return False
        others = np.array(other_pos)
        start_collision = (others[:, 0] <= current_pos[0]) & (current_pos[0] <= others[:, 1])
        end_colllision = (others[:, 0] <= current_pos[1]) & (current_pos[1] <= others[:, 1])
        return bool(np.any(start_collision | end_colllision))
