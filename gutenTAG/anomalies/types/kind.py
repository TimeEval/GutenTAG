from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict

from . import AnomalyProtocol
from .extremum import AnomalyExtremum
from .frequency import AnomalyFrequency
from .platform import AnomalyPlatform
from .variance import AnomalyVariance
from .mean import AnomalyMean
from .pattern import AnomalyPattern
from .pattern_shift import AnomalyPatternShift


def exist_together(list_optionals: List[Optional]) -> bool:
    return all(list(map(lambda x: x is not None, list_optionals)))


class AnomalyKind(Enum):
    Extremum = "extremum"
    Frequency = "frequency"
    Mean = "mean"
    Pattern = "pattern"
    PatternShift = "pattern-shift"
    Platform = "platform"
    Variance = "variance"

    def set_parameters(self, parameters: Dict) -> AnomalyKind:
        self.parameters = parameters
        return self

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if self == AnomalyKind.Platform:
            anomaly = AnomalyPlatform(AnomalyPlatform.get_parameter_class()(**self.parameters))
        elif self == AnomalyKind.Frequency:
            anomaly = AnomalyFrequency(AnomalyFrequency.get_parameter_class()(**self.parameters))
        elif self == AnomalyKind.Extremum:
            anomaly = AnomalyExtremum(AnomalyExtremum.get_parameter_class()(**self.parameters))
        elif self == AnomalyKind.Variance:
            anomaly = AnomalyVariance(AnomalyVariance.get_parameter_class()(**self.parameters))
        elif self == AnomalyKind.Mean:
            anomaly = AnomalyMean(AnomalyMean.get_parameter_class()(**self.parameters))
        elif self == AnomalyKind.Pattern:
            anomaly = AnomalyPattern(AnomalyPattern.get_parameter_class()(**self.parameters))
        elif self == AnomalyKind.PatternShift:
            anomaly = AnomalyPatternShift(AnomalyPatternShift.get_parameter_class()(**self.parameters))
        else:
            raise ValueError(f"AnomalyKind {self.value} is not supported, yet! Guten Tag!")

        return anomaly.generate(anomaly_protocol)

    @staticmethod
    def validate(anomalies: List[AnomalyKind]):
        forbidden_pairs = [
            (AnomalyKind.Platform, AnomalyKind.Extremum),
            (AnomalyKind.Platform, AnomalyKind.Frequency),
            (AnomalyKind.Platform, AnomalyKind.Pattern),
            (AnomalyKind.Platform, AnomalyKind.Mean),
            (AnomalyKind.Platform, AnomalyKind.PatternShift),
        ]
        raise ValueError("The combination of anomaly options for this anomaly is not supported. Guten Tag!")
