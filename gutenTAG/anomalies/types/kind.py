from enum import Enum
from typing import Any, Dict

from .amplitude import AnomalyAmplitude
from .extremum import AnomalyExtremum
from .frequency import AnomalyFrequency
from .mean import AnomalyMean
from .mode_correlation import AnomalyModeCorrelation
from .pattern import AnomalyPattern
from .pattern_shift import AnomalyPatternShift
from .platform import AnomalyPlatform
from .trend import AnomalyTrend
from .variance import AnomalyVariance
from .. import BaseAnomaly
from ...utils.global_variables import ANOMALY_TYPE_NAMES


class AnomalyKind(Enum):
    Extremum = ANOMALY_TYPE_NAMES.EXTREMUM
    Frequency = ANOMALY_TYPE_NAMES.FREQUENCY
    Mean = ANOMALY_TYPE_NAMES.MEAN
    Pattern = ANOMALY_TYPE_NAMES.PATTERN
    PatternShift = ANOMALY_TYPE_NAMES.PATTERN_SHIFT
    Platform = ANOMALY_TYPE_NAMES.PLATFORM
    Variance = ANOMALY_TYPE_NAMES.VARIANCE
    Amplitude = ANOMALY_TYPE_NAMES.AMPLITUDE
    Trend = ANOMALY_TYPE_NAMES.TREND
    ModeCorrelation = ANOMALY_TYPE_NAMES.MODE_CORRELATION

    def create(self, parameters: Dict[str, Any]) -> BaseAnomaly:  # noqa: C901
        if self == AnomalyKind.Platform:
            return self._instantiate_anomaly(AnomalyPlatform, parameters)
        elif self == AnomalyKind.Frequency:
            return self._instantiate_anomaly(AnomalyFrequency, parameters)
        elif self == AnomalyKind.Extremum:
            return self._instantiate_anomaly(AnomalyExtremum, parameters)
        elif self == AnomalyKind.Variance:
            return self._instantiate_anomaly(AnomalyVariance, parameters)
        elif self == AnomalyKind.Mean:
            return self._instantiate_anomaly(AnomalyMean, parameters)
        elif self == AnomalyKind.Pattern:
            return self._instantiate_anomaly(AnomalyPattern, parameters)
        elif self == AnomalyKind.PatternShift:
            return self._instantiate_anomaly(AnomalyPatternShift, parameters)
        elif self == AnomalyKind.Amplitude:
            return self._instantiate_anomaly(AnomalyAmplitude, parameters)
        elif self == AnomalyKind.Trend:
            return self._instantiate_anomaly(AnomalyTrend, parameters)
        elif self == AnomalyKind.ModeCorrelation:
            return self._instantiate_anomaly(AnomalyModeCorrelation, parameters)
        else:
            raise ValueError(
                f"AnomalyKind {self.value} is not supported, yet! Guten Tag!"
            )

    @staticmethod
    def _instantiate_anomaly(cls, parameters: Dict[str, Any]) -> BaseAnomaly:
        return cls(cls.get_parameter_class()(**parameters))

    @classmethod
    def has_value(cls, v: str) -> bool:
        values = set(item.value for item in cls)
        return v in values
