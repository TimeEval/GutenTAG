import os
import sys
import argparse
from pathlib import Path
from typing import List, Type
import numpy as np
import pandas as pd
import importlib

from gutenTAG import GutenTAG
from gutenTAG.generator import Overview
from gutenTAG.addons import BaseAddOn


SUPERVISED_FILENAME = "train_anomaly.csv"
SEMI_SUPERVISED_FILENAME = "train_no_anomaly.csv"
UNSUPERVISED_FILENAME = "test.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GutenTAG! A good Time series Anomaly Generator.")

    parser.add_argument("--config-yaml", type=Path, required=True, help="Path to config YAML")
    parser.add_argument("--output-dir", type=Path, default=Path("./generated-timeseries"), help="Path to output directory")
    parser.add_argument("--plot", action="store_true", help="Plot every generated time series.")
    parser.add_argument("--no-save", action="store_true", help="Prevent GutenTAG from saving the generated time series.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--addons", nargs="*", default=[], help="Use Add-Ons for generating time series.")

    return parser.parse_args(sys.argv[1:])


def save_timeseries(timeseries: List[GutenTAG], overview: Overview, args: argparse.Namespace):
    os.makedirs(args.output_dir, exist_ok=True)
    overview.save_to_output_dir(args.output_dir)

    for i, ts in enumerate(timeseries):
        title = ts.base_oscillation.name or str(i)
        SAVE_DIR = os.path.join(args.output_dir, title)
        os.makedirs(SAVE_DIR, exist_ok=True)
        semi_supervised = pd.DataFrame(ts.semi_supervised_timeseries)
        supervised = pd.DataFrame(ts.supervised_timeseries)
        test = pd.DataFrame(ts.timeseries)
        train_labels = ts.train_labels
        labels = ts.labels

        if not supervised.empty:
            if train_labels is not None:
                supervised["is_anomaly"] = train_labels
            else:
                supervised["is_anomaly"] = np.nan
            supervised.to_csv(os.path.join(SAVE_DIR, SUPERVISED_FILENAME), sep=",")

        if not semi_supervised.empty:
            semi_supervised["is_anomaly"] = 0
            semi_supervised.to_csv(os.path.join(SAVE_DIR, SEMI_SUPERVISED_FILENAME), sep=",")

        if labels is not None:
            test["is_anomaly"] = labels
        else:
            test["is_anomaly"] = 0
        test.to_csv(os.path.join(SAVE_DIR, UNSUPERVISED_FILENAME), sep=",")


def set_random_seed(args: argparse.Namespace):
    import random
    np.random.seed(args.seed)
    random.seed(args.seed)


def import_addons(addons: List[str]) -> List[Type[BaseAddOn]]:
    module_classes = [addon.rsplit(".", 1) for addon in addons]

    classes = [importlib.import_module(package).__dict__[cls] for package, cls in module_classes]
    return [cls for cls in classes if issubclass(cls, BaseAddOn)]


if __name__ == "__main__":
    args = parse_args()
    addons = import_addons(args.addons)
    if args.seed is not None:
        set_random_seed(args)
    generators, overview = GutenTAG.from_yaml(args.config_yaml, args.plot)

    if args.no_save:
        exit(0)
    save_timeseries(generators, overview, args)

    for addon in addons:
        addon().process(overview=overview, generators=generators, args=args)
