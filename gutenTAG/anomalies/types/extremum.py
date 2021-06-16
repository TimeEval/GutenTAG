from __future__ import annotations
from . import BaseAnomaly


class AnomalyExtremum(BaseAnomaly):
    def __init__(self, factor: float, local: bool = False, context_window: int = 5):
        self.factor = factor
        self.local = local
        self.context_window = context_window

    @staticmethod
    def Global(factor: float) -> AnomalyExtremum:
        return AnomalyExtremum(factor, local=False)

    @staticmethod
    def Local(factor: float, context_window: int = 5) -> AnomalyExtremum:
        return AnomalyExtremum(factor, local=True, context_window=context_window)
