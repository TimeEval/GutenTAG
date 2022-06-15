from dataclasses import dataclass
from typing import List, Tuple, Optional, Union

import numpy as np
from numpy.random import SeedSequence

from gutenTAG.utils.base_oscillation_kind import BaseOscillationKind


class GenerationContext:
    def __init__(self, seed: SeedSequence):
        self.seed: SeedSequence = seed
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
    def re_seed(new_seeds: Union[int, Optional[int], List[int]], base_seed: Union[int, SeedSequence] = 0) -> SeedSequence:
        if isinstance(base_seed, SeedSequence):
            initial_entropy = base_seed.entropy
            if isinstance(initial_entropy, int):
                initial_entropy = [initial_entropy]
        else:
            initial_entropy = [base_seed]
        if new_seeds is None:
            new_seeds = [base_seed]
        elif isinstance(new_seeds, int):
            new_seeds = [new_seeds]
        return SeedSequence(initial_entropy + new_seeds)


@dataclass
class BOGenerationContext(GenerationContext):
    seed: SeedSequence
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
    seed: SeedSequence
    rng: np.random.Generator
    base_oscillation: 'BaseOscillationInterface'    # type: ignore  # to prevent circular import
    previous_anomaly_positions: List[Tuple[int, int]]

    @property
    def timeseries_periods(self) -> Optional[int]:
        return self.base_oscillation.get_timeseries_periods()

    @property
    def base_oscillation_kind(self) -> BaseOscillationKind:
        return self.base_oscillation.get_base_oscillation_kind()
