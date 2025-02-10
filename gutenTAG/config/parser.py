from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Tuple, List

from ..anomalies import Anomaly, Position, AnomalyKind, BaseAnomaly
from ..base_oscillations import BaseOscillationInterface, BaseOscillation
from ..utils.compatibility import Compatibility
from ..utils.default_values import default_values
from ..utils.global_variables import (
    BASE_OSCILLATION,
    BASE_OSCILLATIONS,
    TIMESERIES,
    PARAMETERS,
    ANOMALIES,
)


@dataclass
class GenerationOptions:
    semi_supervised: bool = False
    supervised: bool = False
    dataset_name: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict) -> GenerationOptions:
        return GenerationOptions(
            semi_supervised=d.get("semi-supervised", False),
            supervised=d.get("supervised", False),
        )


ResultType = List[
    Tuple[List[BaseOscillationInterface], List[Anomaly], GenerationOptions, Dict]
]


def decode_trend_obj(
    trend: Dict, length_overwrite: int
) -> Optional[BaseOscillationInterface]:
    trend_key = trend.get(PARAMETERS.KIND, None)
    trend[PARAMETERS.LENGTH] = length_overwrite
    if PARAMETERS.TREND in trend:
        trend[PARAMETERS.TREND] = decode_trend_obj(
            trend[PARAMETERS.TREND], length_overwrite
        )
    return BaseOscillation.from_key(trend_key, **trend) if trend_key else None


