from __future__ import annotations

from hashlib import md5
from pathlib import Path
from typing import Optional, List, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.random import SeedSequence

from ..anomalies import Anomaly
from ..base_oscillations import BaseOscillationInterface
from ..consolidator import Consolidator
from ..timeseries import TrainingType, INDEX_COLUMN_NAME, LABEL_COLUMN_NAME, TimeSeries as ExtTimeSeries
from ..utils.types import GenerationContext


class TimeSeries:
    def __init__(self, base_oscillations: List[BaseOscillationInterface], anomalies: List[Anomaly],
                 dataset_name: str, semi_supervised: bool = False, supervised: bool = False):
        self.dataset_name = dataset_name
        self.base_oscillations = base_oscillations
        self.anomalies = anomalies
        self.semi_supervised_timeseries: Optional[np.ndarray] = None
        self.supervised_timeseries: Optional[np.ndarray] = None
        self.timeseries: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None
        self.train_labels: Optional[np.ndarray] = None
        self.semi_train_labels: Optional[np.ndarray] = None
        self.semi_supervised = semi_supervised
        self.supervised = supervised
        self._rng_counter = 0

    def generate(self, random_seed: Optional[int] = None) -> TimeSeries:
        consolidator = Consolidator(self.base_oscillations, self.anomalies)
        self.timeseries, self.labels = consolidator.generate(GenerationContext(seed=self._create_new_seed(random_seed)))

        if self.semi_supervised:
            semi_supervised_consolidator = Consolidator(self.base_oscillations, [],
                                                        semi_supervised=self.semi_supervised)
            self.semi_supervised_timeseries, self.semi_train_labels = semi_supervised_consolidator.generate(
                GenerationContext(seed=self._create_new_seed(random_seed))
            )

        if self.supervised:
            supervised_consolidator = Consolidator(self.base_oscillations, self.anomalies,
                supervised=self.supervised)
            self.supervised_timeseries, self.train_labels = supervised_consolidator.generate(
                GenerationContext(seed=self._create_new_seed(random_seed))
            )

        return self

    def generate_with_dataframe(self, random_seed: Optional[int] = None) -> pd.DataFrame:
        self.generate(random_seed)
        return self.to_dataframe()

    def plot(self) -> None:
        n_series = 1 + np.sum([self.semi_supervised, self.supervised])
        fig, axs = plt.subplots(2, n_series, sharex="col", sharey="row", figsize=(6*n_series, 5))
        # fix indexing, because subplots only returns a 1-dim array in this case:
        if n_series == 1:
            axs = np.array([axs]).T

        fig.suptitle(self.dataset_name)

        names: List[str] = ["test"]
        assert self.timeseries is not None, "TimeSeries is not generated. Please, do so before plotting!"
        assert self.labels is not None, "TimeSeries is not generated. Please, do so before plotting!"
        series: List[np.ndarray] = [self.timeseries]
        labels: List[np.ndarray] = [self.labels]
        if self.supervised and self.supervised_timeseries is not None and self.train_labels is not None:
            names.append("train_supervised")
            series.append(self.supervised_timeseries)
            labels.append(self.train_labels)
        if self.semi_supervised and self.semi_supervised_timeseries is not None and self.semi_train_labels is not None:
            names.append("train_semi-supervised")
            series.append(self.semi_supervised_timeseries)
            labels.append(self.semi_train_labels)
        for i, (name, ts, label) in enumerate(zip(names, series, labels)):
            axs[0, i].set_title(name)
            name_list = list(map(lambda j: f"channel-{j}", range(ts.shape[1]))) if ts.shape[1] > 1 else "time series"
            axs[0, i].plot(ts, label=name_list)
            axs[1, i].plot(label, color="orange", label="ground truth")
        axs[0, 0].legend()
        axs[1, 0].legend()
        plt.show()

    def build_figure_base_oscillation(self) -> plt.Figure:
        assert self.timeseries is not None, "TimeSeries is not generated. Please, do so before building a figure!"

        channels = self.timeseries.shape[1]
        name = list(map(lambda j: f"channel-{j}", range(channels))) if channels > 1 else "time series"

        fig, ax = plt.subplots()
        ax.plot(self.timeseries, label=name)
        return fig

    def to_datasets(self) -> List[ExtTimeSeries]:
        results: List[ExtTimeSeries] = []
        training_types = [TrainingType.TEST]
        if self.semi_supervised:
            training_types.append(TrainingType.TRAIN_NO_ANOMALIES)
        if self.supervised:
            training_types.append(TrainingType.TRAIN_ANOMALIES)

        for training_type in training_types:
            results.append(ExtTimeSeries(
                name=self.dataset_name,
                training_type=training_type,
                timeseries=self.to_dataframe(training_type)
            ))
        return results

    def to_dataframe(self, training_type: TrainingType = TrainingType.TEST) -> pd.DataFrame:
        if training_type == TrainingType.TEST:
            ts, labels = self.timeseries, self.labels
        elif training_type == TrainingType.TRAIN_NO_ANOMALIES:
            ts, labels = self.semi_supervised_timeseries, self.semi_train_labels
        else:  # if training_type == TrainingType.TRAIN_ANOMALIES:
            ts, labels = self.supervised_timeseries, self.train_labels

        assert ts is not None, f"The timeseries for {training_type.value} must be generated before creating a DataFrame"
        if labels is None:
            labels = np.zeros(ts.shape[0])
        channel_names = list(map(lambda i: f"value-{i}", range(ts.shape[1])))
        df = pd.DataFrame(ts, columns=channel_names)
        df.index.name = INDEX_COLUMN_NAME
        df[LABEL_COLUMN_NAME] = labels
        return df

    def to_csv(self, output_dir: Path, training_type: TrainingType = TrainingType.TEST) -> None:
        df = self.to_dataframe(training_type)
        df.to_csv(output_dir, sep=",", index=True)

    def _create_new_seed(self, base_seed: Optional[int]) -> SeedSequence:
        if base_seed is None:
            base_seed1: Union[int, SeedSequence] = SeedSequence()
        else:
            base_seed1 = base_seed
        seeds = [int.from_bytes(md5(self.dataset_name.encode("utf-8")).digest(), byteorder="big")]
        if self._rng_counter > 0:
            seeds.append(self._rng_counter)
        self._rng_counter += 1
        return GenerationContext.re_seed(seeds, base_seed1)
