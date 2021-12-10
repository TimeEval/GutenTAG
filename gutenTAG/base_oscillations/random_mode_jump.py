from typing import Optional

import numpy as np

from .interface import BaseOscillationInterface
from ..utils.types import BaseOscillationKind


class RandomModeJump(BaseOscillationInterface):
    def get_base_oscillation_kind(self) -> BaseOscillationKind:
        return BaseOscillationKind.RandomModeJump

    def get_timeseries_periods(self) -> Optional[int]:
        return self.frequency

    def generate_only_base(self,
                           length: Optional[int] = None,
                           frequency: Optional[float] = None,
                           channel: int = 0,
                           channel_diff: Optional[float] = None,
                           channel_offset: Optional[float] = None,
                           random_seed: Optional[int] = None,
                           *args, **kwargs) -> np.ndarray:
        length = length or self.length
        frequency = frequency or self.frequency
        channel_diff = channel_diff or self.channel_diff
        channel_offset = channel_offset or self.channel_offset
        random_seed = random_seed or self.random_seed
        step_length = int(length // frequency)

        base_random_steps = self._generate_random_steps(length, step_length, random_seed)
        channel_amplitude = self._generate_channel_amplitude(channel, channel_diff, channel_offset)
        ts = base_random_steps * channel_amplitude

        return ts

    def _generate_random_steps(self, length: int, step_length: int, random_seed: Optional[int] = None) -> np.ndarray:
        state = None
        if random_seed is not None:
            state = np.random.get_state()
            np.random.seed(random_seed)
        n_steps = int(np.ceil(length / step_length).item())
        energy = np.random.choice([-1, 1], size=n_steps)
        base = np.repeat(energy, step_length)[:length].astype(np.float64)
        if state is not None:
            np.random.set_state(state)
        return base

    def _generate_channel_amplitude(self, channel: int, channel_diff: float, channel_offset: float) -> float:
        high_val = (channel_diff * channel) + channel_offset
        return high_val
