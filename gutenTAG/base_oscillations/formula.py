# type: ignore  # mypy ends up in recursion
from __future__ import annotations

from enum import Enum
from typing import Optional, List, Dict, Any, NamedTuple, Union

import numpy as np

from . import BaseOscillation
from .interface import BaseOscillationInterface
from ..utils.default_values import default_values
from ..utils.global_variables import (
    BASE_OSCILLATION_NAMES,
    BASE_OSCILLATIONS,
    PARAMETERS,
)
from ..utils.types import BOGenerationContext


BASE = "base"
OPERATION = "operation"
OPERAND = "operand"
AGGREGATION = "aggregation"
KIND = "kind"
AXIS = "axis"


class Formula(BaseOscillationInterface):
    KIND = BASE_OSCILLATION_NAMES.FORMULA

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return None

    def generate_only_base(
        self, ctx: BOGenerationContext, *args, **kwargs
    ) -> np.ndarray:
        c = ctx.previous_channels if ctx.previous_channels else []
        return formula(c, self.formula)


def formula(
    previous_channels: List[np.ndarray] = (),
    formula_dict: Dict[str, Any] = default_values[BASE_OSCILLATIONS][
        PARAMETERS.FORMULA
    ],
) -> np.ndarray:
    return FormulaParser(formula_dict).parse(previous_channels).execute()


BaseOscillation.register(Formula.KIND, Formula)


class OperationType(Enum):
    Plus = "+"
    Minus = "-"
    Multiply = "*"
    Divide = "/"
    Power = "**"

    def __call__(self, operand_a: np.ndarray, operand_b: np.ndarray) -> np.ndarray:
        return eval(f"operand_a {self.value} operand_b")


class AggregationType(Enum):
    Sum = "sum"
    Min = "min"
    Max = "max"
    Median = "median"
    Std = "std"
    Var = "var"

    def __call__(self, base: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
        return eval(f"base.{self.value}(axis=axis)")


class Operation(NamedTuple):
    kind: OperationType
    operand: Union[float, FormulaObj]

    def _get_operand(self) -> np.ndarray:
        if isinstance(self.operand, (float, np.floating)):
            return np.array(self.operand)
        return self.operand.execute()

    def execute(self, base: np.ndarray) -> np.ndarray:
        return self.kind(base, self._get_operand())

    @staticmethod
    def from_dict(d: Dict, prev_channels: List[np.ndarray]) -> Operation:
        kind = OperationType(d.get(KIND))
        operand = d.get(OPERAND)

        if isinstance(operand, (float, np.floating)):
            operand = operand
        elif isinstance(operand, dict):
            operand = FormulaObj.from_dict(operand, prev_channels)
        else:
            raise ValueError(
                "The Operand in Operation has to be either `float` or an `object`"
            )
        return Operation(kind=kind, operand=operand)


class Aggregation(NamedTuple):
    kind: AggregationType
    axis: Optional[int] = None

    def execute(self, base: np.ndarray) -> np.ndarray:
        return self.kind(base, self.axis)

    @staticmethod
    def from_dict(d: Dict) -> Aggregation:
        kind = AggregationType(d.get(KIND))
        axis = d.get(AXIS, None)
        return Aggregation(kind=kind, axis=axis)


class FormulaObj(NamedTuple):
    base: Union[int, FormulaObj]
    prev_channels: List[np.ndarray]
    operation: Optional[Operation] = None
    aggregation: Optional[Aggregation] = None

    def _get_base(self) -> np.ndarray:
        if isinstance(self.base, (int, np.integer)):
            return self.prev_channels[self.base]
        else:
            return self.base.execute()

    def execute(self) -> np.ndarray:
        base = self._get_base()
        if self.operation is not None:
            return self.operation.execute(base)
        elif self.aggregation is not None:
            return self.aggregation.execute(base)
        else:
            return base

    @staticmethod
    def from_dict(d: Dict, prev_channels: List[np.ndarray]) -> FormulaObj:
        base = d.get(BASE)
        operation = d.get(OPERATION, None)
        aggregation = d.get(AGGREGATION, None)
        assert (
            operation is None or aggregation is None
        ), "Only one `operation` or `aggregation` can be set, not both!"

        if isinstance(base, dict):
            base = FormulaObj.from_dict(base, prev_channels=prev_channels)
        elif not isinstance(base, (float, np.floating, int, np.integer)):
            raise ValueError("Base must be `float` or `object`.")

        if operation is not None:
            if isinstance(operation, dict):
                return FormulaObj(
                    base=base,
                    prev_channels=prev_channels,
                    operation=Operation.from_dict(operation, prev_channels),
                )
            else:
                raise ValueError("The Operation has to be an `object`.")
        elif aggregation is not None:
            if isinstance(aggregation, dict):
                return FormulaObj(
                    base=base,
                    prev_channels=prev_channels,
                    aggregation=Aggregation.from_dict(aggregation),
                )
            else:
                raise ValueError("The Aggregation has to be an `object`.")
        else:
            return FormulaObj(base=base, prev_channels=prev_channels)


class FormulaParser:
    def __init__(self, formula: Dict[str, Any]):
        self.formula = formula

    def parse(self, prev_channels: List[np.ndarray]) -> FormulaObj:
        return FormulaObj.from_dict(self.formula, prev_channels)