class ConfigParser:
    def __init__(self, only: Optional[str] = None, skip_errors: bool = False):
        self.result: ResultType = []
        self.only = only
        self.raw_ts_configs: List[Dict] = []
        self.skip_errors = skip_errors

    def parse(self, config: Dict) -> ResultType:
        for i, ts in enumerate(config.get(TIMESERIES, [])):
            name = ts.get(PARAMETERS.NAME, f"ts_{i}")

            bos, n_channel = self._extract_bos(ts, name)

            if self._skip_name(name) or not self._check_compatibility(ts, name, bos, n_channel):
                continue

            raw_ts_config = deepcopy(ts)
            self.raw_ts_configs.append(raw_ts_config)

            generation_options = GenerationOptions.from_dict(ts)
            generation_options.dataset_name = name

            base_oscillations = self._build_base_oscillations(ts, bos)
            anomalies = self._build_anomalies(ts, name)

            self.result.append(
                (base_oscillations, anomalies, generation_options, raw_ts_config)
            )

        return self.result

    def _check_compatibility(self, ts: Dict, name: str, bos: list[dict], n_channels: int) -> bool:
        anomalies = ts.get(ANOMALIES, [])
        for anomaly in anomalies:
            channel = anomaly.get(PARAMETERS.CHANNEL, default_values[ANOMALIES][PARAMETERS.CHANNEL])
            if channel >= n_channels:
                    self._report_error(
                        name,
                        f"Invalid channel index: {channel} >= {n_channels}."
                    )
            base_oscillation = bos[channel][PARAMETERS.KIND]
            for anomaly_kind in anomaly.get(PARAMETERS.KINDS, []):
                anomaly_kind = anomaly_kind[PARAMETERS.KIND]
                if not Compatibility.check(anomaly_kind, base_oscillation):
                    self._report_error(
                        name,
                        f"Incompatible types: {anomaly_kind} -> {base_oscillation}.",
                        warning_msg=f"Skip generation due to incompatible types: {anomaly_kind} -> {base_oscillation}.",
                    )
                    return False
        return True

    def _skip_name(self, name: str) -> bool:
        return self.only is not None and name != self.only

    def _build_base_oscillations(self, d: Dict, bos: list[dict]) -> List[BaseOscillationInterface]:
        length = d.get(
            PARAMETERS.LENGTH, default_values[BASE_OSCILLATIONS][PARAMETERS.LENGTH]
        )
        return [self._build_single_base_oscillation(bo, length) for bo in bos]

    def _extract_bos(self, d: Dict, name: str) -> Tuple[List[Dict], int]:
        if BASE_OSCILLATIONS in d:
            base_oscillations: List[Dict] = d.get(BASE_OSCILLATIONS)  # type: ignore
        elif BASE_OSCILLATION in d and PARAMETERS.CHANNELS not in d:
            self._report_error(
                name,
                f"'{BASE_OSCILLATION}' requires parameter '{PARAMETERS.CHANNELS}'."
            )
        else:
            bo_template = d.get(BASE_OSCILLATION)
            if isinstance(bo_template, list):
                self._report_error(
                    name,
                    f"'{BASE_OSCILLATION}' must be a single object."
                )
            base_oscillations = [bo_template] * d.get(PARAMETERS.CHANNELS, 0)  # type: ignore

        n_channels = len(base_oscillations)
        if n_channels == 0:
            self._report_error(
                name,
                f"No base oscillations defined. Please provide either '{BASE_OSCILLATION}' and '{PARAMETERS.CHANNELS}' or '{BASE_OSCILLATIONS}'."
            )
        return base_oscillations, n_channels

    def _build_single_base_oscillation(
        self, d: Dict, length: int
    ) -> BaseOscillationInterface:
        base_oscillation_config = deepcopy(d)
        base_oscillation_config[PARAMETERS.LENGTH] = length
        trend = base_oscillation_config.get(PARAMETERS.TREND, {})
        base_oscillation_config[PARAMETERS.TREND] = decode_trend_obj(trend, length)
        key = base_oscillation_config[PARAMETERS.KIND]
        return BaseOscillation.from_key(key, **base_oscillation_config)

    def _build_anomalies(self, d: Dict, ts_name: str) -> List[Anomaly]:
        return [
            self._build_single_anomaly(anomaly_config, ts_name)
            for anomaly_config in d.get(ANOMALIES, [])
        ]

    def _build_single_anomaly(self, d: Dict, ts_name: str) -> Anomaly:
        anomaly = Anomaly(
            Position(
                d.get(
                    PARAMETERS.POSITION, default_values[ANOMALIES][PARAMETERS.POSITION]
                )
            ),
            d.get(PARAMETERS.EXACT_POSITION, None),
            d[PARAMETERS.LENGTH],
            d.get(PARAMETERS.CHANNEL, default_values[ANOMALIES][PARAMETERS.CHANNEL]),
            d.get(
                PARAMETERS.CREEPING_LENGTH,
                default_values[ANOMALIES][PARAMETERS.CREEPING_LENGTH],
            ),
        )

        anomaly_kinds = self._build_anomaly_kinds(d, anomaly.anomaly_length, ts_name)
        for kind in anomaly_kinds:
            anomaly.set_anomaly(kind)

        return anomaly

    def _build_anomaly_kinds(self, d: Dict, length: int, ts_name: str) -> List[BaseAnomaly]:
        potential_anomalies = [
            self._build_single_anomaly_kind(anomaly_kind, length, ts_name)
            for anomaly_kind in d.get(PARAMETERS.KINDS, [])
        ]
        return [anomaly for anomaly in potential_anomalies if anomaly is not None]

    def _build_single_anomaly_kind(self, d: Dict, length: int, ts_name: str) -> Optional[BaseAnomaly]:
        kind = d[PARAMETERS.KIND]
        if kind == PARAMETERS.TREND:
            parameters = {
                PARAMETERS.TREND: decode_trend_obj(
                    deepcopy(d[PARAMETERS.OSCILLATION]), length
                )
            }
        else:
            parameters = deepcopy(d)
            del parameters[PARAMETERS.KIND]
        try:
            return AnomalyKind(kind).create(parameters)
        except TypeError as ex:
            if "unexpected keyword argument" in str(ex):
                parameter = str(ex).split("'")[-2]
                raise ValueError(f"Time series {ts_name}: Anomaly kind '{kind}' does not support parameter '{parameter}'.") from ex
            else:
                raise ex

    def _report_error(self, name: str, msg: str, warning_msg: Optional[str] = None) -> None:
        warning_msg = warning_msg or msg
        if self.skip_errors:
            logging.warning(warning_msg)
        else:
            raise ValueError(f"Time series {name}: {msg}")
