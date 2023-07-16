from typing import Any, Dict, Optional

import jsonschema
from jsonschema import RefResolver

from ..anomalies import AnomalyKind
from ..base_oscillations import BaseOscillation
from ..config.schema_loader import ConfigSchemaLoader, FileSystemConfigSchemaLoader
from ..utils.global_variables import (
    CONFIG_SCHEMA,
    TIMESERIES,
    PARAMETERS,
    ANOMALIES,
    BASE_OSCILLATION,
    BASE_OSCILLATIONS,
)


class GutenTAGParseError(BaseException):
    def __init__(self, prefix: str = "", msg: Optional[str] = None):
        if msg is None:
            msg = prefix
            prefix = ""
        if prefix:
            prefix = f" {prefix}"
        super(GutenTAGParseError, self).__init__(
            f"Error in generation configuration{prefix}: {msg}"
        )


class ConfigValidator:
    def __init__(self):
        loader: ConfigSchemaLoader = FileSystemConfigSchemaLoader.from_packaged_schema()
        # load base schema
        base_schema_name = CONFIG_SCHEMA.schema_name(CONFIG_SCHEMA.BASE_ID)
        base_schema = loader.load_schema_file(CONFIG_SCHEMA.BASE_ID)

        # load schema parts
        schema_parts = {}
        for schema_part_id in CONFIG_SCHEMA.SCHEMA_PART_IDS:
            name = CONFIG_SCHEMA.schema_name(schema_part_id)
            schema_parts[name] = loader.load_schema_file(schema_part_id)

        # create resolver containing all schema parts
        self.base_schema = base_schema
        self.resolver = RefResolver(
            base_uri=base_schema_name, referrer=base_schema, store=schema_parts
        )

    def validate(self, config: Dict) -> None:
        self.gutentag_validate(config)
        jsonschema.validate(config, self.base_schema, resolver=self.resolver)

    @staticmethod
    def gutentag_validate(config: Dict) -> None:
        if TIMESERIES not in config:
            raise GutenTAGParseError(f"Key '{TIMESERIES}' not found in root object.")

        for t, ts in enumerate(config.get(TIMESERIES, [])):
            name = ts.get(PARAMETERS.NAME, f"ts_{t}")
            log_prefix = f"TS {name}"

            if ANOMALIES not in ts:
                raise GutenTAGParseError(log_prefix, f"Missing '{ANOMALIES}' property.")

            if BASE_OSCILLATION not in ts and BASE_OSCILLATIONS not in ts:
                raise GutenTAGParseError(
                    log_prefix, f"Missing '{BASE_OSCILLATIONS}' property."
                )

            if BASE_OSCILLATION in ts and PARAMETERS.CHANNELS not in ts:
                raise GutenTAGParseError(
                    log_prefix,
                    f"If a single '{BASE_OSCILLATION}' is defined, the property '{PARAMETERS.CHANNELS}' is required.",
                )

            # check base oscillations
            bos = ts.get(
                BASE_OSCILLATIONS,
                [ts.get(BASE_OSCILLATION)] * ts.get(PARAMETERS.CHANNELS, 0),
            )
            for i, bo in enumerate(bos):
                ConfigValidator._validate_bo(i, bo, log_prefix)

            # check anomaly definitions
            anoms = ts.get(ANOMALIES, [])
            for i, anom in enumerate(anoms):
                ConfigValidator._validate_anomaly(i, anom, log_prefix)

    @staticmethod
    def _validate_bo(i: int, bo: Dict[str, Any], log_prefix: str) -> None:
        log_prefix_bo = f"{log_prefix} BO {i}"
        if PARAMETERS.KIND not in bo:
            raise GutenTAGParseError(
                log_prefix_bo, f"Missing required property '{PARAMETERS.KIND}'."
            )
        bo_kind = bo[PARAMETERS.KIND]
        if bo_kind not in BaseOscillation.key_mapping:
            raise GutenTAGParseError(
                log_prefix_bo,
                f"Base oscillation kind '{bo_kind}' is not supported!",
            )

    @staticmethod
    def _validate_anomaly(i: int, anom: Dict[str, Any], log_prefix: str) -> None:
        log_prefix_anom = f"{log_prefix} Anom {i}"
        if PARAMETERS.KINDS not in anom:
            raise GutenTAGParseError(
                log_prefix_anom,
                f"Missing required property '{PARAMETERS.KINDS}'.",
            )
        if PARAMETERS.LENGTH not in anom:
            raise GutenTAGParseError(
                log_prefix_anom,
                f"Missing required property '{PARAMETERS.LENGTH}'.",
            )

        kinds = anom.get(PARAMETERS.KINDS, [])
        for j, anom_kind in enumerate(kinds):
            log_prefix_kind = f"{log_prefix_anom} Kind {j}"
            if PARAMETERS.KIND not in anom_kind:
                raise GutenTAGParseError(
                    log_prefix_kind,
                    f"Missing required property '{PARAMETERS.KIND}'.",
                )
            if not AnomalyKind.has_value(anom_kind[PARAMETERS.KIND]):
                raise GutenTAGParseError(
                    log_prefix_kind,
                    f"Anomaly kind '{anom_kind[PARAMETERS.KIND]}' is not supported!",
                )
