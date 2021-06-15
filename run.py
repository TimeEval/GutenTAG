import argparse
import sys
from gutenTAG.generator import GutenTAG
from gutenTAG.base_oscillations import BaseOscillation

TITLE = "A good Timeseries Anomaly Generator. Guten Tag!"


def generate_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=TITLE)

    parser.add_argument('--base-oscillation', type=BaseOscillation, default=BaseOscillation.Sinus,
                        help="Choices: [sinus, random_walk, cylinder_bell_funnel, ecg, comut]")

    parser.add_argument('--base-length', type=int, default=10000,
                        help="Length of the Timeseries")

    parser.add_argument('--base-channels', type=int, default=1,
                        help="Number of Channels")

    parser.add_argument('--base-frequency', type=float, default=20.,
                        help="Frequency for base oscillation")

    parser.add_argument('--base-amplitude', type=float, default=1.,
                        help="Amplitude for base oscillation")

    parser.add_argument('--base-variance', type=float, default=1.,
                        help="Variance for CBF base oscillation")

    parser.add_argument('--base-avg-pattern-length', type=int, default=10,
                        help="Average pattern length for CBF base oscillation")

    parser.add_argument('--base-variance-pattern-length', type=int, default=10,
                        help="Variance pattern length for CBF base oscillation")

    parser.add_argument('--base-heart-rate', type=int, default=60,
                        help="Heart rate for ECG base oscillation")

    parser.add_argument('--plot', type=bool, default=False,
                        help="Whether the generated Timeseries should be plotted!")

    return parser.parse_args(sys.argv[1:])


if __name__ == '__main__':
    args = generate_args()
    GutenTAG(args)
