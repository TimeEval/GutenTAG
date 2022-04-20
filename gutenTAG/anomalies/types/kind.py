from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict

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


def exist_together(list_optionals: List[Optional[AnomalyKind]]) -> bool:
    return all(list(map(lambda x: x is not None, list_optionals)))


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

    def create(self, parameters: Dict) -> 'BaseAnomaly':
        if self == AnomalyKind.Platform:
            anomaly: BaseAnomaly = AnomalyPlatform(AnomalyPlatform.get_parameter_class()(**parameters))
        elif self == AnomalyKind.Frequency:
            anomaly = AnomalyFrequency(AnomalyFrequency.get_parameter_class()(**parameters))
        elif self == AnomalyKind.Extremum:
            anomaly = AnomalyExtremum(AnomalyExtremum.get_parameter_class()(**parameters))
        elif self == AnomalyKind.Variance:
            anomaly = AnomalyVariance(AnomalyVariance.get_parameter_class()(**parameters))
        elif self == AnomalyKind.Mean:
            anomaly = AnomalyMean(AnomalyMean.get_parameter_class()(**parameters))
        elif self == AnomalyKind.Pattern:
            anomaly = AnomalyPattern(AnomalyPattern.get_parameter_class()(**parameters))
        elif self == AnomalyKind.PatternShift:
            anomaly = AnomalyPatternShift(AnomalyPatternShift.get_parameter_class()(**parameters))
        elif self == AnomalyKind.Amplitude:
            anomaly = AnomalyAmplitude(AnomalyAmplitude.get_parameter_class()(**parameters))
        elif self == AnomalyKind.Trend:
            anomaly = AnomalyTrend(AnomalyTrend.get_parameter_class()(**parameters))
        elif self == AnomalyKind.ModeCorrelation:
            anomaly = AnomalyModeCorrelation(AnomalyModeCorrelation.get_parameter_class()())
        else:
            raise ValueError(f"AnomalyKind {self.value} is not supported, yet! Guten Tag!")

        return anomaly

    @classmethod
    def has_value(cls, v: str) -> bool:
        values = set(item.value for item in cls)
        return v in values
