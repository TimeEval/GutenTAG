from dataclasses import dataclass
from typing import Type

from . import BaseAnomaly
from .. import AnomalyProtocol
from ...base_oscillations import RandomModeJump


@dataclass
class AnomalyModeCorrelationParameters:
    pass


class AnomalyModeCorrelation(BaseAnomaly):
    def __init__(self, parameters: AnomalyModeCorrelationParameters):
        super().__init__()

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        if anomaly_protocol.base_oscillation_kind == RandomModeJump.KIND:
            timeseries = anomaly_protocol.base_oscillation.timeseries
            subsequence = timeseries[anomaly_protocol.start:anomaly_protocol.end] * -1
            anomaly_protocol.subsequences.append(subsequence)
        else:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind)
            self.logger.warning("A `mode_correlation` anomaly can be injected in only a `random_mode_jump` base oscillation!")
        return anomaly_protocol

    @property
    def requires_period_start_position(self) -> bool:
        return True

    @staticmethod
    def get_parameter_class() -> Type[AnomalyModeCorrelationParameters]:
        return AnomalyModeCorrelationParameters
