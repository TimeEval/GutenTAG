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


def find_trend_anomalies(obj: Dict) -> Dict:
    for anomaly in obj.get("anomalies", []):
        for kind in anomaly.get("kinds", []):
            if kind.get("name", "") == "trend":
                kind["parameters"]["trend"] = decode_trend_obj(kind.get("parameters", {}).get("trend", {}))
    return obj


def decode_trend_obj(trend: Dict) -> Optional[BaseOscillationInterface]:
    trend_key = trend.get("kind", None)
    return BaseOscillation.from_key(trend_key, **trend) if trend_key else None


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
        trend = kwargs.get("trend", {})
        kwargs["trend"] = decode_trend_obj(trend)
        return BaseOscillation.key_mapping[key](*args, **kwargs)
