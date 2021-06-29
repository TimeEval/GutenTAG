from __future__ import annotations

import json
import os
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
        self.semi_supervised = semi_supervised
        self.supervised = supervised
        self.plot = plot

    def generate(self) -> GutenTAG:
        self.timeseries, self.labels = self.base_oscillation.inject_anomalies(self.anomalies).generate()

        if self.semi_supervised:
            self.semi_supervised_timeseries = self.base_oscillation.generate_only_base()
        if self.supervised:
            self.supervised_timeseries, self.train_labels = self.base_oscillation.inject_anomalies(self.anomalies).generate()
        if self.plot:
            self._plot()

        return self

    def _plot(self):
        fig, axs = plt.subplots(2, sharex="all")
        axs[0].set_title("Time series")
        axs[0].plot(self.timeseries)
        axs[1].set_title("Label")
        axs[1].plot(self.labels)
        plt.show()

    @staticmethod
    def from_json(path: os.PathLike, plot: bool = False) -> Tuple[List[GutenTAG], Overview]:
        with open(path, "r") as f:
            config = json.load(f)
        return GutenTAG.from_dict(config, plot)

    @staticmethod
    def from_yaml(path: os.PathLike, plot: bool = False) -> Tuple[List[GutenTAG], Overview]:
        with open(path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        return GutenTAG.from_dict(config, plot)

    @staticmethod
    def from_dict(config: Dict, plot: bool = False) -> Tuple[List[GutenTAG], Overview]:
        overview = Overview()
        result = []
        for ts in config.get("timeseries", []):
            overview.add_dataset(ts)
            name = ts.get("name", None)
            length = ts.get("length", 10000)
            channels = ts.get("channels", 1)
            semi_supervised = ts.get("semi-supervised", False)
            supervised = ts.get("supervised", False)
            base_oscillation_configs = ts.get("base-oscillation", {})
            base_oscillation_configs["name"] = name
            base_oscillation_configs["length"] = length
            base_oscillation_configs["channels"] = channels
            base_oscillation_configs["trend"] = decode_trend_obj(base_oscillation_configs.get("trend", {}), length)
            key = base_oscillation_configs.get("kind", "sinus")
            base_oscillation = BaseOscillation.from_key(key, **base_oscillation_configs)
            anomalies = []
            for anomaly_config in ts.get("anomalies", []):
                anomaly = Anomaly(Position(anomaly_config.get("position", "middle")), anomaly_config.get("length", 200), anomaly_config.get("channel", 0))

                for anomaly_kind in anomaly_config.get("kinds", []):
                    kind = anomaly_kind.get("kind", "platform")
                    if kind == "trend":
                        parameters = {
                            "trend": decode_trend_obj(anomaly_kind.get("parameters", {}), anomaly.anomaly_length)
                        }
                    else:
                        parameters = anomaly_kind.get("parameters", {})
                    anomaly.set_anomaly(AnomalyKind(kind).set_parameters(parameters))
                anomalies.append(anomaly)
            result.append(GutenTAG(base_oscillation, anomalies, semi_supervised, supervised, plot).generate())
        return result, overview


if __name__ == "__main__":
    import random
    np.random.seed(42)
    random.seed(42)
    OUTPUT_DIR = "../../generated-timeseries/"
    timeseries = GutenTAG.from_yaml("./generation_config.yaml", plot=True)
