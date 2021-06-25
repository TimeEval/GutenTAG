from typing import Optional, Any, List, Dict, Type

from .interface import BaseOscillationInterface
from .polynomial import Polynomial
from .sinus import Sinus
from .random_walk import RandomWalk
from .cylinder_bell_funnel import CylinderBellFunnel
from .ecg import ECG


def get_or_error(name: str, value: Optional[Any]) -> Any:
    if value is None:
        raise ValueError(f"Parameter {name} for the base-oscillation must be set!")
    return value


class BaseOscillation:
    key_mapping: Dict[str, Type[BaseOscillationInterface]] = {
        "sinus": Sinus,
        "random_walk": RandomWalk,
        "cylinder_bell_funnel": CylinderBellFunnel,
        "ecg": ECG,
        "polynomial": Polynomial
    }

    @staticmethod
    def from_key(key: str, *args, **kwargs) -> BaseOscillationInterface:
        return BaseOscillation.key_mapping[key](*args, **kwargs)
