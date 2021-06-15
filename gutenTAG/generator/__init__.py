import argparse
from typing import Optional
import numpy as np
import matplotlib.pyplot as plt


class GutenTAG:
    def __init__(self, args: argparse.Namespace):
        print(args)

        self.timeseries: Optional[np.ndarray] = None
        self.args = args

        self._generate_base_oscillation()
        self._plot()

    def _generate_base_oscillation(self):
        self.timeseries = self.args.base_oscillation.generate(self.args.base_length,
                                                              self.args.base_frequency,
                                                              self.args.base_amplitude,
                                                              self.args.base_channels,
                                                              self.args.base_variance,
                                                              self.args.base_avg_pattern_length,
                                                              self.args.base_variance_pattern_length,
                                                              self.args.base_heart_rate)

    def _plot(self):
        if self.args.plot:
            plt.plot(self.timeseries)
            plt.show()
