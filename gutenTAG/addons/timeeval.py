import os
from enum import Enum
from typing import List, Dict, Optional, Iterable, Any, Union

import numpy as np
import pandas as pd

from gutenTAG.addons import BaseAddOn, AddOnProcessContext, AddOnFinalizeContext
from gutenTAG.generator import TimeSeries
from gutenTAG.utils.default_values import default_values
from gutenTAG.utils.global_variables import SUPERVISED_FILENAME, UNSUPERVISED_FILENAME, SEMI_SUPERVISED_FILENAME, \
    BASE_OSCILLATIONS, ANOMALIES, PARAMETERS, BASE_OSCILLATION, BASE_OSCILLATION_NAMES


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
    def __init__(self):
        self.df = pd.DataFrame(columns=columns)
        self.key = self.__class__.__name__

    def process(self, ctx: AddOnProcessContext) -> AddOnProcessContext:
        ts = ctx.timeseries
        config = ctx.config
        datasets = [
            self._process_timeseries(config, ts, LearningType.Unsupervised)
        ]
        if ts.supervised:
            datasets.append(self._process_timeseries(config, ts, LearningType.Supervised))
        if ts.semi_supervised:
            datasets.append(self._process_timeseries(config, ts, LearningType.SemiSupervised))
        return ctx.store_data(self.key, {
            "name": ts.dataset_name,
            "datasets": datasets
        })

    def finalize(self, ctx: AddOnFinalizeContext) -> None:
        df = pd.DataFrame(columns=columns)
        # add metadata
        for ts_obj in ctx.get_data(self.key):
            df = df.append(ts_obj["datasets"], ignore_index=True)
        self._set_global_vals(df)
        self.df = df
        if ctx.should_save and ctx.output_folder is not None:
            filename = os.path.join(ctx.output_folder, "datasets.csv")
            df.to_csv(filename, index=False)

    def _process_timeseries(self, config: Dict, generator: TimeSeries, tpe: LearningType) -> Dict[str, Any]:
        dataset: Dict[str, Any] = dict()

        dataset_name = generator.dataset_name
        filename = tpe.get_filename()
        if filename is not None:
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
        dataset["train_is_normal"] = False if tpe == LearningType.Supervised else True
        dataset["mean"] = ts.mean()
        dataset["stddev"] = ts.std(axis=1).mean()
        dataset["trend"] = config.get(BASE_OSCILLATION, {}).get(PARAMETERS.TREND, {}).get(PARAMETERS.KIND, np.NAN)
        dataset["period_size"] = TimeEvalAddOn._calc_period_size(config.get(BASE_OSCILLATION, config.get(BASE_OSCILLATIONS, [{}])), dataset[PARAMETERS.LENGTH])
        return dataset

    @staticmethod
    def _set_global_vals(df: pd.DataFrame) -> None:
        df["collection_name"] = "GutenTAG"
        df["dataset_type"] = "synthetic"
        df["datetime_index"] = False
        df["split_at"] = np.NAN
        df["stationarity"] = np.NAN

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
            if frequency is None or kind not in [BASE_OSCILLATION_NAMES.SINE, BASE_OSCILLATION_NAMES.COSINE, BASE_OSCILLATION_NAMES.ECG, BASE_OSCILLATION_NAMES.RANDOM_MODE_JUMP]:
                periods.append(np.NAN)
            elif kind in [BASE_OSCILLATION_NAMES.SINE, BASE_OSCILLATION_NAMES.COSINE, BASE_OSCILLATION_NAMES.ECG]:
                periods.append(int(100 / frequency))
            elif kind == BASE_OSCILLATION_NAMES.RANDOM_MODE_JUMP:
                periods.append(int(length / frequency))
        return float(np.nanmedian(periods))
