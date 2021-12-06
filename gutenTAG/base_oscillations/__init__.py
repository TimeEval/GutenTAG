from typing import Optional, Any, List, Dict, Type

from .interface import BaseOscillationInterface
from .polynomial import Polynomial
from .sine import Sine
from .random_walk import RandomWalk
from .cylinder_bell_funnel import CylinderBellFunnel
from .ecg import ECG
from .random_mode_jump import RandomModeJump


def get_or_error(name: str, value: Optional[Any]) -> Any:
    if value is None:
        raise ValueError(f"Parameter {name} for the base-oscillation must be set!")
    return value


class BaseOscillation:
    key_mapping: Dict[str, Type[BaseOscillationInterface]] = {
        "sine": Sine,
        "random_walk": RandomWalk,
        "cylinder_bell_funnel": CylinderBellFunnel,
        "ecg": ECG,
        "polynomial": Polynomial,
        "random_mode_jump": RandomModeJump
    }

    @staticmethod
    def from_key(key: str, *args, **kwargs) -> BaseOscillationInterface:
        return BaseOscillation.key_mapping[key](*args, **kwargs)
