from dataclasses import dataclass
from typing import Type

import numpy as np

from . import BaseAnomaly
from .. import AnomalyProtocol
from ...utils.types import BaseOscillationKind


@dataclass
class AnomalyPatternShiftParameters:
    shift_by: int = 5
    transition_window: int = 10


class AnomalyPatternShift(BaseAnomaly):
    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind in [BaseOscillationKind.Sinus, BaseOscillationKind.ECG]:
            assert abs(self.shift_by) <= self.transition_window, \
                "The parameter 'shift_by' must not be larger than 'transition_window' in absolute terms! Guten Tag!"

            base = anomaly_protocol.base_oscillation

            subsequence = base.timeseries[anomaly_protocol.start:anomaly_protocol.end, anomaly_protocol.channel]
            transition_start = np.interp(np.linspace(0, self.transition_window, self.transition_window + self.shift_by),
                                         np.arange(self.transition_window), subsequence[:self.transition_window])
            shifted = subsequence[self.transition_window:-self.transition_window]
            transition_end = np.interp(np.linspace(0, self.transition_window, self.transition_window - self.shift_by),
                                       np.arange(self.transition_window), subsequence[-self.transition_window:])

            subsequence = np.concatenate([
                transition_start,
                shifted,
                transition_end
            ])

            anomaly_protocol.subsequences.append(subsequence)
        else:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind.name)
        return anomaly_protocol

    @staticmethod
    def get_parameter_class() -> Type[AnomalyPatternShiftParameters]:
        return AnomalyPatternShiftParameters

    def __init__(self, parameters: AnomalyPatternShiftParameters):
        super().__init__()
        self.shift_by = parameters.shift_by
        self.transition_window = parameters.transition_window
