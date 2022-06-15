from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Tuple, List

from ..anomalies import Anomaly, Position, AnomalyKind, BaseAnomaly
from ..base_oscillations import BaseOscillation, BaseOscillationInterface
from ..utils.compatibility import Compatibility
from ..utils.default_values import default_values
from ..utils.global_variables import BASE_OSCILLATION, BASE_OSCILLATIONS, TIMESERIES, PARAMETERS, ANOMALIES


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
    def __init__(self, plot: bool = False, only: Optional[str] = None, skip_errors: bool = False):
        self.result: ResultType = []
        self.plot = plot
        self.only = only
        self.raw_ts: List[Dict] = []
        self.skip_errors = skip_errors

    def parse(self, config: Dict) -> ResultType:
        for t, ts in enumerate(config.get(TIMESERIES, [])):
            name = ts.get(PARAMETERS.NAME, f"ts_{t}")

            self.raw_ts.append(deepcopy(ts))

            if self._skip_name(name) or not self._check_compatibility(ts):
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

    def _check_compatibility(self, ts: Dict) -> bool:
        base_oscillations = ts.get(BASE_OSCILLATIONS, [ts.get(BASE_OSCILLATION)] * ts.get(PARAMETERS.CHANNELS, 0))
        anomalies = ts.get(ANOMALIES, [])
        for anomaly in anomalies:
            base_oscillation = base_oscillations[anomaly.get(PARAMETERS.CHANNEL, default_values[ANOMALIES][PARAMETERS.CHANNEL])][PARAMETERS.KIND]
            for anomaly_kind in anomaly.get(PARAMETERS.KINDS, []):
                anomaly_kind = anomaly_kind[PARAMETERS.KIND]
                if not Compatibility.check(anomaly_kind, base_oscillation):
                    if self.skip_errors:
                        logging.warning(f"Skip generation of time series {ts.get('name', '')} due to incompatible types: {anomaly_kind} -> {base_oscillation}.")
                        return False
                    else:
                        raise ValueError(f"Incompatible types: {anomaly_kind} -> {base_oscillation}.")
        return True

    def _skip_name(self, name: str) -> bool:
        return self.only is not None and name != self.only

    def _build_base_oscillations(self, d: Dict) -> List[BaseOscillationInterface]:
        length = d.get(PARAMETERS.LENGTH, default_values[BASE_OSCILLATIONS][PARAMETERS.LENGTH])
        bos = d.get(BASE_OSCILLATIONS, [d.get(BASE_OSCILLATION)] * d.get(PARAMETERS.CHANNELS, 0))
        return [self._build_single_base_oscillation(bo, length) for bo in bos]

    def _build_single_base_oscillation(self, d: Dict, length: int) -> BaseOscillationInterface:
        base_oscillation_config = deepcopy(d)
        base_oscillation_config[PARAMETERS.LENGTH] = length
        trend = base_oscillation_config.get(PARAMETERS.TREND, {})
        base_oscillation_config[PARAMETERS.TREND] = decode_trend_obj(trend, length)
        key = base_oscillation_config[PARAMETERS.KIND]
        return BaseOscillation.from_key(key, **base_oscillation_config)

    def _build_anomalies(self, d: Dict) -> List[Anomaly]:
        return [self._build_single_anomaly(anomaly_config) for anomaly_config in d.get(ANOMALIES, [])]

    def _build_single_anomaly(self, d: Dict) -> Anomaly:
        anomaly = Anomaly(
            Position(d.get(PARAMETERS.POSITION, default_values[ANOMALIES][PARAMETERS.POSITION])),
            d.get(PARAMETERS.EXACT_POSITION, None),
            d[PARAMETERS.LENGTH],
            d.get(PARAMETERS.CHANNEL, default_values[ANOMALIES][PARAMETERS.CHANNEL]),
            d.get(PARAMETERS.CREEP_LENGTH, default_values[ANOMALIES][PARAMETERS.CREEP_LENGTH])
        )

        anomaly_kinds = self._build_anomaly_kinds(d, anomaly.anomaly_length)
        for kind in anomaly_kinds:
            anomaly.set_anomaly(kind)

        return anomaly

    def _build_anomaly_kinds(self, d: Dict, length: int) -> List[BaseAnomaly]:
        return [self._build_single_anomaly_kind(anomaly_kind, length) for anomaly_kind in d.get(PARAMETERS.KINDS, [])]

    def _build_single_anomaly_kind(self, d: Dict, length: int) -> BaseAnomaly:
        kind = d[PARAMETERS.KIND]
        if kind == PARAMETERS.TREND:
            parameters = {
                PARAMETERS.TREND: decode_trend_obj(deepcopy(d[PARAMETERS.OSCILLATION]), length)
            }
        else:
            parameters = deepcopy(d)
            del parameters[PARAMETERS.KIND]
        try:
            return AnomalyKind(kind).create(parameters)
        except TypeError as ex:
            if "unexpected keyword argument" in str(ex):
                parameter = str(ex).split("'")[-2]
                raise ValueError(f"Anomaly kind '{kind}' does not support parameter '{parameter}'") from ex
            else:
                raise ex
