import os
import sys
import argparse
from pathlib import Path
from typing import List
import numpy as np

from gutenTAG import GutenTAG


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GutenTAG! A good Time series Anomaly Generator.")

    parser.add_argument("--config-yaml", type=Path, required=True, help="Path to config YAML")
    parser.add_argument("--output-dir", type=Path, default=Path("./generated-timeseries/"), help="Path to output directory")
    parser.add_argument("--no-save", action="store_true", help="Prevent GutenTAG from saving the generated time series.")

    return parser.parse_args(sys.argv[1:])


def save_timeseries(timeseries: List[GutenTAG], args: argparse.Namespace):
    os.makedirs(args.output_dir, exist_ok=True)

    for i, ts in enumerate(timeseries):
        SAVE_DIR = os.path.join(args.output_dir, str(i))
        os.makedirs(SAVE_DIR, exist_ok=True)
        train = ts.normal_timeseries
        test = ts.timeseries
        labels = ts.labels
        if train is not None:
            np.savetxt(os.path.join(SAVE_DIR, "train.csv"), train, delimiter=",")
        if labels is not None:
            test = np.hstack([test, labels.reshape(-1, 1)])
        np.savetxt(os.path.join(SAVE_DIR, "test.csv"), test, delimiter=",")


if __name__ == "__main__":
    args = parse_args()
    timeseries = GutenTAG.from_yaml(args.config_yaml)
    if args.no_save:
        exit(0)
    save_timeseries(timeseries, args)
