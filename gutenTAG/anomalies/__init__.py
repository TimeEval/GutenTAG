from enum import Enum
from typing import List, Optional, Union, Any


def list_or_wrap(value: Union[Any, List[Any]]) -> List[Any]:
    if not isinstance(value, List):
        value = [value]
    return value


class Position(Enum):
    Beginning = "beginning"
    Middle = "middle"
    End = "end"


class AnomalyExtremum:
    def __init__(self, factor: float, local: bool = False, context_window: int = 5):
        self.factor = factor
        self.local = local
        self.context_window = context_window

    @staticmethod
    def Global(factor: float) -> 'AnomalyExtremum':
        return AnomalyExtremum(factor, local=False)

    @staticmethod
    def Local(factor: float, context_window: int = 5) -> 'AnomalyExtremum':
        return AnomalyExtremum(factor, local=True, context_window=context_window)


class AnomalyFrequency:
    def __init__(self, factor: float):
        self.factor = factor


class AnomalyPlatform:
    def __init__(self, value: float):
        self.value = value


class AnomalyPattern:
    def __init__(self):
        raise NotImplementedError()


class AnomalyMean:
    def __init__(self, offset: float):
        self.offset = offset


class AnomalyVariance:
    def __init__(self, factor: float):
        self.factor = factor


class AnomalyPatternShift:
    def __init__(self, shift_factor: float):
        self.shift_factor = shift_factor


class Anomaly:
    """This class acts like a generator graph, that collects all options in the beginning and,
    while being injected to a BaseOscillation, performs the changes."""

    def __init__(self,
                 position: Position,
                 anomaly_length: int):
        self.position = position
        self.anomaly_lengths = anomaly_length

        # kinds
        self.anomaly_extremum: Optional[AnomalyExtremum] = None
        self.anomaly_frequency: Optional[AnomalyFrequency] = None
        self.anomaly_platform: Optional[AnomalyPlatform] = None
        self.anomaly_pattern: Optional[AnomalyPattern] = None
        self.anomaly_mean: Optional[AnomalyMean] = None
        self.anomaly_variance: Optional[AnomalyVariance] = None
        self.anomaly_pattern_shift: Optional[AnomalyPatternShift] = None

    def set_extrema(self, anomaly_extremum: AnomalyExtremum) -> 'Anomaly':
        self.anomaly_extremum = anomaly_extremum
        return self

    def set_frequencies(self, anomaly_frequency: AnomalyFrequency) -> 'Anomaly':
        self.anomaly_frequency = anomaly_frequency
        return self

    def set_platform(self, anomaly_platform: AnomalyPlatform) -> 'Anomaly':
        self.anomaly_platform = anomaly_platform
        return self

    def set_pattern(self, anomaly_pattern: AnomalyPattern) -> 'Anomaly':
        self.anomaly_pattern = anomaly_pattern
        return self

    def set_mean(self, anomaly_mean: AnomalyMean) -> 'Anomaly':
        self.anomaly_mean = anomaly_mean
        return self

    def set_variance(self, anomaly_variance: AnomalyVariance) -> 'Anomaly':
        self.anomaly_variance = anomaly_variance
        return self

    def set_pattern_shift(self, anomaly_pattern_shift: AnomalyPatternShift) -> 'Anomaly':
        self.anomaly_pattern_shift = anomaly_pattern_shift
        return self
