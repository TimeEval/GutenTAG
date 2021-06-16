import numpy as np

from . import BaseAnomaly, AnomalyProtocol


class AnomalyPlatform(BaseAnomaly):
    def __init__(self, value: float):
        self.value = value

    def generate(self, anomaly_protocol: AnomalyProtocol) -> AnomalyProtocol:
        values = np.zeros(anomaly_protocol.end - anomaly_protocol.start) + self.value
        anomaly_protocol.subsequence = values
        return anomaly_protocol
