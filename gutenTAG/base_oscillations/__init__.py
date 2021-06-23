from typing import Optional, Any, List, Dict, Type

from .interface import BaseOscillationInterface
from .sinus import Sinus
from .random_walk import RandomWalk
from .cylinder_bell_funnel import CylinderBellFunnel
from .ecg import ECG
from .comut import CorrelatedMultivarGenerator



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
        #"comut": CoMuT,
    }

    @staticmethod
    def Sinus(*args, **kwargs) -> Sinus:
        return Sinus(*args, **kwargs)

    @staticmethod
    def RandomWalk(*args, **kwargs) -> RandomWalk:
        return RandomWalk(*args, **kwargs)

    @staticmethod
    def CylinderBellFunnel(*args, **kwargs) -> CylinderBellFunnel:
        return CylinderBellFunnel(*args, **kwargs)

    @staticmethod
    def ECG(*args, **kwargs) -> ECG:
        return ECG(*args, **kwargs)

    """
    @staticmethod
    def CoMuT(*args, **kwargs) -> CoMuT:
        return CoMuT(*args, **kwargs)
    """

    @staticmethod
    def from_key(key: str, *args, **kwargs) -> BaseOscillationInterface:
        return BaseOscillation.key_mapping[key](*args, **kwargs)

    """
    def generate(self, length: int, frequency: float = 10., amplitude: float = 1., channels: int = 1,
                 variance: float = 1, avg_pattern_length: int = 10, variance_pattern_length: int = 10, heart_rate: int = 60) -> np.ndarray:
        if self == BaseOscillation.Sinus:

        elif self == BaseOscillation.RandomWalk:
            
        elif self == BaseOscillation.CylinderBellFunnel:
            ts = []
            for channel in range(channels):
                ts.append(generate_pattern_data(length, avg_pattern_length, amplitude,
                default_variance=variance, variance_pattern_length=variance_pattern_length))
            return np.column_stack(ts)
        elif self == BaseOscillation.ECG:
            ts = []
            for channel in range(channels):
                
                ts.append(ecg)
            return np.column_stack(ts)
        elif self == BaseOscillation.CoMuT:
            #CorrelatedMultivarGenerator(
             #   length=length,
             #   dimensions=channels,
             #   step_length=int(frequency),
             #   value_diff=int(amplitude),
             #   value_offset=,
             #   dimensions_involved=,
             #   std=
            #)
            pass
        else:
            raise ValueError(f"The Base Oscillation '{self.name}' is not yet supported! Guten Tag!")
    """
