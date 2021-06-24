import os
import sys
import argparse
from pathlib import Path
from typing import List
import numpy as np
import pandas as pd
import importlib

from gutenTAG import GutenTAG
from gutenTAG.generator import Overview
from gutenTAG.addons import BaseAddOn


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
        SAVE_DIR = os.path.join(args.output_dir, str(i))
        os.makedirs(SAVE_DIR, exist_ok=True)
        train = pd.DataFrame(ts.train_timeseries)
        test = pd.DataFrame(ts.timeseries)
        train_labels = ts.train_labels
        labels = ts.labels

        if not train.empty:
            if train_labels is not None:
                train["is_anomaly"] = train_labels
            train.to_csv(os.path.join(SAVE_DIR, "train.csv"), sep=",")

        if labels is not None:
            test["is_anomaly"] = labels
        test.to_csv(os.path.join(SAVE_DIR, "test.csv"), sep=",")


def set_random_seed(args: argparse.Namespace):
    import random
    np.random.seed(args.seed)
    random.seed(args.seed)


def import_addons(addons: List[str]) -> List[BaseAddOn]:
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
        addon_o = addon()
        addon_o.process_overview(overview=overview, args=args)
        addon_o.process_generators(generators=generators, args=args)
