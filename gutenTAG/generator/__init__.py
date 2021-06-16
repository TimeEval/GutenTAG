import argparse
from typing import Optional
import numpy as np
import matplotlib.pyplot as plt

from ..base_oscillations import BaseOscillation
from ..anomalies import Anomaly, AnomalyPlatform, Position


class GutenTAG:
    def __init__(self, **kwargs):
        print(kwargs)

        self.timeseries: Optional[np.ndarray] = None
        self.args = kwargs

        self._generate_base_oscillation()
        self._plot()

    def _generate_base_oscillation(self):
        anomalies = []
        anomalies = [Anomaly(Position.End, 200).set_platform(AnomalyPlatform(0.0))]
        self.timeseries = \
            BaseOscillation.from_key(self.args["base_oscillation"], **self.args).inject_anomalies(anomalies).generate()

    def _plot(self):
        if self.args["plot"]:
            plt.plot(self.timeseries)
            plt.show()
