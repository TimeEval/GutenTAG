from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Optional, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import yaml

from gutenTAG.anomalies import Anomaly, Position, AnomalyKind
from gutenTAG.base_oscillations import BaseOscillation, BaseOscillationInterface
from .overview import Overview


def decode_trend_obj(trend: Dict, length_overwrite: int) -> Optional[BaseOscillationInterface]:
    trend_key = trend.get("kind", None)
    trend["length"] = length_overwrite
    if "trend" in trend:
        trend["trend"] = decode_trend_obj(trend["trend"], length_overwrite)
    return BaseOscillation.from_key(trend_key, **trend) if trend_key else None


class GutenTAG:
    def __init__(self, base_oscillation: BaseOscillationInterface, anomalies: List[Anomaly],
                 semi_supervised: bool = False, supervised: bool = False, plot: bool = False):
        self.base_oscillation = base_oscillation
        self.anomalies = anomalies
        self.semi_supervised_timeseries: Optional[np.ndarray] = None
        self.supervised_timeseries: Optional[np.ndarray] = None
        self.timeseries: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None
        self.train_labels: Optional[np.ndarray] = None
        self.semi_train_labels: Optional[np.ndarray] = None
        self.semi_supervised = semi_supervised
        self.supervised = supervised
        self.will_plot = plot

    def generate(self) -> GutenTAG:
        self.base_oscillation.inject_anomalies(self.anomalies)
        self.timeseries, self.labels = self.base_oscillation.generate()

        if self.semi_supervised:
            self.semi_supervised_timeseries, self.semi_train_labels = self.base_oscillation.generate(with_anomalies=False)
        if self.supervised:
            self.supervised_timeseries, self.train_labels = self.base_oscillation.generate()
        if self.will_plot:
            self.plot()

        return self

    def plot(self):
        n_series = 1 + np.sum([self.semi_supervised, self.supervised])
        fig, axs = plt.subplots(2, n_series, sharex="all", sharey="row", figsize=(10, n_series*4))
        # fix indexing, because subplots only returns a 1-dim array in this case:
        if n_series == 1:
            axs = np.array([axs]).T

        names = ["test"]
        series = [self.timeseries]
        labels = [self.labels]
        if self.supervised:
            names.append("train_supervised")
            series.append(self.supervised_timeseries)
            labels.append(self.train_labels)
        if self.semi_supervised:
            names.append("train_semi-supervised")
            series.append(self.semi_supervised_timeseries)
            labels.append(self.semi_train_labels)
        for i, (name, ts, label) in enumerate(zip(names, series, labels)):
            axs[0, i].set_title(name)
            name = list(map(lambda j: f"channel-{j}", range(ts.shape[1]))) if ts.shape[1] > 1 else "time series"
            axs[0, i].plot(ts, label=name)
            axs[1, i].plot(label, color="orange", label="ground truth")
        axs[0, 0].legend()
        axs[1, 0].legend()
        plt.show()

    @staticmethod
    def from_json(path: os.PathLike, plot: bool = False) -> Tuple[List[GutenTAG], Overview]:
        with open(path, "r") as f:
            config = json.load(f)
        return GutenTAG.from_dict(config, plot)

    @staticmethod
    def from_yaml(path: os.PathLike, plot: bool = False, only: Optional[str] = None) -> Tuple[List[GutenTAG], Overview]:
        with open(path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        return GutenTAG.from_dict(config, plot, only)

    @staticmethod
    def from_dict(config: Dict, plot: bool = False, only: Optional[str] = None) -> Tuple[List[GutenTAG], Overview]:
        overview = Overview()
        result = []
        for ts in config.get("timeseries", []):
            name = ts.get("name", None)

            if only and name != only:
                continue

            overview.add_dataset(ts)
            length = ts.get("length", 10000)
            channels = ts.get("channels", 1)
            semi_supervised = ts.get("semi-supervised", False)
            supervised = ts.get("supervised", False)

            base_oscillation_configs = deepcopy(ts.get("base-oscillation", {}))
            base_oscillation_configs["name"] = name
            base_oscillation_configs["length"] = length
            base_oscillation_configs["channels"] = channels
            trend = base_oscillation_configs.get("trend", {})
            base_oscillation_configs["trend"] = decode_trend_obj(trend, length)
            key = base_oscillation_configs.get("kind", "sinus")
            base_oscillation = BaseOscillation.from_key(key, **base_oscillation_configs)
            anomalies = []
            for anomaly_config in ts.get("anomalies", []):
                anomaly = Anomaly(
                    Position(anomaly_config.get("position", "middle")),
                    anomaly_config.get("exact-position", None),
                    anomaly_config.get("length", 200),
                    anomaly_config.get("channel", 0)
                )

                for anomaly_kind in anomaly_config.get("kinds", []):
                    kind = anomaly_kind.get("kind", "platform")
                    if kind == "trend":
                        parameters = {
                            "trend": decode_trend_obj(anomaly_kind.get("parameters", {}), anomaly.anomaly_length)
                        }
                    else:
                        parameters = anomaly_kind.get("parameters", {})
                    anomaly.set_anomaly(AnomalyKind(kind).create(deepcopy(parameters)))
                anomalies.append(anomaly)
            result.append(GutenTAG(base_oscillation, anomalies, semi_supervised, supervised, plot))
        return result, overview


if __name__ == "__main__":
    import random
    np.random.seed(42)
    random.seed(42)
    OUTPUT_DIR = "../../generated-timeseries/"
    timeseries, _ = GutenTAG.from_yaml("../../generation_configs/example-config.yaml", plot=True)
    for ts in timeseries:
        ts.generate()
