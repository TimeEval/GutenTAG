import argparse
import sys
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional

from variations.base_oscillations import BaseOscillation

TITLE = "A good Timeseries Anomaly Generator."


def generate_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=TITLE)

    parser.add_argument('--base-oscillation', type=BaseOscillation,
                        help="Choices: [sinus, random_walk, cylinder_bell_funnel, ecg]")

    parser.add_argument('--base-length', type=int, default=10000,
                        help="Length of the Timeseries")

    parser.add_argument('--base-channels', type=int, default=1,
                        help="Number of Channels")

    parser.add_argument('--base-frequency', type=float,
                        help="Frequency for base oscillation")

    parser.add_argument('--base-amplitude', type=float, default=1.,
                        help="Amplitude for base oscillation")

    parser.add_argument('--plot', type=bool, default=False,
                        help="Whether the generated Timeseries should be plotted!")


    return parser.parse_args(sys.argv[1:])


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
                                                              self.args.base_channels)

    def _plot(self):
        if self.args.plot:
            plt.plot(self.timeseries)
            plt.show()


if __name__ == '__main__':
    args = generate_args()
    GutenTAG(args)
