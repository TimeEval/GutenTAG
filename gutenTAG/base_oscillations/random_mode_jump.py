from typing import Optional

import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler

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
                           channels: Optional[int] = None,
                           channel_diff: Optional[float] = None,
                           channel_offset: Optional[float] = None,
                           *args, **kwargs) -> np.ndarray:
        length = length or self.length
        frequency = frequency or self.frequency
        channels = channels or self.channels
        channel_diff = channel_diff or self.channel_diff
        channel_offset = channel_offset or self.channel_offset
        step_length = length // frequency

        result = np.zeros((length, channels), dtype=np.float)
        base_random_steps = self._generate_random_steps(length, step_length)

        for channel in range(channels):
            channel_amplitude = self._generate_channel_amplitude(channel, channel_diff, channel_offset)
            result[:, channel] = base_random_steps * channel_amplitude

        return result

    def _generate_random_steps(self, length: int, step_length: int) -> np.ndarray:
        n_steps = int(np.ceil(length / step_length).item())
        energy = np.random.choice([-1, 1], size=n_steps)
        base = np.repeat(energy, step_length)[:length].astype(np.float64)
        return base

    def _generate_channel_amplitude(self, channel: int, channel_diff: float, channel_offset: float) -> float:
        high_val = (channel_diff * channel) + channel_offset
        return high_val
