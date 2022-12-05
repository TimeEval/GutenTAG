from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional, Union, Sequence

import numpy as np
from numpy.random import SeedSequence


class GenerationContext:
    def __init__(self, seed: SeedSequence):
        self.seed: SeedSequence = seed
        self.rng: np.random.Generator = np.random.default_rng(self.seed)

    def to_bo(self, channel: int = 0, previous_channels: Sequence[np.ndarray] = ()) -> BOGenerationContext:
        return BOGenerationContext(
            seed=self.seed,
            rng=self.rng,
            channel=channel,
            previous_channels=list(previous_channels)
        )

    def to_anomaly(self, bo: 'BaseOscillationInterface',  # type: ignore  # to prevent circular import
                   previous_anomaly_positions: Sequence[Tuple[int, int]]) -> AnomalyGenerationContext:
        return AnomalyGenerationContext(
            seed=self.seed,
            rng=self.rng,
            base_oscillation=bo,
            previous_anomaly_positions=list(previous_anomaly_positions)
        )

    @staticmethod
    def re_seed(new_seeds: Union[int, Optional[int], Sequence[int]],
                base_seed: Union[int, SeedSequence] = 0) -> SeedSequence:
        if isinstance(base_seed, SeedSequence):
            if isinstance(base_seed.entropy, int):
                initial_entropy: Sequence[int] = [base_seed.entropy]
            elif base_seed.entropy is not None:
                initial_entropy = base_seed.entropy
            else:
                initial_entropy = []
        else:
            initial_entropy = [base_seed]
        if new_seeds is None:
            new_seeds = []
        elif isinstance(new_seeds, int):
            new_seeds = [new_seeds]
        return SeedSequence(initial_entropy + new_seeds)  # type: ignore  # wrong type declaration in SeedSequence


@dataclass
class BOGenerationContext(GenerationContext):
    seed: SeedSequence
    rng: np.random.Generator
    channel: int
    previous_channels: List[np.ndarray]
    is_trend: bool = False

    def to_trend(self) -> BOGenerationContext:
        return BOGenerationContext(
            seed=self.seed,
            rng=self.rng,
            channel=self.channel,
            previous_channels=self.previous_channels,
            is_trend=True
        )


@dataclass
class AnomalyGenerationContext(GenerationContext):
    seed: SeedSequence
    rng: np.random.Generator
    base_oscillation: 'BaseOscillationInterface'  # type: ignore  # to prevent circular import
    previous_anomaly_positions: List[Tuple[int, int]]

    @property
    def timeseries_periods(self) -> Optional[int]:
        return self.base_oscillation.get_timeseries_periods()

    @property
    def base_oscillation_kind(self) -> str:
        return self.base_oscillation.get_base_oscillation_kind()
