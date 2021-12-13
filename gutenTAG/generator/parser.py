from __future__ import annotations

from copy import deepcopy
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, asdict

from ..anomalies import Anomaly, Position, AnomalyKind, BaseAnomaly
from ..base_oscillations import BaseOscillation, BaseOscillationInterface
from ..utils.default_values import default_values
from ..utils.global_variables import BASE_OSCILLATION, BASE_OSCILLATIONS, TIMESERIES, PARAMETERS, ANOMALIES, \
    ANOMALY_TYPE_NAMES


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
    trend_key = trend.get(PARAMETERS.KIND, None)
    trend[PARAMETERS.LENGTH] = length_overwrite
    if PARAMETERS.TREND in trend:
        trend[PARAMETERS.TREND] = decode_trend_obj(trend[PARAMETERS.TREND], length_overwrite)
    return BaseOscillation.from_key(trend_key, **trend) if trend_key else None


class ConfigParser:
    def __init__(self, plot: bool = False, only: Optional[str] = None):
        self.result: ResultType = []
        self.plot = plot
        self.only = only
        self.raw_ts: List[Dict] = []

    def parse(self, config: Dict) -> ResultType:
        for t, ts in enumerate(config.get(TIMESERIES, [])):
            self.raw_ts.append(deepcopy(ts))

            name = ts.get(PARAMETERS.NAME, f"ts_{t}")

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
        length = d.get(PARAMETERS.LENGTH, default_values[BASE_OSCILLATIONS][PARAMETERS.LENGTH])
        channels = d.get(PARAMETERS.CHANNELS, None)
        if channels:
            return [self._build_single_base_oscillation(d.get(BASE_OSCILLATION, {}), length) for _ in range(channels)]
        return [self._build_single_base_oscillation(bo, length) for bo in d.get(BASE_OSCILLATIONS, [])]

    def _build_single_base_oscillation(self, d: Dict, length: int) -> BaseOscillationInterface:
        base_oscillation_configs = deepcopy(d)
        base_oscillation_configs[PARAMETERS.LENGTH] = length
        trend = base_oscillation_configs.get(PARAMETERS.TREND, {})
        base_oscillation_configs[PARAMETERS.TREND] = decode_trend_obj(trend, length)
        key = base_oscillation_configs.get(PARAMETERS.KIND, default_values[BASE_OSCILLATIONS][PARAMETERS.KIND])
        return BaseOscillation.from_key(key, **base_oscillation_configs)

    def _build_anomalies(self, d: Dict) -> List[Anomaly]:
        return [self._build_single_anomaly(anomaly_config) for anomaly_config in d.get(ANOMALIES, [])]

    def _build_single_anomaly(self, d: Dict) -> Anomaly:
        anomaly = Anomaly(
            Position(d.get(PARAMETERS.POSITION, default_values[ANOMALIES][PARAMETERS.POSITION])),
            d.get(PARAMETERS.EXACT_POSITION, None),
            d.get(PARAMETERS.LENGTH, default_values[ANOMALIES][PARAMETERS.LENGTH]),
            d.get(PARAMETERS.CHANNEL, default_values[ANOMALIES][PARAMETERS.CHANNEL])
        )

        anomaly_kinds = self._build_anomaly_kinds(d, anomaly.anomaly_length)
        for kind in anomaly_kinds:
            anomaly.set_anomaly(kind)

        return anomaly

    def _build_anomaly_kinds(self, d: Dict, length: int) -> List[BaseAnomaly]:
        return [self._build_single_anomaly_kind(anomaly_kind, length) for anomaly_kind in d.get(PARAMETERS.KINDS, [])]

    def _build_single_anomaly_kind(self, d: Dict, length: int) -> BaseAnomaly:
        kind = d.get(PARAMETERS.KIND, ANOMALY_TYPE_NAMES.PLATFORM)
        if kind == PARAMETERS.TREND:
            parameters = {
                PARAMETERS.TREND: decode_trend_obj(d.get(PARAMETERS.PARAMETERS, {}), length)
            }
        else:
            parameters = d.get(PARAMETERS.PARAMETERS, {})
        return AnomalyKind(kind).create(deepcopy(parameters))
