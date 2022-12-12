from typing import Optional

import numpy as np

from . import BaseOscillation
from .interface import BaseOscillationInterface
from ..utils.default_values import default_values
from ..utils.global_variables import BASE_OSCILLATION_NAMES, BASE_OSCILLATIONS, PARAMETERS
from ..utils.types import BOGenerationContext


class RandomModeJump(BaseOscillationInterface):
    KIND = BASE_OSCILLATION_NAMES.RANDOM_MODE_JUMP

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return self.frequency

    def get_period_size(self) -> Optional[int]:
        return int(self.length // self.frequency)

    def is_periodic(self) -> bool:
        """RandomModeJump has reoccurring modes but no fixed periodicity!"""
        return False

    def generate_only_base(self,
                           ctx: BOGenerationContext,
                           length: Optional[int] = None,
                           frequency: Optional[float] = None,
                           channel_diff: Optional[float] = None,
                           channel_offset: Optional[float] = None,
                           random_seed: Optional[int] = None,
                           *args, **kwargs) -> np.ndarray:
        length = length or self.length
        frequency = frequency or self.frequency
        channel_diff = channel_diff or self.channel_diff
        channel_offset = channel_offset or self.channel_offset
        random_seed = random_seed or self.random_seed

        return random_mode_jump(ctx, length, frequency, channel_diff, channel_offset, random_seed)


def _generate_random_steps(ctx: BOGenerationContext, length: int, step_length: int,
                           random_seed: Optional[int] = None) -> np.ndarray:
    rng = np.random.default_rng(BOGenerationContext.re_seed(random_seed, base_seed=ctx.seed))
    n_steps = int(np.ceil(length / step_length).item())
    energy = rng.choice([-1, 1], size=n_steps)
    base = np.repeat(energy, step_length)[:length].astype(np.float64)
    return base


def _generate_channel_amplitude(channel: int, channel_diff: float, channel_offset: float) -> float:
    high_val = (channel_diff * channel) + channel_offset
    return high_val


def random_mode_jump(ctx: BOGenerationContext = BOGenerationContext.default(),
                     length: int = default_values[BASE_OSCILLATIONS][PARAMETERS.LENGTH],
                     frequency: float = default_values[BASE_OSCILLATIONS][PARAMETERS.FREQUENCY],
                     channel_diff: float = default_values[BASE_OSCILLATIONS][PARAMETERS.CHANNEL_DIFF],
                     channel_offset: float = default_values[BASE_OSCILLATIONS][PARAMETERS.CHANNEL_OFFSET],
                     random_seed: Optional[int] = None) -> np.ndarray:
    step_length = int(length // frequency)

    base_random_steps = _generate_random_steps(ctx, length, step_length, random_seed)
    channel_amplitude = _generate_channel_amplitude(ctx.channel, channel_diff, channel_offset)
    ts = base_random_steps * channel_amplitude

    return ts


BaseOscillation.register(RandomModeJump.KIND, RandomModeJump)
