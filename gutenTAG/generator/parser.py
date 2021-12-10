from __future__ import annotations

from copy import deepcopy
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, asdict

from ..anomalies import Anomaly, Position, AnomalyKind, BaseAnomaly
from ..base_oscillations import BaseOscillation, BaseOscillationInterface
from ..utils.default_values import default_values


@dataclass
class GenerationOptions:
    semi_supervised: bool = False
    supervised: bool = False
    plot: bool = False
    dataset_name: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict) -> GenerationOptions:
        return GenerationOptions(
            semi_supervised=d.get("semi-supervised", False),
            supervised=d.get("supervised", False)
        )


ResultType = List[Tuple[List[BaseOscillationInterface], List[Anomaly], GenerationOptions]]


def decode_trend_obj(trend: Dict, length_overwrite: int) -> Optional[BaseOscillationInterface]:
    trend_key = trend.get("kind", None)
    trend["length"] = length_overwrite
    if "trend" in trend:
        trend["trend"] = decode_trend_obj(trend["trend"], length_overwrite)
    return BaseOscillation.from_key(trend_key, **trend) if trend_key else None


class ConfigParser:
    def __init__(self, plot: bool = False, only: Optional[str] = None):
        self.result: ResultType = []
        self.plot = plot
        self.only = only
        self.raw_ts: List[Dict] = []

    def parse(self, config: Dict) -> ResultType:
        for t, ts in enumerate(config.get("timeseries", [])):
            self.raw_ts.append(deepcopy(ts))

            name = ts.get("name", f"ts_{t}")

            if self._skip_name(name):
                continue

            generation_options = GenerationOptions.from_dict(ts)
            generation_options.plot = self.plot
            generation_options.dataset_name = name

            base_oscillations = self._build_base_oscillations(ts)
            anomalies = self._build_anomalies(ts)

            self.result.append(
                (base_oscillations, anomalies, generation_options)
            )

        return self.result

    def _skip_name(self, name: str) -> bool:
        return self.only is not None and name != self.only

    def _build_base_oscillations(self, d: Dict) -> List[BaseOscillationInterface]:
        length = d.get("length", default_values["base_oscillations"]["length"])
        channels = d.get("channels", None)
        if channels:
            return [self._build_single_base_oscillation(d.get("base-oscillation", {}), length) for _ in range(channels)]
        return [self._build_single_base_oscillation(bo, length) for bo in d.get("base-oscillations", [])]

    def _build_single_base_oscillation(self, d: Dict, length: int) -> BaseOscillationInterface:
        base_oscillation_configs = deepcopy(d)
        base_oscillation_configs["length"] = length
        trend = base_oscillation_configs.get("trend", {})
        base_oscillation_configs["trend"] = decode_trend_obj(trend, length)
        key = base_oscillation_configs.get("kind", default_values["base_oscillations"]["kind"])
        return BaseOscillation.from_key(key, **base_oscillation_configs)

    def _build_anomalies(self, d: Dict) -> List[Anomaly]:
        return [self._build_single_anomaly(anomaly_config) for anomaly_config in d.get("anomalies", [])]

    def _build_single_anomaly(self, d: Dict) -> Anomaly:
        anomaly = Anomaly(
            Position(d.get("position", default_values["anomalies"]["position"])),
            d.get("exact-position", None),
            d.get("length", default_values["anomalies"]["length"]),
            d.get("channel", default_values["anomalies"]["channel"])
        )

        anomaly_kinds = self._build_anomaly_kinds(d, anomaly.anomaly_length)
        for kind in anomaly_kinds:
            anomaly.set_anomaly(kind)

        return anomaly

    def _build_anomaly_kinds(self, d: Dict, length: int) -> List[BaseAnomaly]:
        return [self._build_single_anomaly_kind(anomaly_kind, length) for anomaly_kind in d.get("kinds", [])]

    def _build_single_anomaly_kind(self, d: Dict, length: int) -> BaseAnomaly:
        kind = d.get("kind", "platform")
        if kind == "trend":
            parameters = {
                "trend": decode_trend_obj(d.get("parameters", {}), length)
            }
        else:
            parameters = d.get("parameters", {})
        return AnomalyKind(kind).create(deepcopy(parameters))
