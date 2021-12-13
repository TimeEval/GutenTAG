import os
import argparse
from typing import List, Dict, Tuple, Optional, Iterable, Any, Union
from enum import Enum

import numpy as np
import pandas as pd
from . import BaseAddOn
from .. import GutenTAG
from ..generator import Overview, TimeSeries
from ..utils.global_variables import SUPERVISED_FILENAME, UNSUPERVISED_FILENAME, SEMI_SUPERVISED_FILENAME, \
    BASE_OSCILLATIONS, ANOMALIES, PARAMETERS, BASE_OSCILLATION, BASE_OSCILLATION_NAMES
from ..utils.default_values import default_values

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
    "stationarity",
    "period_size"
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
        return None


class TimeEvalAddOn(BaseAddOn):
    def process(self, overview: Overview, gutenTAG: GutenTAG, args: argparse.Namespace) -> Tuple[Overview, GutenTAG]:
        for i, (generator, config) in enumerate(zip(gutenTAG.timeseries, overview.datasets)):
            self._process_timeseries(config, i, generator, LearningType.Unsupervised)
            if generator.supervised:
                self._process_timeseries(config, i, generator, LearningType.Supervised)
            if generator.semi_supervised:
                self._process_timeseries(config, i, generator, LearningType.SemiSupervised)
        self._set_global_vals()

        if args.no_save:
            return overview, gutenTAG

        self.df.to_csv(os.path.join(args.output_dir, "datasets.csv"), index=False)
        return overview, gutenTAG

    def _set_global_vals(self):
        self.df["collection_name"] = "GutenTAG"
        self.df["dataset_type"] = "synthetic"
        self.df["datetime_index"] = False
        self.df["split_at"] = np.NAN
        self.df["train_is_normal"] = True
        self.df["stationarity"] = np.NAN

    def _process_timeseries(self, config: Dict, i: int, generator: TimeSeries, tpe: LearningType):
        dataset: Dict[str, Any] = dict()

        dataset_name = generator.dataset_name or i
        if filename := tpe.get_filename():
            dataset["train_path"] = f"{dataset_name}/{filename}"

        ts = generator.timeseries
        assert ts is not None, "Timeseries should not be None!"

        dataset["dataset_name"] = f"{dataset_name}.{tpe.value}"
        dataset["test_path"] = f"{dataset_name}/{UNSUPERVISED_FILENAME}"
        dataset["input_type"] = "univariate" if ts.shape[1] == 1 else "multivariate"
        dataset["length"] = config.get(PARAMETERS.LENGTH, 10000)
        dataset["dimensions"] = ts.shape[1]
        dataset["contamination"] = self._calc_contamination(config.get(ANOMALIES, []), dataset[PARAMETERS.LENGTH])
        dataset["num_anomalies"] = len(config.get(ANOMALIES, []))
        dataset["min_anomaly_length"] = min([anomaly.get("length") for anomaly in config.get(ANOMALIES, [])])
        dataset["median_anomaly_length"] = np.median([anomaly.get(PARAMETERS.LENGTH) for anomaly in config.get(ANOMALIES, [])])
        dataset["max_anomaly_length"] = max([anomaly.get(PARAMETERS.LENGTH) for anomaly in config.get(ANOMALIES, [])])
        dataset["train_type"] = tpe.value
        dataset["mean"] = None if ts is None else ts.mean()
        dataset["stddev"] = None if ts is None else ts.std(axis=1).mean()
        dataset["trend"] = config.get(BASE_OSCILLATION, {}).get(PARAMETERS.TREND, {}).get(PARAMETERS.KIND, np.NAN)
        dataset["period_size"] = TimeEvalAddOn._calc_period_size(config.get(BASE_OSCILLATION, config.get(BASE_OSCILLATIONS, [{}])), dataset[PARAMETERS.LENGTH])

        self.df: pd.DataFrame = self.df.append(dataset, ignore_index=True)

    @staticmethod
    def _calc_contamination(anomalies: Iterable[Dict], ts_length: int) -> float:

        anomaly_lengths = [anomaly.get(PARAMETERS.LENGTH, default_values[ANOMALIES][PARAMETERS.LENGTH]) for anomaly in anomalies]
        if len(anomaly_lengths) > 0:
            return sum(anomaly_lengths) / ts_length
        return 0

    @staticmethod
    def _calc_period_size(base: Union[Dict[str, Any], List[Dict[str, Any]]], length: int) -> float:
        bases: List[Dict[str, Any]] = []
        if type(base) == dict:
            bases.append(base)  # type: ignore  # does not understand the condition before
        elif type(base) == list:
            bases = base  # type: ignore  # does not understand the condition before

        periods = []

        for dim in bases:
            frequency = dim.get(PARAMETERS.FREQUENCY)
            kind = dim.get(PARAMETERS.KIND)
            if frequency is None or kind not in [BASE_OSCILLATION_NAMES.SINE, BASE_OSCILLATION_NAMES.ECG, BASE_OSCILLATION_NAMES.RANDOM_MODE_JUMP]:
                return np.NAN
            periods.append(int(length / frequency))
        return np.median(periods).item()

    def __init__(self):
        self.df = pd.DataFrame(columns=columns)
