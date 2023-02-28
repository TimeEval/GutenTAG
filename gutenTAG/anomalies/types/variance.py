from dataclasses import dataclass
from typing import Type

from . import BaseAnomaly
from .. import AnomalyProtocol
from ...base_oscillations import CylinderBellFunnel, RandomModeJump


@dataclass
class AnomalyVarianceParameters:
    variance: float = 0.0


class AnomalyVariance(BaseAnomaly):
    def __init__(self, parameters: AnomalyVarianceParameters):
        super().__init__()
        self.variance = parameters.variance

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        base = anomaly_protocol.base_oscillation
        if anomaly_protocol.base_oscillation_kind == RandomModeJump.KIND:
            self.logger.warn_false_combination(self.__class__.__name__, anomaly_protocol.base_oscillation_kind)

        elif anomaly_protocol.base_oscillation_kind == CylinderBellFunnel.KIND:
            subsequence = base.generate_only_base(
                anomaly_protocol.ctx.to_bo(),
                variance=self.variance
            )[anomaly_protocol.start:anomaly_protocol.end]
            anomaly_protocol.subsequences.append(subsequence)

        else:
            length = anomaly_protocol.end - anomaly_protocol.start
            variance_diff = self.variance - base.variance
            creeping = self.generate_creeping(anomaly_protocol) * variance_diff + base.variance  # from 0 to variance_diff
            creeping /= self.variance * base.amplitude  # get relative transition from base variance to anomaly variance
            subsequence_noise = base.generate_noise(anomaly_protocol.ctx.to_bo(), self.variance * base.amplitude, length)
            base.noise[anomaly_protocol.start:anomaly_protocol.end] = subsequence_noise * creeping
        return anomaly_protocol

    @property
    def requires_period_start_position(self) -> bool:
        return False

    @staticmethod
    def get_parameter_class() -> Type[AnomalyVarianceParameters]:
        return AnomalyVarianceParameters
