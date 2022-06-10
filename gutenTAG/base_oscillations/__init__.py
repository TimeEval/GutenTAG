from typing import Optional, Any, Dict, Type

from .cylinder_bell_funnel import CylinderBellFunnel
from .ecg import ECG
from .formula import Formula  # type: ignore  # mypy ends up in recursion
from .interface import BaseOscillationInterface
from .polynomial import Polynomial
from .random_mode_jump import RandomModeJump
from .random_walk import RandomWalk
from .sine import Sine
from ..utils.global_variables import BASE_OSCILLATION_NAMES


def get_or_error(name: str, value: Optional[Any]) -> Any:
    if value is None:
        raise ValueError(f"Parameter {name} for the base_oscillation must be set!")
    return value


class BaseOscillation:
    key_mapping: Dict[str, Type[BaseOscillationInterface]] = {
        BASE_OSCILLATION_NAMES.SINE: Sine,
        BASE_OSCILLATION_NAMES.RANDOM_WALK: RandomWalk,
        BASE_OSCILLATION_NAMES.CYLINDER_BELL_FUNNEL: CylinderBellFunnel,
        BASE_OSCILLATION_NAMES.ECG: ECG,
        BASE_OSCILLATION_NAMES.POLYNOMIAL: Polynomial,
        BASE_OSCILLATION_NAMES.RANDOM_MODE_JUMP: RandomModeJump,
        BASE_OSCILLATION_NAMES.FORMULA: Formula
    }

    @staticmethod
    def from_key(key: str, *args, **kwargs) -> BaseOscillationInterface:
        return BaseOscillation.key_mapping[key](*args, **kwargs)
