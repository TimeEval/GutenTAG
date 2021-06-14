from enum import Enum
from typing import Optional, Any
from sklearn.preprocessing import MinMaxScaler
import numpy as np


def get_or_error(name: str, value: Optional[Any]) -> Any:
    if value is None:
        raise ValueError(f"Parameter {name} for the base-oscillation must be set!")
    return value


class BaseOscillation(Enum):
    Sinus = "sinus"
    RandomWalk = "random_walk"
    CylinderBellFunnel = "cylinder_bell_funnel"
    ECG = "ecg"

    def generate(self, length: int, frequency: Optional[float] = None, amplitude: float = 1., channels: int = 1) -> np.ndarray:
        if self == BaseOscillation.Sinus:
            frequency = get_or_error("frequency", frequency)
            end = 2 * np.pi * frequency
            base_ts = np.arange(0, end, end / length).reshape(length, 1)
            base_ts = np.repeat(base_ts, repeats=channels, axis=1)
            return np.sin(base_ts) * amplitude
        elif self == BaseOscillation.RandomWalk:
            origin = np.zeros((1, channels))
            steps = np.random.choice([-1., 0., 1.], size=(length, channels))
            ts = np.concatenate([origin, steps]).cumsum(0)
            return MinMaxScaler(feature_range=[-amplitude, amplitude]).fit_transform(ts / np.abs(ts).max())
        elif self == BaseOscillation.CylinderBellFunnel:
            pass
        else: # self == BaseOscillation.ECG
            pass
