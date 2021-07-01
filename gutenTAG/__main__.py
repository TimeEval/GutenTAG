import argparse
import importlib
import os
import sys
import warnings
from pathlib import Path
from typing import List, Type, Tuple, Union, Optional

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm

from gutenTAG import GutenTAG
from gutenTAG.addons import BaseAddOn
from gutenTAG.generator import Overview
from gutenTAG.utils.tqdm_joblib import tqdm_joblib


SUPERVISED_FILENAME = "train_anomaly.csv"
SEMI_SUPERVISED_FILENAME = "train_no_anomaly.csv"
UNSUPERVISED_FILENAME = "test.csv"


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GutenTAG! A good Time series Anomaly Generator.")

    parser.add_argument("--config-yaml", type=Path, required=True, help="Path to config YAML")
    parser.add_argument("--output-dir", type=Path, default=Path("./generated-timeseries"), help="Path to output directory")
    parser.add_argument("--plot", action="store_true", help="Plot every generated time series.")
    parser.add_argument("--no-save", action="store_true", help="Prevent GutenTAG from saving the generated time series.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--addons", nargs="*", default=[], help="Use Add-Ons for generating time series.")
    parser.add_argument("--n_jobs", "--n-jobs", type=int, default=1, help="Number of time series to generate in parallel.")
    parser.add_argument("--only", type=str, help="Process only timeseries with the defined name.")

    return parser.parse_args(args)


def _create_ts_df(ts: np.ndarray, labels: Optional[np.ndarray] = None) -> pd.DataFrame:
    if labels is None:
        labels = 0.0
    channel_names = list(map(lambda i: f"value-{i}", range(ts.shape[1])))
    df = pd.DataFrame(ts, columns=channel_names)
    df.index.name = "timestamp"
    df["is_anomaly"] = labels
    return df


def save_timeseries(timeseries: List[GutenTAG], overview: Overview, args: argparse.Namespace):
    os.makedirs(args.output_dir, exist_ok=True)
    overview.save_to_output_dir(args.output_dir)

    for i, ts in tqdm(enumerate(timeseries), desc="Saving datasets to disk", total=len(timeseries)):
        title = ts.base_oscillation.name or str(i)
        save_dir = os.path.join(args.output_dir, title)
        os.makedirs(save_dir, exist_ok=True)

        test = _create_ts_df(ts.timeseries, ts.labels)
        test.to_csv(os.path.join(save_dir, UNSUPERVISED_FILENAME), sep=",", index=True)

        if ts.supervised:
            supervised = _create_ts_df(ts.supervised_timeseries, ts.train_labels)
            supervised.to_csv(os.path.join(save_dir, SUPERVISED_FILENAME), sep=",", index=True)

        if ts.semi_supervised:
            semi_supervised = _create_ts_df(ts.semi_supervised_timeseries)
            semi_supervised.to_csv(os.path.join(save_dir, SEMI_SUPERVISED_FILENAME), sep=",", index=True)


def set_random_seed(args: argparse.Namespace):
    import random
    np.random.seed(args.seed)
    random.seed(args.seed)


def import_addons(addons: List[str]) -> List[Type[BaseAddOn]]:
    module_classes = [addon.rsplit(".", 1) for addon in addons]

    classes = [importlib.import_module(package).__dict__[cls] for package, cls in module_classes]
    return [cls for cls in classes if issubclass(cls, BaseAddOn)]


def generate_all(args: argparse.Namespace) -> Tuple[List[GutenTAG], Overview]:
    generators, overview = GutenTAG.from_yaml(args.config_yaml, args.plot, args.only)
    n_jobs = args.n_jobs
    if n_jobs != 1 and args.plot:
        warnings.warn(f"Cannot generate time series in parallel while plotting ('n_jobs' was set to {n_jobs})! Falling "
                      f"back to serial generation.")
        n_jobs = 1

    with tqdm_joblib(tqdm(desc="Generating datasets", total=len(generators))):
        generators = Parallel(n_jobs=n_jobs)(
            delayed(g.generate)() for g in generators
        )
    return generators, overview


def main(args: List[str]) -> None:
    args = parse_args(args)
    addons = import_addons(args.addons)
    print(
        """

                    Welcome to

       _____       _          _______       _____ _
      / ____|     | |        |__   __|/\   / ____| |
     | |  __ _   _| |_ ___ _ __ | |  /  \ | |  __| |
     | | |_ | | | | __/ _ \ '_ \| | / /\ \| | |_ | |
     | |__| | |_| | ||  __/ | | | |/ ____ \ |__| |_|
      \_____|\__,_|\__\___|_| |_|_/_/    \_\_____(_)

"Good day!" wishes your friendly Timeseries Anomaly Generator.


"""
    )
    if args.seed is not None:
        set_random_seed(args)
    generators, overview = generate_all(args)

    if args.no_save:
        exit(0)
    save_timeseries(generators, overview, args)

    for addon in tqdm(addons, desc="Executing addons"):
        addon().process(overview=overview, generators=generators, args=args)


if __name__ == "__main__":
    main(sys.argv[1:])
