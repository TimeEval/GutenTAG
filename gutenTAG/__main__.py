import argparse
import sys
from pathlib import Path
from typing import List

from ._version import __version__
from .gutenTAG import GutenTAG


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GutenTAG! A good Time series Anomaly Generator.")

    parser.add_argument("--version", action="store_true", help="Display GutenTAG version and exit.")
    parser.add_argument("--config-yaml", type=Path, required=True, help="Path to config YAML")
    parser.add_argument("--output-dir", type=Path, default=Path("./generated-timeseries"),
                        help="Path to output directory")
    parser.add_argument("--plot", action="store_true", help="Plot every generated time series.")
    parser.add_argument("--no-save", action="store_true",
                        help="Prevent GutenTAG from saving the generated time series.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--addons", nargs="*", default=[], help="Use Add-Ons for generating time series.")
    parser.add_argument("--n_jobs", "--n-jobs", type=int, default=1,
                        help="Number of time series to generate in parallel.")
    parser.add_argument("--only", type=str, help="Process only timeseries with the defined name.")

    return parser.parse_args(args)


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
    if args.no_save:
        output = None
    else:
        output = Path(args.output_dir)

    gutentag = GutenTAG.from_yaml(
        args.config_yaml,
        n_jobs=args.n_jobs,
        seed=args.seed,
        addons=args.addons,
        only=args.only
    )

    gutentag.generate(
        return_timeseries=False,
        output_folder=output,
        plot=args.plot
    )


def cli() -> None:
    main(sys.argv[1:])


if __name__ == "__main__":
    cli()
