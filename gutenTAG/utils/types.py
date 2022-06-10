from dataclasses import dataclass
from typing import List, Tuple, Optional, Union

import numpy as np

from gutenTAG.utils.base_oscillation_kind import BaseOscillationKind


class GenerationContext:
    SEED_PRIME: int = 59

    def __init__(self, seed: int):
        self.seed: int = seed
        self.rng: np.random.Generator = np.random.default_rng(self.seed)

    def to_bo(self, channel: int = 0, previous_channels: List[np.ndarray] = ()) -> 'BOGenerationContext':
        return BOGenerationContext(
            seed=self.seed,
            rng=self.rng,
            channel=channel,
            previous_channels=previous_channels
        )

    def to_anomaly(self, bo: 'BaseOscillationInterface',  # type: ignore  # to prevent circular import
                   previous_anomaly_positions: List[Tuple[int, int]]) -> 'AnomalyGenerationContext':
        return AnomalyGenerationContext(
            seed=self.seed,
            rng=self.rng,
            base_oscillation=bo,
            previous_anomaly_positions=previous_anomaly_positions
        )

    @staticmethod
    def re_seed(new_seeds: Union[int, List[int]], base_seed: int = 0) -> int:
        if isinstance(new_seeds, int):
            new_seeds = [new_seeds]
        for seed in new_seeds:
            base_seed = (base_seed + seed) * GenerationContext.SEED_PRIME
        return np.abs(base_seed)


@dataclass
class BOGenerationContext(GenerationContext):
    seed: int
    rng: np.random.Generator
    channel: int
    previous_channels: List[np.ndarray]
    is_trend: bool = False

    def to_trend(self) -> 'BOGenerationContext':
        return BOGenerationContext(
            seed=self.seed,
            rng=self.rng,
            channel=self.channel,
            previous_channels=self.previous_channels,
            is_trend=True
        )


@dataclass
class AnomalyGenerationContext(GenerationContext):
    seed: int
    rng: np.random.Generator
    base_oscillation: 'BaseOscillationInterface'    # type: ignore  # to prevent circular import
    previous_anomaly_positions: List[Tuple[int, int]]

    @property
    def timeseries_periods(self) -> Optional[int]:
        return self.base_oscillation.get_timeseries_periods()

    @property
    def base_oscillation_kind(self) -> BaseOscillationKind:
        return self.base_oscillation.get_base_oscillation_kind()
