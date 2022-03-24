import argparse
import importlib
import sys
import warnings
from pathlib import Path
from typing import List, Type

import numpy as np
from tqdm import tqdm

from gutenTAG import GutenTAG
from gutenTAG.addons import BaseAddOn
from ._version import __version__


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GutenTAG! A good Time series Anomaly Generator.")

    parser.add_argument("--version", action="store_true", help="Display GutenTAG version and exit.")
    parser.add_argument("--config-yaml", type=Path, required=True, help="Path to config YAML")
    parser.add_argument("--output-dir", type=Path, default=Path("./generated-timeseries"), help="Path to output directory")
    parser.add_argument("--plot", action="store_true", help="Plot every generated time series.")
    parser.add_argument("--no-save", action="store_true", help="Prevent GutenTAG from saving the generated time series.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--addons", nargs="*", default=[], help="Use Add-Ons for generating time series.")
    parser.add_argument("--n_jobs", "--n-jobs", type=int, default=1, help="Number of time series to generate in parallel.")
    parser.add_argument("--only", type=str, help="Process only timeseries with the defined name.")

    return parser.parse_args(args)


def set_random_seed(args: argparse.Namespace):
    import random
    np.random.seed(args.seed)
    random.seed(args.seed)


def import_addons(addons: List[str]) -> List[Type[BaseAddOn]]:
    module_classes = [addon.rsplit(".", 1) for addon in addons]

    classes = [importlib.import_module(package).__dict__[cls] for package, cls in module_classes]
    return [cls for cls in classes if issubclass(cls, BaseAddOn)]


def generate_all(args: argparse.Namespace) -> GutenTAG:
    n_jobs = args.n_jobs
    if n_jobs != 1 and args.plot:
        warnings.warn(f"Cannot generate time series in parallel while plotting ('n_jobs' was set to {n_jobs})! Falling "
                      f"back to serial generation.")
        n_jobs = 1

    gutentag = GutenTAG.from_yaml(args.config_yaml, args.plot, args.only)
    gutentag.n_jobs = n_jobs
    gutentag.overview.add_seed(args.seed)

    gutentag.generate()

    return gutentag


def main(sys_args: List[str]) -> None:
    print(f"""

                      Welcome to

       _____       _          _______       _____ _
      / ____|     | |        |__   __|/\\   / ____| |
     | |  __ _   _| |_ ___ _ __ | |  /  \\ | |  __| |
     | | |_ | | | | __/ _ \\ '_ \\| | / /\\ \\| | |_ | |
     | |__| | |_| | ||  __/ | | | |/ ____ \\ |__| |_|
      \\_____|\\__,_|\\__\\___|_| |_|_/_/    \\_\\_____(_)

                     Version {__version__}

"Good day!" wishes your friendly Timeseries Anomaly Generator.


""")

    if "--version" in sys_args:
        return

    args = parse_args(sys_args)
    addons = import_addons(args.addons)
    if args.seed is not None:
        set_random_seed(args)
    gutentag = generate_all(args)

    if args.no_save:
        exit(0)

    gutentag.save_timeseries(Path(args.output_dir))

    for addon in tqdm(addons, desc="Executing addons"):
        addon().process(overview=gutentag.overview, gutenTAG=gutentag, args=args)


def cli() -> None:
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:])
