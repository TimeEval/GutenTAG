import os
import argparse
from typing import List, Dict

import numpy as np
import pandas as pd
from . import BaseAddOn
from .. import GutenTAG
from ..generator import Overview

columns = [
    "collection_name",
    "dataset_name",
    "train_path",
    "test_path",
    "dataset_type",
    "datetime_index",
    "split_at",
    "train_type",
    "train_is_normal",
    "input_type",
    "length",
    "dimensions",
    "contamination",
    "num_anomalies",
    "min_anomaly_length",
    "median_anomaly_length",
    "max_anomaly_length",
    "mean",
    "stddev",
    "trend",
    "stationarity"
]


class TimeEvalAddOn(BaseAddOn):
    def process_overview(self, overview: Overview, args: argparse.Namespace) -> Overview:
        for i, config in enumerate(overview.datasets):
            self._process_timeseries_overview(config, i, args)
        self._set_global_vals(args)
        return overview

    def process_generators(self, generators: List[GutenTAG], args: argparse.Namespace) -> List[GutenTAG]:
        for i, generator in enumerate(generators):
            self._process_timeseries_generator(generator, i, args)
        if args.no_save:
            return generators
        self.df.to_csv(os.path.join(args.output_dir, "datasets.csv"), index=False)
        return generators

    def _set_global_vals(self, args: argparse.Namespace):
        self.df["collection_name"] = "GutenTAG"
        self.df["dataset_type"] = "synthetic"
        self.df["datetime_index"] = False
        self.df["split_at"] = np.NAN
        self.df["train_is_normal"] = True
        self.df["trend"] = np.NAN
        self.df["stationarity"] = np.NAN

    def _process_timeseries_generator(self, generator: GutenTAG, i: int, args: argparse.Namespace):
        self.df.loc[self.df["dataset_name"] == str(i), "mean"] = generator.timeseries.mean()
        self.df.loc[self.df["dataset_name"] == str(i), "stddev"] = generator.timeseries.std()

    def _process_timeseries_overview(self, config: Dict, i: int, args: argparse.Namespace):
        dataset = dict()
        dataset["dataset_name"] = str(i)
        dataset["train_path"] = f"{i}/train.csv"
        dataset["test_path"] = f"{i}/test.csv"
        dataset["input_type"] = "univariate" if config.get("base-oscillation", {}).get("channels", 1) else "multivariate"
        dataset["length"] = config.get("base-oscillation", {}).get("length", 10000)
        dataset["dimensions"] = config.get("base-oscillation", {}).get("channels", 1)
        dataset["contamination"] = self._calc_contamination(config)
        dataset["num_anomalies"] = len(config.get("anomalies", []))
        dataset["min_anomaly_length"] = min([anomaly.get("length") for anomaly in config.get("anomalies", [])])
        dataset["median_anomaly_length"] = np.median([anomaly.get("length") for anomaly in config.get("anomalies", [])])
        dataset["max_anomaly_length"] = max([anomaly.get("length") for anomaly in config.get("anomalies", [])])
        dataset["train_type"] = "semi-supervised" if config.get("base-oscillation", {}).get("with_train", False) else "unsupervised"

        self.df = self.df.append(dataset, ignore_index=True)

    def _calc_contamination(self, config: Dict) -> float:
        anomaly_lengths = [anomaly.get("length") for anomaly in config.get("anomalies", [])]
        length = float(config.get("base-oscillation", {}).get("length"))
        return sum(anomaly_lengths) / length

    def __init__(self):
        self.df = pd.DataFrame(columns=columns)
