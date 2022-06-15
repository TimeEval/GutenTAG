import logging
from dataclasses import dataclass
from typing import Type

from . import BaseAnomaly
from .. import AnomalyProtocol
from ...utils.base_oscillation_kind import BaseOscillationKind


@dataclass
class AnomalyModeCorrelationParameters:
    pass


class AnomalyModeCorrelation(BaseAnomaly):
    def __init__(self, parameters: AnomalyModeCorrelationParameters):
        super().__init__()

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        base = anomaly_protocol.base_oscillation
        if anomaly_protocol.base_oscillation_kind == BaseOscillationKind.RandomModeJump:
            timeseries = base.timeseries
            subsequence = timeseries[anomaly_protocol.start:anomaly_protocol.end] * -1
            anomaly_protocol.subsequences.append(subsequence)
        else:
            logging.warning("A `mode_correlation` anomaly can be injected in only a `random_mode_jump` base oscillation!")
        return anomaly_protocol

    @staticmethod
    def get_parameter_class() -> Type[AnomalyModeCorrelationParameters]:
        return AnomalyModeCorrelationParameters
