import os
import argparse
from typing import List, Dict, Tuple, Optional, Iterable
from enum import Enum

import numpy as np
import pandas as pd
from . import BaseAddOn
from .. import GutenTAG
from ..generator import Overview
from ..__main__ import SUPERVISED_FILENAME, UNSUPERVISED_FILENAME, SEMI_SUPERVISED_FILENAME

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


class LearningType(Enum):
    Unsupervised = "unsupervised"
    Supervised = "supervised"
    SemiSupervised = "semi-supervised"

    def get_filename(self) -> Optional[str]:
        if self == LearningType.Supervised:
            return SUPERVISED_FILENAME
        elif self == LearningType.SemiSupervised:
            return SEMI_SUPERVISED_FILENAME


class TimeEvalAddOn(BaseAddOn):
    def process(self, overview: Overview, generators: List[GutenTAG], args: argparse.Namespace) -> Tuple[Overview, List[GutenTAG]]:
        for i, (generator, config) in enumerate(zip(generators, overview.datasets)):
            self._process_timeseries(config, i, generator, LearningType.Unsupervised)
            if generator.supervised:
                self._process_timeseries(config, i, generator, LearningType.Supervised)
            if generator.semi_supervised:
                self._process_timeseries(config, i, generator, LearningType.SemiSupervised)
        self._set_global_vals()

        if args.no_save:
            return overview, generators

        self.df.to_csv(os.path.join(args.output_dir, "datasets.csv"), index=False)
        return overview, generators

    def _set_global_vals(self):
        self.df["collection_name"] = "GutenTAG"
        self.df["dataset_type"] = "synthetic"
        self.df["datetime_index"] = False
        self.df["split_at"] = np.NAN
        self.df["train_is_normal"] = True
        self.df["stationarity"] = np.NAN

    def _process_timeseries(self, config: Dict, i: int, generator: GutenTAG, tpe: LearningType):
        dataset = dict()

        dataset_name = generator.base_oscillation.name or i
        if filename := tpe.get_filename():
            dataset["train_path"] = f"{dataset_name}/{filename}"

        dataset["dataset_name"] = f"{dataset_name}.{tpe.value}"
        dataset["test_path"] = f"{dataset_name}/{UNSUPERVISED_FILENAME}"
        dataset["input_type"] = "univariate" if config.get("base-oscillation", {}).get("channels", 1) else "multivariate"
        dataset["length"] = config.get("length", 10000)
        dataset["dimensions"] = config.get("channels", 1)
        dataset["contamination"] = self._calc_contamination(config.get("anomalies", []), dataset["length"])
        dataset["num_anomalies"] = len(config.get("anomalies", []))
        dataset["min_anomaly_length"] = min([anomaly.get("length") for anomaly in config.get("anomalies", [])])
        dataset["median_anomaly_length"] = np.median([anomaly.get("length") for anomaly in config.get("anomalies", [])])
        dataset["max_anomaly_length"] = max([anomaly.get("length") for anomaly in config.get("anomalies", [])])
        dataset["train_type"] = tpe.value
        dataset["mean"] = generator.timeseries.mean()
        dataset["stddev"] = generator.timeseries.std()
        dataset["trend"] = config.get("base-oscillation", {}).get("trend", {}).get("kind", np.NAN)

        self.df = self.df.append(dataset, ignore_index=True)

    @staticmethod
    def _calc_contamination(anomalies: Iterable[Dict], ts_length: int) -> float:
        anomaly_lengths = [anomaly.get("length") for anomaly in anomalies]
        return sum(anomaly_lengths) / ts_length

    def __init__(self):
        self.df = pd.DataFrame(columns=columns)
